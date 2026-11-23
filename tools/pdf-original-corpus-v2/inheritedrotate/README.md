# ISO-PAGE-ATTRIBUTE-INHERIT-02

Three independently authored valid MIT PDF1.7 files provide five page-view cases. Only Rotate inheritance changes. All leaf pages explicitly declare MediaBox=CropBox[10,20,170,120], empty Resources and no UserUnit. Direct numeric red[30,40,20,15] and blue[120,80,30,20] rectangles are asymmetric. No Forms, fonts, images, borrowed fixtures, private inputs or malformed/recovery behavior.

* rotate-inheritance-root.pdf: one page inherits root Rotate90.
* rotate-inheritance-explicit.pdf: one page explicitly sets Rotate0, overriding root90.
* rotate-inheritance-siblings.pdf: first root sibling90, nested page inheriting nearer Pages270, then later root sibling90. These three views share one fixture_id/file/sha256, page0/1/2 and page_count3. Count unique PDFs as3, views as5.

Before capture, visible positions were independently declared using unrotated box-local(u,v),W160,H100:0 maps(u,v),90 maps(v,W-u),270 maps(H-v,u). Rectangles transform by all corners. Display dimensions are160x100 for0 and100x160 for90/270;144DPI doubles these. Sample/region coordinates are upright visible display points after the offset box and page rotation; image row=floor((height-y)*dpi/72). Exact PDF-to-device72DPI matrices are in manifest.

Run `bash reproduce.sh`. generator.py writes deterministic source and manifest. verify-structure.py traverses raw Parent/Kids/Count and nearest Rotate owners before flattening, asserts explicit boxes/empty resources and parses vector operands. It separately rotates all box/rectangle corners with integer-rounded sine/cosine and translates the rotated minimum corner, verifying dimensions, positions and matrices. references.py/render-pdfjs.mjs select each page and assert document page_count. score.py constructs analytic rectangles/background before reading outputs. verify.py checks hashes, deterministic regeneration, dimensions and scores; verify-regions.py checks inset controls.

Pins:PDFium153.0.7999.0/pypdfium2 5.13.0;MuPDF1.26.11/PyMuPDF1.26.6;PDF.js6.5.438/build0a4153349,@napi-rs/canvas1.1.1,Node24.22.3. PDFJS_ROOT defaults to the configured checkpoint package path. Python requires NumPy/Pillow/pypdf6.21.4. This is Node Canvas, not WebView.

Results:3uniquePDFs/1993bytes,5page views,30freshreference captures.30analytic passes,0failures,0skips;180named samples,180inset region checks,30pairwise checks and5parsed structure views pass. Predeclared one-device-pixel rectangle boundary bands are unscored. All first captures passed; no expectations were changed after capture. engine-call-accounting.json records exactly30own calls:10PDFium library renders,10MuPDF library renders and10PDF.js Node subprocess renders. One reference-driver execution; no full/partial reruns. Later structural/image verification does not render. Root replay/product calls are separate.

Official2020 public errata verifies7.7.3.4 number/title by the7.8.3 cross-reference and7.7.3.3/Table31 page-object heading. Full unchanged Rotate row and complete inheritance wording remain pending full official text. Verified2008 7.7.3.3/Table30 defines Rotate as inheritable clockwise multiples of90 with default0;7.7.3.4 governs local/ancestor attributes. clause-index.json records limits. Exact RGB scoring is an analytic route criterion, not a normative ISO antialiasing mandate.

Baseline remote688d99e.../localf4a7fe39.../treea3b4932d73af4e3eee35b7d2cea1be11db5585a9 is preserved. Read prior instructions/backlog only; all writes remain in this new inheritedrotate directory. New numeric PDFs/rotation trees and expectations are independent MIT originals; own prior MIT adapter/scoring scaffolding is reused. No exact upstream metadata mapping was established; all upstream IDs null and zero upstream input executions. Root accepts agreed expectations before product grading; no product grading or remote writes here.

Next proposed unclaimed slice:ISO-PAGE-ATTRIBUTE-INHERIT-03, ordinary inherited CropBox with complete local override, nearer ancestor and sibling isolation, using valid in-MediaBox bounds and independent dimensions/inset coordinates. No ownership of the next slice is claimed.
