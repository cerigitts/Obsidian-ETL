# Obsidian ETL

A self-driven project to design and build an end-to-end ETL (Extract, Transform, Load) pipeline as part of a data engineering portfolio.  
This project is not based on a tutorial — it is structured, versioned, and documented from scratch to reinforce core concepts and demonstrate practical implementation.

# Project Goals

- Build a modular, professional-grade ETL system
- Ingest structured datasets from external sources
- Apply metadata-driven transformations
- Write outputs to a clean data model
- Practice CI/CD, version control, and scalable structure

# Project Structure

```
obsidian-etl/
├── data/           # Raw and processed data
├── metadata/       # Schemas, field maps, pipeline configs
├── notebooks/      # Jupyter notebooks for exploration
├── src/            # Source code: loaders, transformers, pipeline logic
├── tests/          # Unit tests
├── README.md       # Project documentation
└── .gitignore      # Git exclusions
```

# Tools and Stack

- Python 3.x
- Pandas
- PyYAML
- Streamlit (for UI layer later)
- GitHub + GitHub Actions (CI)
- AWS S3 / EC2 (planned)

## Status

Setup complete. Data flow and logic implementation begins next.
