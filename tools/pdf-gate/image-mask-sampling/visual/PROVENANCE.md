# Opaque-mask sampling: three original MIT images

Adding a fully opaque mask should not change a color image. In this fixture, the old renderer incorrectly enlarges a 3×5 color image to the 7×11 mask grid with bilinear filtering, despite both Interpolate flags being false. It introduces extra blended colors. The corrected renderer preserves the original 3×5 grid and matches the PDFium reference exactly in RGB for this case.

Use these three existing, unmodified PNGs in order:

1. **before.png:** OneImage e43ee264954a177ff01a16584625a3dea79244fa with unmodified OnePDF d813ec6ba9dd138f7d2a6f3b8f5a51dc9c5f4bc8 (source version 1.22).
2. **after.png:** the final independent-sampling and narrow fast-path candidate against those same bases. OneImage cumulative patch SHA-256 d65b422144deb43f5172f42402713e20b81a3db5269855cd89965cc42db75cf4; separate OnePDF API patch SHA-256 993d2f3a7db2d555ea3918553acd0f8a6a793f1295826cc434a5deb511aef41f.
3. **pdfium-reference.png:** PDFium 153.0.7999.0 through pypdfium2 5.13.0.

All three show the same original numerical PDF at 72 DPI, 240×222 pixels, on opaque white. The two OneImage renders use degree 1. The after PNG is byte-identical to the prior corrected PNG used by the stored independent comparison. That comparison reports 36,720 pixels differing from PDFium by more than two channel values before, and zero differing RGB pixels after. This establishes agreement for this fixture only; interpolation, minification and other reference-engine disagreements remain documented in the broader correctness report.

## Original fixture and generator

The companion **3x5-7x11-opaque.pdf** is an original MIT numerical fixture, not a modified or extracted third-party document. It has a 3×5 DeviceRGB image and a fully opaque 7×11 DeviceGray soft mask, both 8-bit with Interpolate false, no Matte, and mask Decode [0 1]. Page size is 240×222 points; placement is [210 0 0 198 15 12]. Color samples for coordinates x,y are generated as:

- Red: 37 + (59x + 17y) mod 197.
- Green: 29 + (31x + 67y) mod 211.
- Blue: 19 + (83x + 43y) mod 223.
- Every mask sample: 255.

The existing source review already includes **tools/pdf-gate/generate_image_mask_sampling.py**. Run it with --out DIRECTORY; this fixture appears at DIRECTORY/fixtures/3x5-7x11-opaque.pdf. The generator creates other controls too, but they are not included in this visual selection.

No private PDF, imported artwork, font, ICC profile, borrowed audit asset or material from another rendering unit is included. The MIT license covers this original fixture and its visual evidence. External renderer software is not redistributed. These three PNGs have not been resized, cropped, retouched, composited or re-encoded. Full raw observations, binary dumps and all other image/reference collections are explicitly omitted.

## Exact selected hashes

| Selected file | SHA-256 |
|---|---|
| before.png | 8f9ae747bb4a0d52858c3e5c3587aed2b742aeb9601672601eca599d780ec54a |
| after.png | 8eca32f4c186e3a9b8920c3b7e78cc086757023b09c2e0e9f69515f76c7d4b72 |
| pdfium-reference.png | 64ae4cdda2c098ef7534eac4054149a53f42c9fd553d62475e98e17de0ca60b0 |
| 3x5-7x11-opaque.pdf | df062c22c0af4e2de56585bcfc965c4e518eef30626f84e4b6998e1f19cf908a |
| generate_image_mask_sampling.py | c8fbf45725872a9560f30a44da81c7df2f576c933822563999f00d46cbe7cd11 |
| LICENSE | f335dd4613c04c2e0f0186d7febd013d25da3ab794a89674db2373d6d35182c5 |
