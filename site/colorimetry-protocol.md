---
title: Caffeine and vitamin C on the Open Colorimeter
sub: Two assays with a known answer, used to check the instruments before DNA work depends on them
badge: Protocol
status: draft — written from published chemistry and vendor documentation. No measurement has been taken on this bench.
updated: 2026-08-22
toc: true
hero_stats:
  - val: ≈$1
    lbl: reagent cost per run
  - val: 2 instruments
    lbl: UV Open Colorimeter and Multichannel
  - val: 0
    lbl: measurements taken so far
footer:
  org: Good Ancestor Foundation
  line: Open lab — equipment, protocols, and software we use in our work.
---

# Caffeine and vitamin C on the Open Colorimeter

## Why these two assays

The colorimeters on this bench were bought to do DNA quality control. DNA is an
expensive thing to practise on. The extraction chemistry costs about $15 a go,
and the sample is a blood draw. A bad reading shows up three steps later, when a $988
flow cell underperforms.

Caffeine and vitamin C cost about a dollar a run. Both come as pure powders with
a stated purity. Both are also sold as tablets with a label claim, so every
measurement has something to be checked against.

Together they cover every part of the DNA path:

- **Direct UV absorbance.** The same measurement as the A260/A280 purity ratio in
  the [sequencing protocol](/protocol), on the same instrument and the same
  cuvettes.
- **A reaction-based visible assay.** You add a reagent and a colour changes with
  concentration. Every dye-binding and enzymatic assay works this way, including
  the AccuClear fluorometry that quantifies DNA.
- **The calibration workflow.** A dilution series, a fitted curve, and a
  `calibrations.json` file loaded onto the instrument so it reads out in
  concentration units.

## Validation status

Every step carries a marker. The vocabulary is the same as the sequencing
protocol.

| Marker | Meaning |
|---|---|
| **[MFR]** | Vendor documentation. Follow IO Rodeo's page, not ours. |
| **[ADAPTED]** | Established analytical chemistry, adapted to this instrument. |
| **[UNTESTED]** | Our substitution. No measurement taken on this bench. |

IO Rodeo publishes colorimeter tutorials for
[DNA quantification, protein and Bradford assays, beer colour, turbidity, soil
active carbon, and the ammonia, nitrate and nitrite water
tests](https://blog.iorodeo.com/open-colorimeter-tests/). Caffeine and vitamin C
are absent from that list. The firmware ships with four built-in tests: blue food
dye, ammonia, nitrate and nitrite. Both assays below are new calibrations, built
from scratch.

## Safety

**Weigh caffeine powder on a balance. Never measure it by volume.** A level
teaspoon holds several grams, which is in the range that has killed people. Bulk
caffeine powder carries FDA warnings for this reason. Store it away from anyone
who might mistake it for something else. Label the stock solution with its
concentration and the date.

**Do not swallow oxalic acid.** It is toxic. Metaphosphoric acid is corrosive.
DCPIP is a low-hazard dye, but it stains skin, clothing and bench tops.

**Keep the UV beam enclosed.** LEDs at 255 nm and 278 nm are invisible, so the
eye gives no warning that they are on. The UV Open Colorimeter encloses the beam.
Do not run the board outside its holder.

## Equipment

**Caffeine.** UV Open Colorimeter with the 278 nm emitter board. The four
BrandTech ultramicro UV cuvettes it ships with: 10 mm path, 0.4 mL minimum fill,
window centre 15 mm from the base. A 1 L volumetric flask. A balance that reads
to 1 mg. Syringe filters, 0.45 µm. Caffeine anhydrous USP powder. One 200 mg
caffeine tablet as a reference sample.

**Vitamin C.** Multichannel Open Colorimeter with its white LED board. Macro or
semi-micro cuvettes, 1.5 mL minimum fill. L-ascorbic acid USP powder. DCPIP
sodium salt. Sodium bicarbonate. Metaphosphoric acid or oxalic acid. Amber
bottles. One vitamin C tablet of stated strength.

Both instruments take any 10 mm pathlength cuvette with outer dimensions under
12.5 mm. The holder measures 12.65 mm inside.

Mark one face of each ultramicro cuvette and load it the same way round every
time. The window is narrow. Turning the cuvette changes how much of the beam
misses it. That change is larger than most of the differences you are measuring.
Hold the cuvette by its frosted faces. A fingerprint absorbs strongly in the UV.

## Caffeine by UV absorbance at 278 nm
sub: Add nothing to the sample. Dilute it, read it, and compare against a curve built from weighed caffeine.

Caffeine absorbs ultraviolet light strongly. The peak is at 273 nm in water, and
the absorbance is proportional to concentration. Dilute a drink, read it against
a curve of known standards, and you have the caffeine content.

### Choosing the emitter **[ADAPTED]**

Two owned boards sit either side of the 273 nm peak. The UV Open Colorimeter
ships with 255 nm. The 278 nm board was bought for the A280 purity measurement.

Use the 278 nm board. It is closer to the peak, and it sits on the shallower side
of it. The board has a bandwidth of 10 to 15 nm, and LED wavelength varies from
part to part. On the shallow side, both errors move the reading less. At 255 nm
the same error lands on the steep rising flank and costs more.

Reading off the peak costs sensitivity. It does not cost accuracy, because the
calibration curve is measured at the same wavelength as the sample. The assay
needs a wavelength that stays the same between the standards and the sample.

### Working range **[ADAPTED]**

Beer's law fixes the concentration window before you set anything up. Caffeine's
molar absorptivity at the peak is
[reported between about 9,700 and 11,000 L mol⁻¹ cm⁻¹](https://pmc.ncbi.nlm.nih.gov/articles/PMC4641934/).
Take 10,000 and a 10 mm path. Absorbance reaches 1.0 at about 20 mg/L and 0.1 at
about 2 mg/L.

Keep every reading between 0.1 and 1.0. Below 0.1 the blank noise dominates.
Above 1.0 stray light inside the instrument bends the curve toward the axis. That
bend is an instrument artefact, and it looks like a real result.

Absorbance at 278 nm is lower than at the peak, so the usable window sits higher
in concentration than the arithmetic above suggests. Measure where it lands.

Start from these dilutions:

| Sample | Typical caffeine | First dilution to try |
|---|---|---|
| Drip coffee | 400-800 mg/L | 1:50 |
| Espresso | 2,000-5,000 mg/L | 1:200 |
| Black tea | 150-350 mg/L | 1:20 |
| Cola | 90-130 mg/L | 1:10 |
| Energy drink | 250-350 mg/L | 1:25 |
| 200 mg tablet in 1 L | 200 mg/L | 1:20 |

Caffeine levels vary with brand, roast, grind and brew time. Adjust the dilution
until the absorbance lands in the middle of the range.

### 1. Make the standards **[ADAPTED]**

1. Weigh 1.000 g of caffeine anhydrous into a 1 L volumetric flask. Make up to
   the mark with distilled water. This is the 1,000 mg/L stock.
2. Use warm water. Caffeine dissolves slowly in cold water. Let the flask return
   to room temperature before you make up to the mark.
3. Dilute the stock into at least seven working standards, from 1 to 25 mg/L.
   Prepare a water blank as well.
4. Refrigerate the stock. Discard it if it goes cloudy.

Weigh a gram and dilute it. Do not weigh 100 mg directly. A balance that reads to
1 mg gives 0.1% on a 1 g weighing and 1% on a 100 mg weighing. That error carries
into every standard.

### 2. Read the standards **[MFR]**

Fit the 278 nm board and switch the instrument on. Follow the vendor's
[basic operation](https://blog.iorodeo.com/open-colorimeter-user-manual/)
sequence: select the test, insert the blank, press the blank button, then read
each sample.

Change three things in that sequence while you build a curve **[ADAPTED]**:

- Blank with the same water you made the standards from. Do not use a different
  bottle.
- Blank again before every standard. The vendor procedure blanks once per
  session, which suits a field measurement. LED output drifts as the board warms,
  and the drift would land inside the curve.
- Read each standard three times. Take the cuvette out and put it back between
  reads. The spread across those reseats is the repeatability that matters. It is
  usually several times larger than the spread across repeat reads of a cuvette
  left in place.

### 3. Fit and load the calibration **[MFR]**

See [Calibration files](#calibration-files) below.

Inspect the residuals of the fit. Do not judge it on R². A curve bending from
stray light still reports R² above 0.99.

Measure the limit of detection as three times the standard deviation of the
blank. Measure the limit of quantitation as ten times. Ten repeats of the blank
are enough.

### 4. Check recovery against a tablet **[UNTESTED]**

A 200 mg caffeine tablet is the cheapest reference material available. The
excipients are cellulose and magnesium stearate. Neither absorbs in the UV.

1. Crush one tablet and dissolve it in water to 1.000 L.
2. Filter through 0.45 µm. Undissolved cellulose scatters light, and the
   instrument reads scatter as absorbance.
3. Dilute to the working range and read.
4. Calculate back to milligrams per tablet.

The label claim is a specification with its own tolerance, not a certified value.
Agreement to a few percent is as much as this check can show. It still catches a
mis-made stock, a wrong dilution factor, or a curve fitted the wrong way round.

### 5. Real drinks **[UNTESTED]**

Coffee and tea contain chlorogenic acids and other polyphenols. They absorb
across the same UV band. A reading at 278 nm on brewed coffee is the sum of the
caffeine and everything else in the cup.

Published methods extract the caffeine into dichloromethane before reading, or
separate it on HPLC. Neither belongs on this bench, which has no fume
hood.

Three things work without a solvent:

- **Report what you measured.** Absorbance at 278 nm, expressed as caffeine
  equivalents. The number tracks caffeine within one brand and one brewing
  method. It does not compare a coffee against a tea.
- **Subtract a matrix blank.** Brew a decaffeinated coffee the same way. Use the
  same roast where you can, the same grind, the same water and the same contact
  time. Blank against it. Decaf keeps a few percent of the original caffeine, and
  its polyphenol profile shifts with roast. This blank carries a bias we have not
  measured.
- **Use standard addition.** Add a known mass of caffeine to the real sample and
  read it again. Calculate the concentration from the increase, not from the
  absolute reading. This corrects a constant background. It does not correct a
  background that changes with dilution. Run both methods on one sample to find
  out how large that error is.

Cola has a second interferent. Sodium benzoate absorbs weakly between 260 and
280 nm, and most colas contain it at a concentration close to the caffeine.

## Vitamin C by DCPIP decolorisation
sub: The dye loses its colour in proportion to the vitamin C that reduced it

Vitamin C is a reducing agent. DCPIP, or 2,6-dichlorophenolindophenol, is a dye
that is coloured when oxidised and colourless when reduced. Mix a fixed amount of
dye with the sample. The colour that survives tells you how much vitamin C was
there.

This is the colorimetric form of the AOAC indophenol titration, with the visual
endpoint replaced by a reading. One molecule of vitamin C reduces one molecule of
dye, and at acid pH the reaction is fast.

### The instrument **[ADAPTED]**

Use the Multichannel Open Colorimeter. It has a white LED and an AS7341 sensor
that reads eight visible channels: 415, 445, 480, 515, 555, 590, 630 and 680 nm.

DCPIP changes colour with pH. Above about pH 6 it is blue, with a peak near
600 nm and a
[molar absorptivity around 18,500 L mol⁻¹ cm⁻¹](https://jascoinc.com/applications/rapid-kinetic-measurement-26-dichloroindophenol-using-uv-visible-absorption-stopped-flow-system/).
Below pH 6 it turns pink, with a peak near 520 nm. This assay runs acidified,
because vitamin C does not survive at neutral pH. So 515 nm is the working
channel, and 630 nm reports how much blue form is left. The Multichannel reads
both in one measurement, with no board to change.

**Check this first.** The `led` field in a calibration file holds a wavelength.
How that maps onto an AS7341 channel is undocumented. Confirm two things on the
instrument before you build a curve: which channels the menu offers, and which
one a calibration entry binds to.

### Reagents **[ADAPTED]**

**Stabilising acid.** Use 3% metaphosphoric acid or 0.4% oxalic acid. Vitamin C
oxidises within minutes in a neutral solution, and faster in the presence of
copper, iron or dissolved oxygen. The acid holds it. Metaphosphoric acid is the
AOAC choice and also precipitates protein, which matters for milk and smoothies.
Oxalic acid is cheaper and works for juices and tablets. Metaphosphoric acid
degrades in solution, so make it fresh, keep it cold, and use it within a few
days.

**DCPIP.** Dissolve 50 mg of DCPIP sodium salt and 42 mg of sodium bicarbonate in
about 50 mL of hot water. Dilute to 200 mL, filter, and store in an amber bottle
at 4 °C. This recipe comes from the AOAC indophenol titration. Check it against
the method text before you rely on the numbers.

Read a fresh dye blank in every session. The dye loses strength over days. A
blank value carried over from a previous day overstates the vitamin C in every
sample measured against it.

### Standards **[ADAPTED]**

Weigh 1.000 g of L-ascorbic acid into 1 L of the stabilising acid. This is the
1,000 mg/L stock. Make it on the day you use it. Keep it cold and dark. Dilute
from it to make the working standards.

Fix the dye volume and the total reaction volume. Vary only the sample volume.
Set the dye concentration so the strongest standard uses about 80% of it. A
sample that removes all the colour reads the same as one twice over range, and
gives no warning that it did.

Start from 1.0 mL of dye solution plus 1.0 mL of acidified sample, read at
30 seconds. Dilute the dye until a 20 mg/L standard removes most of the starting
absorbance, and a 2 mg/L standard removes a little.

### Read at a fixed time **[ADAPTED]**

Use a timer. Read every sample and every standard at the same number of seconds,
between 15 and 30.

Vitamin C reduces DCPIP in seconds. Polyphenols and most other reducing agents in
food react more slowly. A short fixed read time favours vitamin C. A long one
lets the interferents catch up.

### Selectivity: the difference blank **[UNTESTED]**

DCPIP responds to reducing agents in general. Sulfites in wine and dried fruit,
iron(II), cysteine and polyphenols all remove its colour. The instrument cannot
tell them apart from vitamin C.

Split the sample to solve this. Destroy the vitamin C in one half. Run both
halves. The difference between them is vitamin C, and the remainder is everything
else.

Three ways to destroy it:

- **Ascorbate oxidase.** Specific, and the reference method. It costs money.
- **Copper and air.** Add a trace of copper sulfate at neutral pH and stir for a
  few minutes. Cheap, and less specific, because copper oxidises other reductants
  as well.
- **Alkali.** Hold at about pH 9 for ten minutes, then re-acidify. The cheapest of
  the three.

Characterise the two cheap options against the enzyme, or against a sample spiked
with a known amount of vitamin C, before you trust either one.

### Validation targets **[UNTESTED]**

1. **Tablet recovery.** Dissolve a 500 mg or 1,000 mg vitamin C tablet, filter
   it, dilute it, and calculate back to the label claim.
2. **Iodine cross-check.** Tincture of iodine with a starch indicator titrates
   vitamin C by different chemistry. It gives an independent number for a few
   dollars.
3. **Direction test.** Compare fresh juice against juice left open for 48 hours
   at room temperature, and against juice boiled for ten minutes. Vitamin C falls
   in both. An assay that fails to move in the right direction on a sample you
   degraded on purpose is measuring something else.
4. **Standard addition into juice**, as for caffeine above.

### The UV route **[UNTESTED]**

The UV Open Colorimeter can read vitamin C directly. The
[acid form peaks near 244 nm and the ascorbate anion near 265 nm](https://www.scielo.cl/pdf/jcchems/v59n3/art13.pdf).
Molar absorptivity at 265 nm is around 14,500 L mol⁻¹ cm⁻¹. The owned 255 nm
board falls between the two peaks.

That position leads to a claim we can test. Two forms of one molecule absorb on
either side of 255 nm. The total absorbance there should change little as the
balance between the forms shifts. A reading at 255 nm may therefore hold steady
as the sample pH crosses the first pKa, near 4.1. Read one standard at pH 2, pH 4
and pH 7, and see whether the number moves.

Direct UV has the same problem as caffeine in coffee. Juice contains flavonoids
and other UV-absorbing compounds, and the reading is their sum. The difference
blank above makes the UV route usable. It works there as it does for DCPIP.

## Calibration files
sub: One .toml file per test, fitted by oc-cal into the calibrations.json the instrument reads

The instrument builds its menu from `calibrations.json`. Each entry becomes a test
that reads out in concentration units. Generate the file with `oc-cal`, from the
[open-colorimeter-utils](https://pypi.org/project/open-colorimeter-utils/)
package **[MFR]**.

```toml
# caffeine.toml
name = "Caffeine 278"
led = 278
units = "mg/L"
fit_type = "linear"
fit_order = 1
values = [
    [0.0, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0],   # concentration, mg/L
    [],                                             # absorbance, not yet measured
    ]
```

```toml
# vitamin-c.toml
name = "Vitamin C DCPIP"
led = 515
units = "mg/L"
fit_type = "polynomial"
fit_order = 2
values = [
    [0.0, 2.0, 5.0, 10.0, 15.0, 20.0],   # concentration, mg/L
    [],                                  # absorbance, not yet measured
    ]
```

Leave the absorbance row empty until you have run the series. `oc-cal` fits
whatever you give it. It will not warn you that the numbers were invented.

```bash
pip install open-colorimeter-utils
oc-cal caffeine.toml vitamin-c.toml -o calibrations.json
```

Pass every `.toml` file in one command. `oc-cal` writes a complete file. It does
not merge into an existing one, so running it on a single test drops the other
tests out of the menu.

Two details of the generated file, taken from the vendor's worked example. The
fit maps absorbance to concentration. The `range` block it writes is in
absorbance units, not concentration.

Copy the result to the instrument's CIRCUITPY drive. Check the vendor page for
the exact location before you overwrite anything already there.

Keep the `.toml` files in this repository. They record what the curve was fitted
to. The JSON on the instrument is a derived file.

## Where these are likely to fail

- **Warm-up drift.** LED output moves for the first few minutes after power-on.
  Let the instrument sit before you take the first blank.
- **Stray light above absorbance 1.0.** The curve flattens and the high standards
  read low. R² stays high while it happens.
- **Cuvette handling.** Orientation, fingerprints and small scratches all matter
  more in the UV than in the visible.
- **Temperature.** It sets the DCPIP reaction rate. A fixed read time only helps
  if every sample is at the same temperature.
- **Dye age.** DCPIP solution weakens daily.
- **Traceability.** Every number on this page rests on one weighing and one
  volumetric flask. This bench holds no certified reference material and no
  second instrument to cross-check against. That is the same gap that keeps a
  Qubit on the [buy list](/buy-list) for the DNA work.

## Not yet validated

- No caffeine standard has been weighed. No absorbance has been read at 278 nm on
  this instrument.
- No DCPIP solution has been made. The 80% dye-consumption rule is a design
  choice, not a measured recipe.
- We have not confirmed which AS7341 channel a calibration entry binds to on the
  Multichannel.
- We have not tested whether 255 nm holds steady across the vitamin C pKa.
- The decaf matrix blank and the two cheap ways to destroy vitamin C all carry
  biases we have not measured.

Each item becomes a validated step or a documented failure. We publish both.

---

These assays check the instruments. A number from this bench is not a food-safety
or nutrition measurement. Do not use one to make a claim about any product's
caffeine or vitamin content.
