# Measurement pipeline delivery

18 September 2026. Software and fictional-fixture validation only. No physical session ran.

Start with [the operator guide](../../docs/measurement-pipeline/README.md) and [blank standards-session worksheet](../../docs/measurement-pipeline/standards-session.md). The original run and measurement templates remain compatible and unchanged.

The committed fictional run has 32 rows. Its known fluorescence curve is 10 + 100 × assay concentration. The tool recovers that line from nine independently prepared calibrators, with repeated reads averaged within preparation. Withheld checks at total dilutions 10 and 20 recover 99.6–100.4% of the fictional assigned concentration. Four fictional micrometer spans produce 0.05 µm/pixel calibration and ±0.5% withheld scale error.

The blank drifts by 1 RFU within its fictional 2-RFU limit. Its two readings also exceed the separate 5% CV limit because their mean signal is small. The report preserves that outside-limit result. These synthetic limits and results make no statement about the actual instruments.

Twenty-four mechanism tests pass. They cover finite values, unknown joins, units, duplicate IDs, artifact tampering, absolute-path rejection, late criteria, mismatched limits, stock independence, dilution errors, excluded observations, optical-configuration mixing and preservation of preparation counts. The generated six-panel figure was opened and inspected. All figures and results are labelled fictional.

The CLI uses existing PyYAML/Matplotlib dependencies and runs offline. No raw human data, personal genome, device access, purchases, model inference or deployment was involved. A real standards session still needs an operator, actual configuration/material identity and predeclared acceptance criteria.

The original PR CI run35407719035 stopped at the document rendering check: two approximation tildes on the albumin-volume line would become a subscript span. A bounded follow-up replaces both with `about`; the quantities and purchase data are unchanged. Leakage and document checks now pass locally. Using the base conda Python with PyYAML, the register validator reaches two existing errors, `accuclear` and `lobind-dna`, each a verified price without a source. Page generation passes; `publish.sh build` stops at those same register errors. Generated pages are untracked. These missing price-source corrections remain an outstanding repository gate; a complete site build is not claimed. All24 measurement tests pass after the prose change.

Review corrections add per-quantity physical dilution checks, a microscope-only calculation path, and explicit preservation of source QC status in every derived result family. The microscope-only path also completed a separate CLI run with plotting.
