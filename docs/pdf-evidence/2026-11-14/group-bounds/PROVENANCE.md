# MIT-only evidence asset audit

The newly authored contents of this directory are explicitly MIT licensed under `LICENSE`. The original project history and dependency licenses are not modified or relicensed.

## Inputs

- `generate.py` is an independently written small Python PDF assembler for this review. It creates every PDF object, stream, cross-reference offset and sample from code. It does not open any PDF, image, profile or font as an input.
- The numerical workload is the original narrow-group benchmark introduced in the user's fork by commit `c705783366878618d17e3d60f7d64c838d20f42f`: 40 or 400 thin vector groups on an opaque, flat-color page. That benchmark was added by the user's rendering work, not imported from an upstream PDF corpus. Reusing its numerical scenario permits the before/after comparison to test the same issue.
- `fixtures/group-performance-40.pdf` and `fixtures/group-performance-400.pdf` are fresh outputs of this generator. They contain only generated PDF structure and vector drawing operators. They contain no fonts, image XObjects, user document metadata, copyrighted sourcebook material, or imported fixture data.
- No CC, BSD, Apache-only, uncertain-license, or other upstream PDF assets are included. No upstream PDF is copied, modified, or relicensed.

## Outputs

- The four `renders/01/*.png` files are full, unaltered OneImage renders of only the original MIT inputs above. The harness copies the renderer's RGBA pixels and encodes that same array without resizing or retouching. There are no derived images from any other source.
- The JSON manifests and measurements record those generated inputs and outputs. They contain no user document names or pixels.
- The C# harness, shell reproduction script and documentation were written for this review package and are MIT licensed here. They call the existing OneImage APIs; the compiled libraries are not redistributed in this package.

## Boundary

This audit covers exactly this evidence directory's files listed in `SHA256SUMS`. It does not claim that every pre-existing repository file or software dependency has been relicensed to MIT. No code-history, dependency-license, author or signing changes are part of this evidence publication.
