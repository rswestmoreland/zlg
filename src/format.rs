use crate::chunk::PlainChunk;
use crate::search::{SearchSummary, SearchSummaryMode};

use anyhow::{anyhow, Context, Result};
use crc32fast::Hasher;
use std::io::{Cursor, ErrorKind, Read, Write};

const GLOBAL_MAGIC: &[u8; 8] = b"ZLG1P0\0\0";
const CHUNK_MAGIC: &[u8; 4] = b"ZCH1";
const DIR_MAGIC: &[u8; 4] = b"ZDR1";
const FOOTER_MAGIC: &[u8; 4] = b"ZFT1";
const GLOBAL_HEADER_LEN: u16 = 32;
const CHUNK_HEADER_LEN: u16 = 64;
const DIRECTORY_ENTRY_LEN: u32 = 64;
const FORMAT_VERSION: u16 = 1;

#[derive(Clone, Debug)]
pub struct ChunkHeader {
    pub flags: u16,
    pub chunk_index: u64,
    pub first_line_number: u64,
    pub line_count: u64,
    pub uncompressed_len: u64,
    pub compressed_len: u64,
    pub summary_len: u32,
    pub crc32: u32,
}

#[derive(Clone, Debug)]
pub struct DirectoryEntry {
    pub chunk_offset: u64,
    pub summary_offset: u64,
    pub summary_len: u32,
    pub compressed_offset: u64,
    pub compressed_len: u64,
    pub uncompressed_len: u64,
    pub first_line_number: u64,
    pub line_count: u64,
    pub flags: u32,
}

#[derive(Debug)]
pub struct RawChunk {
    pub header: ChunkHeader,
    pub summary: SearchSummary,
    compressed: Vec<u8>,
}

#[derive(Debug)]
pub struct DecodedChunk {
    pub header: ChunkHeader,
    pub data: Vec<u8>,
}

impl RawChunk {
    pub fn decode(self) -> Result<DecodedChunk> {
        let data = zstd::stream::decode_all(Cursor::new(&self.compressed))
            .context("failed to decode zstd chunk")?;

        if data.len() as u64 != self.header.uncompressed_len {
            return Err(anyhow!(
                "chunk {} decoded length mismatch: expected {}, got {}",
                self.header.chunk_index,
                self.header.uncompressed_len,
                data.len()
            ));
        }

        let crc = crc32(&data);
        if crc != self.header.crc32 {
            return Err(anyhow!(
                "chunk {} crc mismatch: expected {:#010x}, got {:#010x}",
                self.header.chunk_index,
                self.header.crc32,
                crc
            ));
        }

        Ok(DecodedChunk {
            header: self.header,
            data,
        })
    }
}

#[derive(Debug)]
pub struct ZlgWriter<W: Write> {
    writer: CountingWriter<W>,
    level: i32,
    summary_mode: SearchSummaryMode,
    directory: Vec<DirectoryEntry>,
    total_uncompressed_len: u64,
    total_lines: u64,
}

impl<W: Write> ZlgWriter<W> {
    pub fn new(
        writer: W,
        chunk_policy_id: u32,
        level: i32,
        summary_mode: SearchSummaryMode,
    ) -> Result<Self> {
        let mut writer = CountingWriter::new(writer);

        writer.write_all(GLOBAL_MAGIC)?;
        write_u16(&mut writer, FORMAT_VERSION)?;
        write_u16(&mut writer, GLOBAL_HEADER_LEN)?;
        write_u32(&mut writer, 0)?;
        write_u32(&mut writer, chunk_policy_id)?;
        write_u32(&mut writer, 0)?;
        writer.write_all(&[0u8; 8])?;

        Ok(Self {
            writer,
            level,
            summary_mode,
            directory: Vec::new(),
            total_uncompressed_len: 0,
            total_lines: 0,
        })
    }

    pub fn write_chunk(&mut self, chunk: &PlainChunk) -> Result<()> {
        let chunk_offset = self.writer.bytes_written();
        let summary_bytes = match self.summary_mode {
            SearchSummaryMode::Bitmap => SearchSummary::from_bytes(&chunk.data).encode(),
            SearchSummaryMode::None => Vec::new(),
        };

        let compressed = zstd::stream::encode_all(Cursor::new(&chunk.data), self.level)
            .context("failed to encode zstd chunk")?;

        let header = ChunkHeader {
            flags: chunk.flags,
            chunk_index: chunk.index,
            first_line_number: chunk.first_line_number,
            line_count: chunk.line_count,
            uncompressed_len: chunk.data.len() as u64,
            compressed_len: compressed.len() as u64,
            summary_len: summary_bytes.len() as u32,
            crc32: crc32(&chunk.data),
        };

        self.write_chunk_header(&header)?;
        let summary_offset = self.writer.bytes_written();
        self.writer.write_all(&summary_bytes)?;
        let compressed_offset = self.writer.bytes_written();
        self.writer.write_all(&compressed)?;

        self.directory.push(DirectoryEntry {
            chunk_offset,
            summary_offset,
            summary_len: header.summary_len,
            compressed_offset,
            compressed_len: header.compressed_len,
            uncompressed_len: header.uncompressed_len,
            first_line_number: header.first_line_number,
            line_count: header.line_count,
            flags: header.flags as u32,
        });

        self.total_uncompressed_len += header.uncompressed_len;
        self.total_lines += header.line_count;

        Ok(())
    }

    pub fn finish(mut self) -> Result<W> {
        let directory_offset = self.writer.bytes_written();

        self.writer.write_all(DIR_MAGIC)?;
        write_u32(&mut self.writer, DIRECTORY_ENTRY_LEN)?;
        write_u64(&mut self.writer, self.directory.len() as u64)?;

        for entry in &self.directory {
            write_u64(&mut self.writer, entry.chunk_offset)?;
            write_u64(&mut self.writer, entry.summary_offset)?;
            write_u32(&mut self.writer, entry.summary_len)?;
            write_u32(&mut self.writer, entry.flags)?;
            write_u64(&mut self.writer, entry.compressed_offset)?;
            write_u64(&mut self.writer, entry.compressed_len)?;
            write_u64(&mut self.writer, entry.uncompressed_len)?;
            write_u64(&mut self.writer, entry.first_line_number)?;
            write_u64(&mut self.writer, entry.line_count)?;
        }

        let directory_len = self.writer.bytes_written() - directory_offset;

        self.writer.write_all(FOOTER_MAGIC)?;
        write_u32(&mut self.writer, 48)?;
        write_u64(&mut self.writer, self.directory.len() as u64)?;
        write_u64(&mut self.writer, self.total_lines)?;
        write_u64(&mut self.writer, self.total_uncompressed_len)?;
        write_u64(&mut self.writer, directory_offset)?;
        write_u64(&mut self.writer, directory_len)?;

        self.writer.flush()?;
        Ok(self.writer.into_inner())
    }

    fn write_chunk_header(&mut self, header: &ChunkHeader) -> Result<()> {
        self.writer.write_all(CHUNK_MAGIC)?;
        write_u16(&mut self.writer, CHUNK_HEADER_LEN)?;
        write_u16(&mut self.writer, header.flags)?;
        write_u64(&mut self.writer, header.chunk_index)?;
        write_u64(&mut self.writer, header.first_line_number)?;
        write_u64(&mut self.writer, header.line_count)?;
        write_u64(&mut self.writer, header.uncompressed_len)?;
        write_u64(&mut self.writer, header.compressed_len)?;
        write_u32(&mut self.writer, header.summary_len)?;
        write_u32(&mut self.writer, header.crc32)?;
        write_u64(&mut self.writer, 0)?;
        Ok(())
    }
}

#[derive(Debug)]
pub struct ZlgReader<R: Read> {
    reader: R,
    finished: bool,
}

impl<R: Read> ZlgReader<R> {
    pub fn new(mut reader: R) -> Result<Self> {
        let mut magic = [0u8; 8];
        reader
            .read_exact(&mut magic)
            .context("failed to read zlg global header")?;

        if &magic != GLOBAL_MAGIC {
            return Err(anyhow!("unsupported or invalid zlg magic"));
        }

        let version = read_u16(&mut reader)?;
        if version != FORMAT_VERSION {
            return Err(anyhow!("unsupported zlg version {version}"));
        }

        let header_len = read_u16(&mut reader)?;
        if header_len != GLOBAL_HEADER_LEN {
            return Err(anyhow!("unsupported zlg header length {header_len}"));
        }

        let _flags = read_u32(&mut reader)?;
        let _chunk_policy_id = read_u32(&mut reader)?;
        let _reserved0 = read_u32(&mut reader)?;

        let mut reserved = [0u8; 8];
        reader.read_exact(&mut reserved)?;

        Ok(Self {
            reader,
            finished: false,
        })
    }

    pub fn next_raw_chunk(&mut self) -> Result<Option<RawChunk>> {
        if self.finished {
            return Ok(None);
        }

        let mut magic = [0u8; 4];
        match self.reader.read_exact(&mut magic) {
            Ok(()) => {}
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => {
                self.finished = true;
                return Ok(None);
            }
            Err(error) => return Err(error).context("failed to read next zlg record magic"),
        }

        if &magic == DIR_MAGIC {
            self.skip_directory()?;
            self.skip_footer_if_present()?;
            self.finished = true;
            return Ok(None);
        }

        if &magic != CHUNK_MAGIC {
            return Err(anyhow!("unexpected zlg record magic: {:?}", magic));
        }

        let header = self.read_chunk_header_after_magic()?;

        let mut summary_bytes = vec![0u8; header.summary_len as usize];
        self.reader
            .read_exact(&mut summary_bytes)
            .context("failed to read chunk search summary")?;
        let summary = SearchSummary::decode(&summary_bytes)?;

        let mut compressed = vec![0u8; header.compressed_len as usize];
        self.reader
            .read_exact(&mut compressed)
            .context("failed to read compressed chunk payload")?;

        Ok(Some(RawChunk {
            header,
            summary,
            compressed,
        }))
    }

    fn read_chunk_header_after_magic(&mut self) -> Result<ChunkHeader> {
        let header_len = read_u16(&mut self.reader)?;
        if header_len != CHUNK_HEADER_LEN {
            return Err(anyhow!("unsupported zlg chunk header length {header_len}"));
        }

        let flags = read_u16(&mut self.reader)?;
        let chunk_index = read_u64(&mut self.reader)?;
        let first_line_number = read_u64(&mut self.reader)?;
        let line_count = read_u64(&mut self.reader)?;
        let uncompressed_len = read_u64(&mut self.reader)?;
        let compressed_len = read_u64(&mut self.reader)?;
        let summary_len = read_u32(&mut self.reader)?;
        let crc32 = read_u32(&mut self.reader)?;
        let _reserved = read_u64(&mut self.reader)?;

        Ok(ChunkHeader {
            flags,
            chunk_index,
            first_line_number,
            line_count,
            uncompressed_len,
            compressed_len,
            summary_len,
            crc32,
        })
    }

    fn skip_directory(&mut self) -> Result<()> {
        let entry_len = read_u32(&mut self.reader)?;
        if entry_len != DIRECTORY_ENTRY_LEN {
            return Err(anyhow!(
                "unsupported zlg directory entry length {entry_len}"
            ));
        }

        let entry_count = read_u64(&mut self.reader)?;
        let total_len = entry_len as u64 * entry_count;
        copy_n_to_sink(&mut self.reader, total_len)?;
        Ok(())
    }

    fn skip_footer_if_present(&mut self) -> Result<()> {
        let mut magic = [0u8; 4];
        match self.reader.read_exact(&mut magic) {
            Ok(()) => {}
            Err(error) if error.kind() == ErrorKind::UnexpectedEof => return Ok(()),
            Err(error) => return Err(error).context("failed to read zlg footer magic"),
        }

        if &magic != FOOTER_MAGIC {
            return Err(anyhow!("expected zlg footer magic after directory"));
        }

        let footer_len = read_u32(&mut self.reader)?;
        if footer_len < 8 {
            return Err(anyhow!("invalid footer length {footer_len}"));
        }

        copy_n_to_sink(&mut self.reader, (footer_len - 8) as u64)?;
        Ok(())
    }
}

#[derive(Debug)]
struct CountingWriter<W: Write> {
    inner: W,
    bytes_written: u64,
}

impl<W: Write> CountingWriter<W> {
    fn new(inner: W) -> Self {
        Self {
            inner,
            bytes_written: 0,
        }
    }

    fn bytes_written(&self) -> u64 {
        self.bytes_written
    }

    fn into_inner(self) -> W {
        self.inner
    }
}

impl<W: Write> Write for CountingWriter<W> {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        let written = self.inner.write(buf)?;
        self.bytes_written += written as u64;
        Ok(written)
    }

    fn flush(&mut self) -> std::io::Result<()> {
        self.inner.flush()
    }
}

fn copy_n_to_sink<R: Read>(reader: &mut R, mut len: u64) -> Result<()> {
    let mut buffer = [0u8; 8192];

    while len > 0 {
        let want = buffer.len().min(len as usize);
        reader.read_exact(&mut buffer[..want])?;
        len -= want as u64;
    }

    Ok(())
}

fn crc32(bytes: &[u8]) -> u32 {
    let mut hasher = Hasher::new();
    hasher.update(bytes);
    hasher.finalize()
}

fn write_u16<W: Write>(writer: &mut W, value: u16) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn write_u32<W: Write>(writer: &mut W, value: u32) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn write_u64<W: Write>(writer: &mut W, value: u64) -> Result<()> {
    writer.write_all(&value.to_le_bytes())?;
    Ok(())
}

fn read_u16<R: Read>(reader: &mut R) -> Result<u16> {
    let mut bytes = [0u8; 2];
    reader.read_exact(&mut bytes)?;
    Ok(u16::from_le_bytes(bytes))
}

fn read_u32<R: Read>(reader: &mut R) -> Result<u32> {
    let mut bytes = [0u8; 4];
    reader.read_exact(&mut bytes)?;
    Ok(u32::from_le_bytes(bytes))
}

fn read_u64<R: Read>(reader: &mut R) -> Result<u64> {
    let mut bytes = [0u8; 8];
    reader.read_exact(&mut bytes)?;
    Ok(u64::from_le_bytes(bytes))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::chunk::PlainChunk;

    #[test]
    fn round_trip_single_chunk_in_memory() {
        let chunk = PlainChunk {
            index: 0,
            first_line_number: 1,
            line_count: 2,
            data: b"alpha\nbeta\n".to_vec(),
            flags: 1,
        };

        let mut out = Vec::new();
        {
            let mut writer = ZlgWriter::new(&mut out, 1, 1, SearchSummaryMode::Bitmap).unwrap();
            writer.write_chunk(&chunk).unwrap();
            writer.finish().unwrap();
        }

        let mut reader = ZlgReader::new(Cursor::new(out)).unwrap();
        let raw = reader.next_raw_chunk().unwrap().unwrap();
        let decoded = raw.decode().unwrap();

        assert_eq!(decoded.data, b"alpha\nbeta\n");
        assert!(reader.next_raw_chunk().unwrap().is_none());
    }
}
