# Original PDF behavior catalog

ISO32000-2:2020 index. Heading verification and full-text limitations are in the clause records. PDF1.7 image contracts use separately verified2008 clauses. Exact raster quantization is an observed acceptance rule, not a normative ISO pixel requirement.

One canonical fixture root; no duplicated fixture copies. Boundaries outside declared masks are unscored. Every upstream mapping is currently empty; no source input was executed.

## 07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects

### geometry-cropbox-offset

CropBox establishes an offset visible viewport without translating content objects themselves

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-rotate-90

Rotate 90 displays the page clockwise and swaps the visible width/height

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-user-unit-2

UserUnit 2 assigns two 1/72-inch physical units per default user-space unit when supported

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack

### geometry-saved-clip

Q restores the clipping path saved by q

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators

### geometry-concat-order

cm concatenates the user-space scale inside the existing translation

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.05-Path-construction-and-painting

### geometry-fill-rules

Nonzero and even-odd rules treat same-winding nested subpaths differently

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-clip-intersection

Successive clipping paths intersect and cannot expand the current clip

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-clip-path-reset

n ends and clears the current path after W without painting it

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General

### img-gray2-packed-padding

Two-bit DeviceGray samples are MSB-first and each five-sample row starts at a new byte.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-gray4-inverted-decode

Four-bit DeviceGray Decode [1 0] reverses tone after unpacking, with independent row padding.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-gray8-restricted-decode

DeviceGray Decode [0.2 0.8] maps encoded endpoints and exact thirds into the restricted component range.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb8-channel-decode

RGB Decode independently reverses red/blue while preserving green; samples stay interleaved RGB.

Stage: **generated**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-channel-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-indexed2-lookup-padding

Two-bit indices select a nonmonotone RGB lookup directly; five-index scanlines have independent padding.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-indexed4-reversed-decode

Indexed four-bit Decode [3 0] maps four exact encoded values to palette indices 3,2,1,0 before lookup.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb16-big-endian

Sixteen-bit RGB components use big-endian bytes; replicated-byte samples normalize exactly to their eight-bit values.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb8-mirrored-placement

A negative-x image CTM mirrors columns once while retaining top-to-bottom source row orientation.

Stage: **agreed**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.
