# Exact and heuristic methods for the Min-Max Sitting Arrangement Problem in the Cycle <a href="https://doi.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/1/11/DOI_logo.svg" alt="DOI" width="20"/></a> <a href="https://doi.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/e/e8/Zenodo-gradient-square.svg" alt="Zenodo" width="60"/></a>

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=mail" />

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code](https://img.shields.io/badge/Code-Java-orange.svg)]()

## Abstract

We study the Cyclic Min-Max Sitting Arrangement (CMMSA) problem on signed graphs, which seeks to place vertices around a cycle so that the maximum number of conflicts experienced by any single vertex is minimized. A conflict occurs when a negatively connected vertex lies on a shortest path between a vertex and one of its positively connected neighbors. We show that CMMSA is NP-hard. We address this problem with two exact mathematical models designed for commercial solvers and with a tailored Basic Variable Neighborhood Search (BVNS) that combines a greedy constructive start, informed shaking strategies, fast objective evaluation, and a fairness-oriented tie-breaking rule. Our evaluation covers 1,208 instances including synthetic families, real social networks, and engineered graphs adapted from the Harwell-Boeing collection. Under standard time budgets, the proposed method outperforms commercial solvers and a state-of-the-art baseline adapted to this objective, delivering the best results in 266 of 269 benchmarks and reaching optimal or zero-conflict solutions in 153 cases. These findings establish CMMSA as a relevant min-max variant within cyclic graph layout problems and provide models and datasets that enable reproducible comparison and future research.

## Authors

- **Marcos Robles** <sup>1</sup> <a href="mailto:marcos.robles@urjc.es" aria-label="Email"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Email_Shiny_Icon.svg" alt="email" width="20" style="vertical-align:middle;"/></a> <a href="https://orcid.org/0000-0002-8376-6209"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/ORCID_iD.svg" alt="ORCID" width="20" style="vertical-align:middle;"/></a>
- **Sergio Cavero** <sup>1</sup> <a href="mailto:sergio.cavero@urjc.es" aria-label="Email"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Email_Shiny_Icon.svg" alt="email" width="20" style="vertical-align:middle;"/></a> <a href="https://orcid.org/0000-0002-5258-5915"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/ORCID_iD.svg" alt="ORCID" width="20" style="vertical-align:middle;"/></a>
- **Eduardo G. Pardo** <sup>1,*</sup> <a href="mailto:eduardo.pardo@urjc.es" aria-label="Email"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Email_Shiny_Icon.svg" alt="email" width="20" style="vertical-align:middle;"/></a> <a href="https://orcid.org/0000-0002-6247-5269"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/ORCID_iD.svg" alt="ORCID" width="20" style="vertical-align:middle;"/></a>

### Affiliations

1. Universidad Rey Juan Carlos — Calle Tulipán s/n, Móstoles, 28933, Madrid, Spain

<sup>*</sup>Corresponding author.

---

## Table of Contents

- [Repository Structure](#repository-structure)
- [Abstract](#abstract)
- [Authors](#authors)
- [Datasets](#datasets)
- [Code Execution](#code-execution)
- [Requirements](#requirements)
- [Results](#results)
- [License](#license)
- [Funding](#funding)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

---

## Repository Structure

```
.
├── instances/         # Problem instances
├── results/           # Experimental results
├── code/              # Compiled artifacts
├── LICENSE            # License file
└── README.md          # This file
```

---



## Datasets

The repository contains 269 instances used in the experimental evaluation, categorized in different datasets inside the `Instances` folder. These include synthetic families, real social networks, and engineered graphs adapted from the Harwell-Boeing collection organizied in subsets accorcing to their size: small (45), medium (90), big (90) and huge (44). 

### Instance Format

Each instance is encoded as a plain text file representing a graph:
- The first line contains the number of vertices `n` and edges `m`.
- Each subsequent line contains a triplet of integers `u v w` representing an edge between vertex `u` and vertex `v` with a weight `w`, that is either 1 or -1.
- Vertices are indexed from 1 to n.

Example:
```
vertices: 10 edges: 9
2 3 -1
4 9 -1
6 1 -1
6 2 1
6 8 -1
6 10 1
8 4 1
8 7 -1
10 5 -1
```

Note that the most recent instances have a slightly different header, for example:

```
# This is an adaptation of one of the original Harwell-Boeing instances
24 68
1 6 1
1 7 1
1 13 1
...
```
## Code Execution

### Running Experiments

Execution of the program can be done via the command line. The instances that will be used for the execution must be in a folder called "Instances" or a subfolder, and the path must be given by args.
**Example:** Execute default experiment for all the instances.
```bash
java -jar BVNS_CMMSA.jar experiment -i "../Instances/" -l "severe" -s
```

**Example:** Execute default experiment for the small instances only.
```bash
java -jar BVNS_CMMSA.jar experiment -i "../Instances/small/" -l "severe" -s
```
Note that the Instances folder is capitalized, this is important for the code to properly handle strings.
### Configuration Options

## Requirements

- Java 11 or higher
- Minimum 4GB RAM recommended for large instances

## Results

Experimental results are stored in a CSV file after execution. Each result file includes:
- Algorithm ID, which is the same for all rows in the given jar
- Filename
- CMinMax O.F.
- T. CPU (s)
- TimeToBest (s)
- CMinSA Objective Function
- Iterations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

**Alternative licenses:** If you require a different license for commercial or academic use, please contact the corresponding author.

## Funding

This research was supported by:

- **Grant Name/Number**: [Funding Agency Name] - Project Title (Grant #XXXXX)
- **Grant Name/Number**: [Second Funding Source] - Project Title (Grant #YYYYY)
- **Universidad Rey Juan Carlos** - Internal Research Funding Program

The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.

## Citation

If you use this work in your research, please cite our paper:

### DOI

<https://doi.org/XXXXXXX>

### Bibtex

```bibtex
@article{Robles2024,
  title={Exact and heuristic methods for the Min-Max Sitting Arrangement Problem in the Cycle},
  author={Robles, Marcos and Cavero, Sergio and Pardo, Eduardo G.},
  journal={Journal Name},
  volume={XX},
  number={X},
  pages={XXX--XXX},
  year={20XX},
  publisher={Publisher Name},
  doi={XXXXXXX}
}
```

### APA Format

Robles, M., Cavero, S., & Pardo, E. G. (20XX). Exact and heuristic methods for the Min-Max Sitting Arrangement Problem in the Cycle. Journal Name, XX(X), XXX-XXX. https://doi.org/XXXXXXX

### IEEE Format

M. Robles, S. Cavero, and E. G. Pardo, "Exact and heuristic methods for the Min-Max Sitting Arrangement Problem in the Cycle," Journal Name, vol. XX, no. X, pp. XXX-XXX, 20XX, doi: XXXXXXX.

## Acknowledgments

We would like to thank:
- The reviewers for their valuable feedback and suggestions
- GRAFO research group for providing computational resources
- Contributors who helped improve this work
