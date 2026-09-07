---
title: OpenLab adaptations to test
sub: Affordable methods, their limits, and the measurements that would support them
updated: 2026-09-06
badge: Methods to test
---

## Choosing the method

Open hardware and accessible bench methods are part of this project. Manufacturer instructions provide a reference for comparison. We can test departures when cost, equipment access, or a useful experiment justifies them.

The colorimeters, fluorometers, and OpenFlexure are assembled and available for testing. The proposals below remain part of the plan. Assembly, a plausible mechanism, and a measured comparison are separate kinds of evidence.

Use this register with the [preparation protocol](/protocol). Choose the adaptations for each run, record them before starting, and keep enough material or data to investigate a failure. A research pilot can proceed with incomplete comparisons when its limitations are explicit. It cannot establish an assay's accuracy by itself.

## DNA concentration on the open fluorometer

**Proposal retained:** Use the Open Colorimeter Plus with a 470 nm radial LED and a dsDNA dye such as AccuClear. The original proposal uses the 0.2 mL tube format, adjustable gain and integration time, and fluorescence detection at 90 degrees.

**Access reason:** Use the assembled open instrument and inexpensive consumables. Access to a commercial fluorometer can come through a loan or occasional comparison service.

**Evidence and review:** IO Rodeo reports fluorescence experiments, including a radial LED and revised mounting geometry. Match the configuration to the actual assembled hardware. [Vendor measurements](https://blog.iorodeo.com/open-colorimeter-plus-led-boards/).

1. Record the dye product, assay instructions, optical configuration, and raw readings.
2. Prepare standards within the dye assay's specified mass range.
3. Retain the original seven-point dilution-series proposal as a calibration design to review.
4. Use a reagent blank for the series, without blanking away each standard's signal.
5. Test independent check samples, dilution recovery, repeatability, and extraction and library matrices.
6. Compare selected samples with reference fluorometry when access is available.

Keep concentration in the original DNA tube separate from DNA mass added to an assay. The old 0.05–25 ng/µL calibration proposal needs an explicit assay volume and dilution scheme. The useful range follows measured performance.

**Current status:** Assembled. The DNA assay, usable range, accuracy, and reference agreement remain to be demonstrated. A dye standard can test calibration before reference access is arranged. It does not establish matrix performance alone.

## Low-cost emission and excitation filters

**Proposals retained:** A 500 nm longpass filter, a roughly 500–550 nm bandpass filter, stacked OD3 filters, and a 470/40 excitation filter remain candidates. Used optics can reduce cost.

IO Rodeo documents a small filter holder and comparisons between optical configurations. The previous claim that holder dimensions are unpublished is superseded by that article. Confirm the exact hardware revision and fitted filter. [Vendor filter and holder experiments](https://blog.iorodeo.com/open-colorimeter-plus-led-boards/).

OD3 + OD3 suggests OD6 only under compatible spectral and optical conditions. Scatter, gaps, reflections, and LED emission outside the nominal excitation band can limit actual rejection. Measure blank fluorescence, saturation, sensitivity, and repeatability with each configuration. Preserve the comparison even when a cheaper filter performs adequately.

## UV purity experiments at 255 and 278 nm

**Proposal retained:** Use the owned UV boards to explore absorbance ratios, dilution response, and contamination sensitivity.

**Access reason:** The boards are available. A full-spectrum spectrophotometer may require borrowed access.

**Departure:** The wavelength pair differs from 260/280 nm, and the current setup lacks a validated 230 nm channel. Keep readings labelled A255/A278. Do not apply NanoDrop thresholds directly.

**Test:** Compare clean DNA and suitable reference materials with full UV spectra when available. Record blanks, path length, concentration, repeatability, and the effect of the extraction buffer. Adding a 230 nm emitter remains a hardware proposal that also needs optical validation.

**Current status:** Useful research measurements are possible. A purity decision based only on these ratios remains unvalidated. Without reference access, record purity as unresolved and limit claims from the pilot.

The [caffeine and vitamin C exercises](/colorimetry) remain useful instrument tests. Tablet labels are comparison targets, with uncertainty from formulation and preparation. These exercises do not establish a DNA assay's performance.

## Fragment sizing with a Flongle pilot

**Proposal retained:** Prepare a small sequencing pilot before a full MinION run. Record read N50, yield, mapping, quality, and preparation observations.

**Access reason:** A pilot can exercise several stages without buying a gel or sizing instrument. Its total cost includes preparation reagents and the compatible adapter and expansion.

**Departure:** Read lengths reflect extraction, library selection, and sequencing. They do not uniquely measure the input DNA size distribution.

**Test:** Compare pilot reads with input sizing when access becomes available. Keep read filtering and library selection constant across comparisons. If independent sizing is unavailable, report the observed read distribution and that limitation.

**Current status:** Optional pilot design. Confirm the exact Flongle combination and current instructions before execution. The historical $90 cell estimate is not a complete or current pilot quote.

## Water bath and dry-block incubations

**Proposals retained:** Use the owned sous-vide bath or suitable dry blocks for incubation. A thermal cycler remains an option if these arrangements are inadequate.

**Access reason:** Avoid buying equipment solely to hold a small set of temperatures.

**Departure:** A bath or block has different ramp times, tube contact, evaporation, and temperature uniformity. Room temperature also varies.

**Test:** Measure temperature in representative tubes and across positions. Record equilibration time and stability throughout each required hold. Match the selected protocol's temperatures and durations. Record any remaining departure and compare library recovery and run performance.

**Current status:** Alternative equipment retained for testing. PacBio explicitly permits a heat block or water bath with periodic agitation in its cited blood lysis procedure. Other incubation substitutions require separate review. [PacBio blood procedure, REV04](https://www.pacb.com/wp-content/uploads/Procedure-checklist-Extracting-HMW-DNA-from-human-whole-blood-using-Nanobind-kits.pdf).

## Mixing, tube types, and elution

**Original proposals retained for review:** Wide-bore tips, gentle mixing after extraction, common LoBind tubes, and warming elution buffer to 60°C.

**Access reason:** Use available pipettes, tubes, and temperature equipment while reducing handling losses.

**Conflict that needs resolution:** The cited PacBio blood procedure requires specific vortexing during lysis, Protein LoBind tubes, and a solubilization period. Its elution instructions differ from the previous blanket 60°C proposal. The physical kit identity determines which comparison applies. [PacBio extraction procedure](https://www.pacb.com/wp-content/uploads/Procedure-checklist-Extracting-HMW-DNA-from-human-whole-blood-using-Nanobind-kits.pdf).

Keep gentle handling of purified long DNA as a separate proposal from lysis mixing. Record where each method is used. Tube substitution can be tested on split material by comparing DNA recovery and UV purity. A viscous or cloudy eluate needs review because appearance alone cannot identify the cause.

**Current status:** Do not use the former “never vortex” instruction across every stage. Review the original warming proposal after identifying the kit. Retain any tested substitution with its results and limits.

## Printed magnetic rack and short bead drying

**Proposals retained:** Use the printed rack or the owned VISOSCI rack. Observe bead collection within a few minutes. Use the previous 30-second drying estimate as a timing proposal to test.

**Access reason:** Avoid another magnetic separator and reduce sample loss during cleanup.

**Departure:** Magnet position, tube geometry, reagent volume, humidity, and airflow change separation and drying. A fixed time does not prove the beads are ready.

**Test:** Use the actual tube and reagent combination. Record separation time, clarity, residual liquid, pellet condition, DNA recovery, and repeatability. Compare the preparation with the selected kit instructions. Do not release a timing rule from one observation.

**Current status:** Both rack options remain available. The manufacturer cleanup buffer for an adapted library remains chemically distinct from the pre-ligation wash. An ethanol substitution after adapter ligation needs review because it can damage sequencing performance.

## Limited-force centrifuge

The owned mini centrifuge reaches 2,680 × g. The cited PacBio blood procedure includes a 10,000 × g recovery spin. Borrowing a suitable centrifuge or testing another recovery method remain options.

Record the retained liquid or DNA on the disk and the recovered mass when comparing a lower-force method. Increasing time does not automatically reproduce the reference recovery. Confirm the kit-specific step before designing that comparison.

The owned Protein LoBind tubes match the cited extraction procedure. They were previously labelled the wrong variant because ONT specifies DNA LoBind at the library stage. The register now distinguishes those uses. Denatured surface-cleaning alcohol also remains separate from molecular-preparation ethanol.

## Mixing viscous reagents and loading without bubbles

**Proposals retained:** Gentle mixing of enzyme reagents where specified, slow pipette mixing for viscous buffer, and controlled draw-back using the pipette volume wheel.

**Access reason:** These techniques use standard manual pipettes.

**Test:** Rehearse transfer control with water away from the flow cell. Check delivery accuracy and observe bubbles. Compare the exact action with the manufacturer loading video and the kit's mixing instructions. Never use a draw-back maneuver that exposes the sensor array to air.

**Current status:** Technique proposals retained. The former explanation that all glycerol-containing enzymes are destroyed by vortexing was too broad. Follow the reagent-specific instruction or record an explicit, justified departure.

## Washes, reloads, and adaptive sampling

**Proposals retained:** Wash and reload a cell when useful library remains. Keep the previous “about 30% occupancy at 24 hours” idea as a heuristic to evaluate. Adaptive sampling remains an option for a later targeted experiment.

**Access reason:** Extend useful flow-cell output or concentrate sequencing on a defined question.

**Test:** Record pore activity, occupancy, yield rate, library availability, and the reason for a wash. Compare output before and after the intervention. A change in translocation speed alone cannot diagnose damaged pores.

The former 20–40 Gb yield, three-to-four-cell 30× estimate, and 30–50× target-coverage prediction are planning history. Actual yield, mapping, enrichment, and callable coverage decide the next run. The first personal genome and methylome validation uses adaptive sampling off to simplify coverage assessment.

**Current status:** Wash and enrichment experiments remain in scope. Neither a fixed clock time nor a fixed occupancy threshold guarantees benefit.

## Recording an adaptation

Record the original proposal, practical reason, exact departure, expected benefit, possible failure, and validation measurement. Add the outcome, uncertainty, and next revision after the run. Publish useful failures as well as methods that work, after reviewing the material for personal data.
