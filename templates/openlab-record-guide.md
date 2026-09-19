# Shared OpenLab run record

Use one [run record](openlab-run-record.yaml) and one [measurement table](openlab-measurements.csv) per session. Start with the [bench worksheet](first-bench-session.md). These are blank forms; they contain no executed results.

The same field names link instrument checks, sequencing preparation and environmental context. Add measurements to an existing Seagrass specimen or collection event. Location is optional context recorded in the collection system; it does not determine the record format.

| Fields | Meaning |
|---|---|
| `run_id`, `measurement_id` | Stable unique IDs for this session and observation. Never reuse an ID for a changed result. |
| `sample_id`, `event_id` | Existing specimen and collection-event IDs. Both may be blank for a bench standard. Use private codes for human material. |
| `protocol_id`, `protocol_version` | Method and exact revision used; archive instructions as artifacts. |
| `instrument_id`, `configuration_id` | Physical device and a recorded configuration in the YAML file. A configuration change gets a new ID. |
| `operator`, `timestamp` | Operator code and ISO 8601 time with timezone; session start/end are in the YAML record. |
| `measurement`, `value`, `unit` | One quantity per row, such as raw fluorescence, absorbance, concentration or image scale. State actual units, including `RFU`, `1` for dimensionless absorbance, `ng/uL`, or `um/pixel`. |
| `status` | `measured`, `derived`, `not_measured`, `below_range`, `above_range`, or `invalid`. A true measured zero is numeric `0`; unmeasured or censored values stay empty with their reason in `notes`. Preserve an out-of-range raw signal in a separate measured row. |
| `qc_status`, `criterion_id` | `pass`, `fail`, `limited`, `pending`, or `not_applicable`; link the predeclared criterion in YAML. An empty value never means pass. |
| `standard_id`, `matrix` | Link the material, assigned value and preparation record; distinguish water, seawater, extraction buffer, library buffer, etc. |
| `preparation_id`, `replicate`, `read_repeat` | Separate independent preparations from repeated instrument reads of one preparation. |
| `dilution_factor`, `blank_id`, `calibration_id` | Record the total dilution used for this calculated result and links to blank and calibration evidence. Explain its application; preserve intermediate calculations. |
| `adaptation_id` | Link the exact departure, reason, test and outcome in YAML. Leave blank if none. |
| `artifact`, `checksum`, `derived_from` | File path or stable URI, `sha256:<hex>` of those bytes, and source measurement IDs for calculated rows. Put multiple source IDs in a semicolon-separated list. |
| `report` | YAML artifact ID for the summary report, which links back to raw files and the decision. |

Do not put multiple units or a range into the numeric `value` field. Store range limits and reasons in the criterion or notes. Use a CSV writer for commas, quotes or line breaks in notes. Preserve original instrument exports and images, and checksum their bytes before later processing.

The existing [Nanopore run record](nanopore-run-record.yaml) holds additional extraction, acquisition and software details. Use the same `run_id` as its `run.private_code`, the same `sample_id` as `sample.private_code`, and link the completed records through `related_records`. This avoids replacing the existing sequencing form. A later sequencing run can reference an earlier instrument-validation run by its separate ID.

For seawater assays, record the method's matrix scope and checks. Raw optical values can be useful context while a concentration or turbidity calibration remains pending. For images, retain the calibration-slide artifact and camera configuration alongside the specimen image.

Public repositories contain blank forms and reviewed methods. Completed human records, filenames linking identity to samples, and personal reports remain in private storage. Public reference datasets should retain their original accession and source attribution.
