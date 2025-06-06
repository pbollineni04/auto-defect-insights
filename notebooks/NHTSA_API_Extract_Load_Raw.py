#!/usr/bin/env python3
import requests
import pandas as pd
import time
import sys
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging

# ─── Configuration ─────────────────────────────────────────────────────────────
INPUT_CSV        = 'all_makes_complaints_20250513.csv'
API_ENDPOINT     = 'https://api.nhtsa.gov/recalls/recallsByVehicle'
SLEEP_SECONDS    = 0.2
YEARS            = range(2000, 2026)
MAKE_FILTER      = 'toyota'

# Predefined Toyota models
TOYOTA_MODELS = [
    '4Runner', '86', 'Aurion', 'Auris', 'Avalon', 'Avalon Hybrid', 'Avanza', 
    'Avensis', 'bZ4X', 'C-HR', 'Camry', 'Camry Hybrid', 'Carib', 'Carina',
    'Cavalier', 'Celica', 'Corolla', 'Corolla Cross', 'Corolla Cross Hybrid',
    'Corolla Hatchback', 'Corolla Hybrid', 'Corolla Verso', 'Cressida', 'Crown',
    'Dyna', 'Echo', 'Etios', 'Etios Liva', 'FJ Cruiser', 'FJ40', 'Fortuner',
    'GR Corolla', 'GR Supra', 'GR86', 'Grand Highlander', 'Grand Highlander Hybrid',
    'Harrier', 'Hiace', 'Highlander', 'Highlander Hybrid', 'Hilux', 'Innova',
    'iQ2', 'King Cab', 'Land Cruiser', 'Mark X', 'Matrix', 'Mirai', 'MR2',
    'Paseo', 'Pickup', 'Prado', 'Premio', 'Previa', 'Prius', 'Prius c',
    'Prius Plug-in', 'Prius Prime', 'Prius v', 'Raum', 'RAV4', 'RAV4 EV',
    'RAV4 Hybrid', 'RAV4 Prime', 'Scion', 'Se', 'Sequoia', 'Sienna',
    'Sienna Hybrid', 'Solara', 'Sprinter', 'Supra', 'T100', 'Tacoma',
    'Tarago', 'Tercel', 'Tundra', 'Tundra Hybrid', 'Van', 'Venza', 'Verso',
    'Vitz', 'Windom', 'Yaris', 'Yaris Hatchback', 'Yaris Verso'
]

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load database configuration
load_dotenv()
PG_USER = os.environ['PG_USER']
PG_PASSWORD = os.environ['PG_PASSWORD']
PG_HOST = os.environ['PG_HOST']
PG_DB = os.environ['PG_DB']

# ─── Helper ────────────────────────────────────────────────────────────────────
def get_recalls(make: str, model: str, year: int) -> list:
    """Return list of recall dicts for given make/model/year; errors → empty."""
    try:
        resp = requests.get(
            API_ENDPOINT,
            params={'make': make.lower(), 'model': model.lower(), 'modelYear': year},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get('results', [])
    except:
        return []

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Create PostgreSQL connection
    pg_conn_str = f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DB}'
    pg_engine = create_engine(pg_conn_str)

    # Use predefined models list
    models = TOYOTA_MODELS
    total_models = len(models)
    logger.info(f"→ Scanning {total_models} Toyota models across {len(YEARS)} years each")

    # Loop per model × years
    detail_records = []
    summary_records = []
    call_num = 0
    total_calls = total_models * len(YEARS)

    for i, model in enumerate(models, start=1):
        model_recs = []
        for year in YEARS:
            call_num += 1
            recs = get_recalls(MAKE_FILTER, model, year)
            logger.info(f"[{call_num}/{total_calls}] Toyota {model} {year} → {len(recs)} recalls")
            for r in recs:
                r.update({'Make': 'Toyota', 'Model': model, 'Year': year})
            detail_records.extend(recs)
            model_recs.extend(recs)
            time.sleep(SLEEP_SECONDS)

        summary_records.append({
            'Make': 'Toyota',
            'Model': model,
            'Recalls': len(model_recs)
        })
        logger.info(f"  ↳ Total for Toyota {model}: {len(model_recs)} recalls")

    # 5. Write detail records to database
    if detail_records:
        detail_df = pd.DataFrame(detail_records)
        try:
            detail_df.to_sql(
                'nhtsa_recalls_detail',
                pg_engine,
                schema='sql_project',
                if_exists='append',
                index=False
            )
            logger.info("Detailed recalls written to database")
        except Exception as e:
            logger.error(f"Error writing detail records to database: {e}")
            # Fallback to CSV if database write fails
            detail_df.to_csv('nhtsa_recalls_by_toyota_detail_backup.csv', index=False)
            logger.info("Backup detail data saved to CSV")

    # 6. Write summary records to database
    summary_df = pd.DataFrame(summary_records)
    try:
        summary_df.to_sql(
            'nhtsa_recalls_summary',
            pg_engine,
            schema='sql_project',
            if_exists='append',
            index=False
        )
        logger.info("Summary records written to database")
    except Exception as e:
        logger.error(f"Error writing summary records to database: {e}")
        # Fallback to CSV if database write fails
        summary_df.to_csv('nhtsa_toyota_recall_summary_backup.csv', index=False)
        logger.info("Backup summary data saved to CSV")

if __name__ == '__main__':
    main()
