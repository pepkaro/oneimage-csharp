# ISO-PAGE-ATTRIBUTE-INHERIT-01

Three independently authored valid MIT PDF1.7 files give five page views. Only ordinary page-tree MediaBox inheritance varies. All leaf pages have explicit empty Resources, direct numeric red/blue rectangles, no Forms/fonts/images, no CropBox/Rotate/UserUnit overrides, and no private/upstream assets.

* mediabox-inheritance-root.pdf: one page inherits root MediaBox[10,20,170,120], yielding160x100points.
* mediabox-inheritance-explicit.pdf: one page locally overrides that root with[0,0,120,80], yielding120x80points.
* mediabox-inheritance-siblings.pdf: root child inherits160x100; nested child inherits nearer Pages MediaBox[-10,-10,130,80], yielding140x90; later root sibling returns to160x100. Its three views share one file/fixture_id/sha256 and use page0/1/2,page_count3.

Each page paints red[30,40,20,15] and blue[80,60,20,15] in PDF default space. Analytic visible rectangles subtract the effective MediaBox lower-left; exact device transformation at72DPI is recorded. Insets and named points use upright visible page points after origin translation, not untranslated PDF default coordinates. Image row=floor((height-y)*dpi/72). Thus dimensions and coordinate translations are independently tested at72/144physicalDPI.

Run `bash reproduce.sh`. generator.py deterministically creates PDFs/manifest; verify-structure.py parses the raw page tree before flattening, asserting Parent/Kids/Count, local versus inherited MediaBox owners, empty Resources and actual vector operands. It independently transforms parsed rectangle operands and checks dimensions. references.py and render-pdfjs.mjs select the explicit page, assert document page_count and pinned versions. score.py constructs analytic interiors before reading outputs; verify.py checks hashes/dimensions/results and in-memory deterministic regeneration; verify-regions.py checks separate inset controls. pypdf6.21.4 is pinned for structural checks; NumPy/Pillow are required.

Reference pins:PDFium153.0.7999.0/pypdfium2 5.13.0;MuPDF1.26.11/PyMuPDF1.26.6;PDF.js6.5.438/build0a4153349,@napi-rs/canvas1.1.1,Node24.22.3. PDFJS_ROOT defaults to the configured existing cloud package installation. This is Node Canvas, not browser WebView.

Results:3uniquePDFs/1808bytes,5page views,30freshreference captures.30analytic passes,0failures,0skips;180named samples,180inset region checks and30pairwise checks pass.5parsed structure views pass. Rectangle boundaries within one device pixel are predeclared unscored. No expectations changed after capture, and no disagreement was hidden. Do not count shared page views or repeated identical output bytes as new PDFs. Root selects accepted expectations and grades product after integration; no product grading ran here.

Official2020 public errata verifies the7.7.3.4 number/title cross-reference via7.8.3, plus7.7.3.3 page objects and7.7.3.2 count corrections. The full2020 MediaBox/nearest-ancestor wording remains pending. Verified2008 7.7.3.3/Table30 and7.7.3.4 govern these1.7inheritance controls;8.3.2.3 supplies coordinate context. clause-index.json records exact limits. No ISO-mandated pixel quantization or upstream-suite parity is claimed.

Prior baseline#94 1cd8573/tree22257be8e is preserved. Read-only instruction repository9b4b911... has tree22257be8ecf9bc14a30db43c721db374e0da7fd0. Only this new pageattributes directory changed. Numeric PDFs, MediaBox choices and analytic geometry are original MIT work; own prior MIT adapters/scoring scaffolding are reused. All upstream IDs null; no upstream bytes executed, product source changes or remote writes.

Next proposed unclaimed slice:ISO-PAGE-ATTRIBUTE-INHERIT-02, valid inherited Rotate with a local page override and a nearer Pages ancestor, including asymmetric point controls and sibling isolation. No ownership of that next slice is claimed.
