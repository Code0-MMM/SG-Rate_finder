import json
import tempfile
import unittest
from pathlib import Path
from database import replace_data, load_s_events
from excel_parser import ParsedWorkbook
from publish_data import publish


class PublishTests(unittest.TestCase):
    def test_public_snapshot_excludes_source_file(self):
        with tempfile.TemporaryDirectory() as d:
            source, destination = Path(d) / 'sg_rate.db', Path(d) / 'published.json'
            parsed = ParsedWorkbook(
                general_rates=[dict(category='LTSC 一般点', payment_method='券扣4%', rate=.13, effective_date='2026-09-01')],
                s_events=[dict(brand_name='AMI', aging='240911', ref_no='AM3651CL13_3',
                               rates=[dict(rate=.29, effective_date='2026-09-25')])],
                brands=[dict(brand_name='CHANEL W&J', category='LF', payment_method='券扣4%', note='W&J 12%',
                             rates=[dict(rate=0, effective_date='2026-09-12')])])
            replace_data(parsed, 'internal-source.xlsx', source)
            self.assertEqual(load_s_events(source)[0]['aging'], '240911')
            publish(source, destination)
            content = destination.read_text(encoding='utf-8')
            self.assertNotIn('internal-source.xlsx', content)
            data = json.loads(content)
            self.assertEqual(data['brands'][0]['rates'][0]['rate'], 0)
            self.assertEqual(data['brands'][0]['note'], 'W&J 12%')
            self.assertEqual(data['s_events'][0]['ref_no'], 'AM3651CL13_3')
            self.assertEqual(data['s_events'][0]['rates'][0]['rate'], .29)
