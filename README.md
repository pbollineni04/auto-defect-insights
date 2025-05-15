# Auto Defect Insights

## Tech Stack  
- Python (requests, pandas, BeautifulSoup)  
- SQL (PostgreSQL on AWS RDS)  
- Jupyter Notebooks  
- Excel (for visualization and dashboards)  
- Mermaid, draw.io (for diagrams)  
- Git & GitHub  

## Project Objective  
This project helps automotive manufacturers and suppliers identify which vehicle models and components drive the most recalls and consumer complaints. By connecting real-world defect data from the **NHTSA API** and **CarComplaints.com**, I surface insights to help QA and operations teams prioritize fixes that will reduce risk, warranty costs, and customer dissatisfaction.

## Job Description  
This project was built in alignment with the **Data Analyst Intern** role at **Sanmina Corporation**, a leading electronics manufacturing services (EMS) provider. The role emphasizes data extraction, cleaning, KPI analysis, dashboard development, and support for operational decisions across sectors like automotive and clean tech.

Sanmina’s focus on product quality and cross-functional analytics aligns perfectly with this project, which builds end-to-end pipelines to extract, analyze, and visualize defect trends for automotive programs.

[📄 Job_Description.pdf](proposal/Job_Description.pdf)

## Data  

**Sources:**  
- [NHTSA Recalls API](https://api.nhtsa.gov/recalls/recallsByVehicle)  
- [CarComplaints.com](https://www.carcomplaints.com/)

**Key Characteristics:**  
- **NHTSA API**: JSON, 2000–2025 recall data by make, model, year, component  
- **CarComplaints.com**: HTML-scraped complaint counts by vehicle model

## Notebooks / Python Scripts  

- [`NHTSA_API_SQL_Analysis.ipynb`](notebooks/NHTSA_API_SQL_Analysis.ipynb)  
  Performs descriptive and diagnostic analysis of government recall data using SQL CTEs, window functions, and joins.

- [`CarComplaints_Web_Scrape_SQL_Analysis.ipynb`](notebooks/CarComplaints_Web_Scrape_SQL_Analysis.ipynb)  
  Analyzes consumer complaint volume by model, identifying which cars generate the most dissatisfaction.

- [`export_to_csv.py`](reports/export_to_csv.py)  
  Exports cleaned SQL query results to CSV for visualization in Excel.

## Future Improvements  

- Automate the full pipeline using **dbt** or **Airflow**, with scheduled refreshes and version-controlled SQL models.  
- Integrate **Looker Studio** or **Power BI** for real-time dashboards instead of static Excel charts.

