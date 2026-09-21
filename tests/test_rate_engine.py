import tempfile
import unittest
from datetime import date
from pathlib import Path
from database import replace_data, load_data
from excel_parser import ParsedWorkbook
from rate_engine import current_rate, general_for_category, format_rate


class RateTests(unittest.TestCase):
    def test_dates_and_zero(self):
        rates = [{'rate': .12, 'effective_date':'2026-09-12'}, {'rate': 0, 'effective_date':'2026-09-20'},
                 {'rate': .25, 'effective_date':'2026-09-25'}]
        self.assertEqual(current_rate(rates, date(2026,9,21))['rate'], 0)
        self.assertEqual(current_rate(rates, date(2026,9,26))['rate'], .25)
        self.assertEqual(format_rate(0), '0%')

    def test_transaction_preserves_data(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'rates.db'
            p = ParsedWorkbook(general_rates=[dict(category='LTSC 一般点', payment_method='券扣4%', rate=.13, effective_date='2026-09-01')],
                               brands=[dict(brand_name='BURBERRY', category='LF', payment_method='券扣4%', note='', rates=[dict(rate=.33,effective_date='2026-09-12')])])
            replace_data(p, 'ok.xlsx', path)
            p.brands[0]['rates'][0]['rate'] = 'bad'
            with self.assertRaises(Exception):
                replace_data(p, 'bad.xlsx', path)
            brands, general, _ = load_data(path)
            self.assertEqual(brands[0]['rates'][0]['rate'], .33)
            self.assertEqual(general_for_category(general, 'LTSC', date(2026,9,21))['rate'], .13)
