# igv-session-generator

Python scripts to generate [IGV](https://igv.org/) session XML files for visualizing phased genomic data (DNA methylation and haplotype blocks) served from a local HTTP server.

## Scripts

### `single-individual.py`

Generates an IGV session for **one individual**, including:

- Paternal and maternal DNA methylation tracks (bigWig)
- Paternal and maternal haplotype map block tracks (BED)
- Haplotagged BAM alignment track (with base modification coloring, grouped by phase)
- Reference sequence and RefSeq Select gene annotations

```bash
python single-individual.py <individual_id> <locus>
```

**Example:**

```bash
python single-individual.py 200081 chr14:100826000-100827000
```

### `multiple-individuals.py`

Generates an IGV session for **multiple individuals** (without BAM tracks), including:

- Paternal and maternal DNA methylation tracks for each sample
- Paternal and maternal haplotype block tracks for each sample
- Reference sequence track

```bash
python multiple-individuals.py --samples <id1,id2,...> --locus <locus> [--out <filename>]
```

**Example:**

```bash
python multiple-individuals.py --samples 200081,200082,200084,200085,200086,200087,200101,200102,200103,200104,200105,200106,NA12877,NA12878,NA12879,NA12881,NA12882,NA12883,NA12884,NA12885,NA12886,NA12887 --locus chr14:100826000-100827000 
```

## Output

Session XML files are written to the `igv-sessions/` directory. Open them in IGV via **File > Open Session**.

## Data expectations

The scripts assume genomic data files are served at `http://localhost:8080` with this structure:

```
founder-phased/
  {id}.dna-methylation.founder-phased.mat.count.hg38.bw
  {id}.dna-methylation.founder-phased.pat.count.hg38.bw
  {id}.hap-map-blocks.paternal.sorted.bed.gz (+.tbi)
  {id}.hap-map-blocks.maternal.sorted.bed.gz (+.tbi)
read-backed-phased/
  {id}.GRCh38.haplotagged.bam (+.bai)
```