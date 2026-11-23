# Original PDF behavior catalog

ISO32000-2:2020 index. Heading verification and full-text limitations are in the clause records. PDF1.7 image contracts use separately verified2008 clauses. Exact raster quantization is an observed acceptance rule, not a normative ISO pixel requirement.

One canonical fixture root; no duplicated fixture copies. Boundaries outside declared masks are unscored. Every upstream mapping is currently empty; no source input was executed.

## 07-Syntax/07.04-Filters/07.04.01-General

### img-filter-equivalence-raw

Identical authored RGB sample grid survives the raw image stream route unchanged.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-raw/original.pdf); [clause evidence](filters/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-raw/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-raw/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-filter-equivalence-flate

Identical authored RGB sample grid survives the flate image stream route unchanged.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-flate/original.pdf); [clause evidence](filters/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-flate/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-flate/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-filter-equivalence-runlength

Identical authored RGB sample grid survives the runlength image stream route unchanged.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-runlength/original.pdf); [clause evidence](filters/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-runlength/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.01-General/img-filter-equivalence-runlength/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters

### img-predictor-none

Authored RGB8 sample rows recover exactly through Flate with none prediction.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-none/original.pdf); [clause evidence](predictors/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-none/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-none/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-predictor-tiff-sub

Authored RGB8 sample rows recover exactly through Flate with tiff-sub prediction.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-tiff-sub/original.pdf); [clause evidence](predictors/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-tiff-sub/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-tiff-sub/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-predictor-png-sub

Authored RGB8 sample rows recover exactly through Flate with png-sub prediction.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-sub/original.pdf); [clause evidence](predictors/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-sub/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-sub/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-predictor-png-up

Authored RGB8 sample rows recover exactly through Flate with png-up prediction.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-up/original.pdf); [clause evidence](predictors/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-up/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.04-Filters/07.04.04-LZWDecode-and-FlateDecode-filters/07.04.04.03-LZWDecode-and-FlateDecode-parameters/img-predictor-png-up/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects

### geometry-cropbox-offset

CropBox establishes an offset visible viewport without translating content objects themselves

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-cropbox-offset/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-rotate-90

Rotate 90 displays the page clockwise and swaps the visible width/height

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-rotate-90/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-user-unit-2

UserUnit 2 assigns two 1/72-inch physical units per default user-space unit when supported

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.07-Document-structure/07.07.03-Page-tree/07.07.03.03-Page-objects/geometry-user-unit-2/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries

### resource-page-form-isolation

Page and Form bind /Mark independently; page binding survives the Form call

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-page-form-isolation/original.pdf); [clause evidence](resources/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-page-form-isolation/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-page-form-isolation/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### resource-sibling-form-isolation

Sibling Forms reuse /Mark for different leaf Forms without cross-contamination; page binding remains independent

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-sibling-form-isolation/original.pdf); [clause evidence](resources/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-sibling-form-isolation/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-sibling-form-isolation/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### resource-nested-form-restoration

Nested Form resolves its own /Mark, then restores outer and page name bindings

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-nested-form-restoration/original.pdf); [clause evidence](resources/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-nested-form-restoration/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-nested-form-restoration/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### resource-category-page

The page resolves /Shared independently in its ColorSpace and XObject categories

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page/original.pdf); [clause evidence](resources2/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### resource-category-page-form

A Form binds /Shared to DeviceRGB and its red leaf while the page binds it to DeviceGray and a blue leaf; postForm calls use page bindings

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page-form/original.pdf); [clause evidence](resources2/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page-form/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-page-form/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### resource-category-sibling-forms

Two sibling Forms each resolve /Shared in separate ColorSpace and XObject categories with RGB versus Gray and different leaf colors

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-sibling-forms/original.pdf); [clause evidence](resources2/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-sibling-forms/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/07-Syntax/07.08-Content-streams-and-resources/07.08.03-Resource-dictionaries/resource-category-sibling-forms/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack

### geometry-saved-clip

Q restores the clipping path saved by q

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.02-Graphics-state-stack/geometry-saved-clip/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators

### geometry-concat-order

cm concatenates the user-space scale inside the existing translation

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.04-Graphics-state/08.04.04-Graphics-state-operators/geometry-concat-order/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.05-Path-construction-and-painting

### geometry-fill-rules

Nonzero and even-odd rules treat same-winding nested subpaths differently

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-fill-rules/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-clip-intersection

Successive clipping paths intersect and cannot expand the current clip

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-intersection/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### geometry-clip-path-reset

n ends and clears the current path after W without painting it

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/original.pdf); [clause evidence](geometry/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/geometry-clip-path-reset/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-cap-butt

Open horizontal subpath line cap butt

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-butt/original.pdf); [clause evidence](stroke/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-butt/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-butt/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-cap-round

Open horizontal subpath line cap round

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-round/original.pdf); [clause evidence](stroke/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-round/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-round/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-cap-projecting-square

Open horizontal subpath line cap projecting-square

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-projecting-square/original.pdf); [clause evidence](stroke/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-projecting-square/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-cap-projecting-square/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-join-miter

Ordinary 90-degree miter line join

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-miter/original.pdf); [clause evidence](joins/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-miter/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-miter/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-join-round

Ordinary 90-degree round line join

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-round/original.pdf); [clause evidence](joins/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-round/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-round/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-join-bevel

Ordinary 90-degree bevel line join

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-bevel/original.pdf); [clause evidence](joins/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-bevel/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-join-bevel/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-dash-pair-phase0

Positive even-length dash array and ordinary phase on a straight butt-cap stroke

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase0/original.pdf); [clause evidence](dash/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase0/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase0/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-dash-pair-phase5

Positive even-length dash array and ordinary phase on a straight butt-cap stroke

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase5/original.pdf); [clause evidence](dash/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase5/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-pair-phase5/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### stroke-dash-four-phase2

Positive even-length dash array and ordinary phase on a straight butt-cap stroke

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-four-phase2/original.pdf); [clause evidence](dash/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-four-phase2/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.05-Path-construction-and-painting/stroke-dash-four-phase2/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General

### img-gray2-packed-padding

Two-bit DeviceGray samples are MSB-first and each five-sample row starts at a new byte.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray2-packed-padding/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-gray4-inverted-decode

Four-bit DeviceGray Decode [1 0] reverses tone after unpacking, with independent row padding.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray4-inverted-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-gray8-restricted-decode

DeviceGray Decode [0.2 0.8] maps encoded endpoints and exact thirds into the restricted component range.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-gray8-restricted-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb8-channel-decode

RGB Decode independently reverses red/blue while preserving green; samples stay interleaved RGB.

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-channel-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-indexed2-lookup-padding

Two-bit indices select a nonmonotone RGB lookup directly; five-index scanlines have independent padding.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed2-lookup-padding/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-indexed4-reversed-decode

Indexed four-bit Decode [3 0] maps four exact encoded values to palette indices 3,2,1,0 before lookup.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-indexed4-reversed-decode/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb16-big-endian

Sixteen-bit RGB components use big-endian bytes; replicated-byte samples normalize exactly to their eight-bit values.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb16-big-endian/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-rgb8-mirrored-placement

A negative-x image CTM mirrors columns once while retaining top-to-bottom source row orientation.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/original.pdf); [clause evidence](images/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.05-Image-dictionaries/08.09.05.01-General/img-rgb8-mirrored-placement/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 08-Graphics/08.09-Images/08.09.06-Masked-images

### img-colorkey-control

Original RGB8 control color-key masking; inclusive per-component intersection over authored source samples, composited on white.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-control/original.pdf); [clause evidence](colorkey/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-control/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-control/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-colorkey-exact

Original RGB8 exact color-key masking; inclusive per-component intersection over authored source samples, composited on white.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-exact/original.pdf); [clause evidence](colorkey/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-exact/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-exact/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### img-colorkey-range

Original RGB8 range color-key masking; inclusive per-component intersection over authored source samples, composited on white.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-range/original.pdf); [clause evidence](colorkey/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-range/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/08-Graphics/08.09-Images/08.09.06-Masked-images/img-colorkey-range/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 09-Text/09.03-Text-state-parameters-and-operators

### text-tc-tw-spacing

Independent default/Tc/Tw controls distinguish character advancement from single-byte space advancement.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/text-tc-tw-spacing/original.pdf); [clause evidence](text/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/text-tc-tw-spacing/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/text-tc-tw-spacing/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### textscale-ts-baselines

Positive/negative Ts shifts glyph baselines without changing text-matrix origins or horizontal advances.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/textscale-ts-baselines/original.pdf); [clause evidence](textscale/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/textscale-ts-baselines/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/textscale-ts-baselines/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling

### textscale-tz-shape-advance

Tz scales original glyph width and horizontal advancement, retaining vertical size.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-shape-advance/original.pdf); [clause evidence](textscale/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-shape-advance/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-shape-advance/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### textscale-tz-spacing

Tz scales character spacing and single-byte word spacing together with glyph advancement.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-spacing/original.pdf); [clause evidence](textscale/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-spacing/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-spacing/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### textscale-tz-tj-rise

Tz scales signed TJ displacements and character spacing; Ts shifts painting independently.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-tj-rise/original.pdf); [clause evidence](textscale/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-tj-rise/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.03-Text-state-parameters-and-operators/09.03.04-Horizontal-scaling/textscale-tz-tj-rise/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators

### text-td-line-origin

Td restores the line origin after Tj advances the text matrix.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-td-line-origin/original.pdf); [clause evidence](text/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-td-line-origin/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-td-line-origin/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### text-tm-rotate-replace

Tm rotates glyph shape/advance, then replaces both text matrices with a new ordinary matrix.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-tm-rotate-replace/original.pdf); [clause evidence](text/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-tm-rotate-replace/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.02-Text-positioning-operators/text-tm-rotate-replace/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 09-Text/09.04-Text-objects/09.04.03-Text-showing-operators

### text-tj-signed-adjustment

TJ positive/negative adjustments subtract their thousandths-of-font-size displacement, separate from Tc.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.03-Text-showing-operators/text-tj-signed-adjustment/original.pdf); [clause evidence](text/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.03-Text-showing-operators/text-tj-signed-adjustment/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/09-Text/09.04-Text-objects/09.04.03-Text-showing-operators/text-tj-signed-adjustment/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

## 11-Transparency/11.06-Specifying-transparency-in-PDF

### alpha-fill-endpoints

Nonstroking ca0 leaves the opaque backdrop unchanged; ca1 replaces it.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-fill-endpoints/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-fill-endpoints/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-fill-endpoints/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-stroke-endpoints

Stroking CA0 is invisible; CA1 is opaque, and CA does not suppress an ordinary fill.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-stroke-endpoints/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-stroke-endpoints/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-stroke-endpoints/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-ca-state-restore

Balanced q/Q restores the prior nonstroking alpha after a ca0 scope.

Stage: **pass**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-ca-state-restore/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: [expected-72.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-ca-state-restore/expected-72.png), [expected-144.png](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-ca-state-restore/expected-144.png).

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-fill-fraction06

Normal nonstroking alpha0.6 composites an ordinary red fill over white; byte quantization is measured separately from normative real-valued blending.

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-fill-fraction06/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-stroke-fraction06

Normal stroking alpha0.6 composites an ordinary blue stroke over white while a nonstroking fill remains opaque.

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-stroke-fraction06/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-fill-fraction025

A separate binary-exact ca0.25 control composites red over white; nearest8bit analytic samples are191 for the backdrop channels.

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-fill-fraction025/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.

### alpha-stroke-fraction025

A separate binary-exact CA0.25 control composites blue over white while the ordinary fill remains opaque.

Stage: **mismatch**; page0,72/144DPI, white, annotations off. [Original](../../tests/testdata/pdf-original-v2/11-Transparency/11.06-Specifying-transparency-in-PDF/alpha-stroke-fraction025/original.pdf); [clause evidence](alpha/clause-index.json).

Expected: withheld: reference disagreement.

Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`. Upstream pinned IDs: none; standard-contract-only.
