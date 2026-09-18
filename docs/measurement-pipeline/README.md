# Offline measurement validation and analysis

The tool checks completed OpenLab records and calculates calibration evidence. Its included example is fictional. No instrument calibration, physical measurement or reference agreement has been established by this software delivery.

## Run the fictional example

Use Python 3.11 or newer with the pinned packages in `software/measurement_pipeline/requirements.txt`. Record validation and calculations need PyYAML. Plotting also needs Matplotlib. Dependency installation is separate from offline execution.

```sh
python software/measurement_pipeline/pipeline.py \
  --run fixtures/measurement-fictional/run.json \
  --measurements fixtures/measurement-fictional/measurements.csv \
  --plan fixtures/measurement-fictional/analysis-plan.json \
  --out scratch/fictional-results
python -m unittest discover -s tests -p test_measurement_pipeline.py
```

The JSON run file is compatible with the existing YAML run-record fields. The measurement CSV uses the exact existing template header. YAML or JSON is accepted for the run and analysis plan. Add `--no-plots` for calculations without Matplotlib. The tool makes no network calls.

Read `analysis.json` and the CSVs first. `calibration-review.png` shows the calibration estimates, residuals, withheld checks by dilution, blank drift, repeated-read variability and microscope scale spans. The report retains actual numeric limits and input hashes through its source files. A `within_limit` calculation does not establish general instrument fitness or assay accuracy. Every derived row retains `source_qc_status`, including pending or limited input status. Numerical criterion results never replace source QC.

## Record checks

- IDs, session times and timezone, protocol version, instrument/configuration, specimen/event joins and matrix must agree.
- Each raw artifact is a relative local file with a matching SHA256. Paths outside the record directory and remote URIs are rejected. Copy an approved original artifact into the session directory before analysis.
- Measured and derived values must be finite numbers. Missing, invalid and censored values must be empty with a reason. A measured zero stays numeric zero.
- Acceptance criteria and the analysis plan must precede the session. Plan limits must equal the named run-record criterion.
- Preparations declare pre-dilution, assay volume and sample aliquot. Pre-dilution must be at least one. Assay volume and aliquot must be positive, and the aliquot cannot exceed assay volume. Their product defines total dilution. Derived check concentrations are compared with one application of that factor.
- Calibrators use final assay concentrations and dilution factor one. Independent checks use assigned original-tube concentrations. Shared calibration/check stock cannot be labelled independent.
- Configuration changes cannot borrow another configuration's fluorescence calibration. Adaptation IDs must link to the run record.

The current analysis supports raw fluorescence and concentration in ng/µL, dimensionless absorbance record validation, and microscope spans in pixels. It does not convert A255/A278 into standard purity ratios, infer turbidity, identify species or analyze genomic material. Unsupported quantities fail explicitly; add a reviewed unit/method extension before using them.

## Calculation scope

An ordinary least-squares line fits mean raw signal for each independently prepared calibrator. Three distinct concentrations are required. Each preparation has equal weight. Repeated reads do not multiply the number of preparations. The fitted intercept remains explicit; no blank subtraction is applied a second time.

Repeatability is reported separately within a preparation and between preparation means. These are descriptive signal CVs. Near zero, read CV is omitted and signal SD remains available. A curve fit alone does not establish accuracy.

Each withheld check is converted from assay to original concentration once. Outside-range estimates remain flagged and cannot receive `within_limit`. Stock-independence uncertainty remains pending. Nonlinearity, detection limits, saturation thresholds, matrix transfer and reference-instrument agreement require additional evidence. Do not use this linear method outside an assay's supported response regime.

Microscope scale is known micrometer length divided by observed pixels. Calibration spans form the mean reference scale. Withheld spans retain axis, centre/edge position and signed scale error. This tests the recorded optical configuration only. Physical motion, autofocus and specimen identification are outside the tool.

Invalid, censored and QC-failed rows appear in the exclusion table. The tool makes no deletion or correction to input records. Numerical results and raw source hashes remain in the output.

## Prepare the real session

Use [the standards-session worksheet](standards-session.md), the existing [first-bench worksheet](../../templates/first-bench-session.md) and [record guide](../../templates/openlab-record-guide.md). Confirm actual equipment, assay and material identity before accepting an analysis plan. Keep human sample records in their existing private workspace. This approved lane has used only fictional standards records.

The accepted analysis plan is an additional file. The example documents its structure. Replace every fictional value and limit, preserve the existing run/measurement templates, and record `source_kind: standards_session`. If evidence is missing, stop that measurement or record its limited scope. No purchase, instrument movement, extraction or sequencing action is authorized by this software.

Microscope-only sessions are supported. Supply only `scale_span_pixels` rows and their scale spans. The analysis group needs `criterion_id` and `scale_error_max_pct`; no fluorescence levels, standards, preparations or fluorescence limits are required. The run still records the microscope configuration, source artifacts and predeclared scale criterion. Empty fluorescence panels indicate that no fluorescence measurement was analyzed.
