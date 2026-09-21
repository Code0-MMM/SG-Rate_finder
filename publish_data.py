"""Export a reviewable public snapshot from the local, validated SQLite DB.

No Excel file or administrator password is included. This script never uploads data.
"""
import argparse
import json
import os
from pathlib import Path
from config import DB_PATH, PUBLISHED_PATH
from database import load_data, load_s_events


def publish(source=DB_PATH, destination=PUBLISHED_PATH):
    source, destination = Path(source), Path(destination)
    if not source.is_file():
        raise FileNotFoundError(f"No imported database: {source}")
    brands, general_rates, meta = load_data(source)
    s_events = load_s_events(source)
    if not brands or not general_rates:
        raise ValueError("The imported database has no complete rate data")
    # Only fields required for public lookup are exported.
    public_brands = [dict(id=b['id'], brand_name=b['brand_name'], category=b['category'],
                          payment_method=b['payment_method'], note=b['note'],
                          rates=[dict(rate=r['rate'], effective_date=r['effective_date']) for r in b['rates']])
                     for b in brands]
    public_general = [dict(category=r['category'], payment_method=r['payment_method'],
                           rate=r['rate'], effective_date=r['effective_date']) for r in general_rates]
    public_s_events = [dict(brand_name=e['brand_name'], aging=e['aging'], ref_no=e['ref_no'],
                            rates=[dict(rate=r['rate'], effective_date=r['effective_date']) for r in e['rates']])
                       for e in s_events]
    payload = dict(brands=public_brands, general_rates=public_general, s_events=public_s_events,
                   meta={key: meta.get(key, '') for key in ('last_update', 'source_month', 'latest_effective_date')})
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix('.json.tmp')
    try:
        with open(temporary, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return len(public_brands), len(public_general)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=DB_PATH)
    parser.add_argument('--destination', type=Path, default=PUBLISHED_PATH)
    args = parser.parse_args()
    brand_count, general_count = publish(args.source, args.destination)
    print(f"Published snapshot: {brand_count} brands, {general_count} general rates -> {args.destination}")
