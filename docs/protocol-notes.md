# Preparation notes

The canonical bench plan is [the sequencing protocol](../site/sequencing-protocol.md). It links the manufacturer revisions, readiness checklist, and blank run record. Record results in private storage.

The [adaptation register](../site/adapted-methods.md) retains the original practical proposals, reasons, departures, and review questions. Reference access can be limited. Record that limitation when designing a pilot.

The 2026-09-06 revision corrects these earlier assumptions:

- Assembled colorimeters, fluorometers, and OpenFlexure are available for testing. DNA assay validation remains pending.
- The exact Nanobind catalog number must select the extraction procedure. The cited blood procedure requires mixing steps that the previous blanket “never vortex” rule would omit.
- Reagent storage, elution, tube type, incubation, and bead handling follow the selected manufacturer procedure.
- UV readings at 255 and 278 nm cannot be labelled A260/A280. Reference purity measurements provide a comparison. Record unresolved purity when access is unavailable.
- A Flongle pilot records sequencing performance and read lengths. Input DNA sizing remains a separate measurement.
- The first personal run uses whole-genome acquisition. Adaptive sampling and panel enrichment remain separate experiments.
- Yield, coverage, reload timing, and run cost must be measured. Earlier fixed predictions were planning assumptions.
- Alignment must preserve modification tags. The old minimap2 command supplied BAM where sequence input was expected.

Human blood collection uses a qualified professional. Preserve native DNA for methylation analysis. Use the manufacturer documents for the complete bench instructions.

The environmental work continues alongside sequencing. Seagrass measurements describe each collected specimen's environmental context. The collection method applies across locations.
