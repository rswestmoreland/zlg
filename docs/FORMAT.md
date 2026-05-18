# zlg file format overview

`.zlg` is a line-oriented compressed log archive format. The on-disk format is versioned and frozen at format version 1.

A `.zlg` file contains:

1. a global header;
2. repeated chunks;
3. a seekable directory;
4. a footer.

![zlg file layout](assets/zlg-file-layout.svg)

## Chunks

Each chunk is independent. A chunk contains:

- a chunk header;
- a mesh-bigram search summary;
- a compressed or stored payload.

zlg groups input by lines until a target line count or byte cap is reached. This gives zstd enough data to compress effectively while keeping each decode unit bounded.

The chunk header stores line counts, byte counts, compression mode information, and a CRC over the uncompressed chunk bytes.

## Mesh-bigram summaries

The mesh-bigram summary is a compact per-chunk search filter.

![Mesh-bigram planner](assets/mesh-bigram-planner.svg)

When zlg writes a chunk, it records compact byte-pair clues from the chunk text. When zlg searches, the planner derives selectors from the search pattern and compares them to each chunk summary.

- If the summary proves the pattern cannot be present, zlg skips the chunk.
- If the summary says the chunk might match, zlg decodes the chunk and runs the normal matcher.
- The summary is a filter, not final proof. Candidate chunks are still decoded and matched normally.

## Directory and footer

The footer points to the directory. The directory records chunk offsets, lengths, line counts, and byte counts.

This is what makes file-backed commands efficient:

- `zlg tail` can seek near the end of the archive;
- `zlg info` can report layout metadata without a full decode;
- `zlg stats` can calculate component sizes quickly.

## Checksums

zlg stores a CRC over uncompressed chunk bytes. That means the integrity check is over the data users actually see after decompression.

Default grep output remains streaming for low latency. `zlg grep --strict` verifies each candidate chunk before emitting output from that chunk.
