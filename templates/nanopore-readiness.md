# Nanopore readiness checklist

Copy this blank form into private storage. Record pass, fail, or pending for each item, with evidence and the reviewer date. Record the reason for any unresolved item and the limited purpose of a pilot that proceeds without it. Resolve kit identity and sample handling before collection.

## Next decisions and their evidence

Use the [first bench session](first-bench-session.md) and [shared run record](openlab-run-record.yaml) to collect the evidence below. Instrument calibration can start while the exact extraction kit and small-volume pipettes remain unknown. All status cells begin pending; this table records no completed measurements.

| Decision | Evidence needed | Status / evidence artifact / next action |
|---|---|---|
| Start standards and imaging session | Available assay/standards and their instructions; microscope test slide; recorded optical configuration. Missing standards allow a labelled stability or capture exercise. | pending / / |
| Choose the extraction procedure | Physical kit name: ___; catalog: ___; lot: ___; matching sample-specific document and revision: ___. | pending / / |
| Make the required transfers | Small-volume pipettes available: ___; ranges: ___; accuracy/repeatability records at the planned volumes. | pending / / |
| Use the open fluorometer for DNA mass | Calibration, independent checks, dilution recovery and range/matrix evidence. State reference agreement separately if reference access remains pending. | pending / / |
| Use a lower-force recovery step | Kit-specific comparison plan; recovered volume and mass, retained material, repeats and limitations. Longer time alone does not establish equivalence. | pending / / |
| Use the bath/block and printed rack | Measured tube temperature/stability; actual rack/tube separation and recovery observations. Record accepted scope for each adaptation. | pending / / |
| Prepare the first personal library | Extraction QC, sample tracking, sufficient measured native DNA, applicable kit instructions and an explicit decision about unresolved properties. | pending / / |
| Run the computational handoff | Reference dataset identity, input/output hashes, pinned tools/models/reference, both branches completed and exclusions reviewed. Report rendering and read-processing accuracy need separate evidence. | pending / / |
| Commit the sequencing run | Library and flow-cell checks, raw-signal retention, verified private backup, acquisition configuration and a coverage objective. | pending / / |

**Current decision / purpose of any limited pilot:** __________________

**Reviewer / date / next measurement:** ______________________________

## Before sample collection

- Record the private sample and run codes.
- Confirm the tissue and professional collection arrangement.
- Confirm suitable sample handling and waste arrangements.
- Match the extraction kit catalog number to its sample-specific instructions.
- Save the extraction, library, device, QC, and assay instructions with revisions and checksums.
- Check kit lots, expiry dates, storage histories, and all required supplies.
- Confirm suitable pipettes cover every required volume and record their accuracy checks.
- Verify the temperature equipment and magnetic rack.
- Arrange reference fluorometry, UV purity measurement, and suitable DNA sizing, or record the pilot limitations.
- Record the open fluorometer comparison plan and acceptance limits before testing.
- Complete the device and flow-cell checks. Record the control experiment or the reason for deferring it.
- Verify private storage, backup space, transfer checksums, and software configuration.
- Record the analysis checks completed and any reference-dataset comparison still pending.

- Record selected adaptations, access or cost reasons, expected failures, and planned comparisons.

## Before library preparation

- Record sample preservation, extraction, and deviation history.
- Review extraction QC and record any unresolved properties before proceeding.
- Confirm sufficient measured native DNA mass remains after QC.
- Save the raw reference measurements and open instrument comparison.
- Confirm the SQK-LSK114 revision matches the companion reagents and flow cell.
- Record any unresolved limitations and the decision to proceed or repeat extraction.

## Before sequencing

- Record prepared library quantity and the manufacturer's loading requirement for its size distribution.
- Confirm the flow-cell check passes the manufacturer's current conditions.
- Confirm private sample identity, kit, flow cell, output paths, and POD5 retention in MinKNOW.
- Disable adaptive sampling for the first whole-genome validation.
- Record the model names, run settings, storage plan, and coverage objective.

## Before accepting the analysis

- Verify raw-data and backup checksums.
- Confirm the same sample identity across every input and output.
- Confirm the reference assembly, contig names, and reference checksum.
- Confirm modification tags survive basecalling and alignment.
- Confirm variant caller and model compatibility with the basecalled data.
- Review mapping, callable coverage, methylation site coverage, and missing loci.
- Confirm the variant and methylation branches both completed.
- Confirm array-trained clocks remain disabled for this unvalidated platform.
- Record the software and model versions, configuration, output hashes, and limitations.
- Keep the report and all personal data outside the public repository.

## Before publishing the validation

- Separate bench execution evidence from analytical accuracy evidence.
- Review instrument bias, repeatability, range, and matrix limitations.
- Record deviations, failures, and follow-up measurements.
- Remove personal sample identifiers and personal findings from public material.
