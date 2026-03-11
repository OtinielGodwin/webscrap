# Webscrapping

This repository contains a Python project for scraping and analysing football data.

## Structure

- `app/` contains Streamlit pages and the main application.
- `scraper/`, `parser/`, `processing/` implement data collection and cleaning.
- `data/` holds raw and processed CSV files and images.
- `config/` stores helper functions for club and league logos.

## Usage

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

## Git

This project uses a `.gitignore` that excludes virtual environments, data files and common build artifacts.


