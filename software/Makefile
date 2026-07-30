.PHONY: help env dorado readfish reference check clean

SHELL := /bin/bash
REF_DIR ?= ref
CONDA ?= mamba

help:
	@echo "make env        - create the openlab conda environment"
	@echo "make dorado     - install Dorado + basecalling models"
	@echo "make readfish   - install Readfish for adaptive sampling"
	@echo "make reference  - download and index GRCh38"
	@echo "make check      - validate data/items.yaml"
	@echo ""
	@echo "MinKNOW installs from the ONT Community portal by hand."

env:
	$(CONDA) env create -f software/environment.yml || \
	$(CONDA) env update -f software/environment.yml
	@echo "Activate with: conda activate openlab"

dorado:
	bash software/install-dorado.sh

# Readfish drives adaptive sampling against MinKNOW's API.
readfish:
	pip install "readfish[all]"
	@echo "Configure against MinKNOW before a run — see readfish docs."

# GRCh38 primary assembly. ~900 MB compressed. Not committed to the repo.
reference:
	mkdir -p $(REF_DIR)
	cd $(REF_DIR) && \
	curl -fSLO https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz && \
	gunzip -k Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz && \
	samtools faidx Homo_sapiens.GRCh38.dna.primary_assembly.fa && \
	minimap2 -x map-ont -d GRCh38.ont.mmi Homo_sapiens.GRCh38.dna.primary_assembly.fa
	@echo "Index written to $(REF_DIR)/GRCh38.ont.mmi"

check:
	@python3 software/validate_register.py

clean:
	rm -rf $(REF_DIR)/*.gz
