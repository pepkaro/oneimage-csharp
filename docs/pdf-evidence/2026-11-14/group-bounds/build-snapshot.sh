#!/usr/bin/env bash
# Build an immutable source snapshot without changing the caller's checkout or git identity.
set -euo pipefail
REPO=${1:?Pass a local clone of pepkaro/oneimage-csharp}
SHA=${2:?Pass the full source commit}
WORK=${3:?Pass an empty worker-owned artifact directory}
WORK=$(realpath -m "$WORK")
KEY=${SHA:0:7}
mkdir -p "$WORK/sources/$KEY" "$WORK/logs"
git -C "$REPO" cat-file -e "$SHA^{commit}"
git -C "$REPO" archive "$SHA" | tar -x -C "$WORK/sources/$KEY"
export ONEIMAGE_ARTIFACTS="$WORK/artifacts/$KEY"
dotnet build "$WORK/sources/$KEY/tests/OneImage.Pdf.Tests/OneImage.Pdf.Tests.csproj" -c Release --nologo -m:1 | tee "$WORK/logs/$KEY-build.log"
dotnet "$ONEIMAGE_ARTIFACTS/bin/OneImage.Pdf.Tests/release/OneImage.Pdf.Tests.dll" | tee "$WORK/logs/$KEY-tests.log"
echo "Source commit: $SHA"
echo "Source tree: $(git -C "$REPO" rev-parse "$SHA^{tree}")"
