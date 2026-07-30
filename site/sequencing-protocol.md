---
title: Sequencing a human genome on open hardware
sub: Blood, a MinION, and an open-source QC bench
status: draft — not yet executed end to end
updated: 2026-07-29
---

# Sequencing a human genome on open hardware

Existing home-sequencing write-ups solve the sequencing and leave quality
control to a $500-3,000 commercial fluorometer, or skip it. This protocol
replaces that instrument with open hardware: an Open Colorimeter Plus for
concentration, a UV Open Colorimeter for purity, and a $90 Flongle flow cell
for fragment length.

Whether the substitution works is the open question this page exists to
answer.

## Validation status

Every step carries a marker. Read them.

| Marker | Meaning |
|---|---|
| **[MFR]** | Manufacturer protocol. Follow their document, not ours. |
| **[ADAPTED]** | Established practice, adapted to this equipment. |
| **[UNTESTED]** | Our substitution. Not yet run by us or, as far as we know, anyone. |

Nothing on this page has been executed end to end. The QC section is entirely
**[UNTESTED]**. It will be marked otherwise when it has been run against a
calibrated reference.

## What differs from the reference approach

The starting point is Seth Showes' account at
[iwantosequencemygenomeathome.com](https://iwantosequencemygenomeathome.com/),
which documents a completed run and is the better guide if you want a path
someone has walked.

| | Reference approach | Here |
|---|---|---|
| Sample | Buccal swab | Whole blood, EDTA |
| Extraction | NEB Monarch T3010 | PacBio Nanobind HMW |
| Expected read N50 | ≈4 kb | Longer; blood gives higher DIN |
| Concentration | None on first run | Open Colorimeter Plus + AccuClear |
| Purity | None | UV Open Colorimeter, 255 nm and 278 nm |
| Fragment length | None | Flongle pilot |
| Sequencer | Mk1B | Mk1D |
| Basecalling | HAC live, SUP on selected regions | SUP with modifications throughout |
| POD5 | Deleted after basecalling | Retained indefinitely |

The last two follow from compute rather than cleverness. SUP with
modified-base calling is the mode the epigenome work requires, and it is
routine on a GPU fleet. Retaining raw signal costs about 7 GB per gigabase,
so a 30 Gb run is roughly 210 GB — a constraint for most labs and not for
this one. Every improvement to Dorado's modification models can then be
applied retrospectively to the whole archive.

## Equipment

See the [inventory](/inventory). Sequencing-specific items:

- MinION Mk1D, R10.4.1 flow cells (FLO-MIN114), Flongle adapter and Flongle
  cells (FLO-FLG114), Flow Cell Wash Kit (EXP-WSH004)
- SQK-LSK114 ligation kit, NEBNext Companion Module v2 (E7672S), AMPure XP
- PacBio Nanobind HMW extraction kit
- Open Colorimeter Plus with 470 nm LED board and emission filter
- UV Open Colorimeter with 255 nm and 278 nm boards
- Dual-block dry bath (56 C, 65 C), vortex, microcentrifuge, printed magnetic
  rack, wide-bore tips, LoBind tubes

Freezer at −20 C for kits, refrigerator at 4 C for flow cells and beads.
Ethanol at room temperature, in neither.

## 0. Setup **[MFR]**

Install MinKNOW, version 24.11.10 or later. The Mk1D connects over USB-C only;
USB-A adapters do not supply enough power.

Pore-check the flow cell before anything else. Seat it, warm it 20 minutes,
run the check. Expect about 1,200 pores; require at least 800. Below that,
claim the warranty before loading — after your library is on it, that argument
is gone.

For adaptive sampling, prepare the BED file and load it with the GRCh38
reference. Target regions should total under 1% of the genome. Panel files
tied to a specific person's clinical questions are kept in a separate private
repository and are not published here.

## 1. Sample **[ADAPTED]**

Whole blood into EDTA tubes, drawn by a phlebotomist. Nanobind protocols
typically start from 100-300 µL, so one tube supports many attempts.

Fresh is best. Frozen whole blood works. Blood held refrigerated for days does
not.

Saliva via Oragene OG-500 is the fallback where a draw is impractical, at the
cost of shorter fragments and a bacterial DNA fraction that commonly runs
10-30% — flow cell capacity paid for and unused.

## 2. Extraction **[MFR]**

Follow the PacBio Nanobind protocol for your kit variant. Blood and cell
culture differs from tissue.

Points that carry over regardless of kit:

- Wide-bore tips throughout. Standard tips shear HMW DNA.
- Never vortex. Flick, or rotate.
- Pre-warm elution buffer to 60 C.
- A cloudy eluate means salt carry-through. Re-wash before proceeding.

## 3. Quality control **[UNTESTED]**

Three measurements. None substitutes for another.

### 3a. Concentration — Open Colorimeter Plus

The instrument is a fluorometer: a TSL2591 sensor at 90° to the excitation
LED, a second TSL2591 at 180° reading LED intensity for normalisation, 0.2 mL
PCR tubes, and a removable cover that accepts filters. Gain and integration
time are adjustable on both sensors, which is where the sensitivity headroom
sits.

Chemistry: Biotium AccuClear Ultra High Sensitivity, excitation 468 nm,
emission 507 nm, linear from 0.03 to 250 ng. The 470 nm LED board is a close
excitation match.

Emission filter: passband roughly 500-550 nm with OD4 or better blocking at
470 nm. Stacking two OD3 filters gives OD6 and often suffices, because 90°
geometry means the background is scatter rather than the direct beam. Filter
slot dimensions are unpublished; confirm with IO Rodeo before ordering.
[traulab/diynafluor](https://github.com/traulab/diynafluor) documents an
$80 open-source DNA fluorometer and is the better starting point for optics
selection.

An excitation filter at 470/40 is a later addition if background is high. Blue
LEDs have a red tail that leaks straight through the emission filter, and
cleaning up the excitation often buys more than a better emission filter.

**Calibration and validation — do this before trusting a single number:**

1. Serial-dilute the 25 ng/µL AccuClear standard to at least seven points
   spanning 0.05 to 25 ng/µL.
2. Read each in Relative Units mode, blanking before each sample.
3. Fit the curve. Inspect residuals, not just R².
4. Determine limit of detection as 3× the standard deviation of the blank, and
   limit of quantitation as 10×.
5. Read the same dilution series on a calibrated Qubit.
6. Compare across the range and record where the two diverge.
7. Generate `calibrations.json` with `oc-cal` from the
   `open-colorimeter-utils` package so the fitted curve becomes a menu entry
   on the instrument.

Step 5 is why a Qubit 3 remains on the buy list. Validating an unproven
instrument against nothing produces a number with no error bar attached.

### 3b. Purity — UV Open Colorimeter

The vendor publishes a DNA quantification tutorial for this instrument with
the 255 nm board, and a protein quantification tutorial using 270-280 nm.

What we are attempting is different: a purity ratio, using the 255 nm and
278 nm boards as proxies for A260 and A280. Three reasons this may not work:

- 255 nm and 278 nm are not 260 nm and 280 nm, and both sit on steep parts of
  the nucleic acid absorbance curve.
- LED bandwidth is roughly ±10-15 nm FWHM against a monochromator's ≈1 nm.
- No 230 nm source is available, so A260/230 — the ratio that predicts pore
  fouling from guanidinium, phenol, and polysaccharides — cannot be measured
  at all.

The third is the limiting one. A260/230 is the measurement that matters most
for nanopore, and this bench cannot produce it. Until that is solved, purity
is assessed indirectly: through the Flongle pilot below, and through pore
occupancy during the run itself.

Characterise against known-clean and deliberately contaminated samples before
drawing conclusions from any ratio this produces.

### 3c. Fragment length — Flongle pilot

A Flongle costs $90 and reports read N50 directly. That is the number that
matters, measured rather than inferred, and it simultaneously tests the
extraction, the library prep, and the loading technique.

Run one before committing a $988 flow cell. It is cheaper than a gel rig and
answers a better question.

## 4. Library preparation **[MFR]**

Follow the ONT SQK-LSK114 protocol. Expect around 70 minutes: end-prep and
FFPE repair, bead cleanup, adapter ligation, second cleanup with Long Fragment
Buffer.

No PCR-based kit. Amplification erases base modifications, and methylation
survives only in native DNA.

Points the protocol underplays, from published experience **[ADAPTED]**:

- Enzyme mixes are formulated in glycerol. Vortexing froths them and destroys
  activity. Flick.
- Ligation Buffer is viscous and will not vortex into solution. Pipette-mix
  slowly.
- Thirty seconds of air-drying is enough for the AMPure pellet. Longer and the
  beads crack and weld to the tube wall.
- Long Fragment Buffer for the second cleanup, never ethanol. LFB preserves
  the adapter's motor protein; ethanol strips it, and the adapter can then no
  longer pull DNA through a pore.
- At the magnet, a brown line should appear within a minute or two. If nothing
  has happened by 2.5 minutes, the magnet is too weak or too far from the tube.

Expect 150-450 ng in 15 µL. Twelve µL loads; the rest is reload reserve.

## 5. Loading **[MFR]**

Watch ONT's priming and loading video before the first attempt.

Air across the pore array takes pores offline permanently. Draw back by
dialling the volume wheel rather than pressing the plunger — the suction is
gentler and overshoot is far less likely. Never exceed the 30 µL the protocol
allows.

## 6. Sequencing **[MFR]**

```
kit:          SQK-LSK114
flow_cell:    FLO-MIN114
basecalling:  Dorado SUP, real-time, modified bases enabled
adaptive_sampling:
  enabled:    true
  mode:       enrich
  bed_file:   <panel>.bed
  reference:  GRCh38.fa
```

Watch pore occupancy. Below about 30% at 24 hours, with library still in the
fridge, run a nuclease wash and reload for roughly another 24 hours.
Translocation speed holds near 400 bases/second; a sharp drop means damaged
pores.

Expect 20-40 Gb across 48 hours. Whole genome from one cell gives about 10×.
Three to four cells merged reach 30×. Adaptive sampling on a panel under 1%
concentrates the same budget to 30-50× across the targets.

## 7. Basecalling **[ADAPTED]**

```bash
dorado basecaller -x auto \
  --modified-bases 5mCG_5hmCG \
  models/dna_r10.4.1_e8.2_400bps_sup@v5.2.0 \
  runs/<date>/pod5/ > reads.sup.bam
```

Most home setups run HAC live and reserve SUP for selected regions, because
SUP is roughly 10× slower. With adequate GPU it runs throughout, and
modified-base calling comes with it rather than as a second pass.

Methylation arrives from a software model reading the same raw signal — no
separate library, no bisulfite conversion, no different chemistry.

Retain POD5.

## 8. Alignment and coverage **[MFR]**

```bash
minimap2 -ax map-ont --MD ref/GRCh38.fa reads.sup.bam \
  | samtools sort -o aligned.bam -
samtools index aligned.bam
samtools flagstat aligned.bam
mosdepth --by panels/<panel>.bed cov aligned.bam
```

Expect over 95% mapped. On a 1% panel, adaptive sampling should show 5-6×
enrichment. A 1× result means it was not active.

Outputs are personal genomic data and are not stored in this repository.

## Cost per run

| | |
|---|---|
| R10.4.1 flow cell | ≈$988 |
| LSK114, one reaction of six | ≈$100 |
| NEBNext v2, one reaction of 24 | ≈$55 |
| Nanobind extraction | ≈$15 |
| AMPure, tips, tubes, ethanol | ≈$50 |
| **Per run** | **≈$1,200** |

Plus a $90 Flongle per pilot. The Mk1D and QC instruments are one-time.

## Not yet validated

- The Open Colorimeter Plus has never been used, by us, as a DNA fluorometer.
  The vendor's own fluorescence documentation is marked in progress.
- No emission filter has been selected. Slot dimensions are unknown.
- The 255/278 nm purity ratio is untested and may not be meaningful.
- A260/230 cannot be measured on this bench. This is the significant gap.
- No end-to-end run has been performed.

Each of these converts to a validated step or a documented failure. Both
outcomes get published here.

---

This is not a diagnostic service. Results from a kitchen-table sequencer have
not been validated by anyone and should not inform health decisions. Take
anything that concerns you to a clinician with access to diagnostic-grade
data.
