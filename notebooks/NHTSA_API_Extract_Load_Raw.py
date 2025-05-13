''' #!/usr/bin/env python3
import requests
import pandas as pd
import time
import sys

# ─── Configuration ─────────────────────────────────────────────────────────────
INPUT_CSV     = 'all_makes_complaints_20250513.csv'
OUTPUT_CSV    = 'nhtsa_recalls_by_vehicle_2000_2025.csv'
API_ENDPOINT  = 'https://api.nhtsa.gov/recalls/recallsByVehicle'
SLEEP_SECONDS = 0.2
YEARS         = range(2000, 2026)

# ─── Helper ────────────────────────────────────────────────────────────────────
def get_recalls(make: str, model: str, year: int) -> list:
    """Return list of recall dicts for given make/model/modelYear."""
    try:
        resp = requests.get(API_ENDPOINT,
                            params={'make': make.lower(),
                                    'model': model.lower(),
                                    'modelYear': year},
                            timeout=10)
        resp.raise_for_status()
        return resp.json().get('results', [])
    except:
        return []  # swallow all errors

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. load CSV
    try:
        df = pd.read_csv(INPUT_CSV, dtype=str)
    except FileNotFoundError:
        print(f"Input file not found: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    # 2. extract unique make/model pairs
    if 'Make' not in df.columns or 'Model' not in df.columns:
        print("CSV needs 'Make' and 'Model' columns.", file=sys.stderr)
        sys.exit(1)
    df = df[['Make','Model']].dropna().copy()
    df['Make']  = df['Make'].str.strip()
    df['Model'] = df['Model'].str.strip()
    df = df.drop_duplicates().reset_index(drop=True)

    total = len(df)
    print(f"→ {total} unique make/model pairs, scanning years {YEARS.start}–{YEARS.stop-1}")

    all_records = []
    summary = []

    # 3. for each make/model, collect across all years
    for idx, row in df.iterrows():
        make, model = row['Make'], row['Model']
        model_recs = []
        for year in YEARS:
            recs = get_recalls(make, model, year)
            for r in recs:
                r.update({'Make': make, 'Model': model, 'Year': year})
            model_recs.extend(recs)
            all_records.extend(recs)
            time.sleep(SLEEP_SECONDS)

        # one summary line per model
        count = len(model_recs)
        print(f"[{idx+1}/{total}] {make} {model} → {count} recalls (2000–2025)")
        summary.append({'Make': make, 'Model': model, 'RecallCount': count})

    # 4. write full-detail CSV
    if all_records:
        pd.DataFrame(all_records).to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ Detailed recalls written to {OUTPUT_CSV}")
    else:
        print("\nℹ️ No individual recall records found.")

    # 5. write summary CSV
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv('nhtsa_recall_summary.csv', index=False)
    print(f"✅ Summary counts written to nhtsa_recall_summary.csv")

if __name__ == '__main__':
    main()
'''

#!/usr/bin/env python3
import requests
import pandas as pd
import time
import sys

# ─── Configuration ─────────────────────────────────────────────────────────────
INPUT_CSV        = 'all_makes_complaints_20250513.csv'
DETAIL_OUTPUT    = 'nhtsa_recalls_by_toyota_detail.csv'
SUMMARY_OUTPUT   = 'nhtsa_toyota_recall_summary.csv'
API_ENDPOINT     = 'https://api.nhtsa.gov/recalls/recallsByVehicle'
SLEEP_SECONDS    = 0.2
YEARS            = range(2000, 2026)
MAKE_FILTER      = 'toyota'

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
    # 1. Load CSV
    try:
        df = pd.read_csv(INPUT_CSV, dtype=str)
    except FileNotFoundError:
        print(f"Input file not found: {INPUT_CSV}", file=sys.stderr)
        sys.exit(1)

    # 2. Filter to Toyota only
    if 'Make' not in df.columns or 'Model' not in df.columns:
        print("CSV needs 'Make' and 'Model' columns.", file=sys.stderr)
        sys.exit(1)
    toyota_df = df[df['Make'].str.strip().str.lower() == MAKE_FILTER].copy()
    if toyota_df.empty:
        print("❗ No Toyota rows found in your CSV.", file=sys.stderr)
        sys.exit(1)

    # 3. Unique Toyota models
    toyota_df['Model'] = toyota_df['Model'].str.strip()
    models = toyota_df['Model'].dropna().drop_duplicates().tolist()
    total_models = len(models)
    print(f"→ Found {total_models} unique Toyota models; scanning {len(YEARS)} years each.")

    # 4. Loop per model × years
    detail_records = []
    summary_records = []
    call_num = 0
    total_calls = total_models * len(YEARS)

    for i, model in enumerate(models, start=1):
        model_recs = []
        for year in YEARS:
            call_num += 1
            recs = get_recalls(MAKE_FILTER, model, year)
            print(f"[{call_num}/{total_calls}] Toyota {model} {year} → {len(recs)} recalls")
            for r in recs:
                r.update({'Make': 'Toyota', 'Model': model, 'Year': year})
            detail_records.extend(recs)
            model_recs.extend(recs)
            time.sleep(SLEEP_SECONDS)

        summary_records.append({
            'Make': 'Toyota',
            'Model': model,
            'RecallCount_2000_2025': len(model_recs)
        })
        print(f"  ↳ Total for Toyota {model}: {len(model_recs)} recalls")

    # 5. Write out detail CSV
    if detail_records:
        pd.DataFrame(detail_records).to_csv(DETAIL_OUTPUT, index=False)
        print(f"\n✅ Detailed recalls written to {DETAIL_OUTPUT}")
    else:
        print("\nℹ️ No recall details found for any Toyota model.")

    # 6. Write out summary CSV
    pd.DataFrame(summary_records).to_csv(SUMMARY_OUTPUT, index=False)
    print(f"✅ Summary counts written to {SUMMARY_OUTPUT}")

if __name__ == '__main__':
    main()
