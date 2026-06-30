# HENGYUN Grant Intelligence Monitor

This repository contains a Python-based internal grant and public funding intelligence monitor for HENGYUN Technology.

## Scope

The monitor tracks public funding opportunities relevant to:
- Taiwan startup grants and R&D subsidies
- Taipei City startup and R&D programs
- Taiwan national R&D and startup programs
- Energy, net-zero, and climate technology grants
- Smart city, testbed, and demonstration programs
- Japan GX, NEDO, and decarbonization programs
- Singapore urban climate and testbed programs

This system is for internal intelligence only and must not generate unsupported technical, ESG, carbon-credit, SBTi, or emissions-reduction claims.

## Structure

- src/main.py: daily collection entry point
- src/fetch_sources.py: source fetching and normalization
- src/classify.py: classification and scoring
- src/report.py: daily report generation
- src/weekly_report.py: weekly summary generation
- data/: raw and classified output
- reports/: generated Markdown and NotebookLM text reports

## Usage

Run the scripts locally with:

```bash
python3 -m py_compile src/*.py
python3 src/main.py
python3 src/weekly_report.py
```
