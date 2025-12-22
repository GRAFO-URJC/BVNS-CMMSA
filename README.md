# Title of the Paper Here <a href="https://doi.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/1/11/DOI_logo.svg" alt="DOI" width="20"/></a> <a href="https://doi.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/e/e8/Zenodo-gradient-square.svg" alt="Zenodo" width="60"/></a>

<!-- Load Material Symbols Outlined for icons -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&icon_names=mail" />

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code](https://img.shields.io/badge/Code-Java-orange.svg)]()
[![Framework](https://img.shields.io/badge/Powered_by-MORK-green.svg)](https://mork-optimization.com/)


## Abstract

Paper under review. To be added upon acceptance.

## Authors

- First Author <sup>1,*</sup> <a href="mailto:first.author@urjc.es" aria-label="First Author Email"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Email_Shiny_Icon.svg" alt="email" width="20" style="vertical-align:middle;"/></a> <a href="https://orcid.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/ORCID_iD.svg" alt="ORCID" width="20" style="vertical-align:middle;"/></a>
- Second Author <sup>2</sup> <a href="mailto:second.author@institution.edu" aria-label="Second Author Email"><img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Email_Shiny_Icon.svg" alt="email" width="20" style="vertical-align:middle;"/></a> <a href="https://orcid.org/"><img src="https://upload.wikimedia.org/wikipedia/commons/0/06/ORCID_iD.svg" alt="ORCID" width="20" style="vertical-align:middle;"/></a>

### Affiliations

1. Departamento de Informática y Estadística, Universidad Rey Juan Carlos — C. Tulipán, s/n, Móstoles, 28933, Madrid, Spain
2. Department Name, Institution Name — Address, City, Postal Code, Country

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
- [Contact](#contact)
- [Powered by MORK](#powered-by-mork-metaheuristic-optimization-framework)

---

## Repository Structure

```
.
├── instances/          # Problem instances
├── results/           # Experimental results
├── src/               # Source code
├── target/            # Compiled artifacts
├── analysis/          # Analysis scripts
├── LICENSE            # License file
├── README.md          # This file
└── pom.xml            # Maven configuration
```

---



## Datasets

Instances are categorized in different datasets inside the `instances` folder.

### Instance Format

Each instance is encoded as a plain text file representing a graph:
- The first line contains the number of vertices `n` and edges `m`.
- Each subsequent line contains a pair of integers `u v` representing an edge between vertex `u` and vertex `v`.
- Vertices are indexed from 0 to n-1.

Example:
```
10 15
0 1
0 2
1 3
...
```

### Dataset Statistics

| Dataset | Instances | Vertices Range | Edges Range | Description |
|---------|-----------|----------------|-------------|-------------|
| Small   | 10        | 10-50          | 15-100      | Small test instances |
| Medium  | 20        | 50-200         | 100-500     | Medium-sized instances |
| Large   | 15        | 200-1000       | 500-5000    | Large benchmark instances |

## Code Execution

### Building the Project

```bash
mvn clean package
```

### Running Experiments

Execution of the program can be done via the command line.

**Example 1:** Execute default experiment with the default set of instances
```bash
java -jar target/code.jar 
```

**Example 2:** Execute using a different set of instances located inside the `newinstances` folder
```bash
java -jar target/code.jar --instances.path.default=newinstances
```

**Example 3:** Execute with custom parameters
```bash
java -jar target/code.jar --instances.path.default=newinstances --algorithm.maxIterations=1000 --seed=42
```

### Configuration Options

Available command-line parameters:
- `--instances.path.default`: Path to instances folder (default: `instances`)
- `--algorithm.maxIterations`: Maximum number of iterations (default: `1000`)
- `--algorithm.populationSize`: Population size for metaheuristics (default: `100`)
- `--seed`: Random seed for reproducibility (default: `0`)
- `--output.path`: Output directory for results (default: `results`)

## Requirements

- Java 11 or higher
- Maven 3.6+ (for building from source)
- Minimum 4GB RAM recommended for large instances

### Dependencies

All dependencies are managed through Maven and will be automatically downloaded during the build process. Main dependencies include:
- MORK Framework (latest version)
- Apache Commons Math3
- JUnit 5 (for testing)

## Results

Experimental results are stored in the `results` folder after execution. Each result file includes:
- Instance name
- Best solution found
- Solution quality metrics
- Execution time
- Algorithm parameters used

Results can be analyzed using the provided visualization scripts in the `analysis` folder.

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
@article{citeKey2024,
  title={Title of the Paper Here},
  author={Surname, First Name and Surname2, Second Name},
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

Surname, F. N., & Surname2, S. N. (20XX). Title of the paper here. *Journal Name*, *XX*(X), XXX-XXX. https://doi.org/XXXXXXX

### IEEE Format

F. N. Surname and S. N. Surname2, "Title of the paper here," *Journal Name*, vol. XX, no. X, pp. XXX-XXX, 20XX, doi: XXXXXXX.

## Acknowledgments

We would like to thank:
- The reviewers for their valuable feedback and suggestions
- [Name/Organization] for providing computational resources
- The MORK development team for their excellent framework
- Contributors who helped improve this work

## Contact

For questions, issues, or collaborations, please contact:

- **First Author**: [first.author@urjc.es](mailto:first.author@urjc.es)
- **Project Issues**: [GitHub Issues](https://github.com/username/repository/issues)
- **Project Website**: [https://project-website.com](https://project-website.com)

## Powered by MORK (Metaheuristic Optimization framewoRK)

| ![Mork logo](https://user-images.githubusercontent.com/55482385/233611563-4f5c91f2-af36-4437-a4b5-572b6655487a.svg) | MORK is a Java framework for easily solving hard optimization problems. You can [create a project](https://generator.mork-optimization.com/) and try the framework in under one minute. See the [documentation](https://docs.mork-optimization.com/en/latest/) or the [source code](https://github.com/mork-optimization/mork). |
|:--:|--|

---
