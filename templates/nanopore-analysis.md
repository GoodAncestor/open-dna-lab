# Nanopore to DNA-Report handoff

Use the local integration for a single human sample. The initial workflow measures CpG 5mC and calls autosomal small germline variants. It does not assess structural variants, copy-number changes, repeat expansions, or X, Y, and mitochondrial variants. Array-trained age clocks remain disabled until Nanopore platform validation supports their use.

The OpenLab bench workflow remains unexecuted end to end. Software fixture tests do not establish accuracy for a human genome or a chosen model. Record the tested software revisions and validation evidence with each run. The live upload service can differ from the local checkout.

## Prepare local inputs

1. Keep the source POD5 or modification-tagged BAM in private storage, outside the analysis scratch directory.
2. Verify a second copy by checksum before processing.
3. Use one sample identity throughout the run.
4. Prepare a local GRCh38 FASTA and its samtools `.fai` index.
5. Record the reference checksum and contig naming.
6. Install the required tools and place reviewed models in local directories.
7. Record tool versions, model names, model checksums, and chemistry compatibility.

The same aligned BAM feeds the variant and methylation branches. The workflow checks reference identity and sample metadata. Matching sample labels do not independently establish biological sample identity.

BAM must retain `MM` and `ML` modification tags. FASTQ cannot carry those tags. Dorado is required for POD5 and for realignment when the BAM header cannot verify the reference. CpG pileup combines strands while keeping 5mC distinct from other modifications.

## Combine a complete run's POD5 chunks

The integration accepts one POD5 file or one BAM file. A MinKNOW run can contain multiple POD5 chunks. Supplying one chunk analyzes only that chunk.

1. Identify every chunk belonging to this single sample and completed run.
2. Keep chunks from other samples and barcoded mixtures outside the input directory.
3. Record the input file list, sizes, checksums, run metadata, and read count.
4. Check the installed POD5 tool version and merge help.
5. Merge into a new file outside the input directory.

```bash
pod5 merge --help
pod5 merge '/private/source/run-pod5' --recursive \
  --output '/private/merged/complete-run.pod5'
```

Keep duplicate-read detection enabled. Investigate overlapping inputs instead of disabling the check. Verify the merged read count and sample/run metadata, record its checksum, and retain the original chunks. Provide the merged file to `dna-report analyze`. The merge requires additional disk space.

The directory and recursive-input behavior are documented in the [official POD5 changelog](https://github.com/nanoporetech/pod5-file-format/blob/master/CHANGELOG.md). The [official merge examples](https://github.com/nanoporetech/pod5-file-format/blob/master/python/pod5/README.md#pod5-merge) describe output selection and duplicate-read checks. Confirm these options against the installed release before use.

## Configure the local workflow

Set these variables in a private shell configuration. Replace every example path and identifier with the reviewed local value. The workflow does not download references or models.

```bash
export DNAREPORT_ONT_REFERENCE='/private/reference/GRCh38.fa'
export DNAREPORT_ONT_REFERENCE_SHA256='REPLACE_WITH_VERIFIED_64_CHARACTER_SHA256'
export DNAREPORT_ONT_BUILD='GRCh38'
export DNAREPORT_ONT_CLAIR3_MODEL='/private/models/clair3'
export DNAREPORT_ONT_CLAIR3_MODEL_ID='REPLACE_WITH_MATCHED_MODEL_IDENTIFIER'
export DNAREPORT_ONT_SCRATCH='/private/analysis-scratch'
export DNAREPORT_ONT_THREADS='4'
export DNAREPORT_ONT_TIMEOUT='86400'
export DNAREPORT_ONT_SCRATCH_GB='500'
```

Provide installed `samtools`, `modkit`, and Clair3's `run_clair3.sh` on the executable search path. Their paths can also be set with `DNAREPORT_ONT_SAMTOOLS`, `DNAREPORT_ONT_MODKIT`, and `DNAREPORT_ONT_CLAIR3`.

For POD5, configure local Dorado canonical and modification models:

```bash
export DNAREPORT_ONT_DORADO_MODEL='/private/models/dorado-canonical'
export DNAREPORT_ONT_MOD_MODEL='/private/models/dorado-modification'
export DNAREPORT_ONT_DEVICE='cpu'
```

Set `DNAREPORT_ONT_DORADO` when Dorado is outside the executable search path. Select a supported device for the actual host. CPU is the default, and does not imply practical whole-genome throughput. Benchmark a small public input before the full run.

Match the Dorado models to the flow-cell chemistry and acquisition conditions. Match the Clair3 model to the basecalling configuration. The initial integration excludes Clair3 models that require move-table input. It cannot infer model compatibility from a directory name alone.

The resource values above are configurable bounds. Size scratch space and time from measured performance. Use encrypted scratch storage. Temporary analysis files are removed when processing ends. Source retention and backup remain separate responsibilities.

## Run the combined report

Use the current local DNA-Report CLI after installing the integration and its matching bio-core, GeneAsk, and MethylAsk revisions. Record `dna-report analyze --help` with the software revision before the first run.

```bash
dna-report analyze '/private/source/sample.bam' \
  --sample-id SELF-001 \
  --tissue blood \
  --reference-build GRCh38 \
  --min-coverage 5 \
  --out '/private/reports/report.html'
```

Replace the BAM path with a single-sample POD5 input when using configured Dorado models. Use `--reference /private/reference/GRCh38.fa` for an explicit local reference override, with its matching configured checksum. Optional `--age` and `--sex` describe the sample context. Keep those values private.

An existing small-variant file can be supplied with `--nanopore-vcf /private/source/existing.vcf`. The workflow checks matching sample metadata and reference alleles. Record how the file was produced and why it belongs to this sample.

A bedMethyl input uses `--reference-build GRCh38`. Add `--combined-strands` only when it was produced with a strand-combining operation such as modkit `--combine-strands`. This methylation-only input does not itself supply small-variant data. Record the coordinate convention, modification type, strand treatment, and site coverage.

For native inputs, the CLI writes `report.json` and `report.md` beside `report.html`. These sidecars preserve structured results and provenance. BAM, VCF, and bedMethyl intermediates in scratch remain temporary. Keep the original source and configuration so they can be regenerated.

## Review the result

1. Confirm both analysis branches completed.
2. Review mapped coverage, excluded calls, measured CpG coverage, and missing loci.
3. Record all model and reference identifiers, input hashes, thresholds, and analysis notes.
4. Keep the rendered report and provenance in private storage.
5. Retain source POD5 or BAM so transient intermediate files can be regenerated.
6. Record any unsupported result class or unmeasured region as unassessed.

Coverage and confidence thresholds are analysis settings, not clinical validation. A completed report does not establish that every locus was measured. Use appropriate reference datasets and independent evidence before making accuracy claims.
