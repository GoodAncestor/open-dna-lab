#!/usr/bin/env bash
# leakage_scan.sh — block personal genomic data from reaching GoodAncestor/openlab.
#
# Adapted from the seagrass-site-publish scan. This lab sequences human genomes
# including the operator's own; anything downstream of a personal sample belongs
# in colbyt/genomics. This script is the last gate before a push.
#
#   ./scripts/leakage_scan.sh          # scan the working tree
#
# Exits non-zero on any hit. Three independent checks, because each catches what
# the others miss:
#
#   1. Content — identity and clinical markers. Keyed on who the data is about,
#      not what the file is called, so it survives renaming.
#   2. Payload — file-format signatures and raw sequence pasted into text files.
#      Catches a VCF body dropped into a .md or .json where no extension rule
#      would see it.
#   3. Tracked files — sample-derived file types staged in git. Backstop for
#      .gitignore being bypassed with `git add -f` or edited away.
#
# Documentation legitimately names tools and formats: reads.sup.bam,
# runs/<date>/pod5/, panels/<panel>.bed, the word methylation. Those are correct
# content for this repo. The checks below do not match them — that is deliberate,
# and why the content rules key on identity rather than on file extensions.

set -uo pipefail
cd "$(dirname "$0")/.."

TEXT_INCLUDES=(
  '--include=*.md' '--include=*.txt' '--include=*.csv' '--include=*.tsv'
  '--include=*.py'  '--include=*.json' '--include=*.yaml' '--include=*.yml'
  '--include=*.sh'  '--include=*.html'
)
EXCLUDES=(
  '--exclude-dir=.git' '--exclude-dir=publish' '--exclude-dir=_generated'
  '--exclude-dir=__pycache__' '--exclude-dir=.pdfcache'
  '--exclude=leakage_scan.sh'
)

fail=0

# --- 1. Identity and result markers -----------------------------------------
# What makes data personal is whose it is and what it says: the provenance of a
# named individual's sample, or an actual interpreted result. Those hard-fail.
#
# Public database and discipline names are NOT in this list. This repo documents
# software that queries ClinVar and does pharmacogenomics, so those words appear
# in ordinary descriptive prose; failing on them would make the gate cry wolf on
# correct content, and a gate that cries wolf gets switched off. A real finding
# drags a result token with it — a call, an rsID, a gene symbol — and those are
# here. Database names are reported below as a warning instead.
# Sample identifiers, interpreted calls, and the gene symbols that appear in the
# operator's screening reports. Every one of these is either "whose sample" or
# "what it says" — neither has a legitimate reason to appear in this repo.
IDENTITY='GS0000|hu63A000|pathogenic|likely benign|variant of uncertain'
IDENTITY+='|MTHFR|COMT|APOE|rs[0-9]{4,}|heterozygous|homozygous'

echo "==> 1/3 identity and result markers"
if hits=$(grep -rinE "$IDENTITY" . "${TEXT_INCLUDES[@]}" "${EXCLUDES[@]}" 2>/dev/null); then
  echo "$hits"
  echo "    FAIL: personal-genomics markers found. These belong in colbyt/genomics."
  fail=1
else
  echo "    clean"
fi

# Advisory only. Flags where interpretation vocabulary appears so a reviewer can
# glance at it, without blocking the build on a word.
# Provider, database, and discipline names. These are documentation vocabulary —
# DNA-Report accepts 23andMe exports, GeneAsk queries ClinVar, and both repos say
# so in plain prose. A file that genuinely holds one of these products carries
# result tokens too (rsIDs, genotype calls, gene symbols), which the list above
# catches, so the names alone are reported rather than blocking.
CONTEXT='23andme|promethease|complete genomics|personal genome project'
CONTEXT+='|clinvar|pharmacogen|epigenetic clock|allele frequency'
if hits=$(grep -rilE "$CONTEXT" . "${TEXT_INCLUDES[@]}" "${EXCLUDES[@]}" 2>/dev/null); then
  echo "    note: interpretation vocabulary in $(echo "$hits" | wc -l | tr -d ' ') file(s) —"
  echo "$hits" | sed 's/^/      /'
  echo "      Descriptive prose is fine here. Results are not."
fi

# --- 2. Payload signatures --------------------------------------------------
# A VCF/SAM/FASTQ body or a raw sequence block pasted into a text file. The
# 40-base threshold clears primer and adapter sequences, which are short and
# are legitimate protocol content.
echo "==> 2/3 payload signatures in text files"
PAYLOAD='##fileformat=VCFv|^@HD[[:space:]]+VN:|^@SQ[[:space:]]+SN:|^[ACGTN]{40,}$'
if hits=$(grep -rnE "$PAYLOAD" . "${TEXT_INCLUDES[@]}" "${EXCLUDES[@]}" 2>/dev/null); then
  echo "$hits"
  echo "    FAIL: sequence or variant payload embedded in a text file."
  fail=1
else
  echo "    clean"
fi

# --- 3. Tracked sample-derived files ----------------------------------------
# .gitignore covers these, but an explicit `git add -f` overrides it silently.
echo "==> 3/3 tracked sample-derived files"
if git rev-parse --git-dir >/dev/null 2>&1; then
  tracked=$(git ls-files | grep -iE \
    '\.(pod5|fast5|blow5|slow5|fastq|fq|bam|bai|cram|crai|sam|vcf|gvcf|bcf|bed|bedmethyl)($|\.)|^(runs|panels|vcf|basecalls|alignments)/|(^|/)methylation_' \
    || true)
  if [ -n "$tracked" ]; then
    echo "$tracked"
    echo "    FAIL: sample-derived files are tracked. Remove from the index."
    fail=1
  else
    echo "    clean"
  fi
else
  echo "    skipped (not a git repository)"
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "LEAKAGE SCAN FAILED — do not push."
  exit 1
fi
echo "LEAKAGE SCAN PASSED"
