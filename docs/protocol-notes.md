# Protocol notes

Practical points gathered while planning the build. The authoritative
documents are the NEB and ONT protocols; these are the things those documents
underplay or omit.

Sources are listed in `sources.md`. Where a note comes from one person's
published account rather than a manufacturer, that is marked.

## Before the run

**Pore-check every flow cell before loading anything.** Seat it, let it warm
for 20 minutes, run the check in MinKNOW. A fresh cell shows around 1,200
pores. Require at least 800. Below that, claim the warranty before loading —
once your library is on it, the warranty argument is gone. Some cells arrive
dead. Twenty minutes protects $988.

**Flow cells store at 4 C.** Reagent kits store at −20 C. Ethanol stores at
room temperature and never goes in either.

## Extraction

Blood gives longer fragments and higher DIN than saliva. Saliva carries a
10-30% bacterial DNA fraction, which consumes flow cell capacity that was paid
for. Cheek-cell read lengths peak around 4 kb in one published home run.

Wide-bore tips throughout. Standard tips shear high-molecular-weight DNA.

Never vortex HMW DNA. Flick to mix, or use a rotator.

Pre-heat elution buffer to 60 C before the final elution. Reported as the
difference between a clean 100-150 ng/uL eluate and leaving half the DNA on
the column. (Single published account, buccal protocol.)

A cloudy eluate indicates salt carry-through. Re-wash the column before
library prep.

## QC

Three measurements, and they are not substitutes for each other.

| Measurement | Instrument | What it gates |
|---|---|---|
| Concentration | Fluorometer | Library input mass |
| Purity, A260/280 and A260/230 | Full-spectrum absorbance | Pore fouling |
| Fragment length | TapeStation, gel, or a Flongle | Read length |

Absorbance overestimates DNA when RNA or free nucleotides are present, so it
cannot replace fluorometric quantification for input mass.

A260/230 predicts pore fouling. Phenol, guanidinium, polysaccharides,
polyphenols, and detergents all foul pores, and the failure appears four hours
into a run as collapsing active-pore count.

One published home run skipped fluorometric quant entirely, got poor pore
occupancy, and could not distinguish a failed extraction from a failed library
prep. Quantification is what makes the run debuggable.

## Library prep

**No PCR-based kit for epigenome work.** Amplification erases base
modifications. Methylation survives only in native DNA, which rules out the
PCR and cDNA-PCR kits.

Do not vortex the enzyme mixes. They are formulated in glycerol; vortexing
froths them and destroys activity. Flick instead.

Ligation Buffer (LNB) is viscous and will not vortex into solution. Pipette-mix
slowly or you get invisible layers in a nominally mixed reaction.

Do not over-dry the AMPure pellet. Thirty seconds of air-drying is enough.
Longer and the beads crack and weld to the tube wall.

Use Long Fragment Buffer for the second cleanup, not ethanol. LFB preserves
the adapter's motor protein; ethanol strips it, and without the motor protein
the adapter cannot pull DNA through a pore.

At the magnetic rack, a brown line should form against the tube wall within a
minute or two and the solution should start to clear. If neither has happened
by about 2.5 minutes, the magnet is too weak or sitting too far from the
sample.

Expect 150-450 ng of library in 15 uL. Twelve uL goes onto the flow cell; the
remainder is the reload reserve for a mid-run wash.

## Loading

Air in the flow cell is the single most common way to ruin a run. Pores that
air crosses go offline permanently. Watch ONT's priming and loading video
before the first attempt.

For the draw-back, dial the volume wheel rather than pressing the plunger. The
suction is gentler and overshoot is much less likely. Never exceed the 30 uL
the protocol allows.

## During the run

Watch pore occupancy. It falls as pores block or die. Below about 30% at the
24-hour mark, with library still in the fridge, run a nuclease wash and reload.
That typically buys another 24 hours.

Translocation speed holds around 400 bases/second. A sharp drop means damaged
pores.

Read-length distribution should match what the extraction produced.

## Coverage arithmetic

A flow cell yields 20-40 Gb over 48 hours. The human genome is 3.2 Gb.

- One flow cell, whole genome: about 10x. Enough for common variants.
- Three to four flow cells merged: 30x, the threshold for confident variant
  calling.
- One flow cell with adaptive sampling on a panel under 1% of the genome:
  30-50x across the panel.

Adaptive sampling reads the first ~500 bases of each fragment, checks it
against a reference, and reverses the pore voltage to eject fragments outside
the target regions. Targeted enrichment with no probes, no PCR, and no special
library. Readfish is the open implementation.

Plant genome sizes vary by two orders of magnitude and change the arithmetic
completely — 135 Mb for Arabidopsis against 16 Gb for wheat.

## Plant work, when it starts

Isolate nuclei before extraction. It strips cytoplasmic contaminants and cuts
chloroplast and mitochondrial reads.

CTAB protocols use chloroform, which requires ventilation and halogenated
waste disposal. Kit-based nuclei isolation avoids it.

Tissue must be fresh or flash-frozen, never dried. Young low-pigment tissue
extracts better than mature tissue.

Plants methylate CG, CHG, and CHH contexts. ONT's flagship modified-base
models are CpG-context — the Mk1D specification cites CpG-context 5mC/5hmC for
real-time modification calling. Dorado ships all-context 5mC models; verify
availability and accuracy for non-CG contexts before planning plant epigenome
work around them.
