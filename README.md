# Texas Food Insecurity Dashboard

An interactive analytics dashboard that combines publicly available economic indicators into a Food Risk Score for every county in Texas.

![SQL](https://img.shields.io/badge/SQL-MySQL-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

> **Dashboard Screenshot**
>
> ![Texas Food Insecurity Dashboard](assests/dashboard.pgn)

---

## Project Highlights

- Built an end-to-end analytics pipeline using SQL, Python, MySQL, and Streamlit.
- Developed a composite Food Risk Score to compare all 254 Texas counties.
- Designed an interactive dashboard with county filtering, visualizations, and drill-down analysis.
- Implemented an AI Analytics Assistant that answers questions using the project's verified dataset.


# Project Overview

Food insecurity is influenced by multiple economic factors, including poverty, household income, unemployment, and participation in the Supplemental Nutrition Assistance Program (SNAP). Looking at only one of these measures makes it difficult to compare overall levels of need across communities.

This project addresses that challenge by combining these indicators into a single Food Risk Score for every county in Texas. Publicly available county-level data from Data Commons is stored in a MySQL database, analyzed using SQL and Python, and presented through an interactive Streamlit dashboard.

The dashboard allows users to compare counties, explore county-level economic indicators, visualize food insecurity trends, and ask questions through an AI Analytics Assistant that responds using the project's verified dataset.

### This project explores the following areas

- Food Risk Score
- County-level economic indicators
- County comparisons
- AI Analytics Assistant

### Project Resources

- SQL scripts for data cleaning and preparation *(link)*
- SQL scripts for analytical queries *(link)*
- Interactive Streamlit dashboard *(link)*

---

# Project Structure & Data Overview

This project follows an end-to-end analytics workflow that transforms publicly available county-level economic data into an interactive dashboard for exploring food insecurity across Texas.

### Analytics Workflow

```
Data Commons
      │
      ▼
MySQL Database
      │
      ▼
SQL & Python Data Processing
      │
      ▼
Food Risk Score Calculation
      │
      ▼
Streamlit Dashboard
      │
      ▼
AI Analytics Assistant
```

### Database Structure

The project database is organized into three analytical tables that separate county information, economic indicators, and calculated food risk metrics. This structure keeps the source data separate from derived metrics while supporting dashboard visualizations and analytical queries.

> **Entity Relationship Diagram**
>
> *(Insert ERD here.)*

### Data Model

#### counties

Stores the unique identifier and name for each Texas county. This table serves as the reference table used throughout the project and links county information across the database.

#### county_metrics

Stores the county-level economic indicators used throughout the analysis, including:

- Household median income
- Poverty count
- SNAP participation
- Unemployment rate
- Population

#### county_scores

Stores the calculated metrics generated during the analytical process, including:

- Poverty rate
- Food Risk Score
- Risk Quartile
- Risk Level

These metrics power the dashboard visualizations, county rankings, and AI Analytics Assistant.

---

# Executive Summary

## Overview of Findings

This analysis combines four county-level economic indicators into a single Food Risk Score that supports comparisons across all 254 Texas counties.

Three key findings emerged from the analysis:

- **Finding 1** *(Replace with final insight and statistics.)*

- **Finding 2** *(Replace with final insight and statistics.)*

- **Finding 3** *(Replace with final insight and statistics.)*

The Streamlit dashboard allows users to explore these findings through interactive visualizations, county comparisons, and an AI Analytics Assistant that answers questions using the project's verified dataset.

> **Dashboard Overview**
>
> *(Insert dashboard overview screenshot here.)*