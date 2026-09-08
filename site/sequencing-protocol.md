---
title: Prepare a native genome and methylome run
sub: From our assembled bench to a private DNA-Report
status: Preparation protocol; end-to-end bench validation pending
updated: 2026-09-07
badge: Preparation
---

## First validation

Our first sequencing validation will use our own DNA. We will prepare a native DNA library, retain its raw signal, and test the path into DNA-Report. The same reads can support small-variant calls and measurements of DNA methylation.

The colorimeters, fluorometers, and OpenFlexure microscope are assembled and available for testing. Their assembly does not establish measurement accuracy. DNA quantification, extraction, library preparation, and the complete sequencing workflow still need recorded validation.

Download the blank [readiness checklist](/downloads/nanopore-readiness.md), [run record](/downloads/nanopore-run-record.yaml), and [instrument comparison table](/downloads/fluorometer-comparison.csv). Complete them in private storage. This public repository contains methods and blank forms only.

Start with the [first bench session worksheet](/downloads/first-bench-session.md) for fluorometer standards, colorimeter checks and OpenFlexure image scale. The [shared record guide](/downloads/openlab-record-guide.md), [session record](/downloads/openlab-run-record.yaml) and [measurement table](/downloads/openlab-measurements.csv) link raw measurements, configurations and adaptations to existing sample or collection-event IDs. Kit identity and pipette availability can remain open while instrument checks begin.

The [adaptation register](/adaptations) preserves the practical alternatives: open fluorometry, UV experiments, sequencing pilots, water baths, printed racks, and handling techniques. Choose and record the adaptations for each run. Manufacturer instructions provide the comparison method.

## 1. Fix the method before collecting a sample

1. Assign a private sample code and a separate run code.
2. Record the sample tissue, collection method, and planned analysis.
3. Confirm the exact extraction kit name, catalog number, lot, expiry, and storage history.
4. Download the manufacturer instructions for that kit and sample type.
5. Record each document revision and file checksum in the run record.
6. Check the supplies against those documents and the [inventory](/inventory).

**Stop before collection if the extraction kit variant is unknown.** The inventory currently says “PacBio Nanobind HMW DNA kit.” That description alone cannot select the extraction procedure.

For manual human blood extraction, PacBio lists CBB 102-301-900 and PanDNA 103-260-000 in document **102-573-500 REV04 AUG2024**. The document includes collection handling, reagent storage, extraction, and QC. Confirm that the physical kit matches it. Other kits require their own procedure. [PacBio blood extraction checklist](https://www.pacb.com/wp-content/uploads/Procedure-checklist-Extracting-HMW-DNA-from-human-whole-blood-using-Nanobind-kits.pdf).

The planned sequencing combination is **MinION Mk1D + FLO-MIN114 R10.4.1 + SQK-LSK114**. ONT lists NEBNext Companion Module v2, E7672S or E7672L, for this preparation. The source revision checked is **GDE_9161_v114_revAC_24Sep2025**. Save the exact revision used at the bench. [ONT native DNA ligation protocol](https://nanoporetech.com/document/genomic-dna-by-ligation-sqk-lsk114).

## 2. Check the bench and plan the control

1. Check pipette accuracy across the volumes planned for the preparation.
2. Verify incubator temperatures with an independent probe and record the measurements.
3. Check the magnetic rack with the actual tubes and bead reagent.
4. Inventory the required mixers, tubes, tips, reagents, and storage locations.
5. Check the acquisition computer, USB connection, storage space, and software versions.
6. Choose a control experiment and record any reason for deferring it.

The owned pipette range starts at 10 µL. Confirm suitable calibrated pipettes for smaller transfers before preparing reagents. A water bath or dry block needs a documented temperature check before substitution for a thermal cycler.

The owned mini centrifuge reaches 2,680 × g. Review the higher-force recovery step in the cited extraction method. The owned Protein LoBind tubes match that extraction procedure, while ONT lists DNA LoBind for library preparation. These stage-specific gaps and alternatives are in the [adaptation register](/adaptations).

Use the current [Mk1D device and IT requirements](https://nanoporetech.com/document/requirements/minion-mk1d-it-reqs) and [user manual](https://nanoporetech.com/document/minion-mk1d-user-manual/). The Mk1D requires a supported USB-C connection. Record the hardware-check report and flow-cell-check report. Check the current replacement conditions before loading a cell with a failed check.

ONT recommends a Lambda control experiment for new users. It exercises library preparation and sequencing. It does not validate human extraction or human methylation interpretation. [ONT control and preparation instructions](https://nanoporetech.com/document/genomic-dna-by-ligation-sqk-lsk114).

## 3. Establish usable DNA measurements

Each measurement answers a separate question. Reference measurements on the first extraction and library provide the strongest comparison. Borrowing access or using a measurement service can avoid an instrument purchase.

If reference access is unavailable, use the [adaptation register](/adaptations) to plan a limited pilot. Record which properties remain unresolved and what evidence the pilot can provide. Keep an aliquot for later comparison when storage and available mass permit.

| Measurement | Reference for the first run | OpenLab test |
|---|---|---|
| DNA concentration | dsDNA fluorometric assay with its specified instrument and standards | Compare the assembled fluorometer on the same samples. |
| Purity | UV spectrum including 230, 260, and 280 nm | Record the UV colorimeter's actual wavelengths separately. |
| Fragment size | A sizing method with a suitable range for long DNA | Compare the input distribution with the later read-length distribution. |

ONT's QC guide recommends DNA purity ratios near 1.8 for A260/A280 and 2.0–2.2 for A260/A230. Interpret ratios with concentration, the spectrum, and extraction history. Its long-fragment input recommendation is 1 µg, with 300 ng of prepared library for loading when fragments exceed 10 kb. Other size distributions have different requirements. [ONT QC, IDI_S1006_v1_revD_10Oct2025](https://nanoporetech.com/document/input-dna-rna-qc).

**Keep 255/278 nm measurements labelled with those wavelengths.** They cannot be reported as A260/A280. The current UV setup also lacks a demonstrated A260/A230 measurement. A good sequencing yield cannot establish purity retrospectively.

For the open fluorometer comparison:

1. Record the instrument, firmware, filter, LED, tube type, gain, and integration time.
2. Follow the selected dye manufacturer's assay instructions and incubation times.
3. Read one reagent blank for the series and preserve the raw readings.
4. Measure standards spanning the required range, with independent replicates.
5. Measure separate check samples and representative extraction and library aliquots on both instruments.
6. Calculate bias, repeatability, residuals, dilution recovery, and the useful concentration range.
7. Record the acceptance limits before reviewing the results.
8. Limit claims of measurement accuracy to the range and sample matrices that pass.

Do not blank against each standard. That would remove the signal needed for the calibration curve. A good curve fit alone does not establish accuracy.

The filter and geometry must match the assembled instrument. IO Rodeo documents a 6 × 6 mm filter holder and several optical configurations. Confirm the hardware revision before selecting a filter. [IO Rodeo fluorescence measurements](https://blog.iorodeo.com/open-colorimeter-plus-led-boards/).

A sequencing pilot is optional. Its read-length distribution also reflects library preparation and sequencing selection. Record it separately from input DNA sizing.

**Ask ONT sales whether the Flongle is still available.** The US price list showed no Flongle flow cell and no adapter on 2026-09-07. Without one, load the library on a MinION cell and stop the run after one to two hours. Recover the cell with the Flow Cell Wash Kit. A wash does not restore pores that a contaminated library has blocked. Sequence the Lambda control library first. See the [adaptation register](/adaptations).

## 4. Collect and extract the sample

**Arrange the blood draw with a qualified professional.** Establish suitable blood handling, protective equipment, surface cleaning, sharps disposal, and biological waste arrangements before collection.

1. Record the tissue, tube type, collection time, and preservation conditions under the private sample code.
2. Follow the selected extraction document for transport, storage, and sample input.
3. Record each transfer, storage interval, freeze-thaw event, and extraction deviation.
4. Follow the manufacturer procedure through lysis, binding, washing, elution, and DNA solubilization.
5. Save the extraction QC results before starting the library.

For the cited PacBio blood procedure, follow its vortexing steps during lysis and its Protein LoBind tube requirements. It includes an overnight solubilization period. Store each reagent as specified for that component. Blanket rules such as “never vortex” or “freeze every kit” conflict with this procedure. [PacBio REV04 blood procedure](https://www.pacb.com/wp-content/uploads/Procedure-checklist-Extracting-HMW-DNA-from-human-whole-blood-using-Nanobind-kits.pdf).

**Pause if the eluate fails QC or remains heterogeneous.** Use the extraction document's troubleshooting guidance. Record repeat measurements after any cleanup. Reassess the available mass before continuing.

Methylation depends on tissue and cell composition. A saliva sample is a separate sample type with a separate extraction method and interpretation context. Keep tissue and collection history with every analysis.

## 5. Prepare and load the native library

1. Open the saved SQK-LSK114 protocol and its manufacturer checklist at the bench.
2. Verify the kit and companion module against that revision.
3. Record the measured input mass, concentration, volume, and fragment-size evidence.
4. Follow the DNA repair, end-preparation, adapter ligation, and cleanup sections in order.
5. Record recovery measurements and any protocol deviations after each checkpoint.
6. Follow the priming and loading section for the exact flow-cell format.
7. Record the loaded library amount and the remaining library's storage conditions.

Use the manufacturer's volumes, mixing methods, temperatures, timing, and pause points as the reference. Record chosen departures in the [adaptation register](/adaptations). The Ligation Adapter is kit-specific. The current MinION procedure includes BSA in the priming mixture. Avoid introducing air over the sensor array. [ONT SQK-LSK114 bench instructions](https://nanoporetech.com/document/genomic-dna-by-ligation-sqk-lsk114).

Preserve native DNA for methylation analysis. PCR amplification and bisulfite conversion are excluded from this preparation. Do not substitute an amplification workflow to rescue a sample intended for native methylation measurement.

## 6. Acquire and preserve the run

The first personal validation uses whole-genome acquisition with adaptive sampling **off**. Target enrichment would change coverage and complicate assessment of the genome and methylome together.

1. Enter the private sample and run codes in MinKNOW.
2. Confirm SQK-LSK114 and the actual flow-cell identity in the run setup.
3. Enable POD5 retention and record output paths before starting.
4. Record the basecalling configuration and complete model identifiers.
5. Save the run settings, run report, software versions, and timestamps.
6. Monitor acquisition, disk space, yield, quality, pore activity, and temperature.
7. Use the manufacturer's troubleshooting and wash instructions when a problem occurs.
8. Record the reason and time for any pause, wash, reload, or stop.
9. Verify checksums after copying the raw data to a second private storage location.

Choose sequencing duration from observed performance and the coverage objective. A flow-cell count or elapsed time cannot guarantee coverage. For planning, 30× across a 3.1 Gb reference requires about 93 Gb of aligned bases before accounting for uneven coverage. Measure callable positions and per-site methylation coverage before interpreting a result.

Retain POD5, including when live basecalling succeeds. Reprocessing needs raw signal. Estimate storage from the control run, then allow space for raw data, alignments, work files, and a second copy.

## 7. Pass the data into DNA-Report

The local integration is being built and tested alongside this protocol. It has not yet been validated on this bench's personal sequencing run. The public upload service can have a different software version.

The intended analysis chain is:

**POD5 → Dorado basecalls with modification tags → reference alignment → small-variant calls and CpG methylation → one DNA-Report.**

Keep the same private sample identity across all files. Preserve the `MM` and `ML` tags through alignment. FASTQ cannot preserve these modification tags. Keep the reference FASTA, checksum, assembly, contig names, and model versions with the analysis.

Use the [analysis handoff](/downloads/nanopore-analysis.md) for the local command and its required inputs. The integration accepts one POD5 file or one BAM. Merge all single-sample run chunks using the documented POD5 preparation step before requesting a complete-run analysis. The initial supported scope is autosomal small germline variants plus measured CpG 5mC. Structural variants, copy-number changes, repeat expansions, and X, Y, and mitochondrial variants require separate analysis. Phased methylation also needs separate validation. Array-trained age clocks remain disabled for Nanopore until platform validation supports their use.

## 8. Review the evidence before publishing a method

1. Confirm the control run, extraction QC, library QC, and run reports are complete.
2. Check sample identity and reference consistency across variant and methylation outputs.
3. Review coverage, low-confidence calls, missing loci, and failed analysis stages.
4. Compare the open fluorometer with the reference measurements across both QC stages.
5. Record what passed, what failed, and what requires another run.
6. Review public figures and tables for personal data before publishing them.

A completed pipeline is evidence that the software ran. Analytical accuracy requires comparison with an appropriate reference dataset or independent measurements. Personal research findings that could affect care require clinical confirmation.

## Costs and related collections

The [equipment register](/inventory) retains item prices and estimates. Obtain current quotes and record the cost of each extraction, library, flow cell, assay, and repeat. Earlier per-run totals are planning history and do not establish the cost of this validation.

For [Seagrass](https://seagrass.goodancestor.com), the assembled instruments add environmental context to existing specimen collections. Link temperature, salinity, collection depth, light or clarity, and validated chemistry measurements to each specimen. Record instrument checks, units, collection times, and missing values. Apply the collection method anywhere. Bay Area access makes local testing convenient.

Human sample records stay private. Generic protocols, blank forms, instrument validation methods, and approved environmental data can be public.
