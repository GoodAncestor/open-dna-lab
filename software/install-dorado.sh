#!/usr/bin/env bash
# Install Dorado and fetch basecalling models.
#
# Dorado ships as a standalone binary, not through conda. The Linux x64 build
# bundles CUDA. Apple Silicon uses Metal.
#
# Check github.com/nanoporetech/dorado/releases for the current version and
# update DORADO_VER below.

set -euo pipefail

DORADO_VER="${DORADO_VER:-1.0.0}"
PREFIX="${PREFIX:-$HOME/.local}"
MODEL_DIR="${MODEL_DIR:-$HOME/dorado-models}"

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)   PLAT="linux-x64"  ;;
  Darwin-arm64)   PLAT="osx-arm64"  ;;
  *) echo "Unsupported platform: $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

TARBALL="dorado-${DORADO_VER}-${PLAT}.tar.gz"
URL="https://cdn.oxfordnanoportal.com/software/analysis/${TARBALL}"

echo "Platform : ${PLAT}"
echo "Version  : ${DORADO_VER}"
echo "Prefix   : ${PREFIX}"

mkdir -p "${PREFIX}" "${MODEL_DIR}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

echo "Downloading ${URL}"
curl -fSL "${URL}" -o "${tmp}/${TARBALL}"
tar -xzf "${tmp}/${TARBALL}" -C "${tmp}"
cp -r "${tmp}/dorado-${DORADO_VER}-${PLAT}/"* "${PREFIX}/"

export PATH="${PREFIX}/bin:${PATH}"
dorado --version

# Models. sup is the accuracy tier; the 5mCG_5hmCG model adds methylation
# calling in CpG context. Both are needed for epigenome work.
echo "Fetching models into ${MODEL_DIR}"
cd "${MODEL_DIR}"
dorado download --model dna_r10.4.1_e8.2_400bps_sup@v5.2.0
dorado download --model dna_r10.4.1_e8.2_400bps_hac@v5.2.0
dorado download --model dna_r10.4.1_e8.2_400bps_sup@v5.2.0_5mCG_5hmCG@v3

cat <<EOF

Done. Add to your shell profile:

  export PATH="${PREFIX}/bin:\$PATH"
  export DORADO_MODELS="${MODEL_DIR}"

Basecall with methylation:

  dorado basecaller -x auto \\
    --modified-bases 5mCG_5hmCG \\
    \${DORADO_MODELS}/dna_r10.4.1_e8.2_400bps_sup@v5.2.0 \\
    runs/<date>/pod5/ > reads.sup.bam

EOF
