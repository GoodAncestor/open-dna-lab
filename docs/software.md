# Software

Everything here is free. Install it while hardware ships.

## Sequencing

| Tool | Purpose | Install |
|---|---|---|
| MinKNOW | Drives the flow cell, real-time basecalling, adaptive sampling | Vendor download, requires a free ONT Community account. Use the currently supported release for the Mk1D host. |
| Dorado | Basecalling and modified-base calling | `github.com/nanoporetech/dorado` |
| Readfish | Open adaptive sampling | `github.com/LooseLab/readfish` |
| minimap2 | Alignment | `conda install -c bioconda minimap2` |
| samtools | BAM handling | `conda install -c bioconda samtools` |
| mosdepth | Per-target coverage | `conda install -c bioconda mosdepth` |
| EPI2ME | Vendor analysis workflows, local or cloud | Vendor download |

### Native genome and methylome integration

Use the [analysis handoff](../templates/nanopore-analysis.md) with the [preparation protocol](../site/sequencing-protocol.md). Record the exact software, model, and reference versions for each run.

Dorado basecalling must retain modification tags in BAM. Alignment must preserve those tags. The previous minimap2 example incorrectly supplied BAM as sequence input. The integration performs the supported alignment path and checks its output.

Retain POD5 and verify a second private copy. Record actual storage use and allow space for analysis work files. Human sample inputs, alignments, variants, methylation, and reports remain outside this public repository.

## Instrument control

The design target is agent-driven operation, so the ranking is by quality of
the programmatic surface.

| Layer | Covers | Notes |
|---|---|---|
| Micro-Manager + pymmcore-plus + useq-schema | Microscopes, cameras, stages | ~200 device adapters. `useq` expresses an acquisition declaratively as JSON, which is a far better agent target than driving a GUI. |
| OpenFlexure server | The owned microscope | HTTP/JSON API. Already a network service. Usable today with no purchase. |
| open-colorimeter-utils (`oc-cal`) | Colorimeter calibration | On PyPI. Generates `calibrations.json`, which defines the tests in the instrument menu. A web app version exists. |
| ImSwitch | openUC2 hardware | Python, napari-based, REST API. Relevant if the XIAO leads anywhere. |
| Squid | Cephla hardware and third-party | `github.com/Cephla-Lab/Squid`. Full design is open even though the assembled product is out of budget. |

The OpenFlexure API is the cheapest way to prototype the whole agent-control
loop. It costs nothing and it determines what the interface needs to look like
before any instrument gets bought.

## Reference data

GRCh38 from Ensembl or UCSC. Fetch scripts belong in this repo; the downloaded
reference does not.

## Panel design

Adaptive sampling takes a BED file — chromosome, start, end, one region per
line, GRCh38 coordinates, overlaps merged, total target under 5% of the genome
and preferably under 1%.

Panel files tied to a specific person's clinical questions go in
`colbyt/genomics`. Generic panels and the tooling that builds them can live
here.
