# Software

Everything here is free. Install it while hardware ships.

## Sequencing

| Tool | Purpose | Install |
|---|---|---|
| MinKNOW | Drives the flow cell, real-time basecalling, adaptive sampling | Vendor download, requires a free ONT Community account. 24.11.10 or later for Mk1D. |
| Dorado | Basecalling and modified-base calling | `github.com/nanoporetech/dorado` |
| Readfish | Open adaptive sampling | `github.com/LooseLab/readfish` |
| minimap2 | Alignment | `conda install -c bioconda minimap2` |
| samtools | BAM handling | `conda install -c bioconda samtools` |
| mosdepth | Per-target coverage | `conda install -c bioconda mosdepth` |
| EPI2ME | Vendor analysis workflows, local or cloud | Vendor download |

### Basecalling

HAC runs in real time on modest hardware. SUP is roughly 10x slower and is the
mode that matters here, because super-accuracy plus modified-base calling is
what the epigenome work needs.

```bash
# whole run, SUP with CpG methylation
dorado basecaller \
  -x auto \
  --modified-bases 5mCG_5hmCG \
  models/dna_r10.4.1_e8.2_400bps_sup@v5.2.0 \
  runs/<date>/pod5/ > reads.sup.bam
```

```bash
# align, sort, index, coverage
minimap2 -ax map-ont --MD ref/GRCh38.fa reads.sup.bam \
  | samtools sort -o aligned.bam -
samtools index aligned.bam
samtools flagstat aligned.bam
mosdepth --by panels/<panel>.bed cov aligned.bam
```

Keep POD5. Storage runs about 7 GB per gigabase, so a 30 Gb run is roughly
210 GB. Re-basecalling archived signal against improved Dorado modification
models is a recurring gain, and most labs give it up because they cannot
afford the storage. Capacity here is not a constraint.

Outputs go to `colbyt/genomics`, never to this repo.

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
