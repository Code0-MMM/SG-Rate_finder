import re
import unicodedata


def normalize(value):
    return ' '.join(unicodedata.normalize('NFKC', str(value)).upper().split())


def search(brands, query, limit=20):
    q = normalize(query)
    if not q:
        return []
    found = []
    for brand in brands:
        name = normalize(brand['brand_name'])
        if q not in name:
            continue
        rank = 0 if name == q else 1 if name.startswith(q) else 2 if re.search(r'(?<!\w)' + re.escape(q), name) else 3
        found.append((rank, name, brand['id'], brand))
    return [x[3] for x in sorted(found)[:limit]]
