from datetime import date


def current_rate(rates, today=None):
    today = today or date.today()
    eligible = [r for r in rates if r.get('rate') is not None and date.fromisoformat(r['effective_date']) <= today]
    return max(eligible, key=lambda r: r['effective_date']) if eligible else None


def general_for_category(general_rates, category, today=None):
    exact = [r for r in general_rates if r['category'] == category or r['category'].replace(' 一般点', '').strip() == category]
    return current_rate(exact, today)


def format_rate(rate):
    return f"{rate * 100:g}%"
