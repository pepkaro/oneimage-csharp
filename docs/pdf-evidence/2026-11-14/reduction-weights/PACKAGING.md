# Lossless evidence transport

This packaging changes storage only. The original source, analytical result, raw pixels, readable PNGs, and performance conclusions are unchanged. Production Area's controlled median remains **20.50% lower**; fresh-PDF process medians still overlap, so there is no clear end-to-end speedup claim.

The four `.rgba` files are stored as `.rgba.gz`, with gzip level 9, empty original filename and modification time 0. Gzip is lossless. Before/after page buffers are identical, as are before/after Area buffers. Separate filenames preserve the captured experiment's layout. No PNG pixel data is substituted for a raw capture.

The PDF and already-compressed numerical RGB source are stored unchanged. Their size has not been treated as an unsupported limit; no chunks or reconstructed PDF syntax are involved. All PNGs remain directly readable in the pull request.

## Reconstruct the exact original package

Use Python 3's standard library, no network or rendering dependency:

```sh
# From the transport package directory:
sha256sum -c TRANSPORT-SHA256SUMS
python tools/restore-evidence.py /absolute/new/reconstructed-evidence
cd /absolute/new/reconstructed-evidence
sha256sum -c SHA256SUMS
# With the dependencies listed in the original provenance installed:
OPENBLAS_NUM_THREADS=1 python tools/check.py
python tools/summarize-timing.py
sha256sum -c SHA256SUMS
```

The output must be absent or empty and separate from this transport package. The script refuses to overwrite existing work. It checks the stored size/SHA-256, decompresses gzip entries, checks every original size/SHA-256, and only then writes all 60 original files. Reconstruction is byte-for-byte, including the captured README, reproduction instructions, manifest and checksums. It does not rerender, reinterpret pixels, rerun performance measurements, use the network, or alter the transport package.

`transport-manifest.json` is an explicit mapping between original and stored filenames, encodings, lengths and SHA-256 values. The original `manifest.json` remains at its original path with exactly its original bytes. It is never embedded or duplicated under another filename. `SHA256SUMS` also remains the original capture's checksum list. README/reproduction have transport notices; their frozen originals are retained under `transport/original-documents/` solely for exact reconstruction. `TRANSPORT-SHA256SUMS` covers the files actually stored in this transport package (excluding itself).

The complete frozen original package is retained separately by the reviewer and was not deleted or modified. Compression output was generated twice and compared, then the complete package was reconstructed and every file hash checked against the frozen originals. Recompression with another zlib version may produce different gzip bytes; decompression must still produce the exact recorded original hashes.

This is packaging, not an authorization workaround: the original manifest is unchanged. Publication and any retry remain the publisher's responsibility. No remote write is performed by these tools.
