# First OpenLab bench session

Blank worksheet, revision 1, 2026-09-06. No measurements have been performed for this worksheet. Copy it and the [shared run record](openlab-run-record.yaml) into your working storage. Use [measurement rows](openlab-measurements.csv) for raw and calculated values. Keep completed human-sample records private.

The first session establishes what the assembled instruments can measure. Use standards and a calibration slide; an extraction kit decision can follow. Choose one optical configuration at a time. Keep useful low-cost adaptations and record their measured limits.

## Start the record

| Field | Entry |
|---|---|
| run_id / purpose | |
| sample_id or event_id, if applicable | |
| operator / start and end timestamps, with timezone | |
| protocol_id / version | OPENLAB-FIRST-BENCH / 1 |
| instrument IDs / firmware or server versions | |
| raw data folder / backup / report | |
| standards, lots, expiry, preparation record | |
| planned acceptance limits and reason | |

Use independent preparations to test preparation variability; use repeat readings of the same tube to test reading variability. Label these separately. A suggested first-session design is three independent preparations at each chosen level, plus repeated readings of one check sample. This is a starting comparison design, not an established performance claim. Record any smaller design and its limits.

## Fluorometer: calibration, checks, dilution recovery

1. Record the actual LED wavelength and board revision, detector geometry, filters, tube type, gain, integration time, firmware and ambient-light conditions. Photograph the configuration.
2. Select the dye assay and save its instructions. Fill in assay volume, DNA aliquot volume, standard mass range and dilution scheme before preparing standards. These depend on the selected assay.
3. Read a reagent blank and standards spanning the planned working range. Preserve every raw reading and the blank ID; do not blank away each standard's signal. Re-read the blank at the end to check drift.
4. Fit a stated calibration model and save the coefficients, residuals and excluded readings with reasons. Flag saturation and results outside the tested range.
5. Read independently prepared check samples that were withheld from fitting. Record whether the check material comes from an independent stock or the calibration stock; a shared stock cannot test stock-value error.
6. Measure a check sample at two or more planned dilutions. Back-calculate the original concentration and compare it with the assigned check concentration. Record all dilution factors, including any pre-assay dilution; do not apply the assay dilution twice.
7. Compare the same aliquots with a reference fluorometer when available. Without one, retain the calibration and repeatability results and leave reference agreement pending. Test extraction and library matrices separately when available.

| Assay planning field | Entry |
|---|---|
| Assay product / catalog / lot / instructions revision | |
| Stock assigned concentration and source / uncertainty | |
| Total assay volume / DNA aliquot volume, µL | |
| Standard levels: DNA mass per assay, ng | |
| Independent preparations / repeated reads per tube | |
| Check sample IDs / matrix / dilution factors | |
| Blank drift / check recovery / repeatability limits | |
| Calibration equation, units and supported range | |
| Observed result / QC status / evidence files | |

Report concentration in the original tube separately from mass in the assay. Record dilution recovery as `100 × back-calculated concentration / assigned original concentration`. For a nonzero mean, report repeatability as `100 × sample standard deviation / mean`; near zero, use the standard deviation in signal units. A good curve fit alone does not establish accuracy.

IO Rodeo documents comparisons of LED placement and emission filters on this instrument. Use the owned optical configuration as the starting point and compare changes with the same blank and check material. [IO Rodeo fluorescence experiments](https://blog.iorodeo.com/open-colorimeter-plus-led-boards/).

## Colorimeter: blank, standards and context

1. Choose one intended measurement and its documented assay. Record the analyte, matrix, actual wavelength, cuvette material and path length, reagent lot, timing and instrument settings.
2. Record the method blank, assigned standards, independent check samples and repeated readings as above. Keep the original absorbance or detector readings alongside calculated concentrations.
3. For a water assay, record whether the method covers seawater or needs a matrix comparison. Preserve dilution, sample colour and visible particles in the record. Compare blanks and checks in the relevant matrix before treating the result as an environmental concentration.
4. If the standard or assay is unavailable, record an optical stability exercise and its raw signal. Leave quantitative assay validation pending.

| Planned analyte / matrix / units | Wavelength / path length | Blank and standards | Check limits / results / usable range |
|---|---|---|---|
| | | | |

Keep UV measurements labelled A255 and A278 when those are the fitted boards. A255/A278 does not supply A260/A280 or A260/A230. Keep raw scattering signals in their actual units until comparison with suitable standards supports a turbidity scale.

## OpenFlexure: image scale and a repeat capture

1. Record microscope ID, objective, camera, server version, image dimensions, exposure, gain and illumination. Save an original image of a stage micrometer with known division spacing. Record the slide ID, spacing and stated accuracy; borrow a slide if needed.
2. Measure the pixel distance across several known divisions. Calculate `µm per pixel = known length in µm / measured length in pixels`. Repeat at the centre and near the edges, and in both image directions by repositioning the scale. Record each span and result.
3. Check the resulting scale against a separate span excluded from calibration. In ImageJ, a line selection and **Analyze → Set Scale** associate known length and units with pixel distance. Preserve the original calibration image and measurement selections. [ImageJ spatial calibration](https://imagej.net/ij/docs/guide/146-30.html#sub:Set-Scale).
4. Capture a prepared non-human test slide, move away and return, then repeat the image. Record focus, illumination, visible detail and return error. Use the installed version's stage-mapping controls only after confirming slide clearance. Camera-to-stage mapping supports motion; record the micrometer measurement separately as the evidence for physical image scale. [OpenFlexure stage-mapping documentation](https://openflexure.gitlab.io/openflexure-microscope-server/python/openflexure_microscope_server.things.camera_stage_mapping.html).
5. Save images with the run and sample/event IDs. Recheck scale after changes to objective, optics, camera mode or image resizing. If no micrometer is available, save the capture exercise with scale marked pending and omit physical size claims.

| Slide ID / spacing / accuracy | Image ID / dimensions | Axis / position / known span, µm | Measured pixels / µm per pixel | Check result / QC |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

## Keep or revise each adaptation

| adaptation_id / exact change | Access or cost reason | Expected benefit / possible failure | Measurement and predeclared limit | Outcome / keep, revise or retest |
|---|---|---|---|---|
| | | | | |

A lower-cost filter, printed holder or substituted instrument can remain in use within its demonstrated range. Record unresolved comparisons as pending. Keep the raw data from unsuccessful trials.

## Close the session

- Record the supported range, matrix and configuration for each measurement; leave untested properties explicit.
- Save original readings, images, calibration calculations and a brief report; add SHA-256 checksums to the artifact list.
- Choose one next experiment from the largest measured uncertainty. Record its owner and needed material.
- Carry the results into the [Nanopore readiness checklist](nanopore-readiness.md). Pending kit identity or pipette availability does not prevent another standards or imaging session.

**Session conclusion:** ______________________________________________

**Next experiment / owner / needed material:** _______________________
