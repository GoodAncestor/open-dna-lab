---
title: Good Ancestor open DNA lab
description: An open genomics for citizen science
badge: Open lab
tagline: A repository of open hardware and software for the citizen scientist.  Including everything we use to sequence and analyze DNA affordably at home.
hero_stats:
  - val: Assembled
    lbl: optical instruments ready for testing
  - val: First run
    lbl: genome and methylome validation
  - val: Open
    lbl: hardware, protocols, software
footer:
  org: Good Ancestor Foundation
  line: Open lab — equipment, protocols, and software we use in our work.

---

## What does the Open DNA Lab do

The lab's goal is to document the process from end to end: capturing aquatic, mammalian, insect, plant, and other tissue samples, characterizing their environment and traits, sequencing their DNA and epigenome, and performing and publishing new citizen research.  

Below you can find details on our quest to implement a $10k open DNA lab from what started out as $80k in proprietary vendor recommendations. The $10k figure is a planning target. Current item costs and estimates are in the [equipment register](/inventory).

The colorimeters, fluorometers, and OpenFlexure have arrived and are assembled. Our first validation will prepare our own native DNA for Oxford Nanopore sequencing and analysis in DNA-Report. [Follow the preparation protocol](/protocol) and its blank run records. DNA assay calibration and an end-to-end bench run remain pending.

## Why we published this

This lab and its methods and software is a contribution back to the community and our grantee [Humanitarian Technology Trust](https://httrust.org/).  Many of the parts and devices here are purchasable in the US from the wonderful vendor [IO Rodeo](https://iorodeo.com/) - [Github](https://github.com/iorodeo/) who contributes 20% of OpenFlexure Microscopes back to Humanitarian Technology trust https://openflexure.org/ - and includes components from Sangaboard which contribute to support a Tanzanian makerspace co-founded by the original Sangaboard creator.  If you are outside the US and would like to find a vendor in your region, check [Open Science Shop](https://www.openscienceshop.org/manufacturer-page/).  We are big fans of the [distributed local manufacturing model](https://www.nyuengelberg.org/outputs/distributed-manufacturing-of-open-hardware/) seen here and at our grantee [Open Source Ecology](https://opensourceecology.org).

## Four ways to participate with us

::: cards
variant: why
items:
  - title: Sequence your own DNA
    desc: "Start with [the protocol](/protocol) — a
      blood draw, extracting long intact DNA, quality control, library
      preparation, sequencing on a MinION, and analysis. Help us refine and improve the process"
  - title: Analyse genetic data you already have
    desc: "If you have 23andMe raw data, a VCF, or a nanopore file, [DNA-Report](https://dna.goodancestor.com) will show what science currently knows about your DNA (genome and epigenome)."
  - title: Improve our software
    desc: "
      [bio-core](https://github.com/GoodAncestor/bio-core) handles basics, human genetic knowledge lives in [GeneAsk](https://github.com/GoodAncestor/GeneAsk) for genomes and [MethylAsk](https://github.com/GoodAncestor/MethylAsk) for methylation. And of course [DNA-Report](https://dna.goodancestor.com) for the results."
  - title: Join the seagrass work
    desc: "[Seagrass climate resilience](https://seagrass.goodancestor.com) is our project to protect the coral reef ecosystem, and its carbon sequestration by helping seagrass thrive in adverse conditions."
:::

## Open Tools in this lab

The tools we use are primarily open designs you can build, repair, and modify yourself -- they can also be run by your local AI agent.  All the tools below are affordable and available globally, well documented and simple to use.


**Measuring with light**

We use **[Open Colorimeter Plus](https://iorodeo.com/pages/open-colorimeter)**. Sold as a colorimeter, it becomes a fluorometer once you add a filter: a light sensor sits at ninety
degrees to a blue LED, so it sees only the light a fluorescent dye emits rather
than the beam passing through. That is the same trick a $3,000 benchtop
fluorometer uses, in a $200 box running open CircuitPython firmware.

The **[UV Open Colorimeter](https://iorodeo.com/pages/open-colorimeter)** measures absorbance. IO Rodeo documents measurements of [DNA](https://blog.iorodeo.com/uv-dna-quantification/) and [proteins](https://blog.iorodeo.com/uv-colorimeter-bsa/). Our 255 and 278 nm measurements cannot be labelled A260/A280, and the current setup does not provide A260/A230. We will seek reference UV measurements for comparison. The [adaptation register](/adaptations) describes a pilot when reference access is limited.

Feeding them are twelve [LED emitter boards](/inventory), each a different
wavelength. Three matter for DNA work: 255 nm and 278 nm support UV experiments,
and 470 nm excites the dye proposed for measuring concentration. The other nine do cell
density, chlorophyll, and enzyme assays — the colorimetry and biology side of the
lab rather than the sequencing side.

We check both instruments against something whose answer is already known before
we trust them with DNA. [Caffeine and vitamin C](/colorimetry) cost about a
dollar a run, and both are sold as tablets with a label claim to measure
against.


**Potentiostat**

The **[Rodeostat](https://iorodeo.com/products/rodeostat-hc)** is a potentiostat - it allows us to do many things -- to measure water quality/chemistry dissolved oxygen, chlorine peroxide, nitrate farm runoff sensors to characterize samples for our [seagrass project](https://seagrass.goodancestor.com) -- it can be used to detect heavy metals — lead, cadmium, copper, zinc, nitrates in drinking water lake water groundwater soil extracts on our research farm --  it can even be used for battery research, corrosion science on our [electric vehicle](https://ev.goodancestor.com) or to measure [glucose in your soda](https://blog.iorodeo.com/chronoamperometry-with-glucose-test-strips/).

In a future DNA kit the lower power version could help us develop, custom DNA sensors, RNA sensors, CRISPR-based electrochemical assays, nanopore electrode experiments, impedance-based biosensors and more.

**Automated Microscopes**

The **[OpenFlexure microscope](https://openflexure.org/)** allows us to look at and characterize tissue samples -- it is affordable, capable 3D-printed, motorised, and exposes an HTTP API — which means an agent can drive it directly instead of a person turning knobs.  

Another great open microscope we use for portable microscopy is based on [OpenUC2](https://shop.openuc2.com/). You can [find it at Seeed Studio](https://www.seeedstudio.com/XIAO-Microscope-p-5971.html), which is also a great place to get [environmental sensors](https://www.seeedstudio.com/Grove-c-2421.html).

**Environmental Monitoring and Collection**

A genome tells you what an organism can do. Its environment decides what it
actually does, so a trait only means something when you have measured both —
which is why heat, light, water chemistry, and soil get logged alongside the
sequencing. The environment is also a sample in its own right: water and soil
carry shed DNA from everything living in them, and reading it is how you survey
a site without catching anything.

For Seagrass, these measurements add environmental context to each existing specimen collection. Link water temperature, salinity, collection depth, light or clarity, and validated chemistry results to the specimen record. The method applies across locations. Bay Area access makes local testing convenient.

Seeed Studio is where we get most of the [environmental monitoring](https://www.seeed.cc/solutions/environment-monitoring) sensors and [smart agriculture sensors](https://www.seeed.cc/solutions/smart-agriculture-sensing) we use on our research farm and environmental / conservation projects.

We are building a [Mothbox](https://mothbox.org/) [2](https://blog.iorodeo.com/mothbox-introduction/) for monitoring insect ecosystem impacts at our research farm.

## Should you use a vendor, or sequence yourself at home?

Sequencing your own genome at home is already possible.  What most of those write-ups have in common is that they hand the hard part — checking whether your DNA sample is good enough to sequence in the first place — to a $3,000 commercial instrument. Or they skip the check entirely and hope.

This lab tests affordable open hardware for DNA quality control. We will compare the assembled fluorometers with reference measurements before using them to set library input mass. Input DNA sizing and UV purity measurements remain separate checks. The [adaptation register](/adaptations) preserves lower-cost alternatives and the tests that could validate them. An optional Flongle pilot can test library preparation and sequencing performance.

Even still -- the simple answer for most people is to have their genome sequenced at a professional lab. At a vendor like [Renew Biotechnologies](https://www.renewbt.com/) you can get a high quality genome and epigenome run for a few thousand dollars.  

The DIY approach documented here is appropriate for someone sequencing multiple genomes and wanting to do/learn the bench work themselves, who is interested in keeping their genetics private beyond the company's TOS, or who wishes to have the raw machine output to process again in the future. Beyond that, both routes end in the same kind of file, and both can put input into our [DNA-Report](https://dna.goodancestor.com/).  

| | Your own bench | Service laboratory |
|---|---|---|
| **Up-front cost** | Instrument and bench kit — see the [buy list](/buy-list) | Nothing |
| **Cost per sample** | Consumables only, once the instrument is paid for | Full price, every sample |
| **Time** | Hands-on work | Ship it and wait |
| **If it fails** | A wasted flow cell, and the cost is yours | Usually re-run at their expense |
| **Raw signal** | Stays in the building | Most return processed data only |
| **Re-analysis later** | Re-run the basecaller as the models improve | Only if you were given the raw data |
| **Methylation** | Native, in the same run | Confirm they preserve it; many pipelines do not |
| **Trustworthiness** | DIY | Accredited, audited, and answerable |

**Archiving raw signal** allows us to repeat basecalling and modification analysis when methods change. Measure storage use on the control run and plan capacity for POD5, alignments, working files, and a second private copy. Confirm raw-signal access and retention terms when using a sequencing service.




