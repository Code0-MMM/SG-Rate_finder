import unittest
from search_engine import search, normalize


class SearchTests(unittest.TestCase):
    def test_search(self):
        brands = [{'id':1,'brand_name':'BOTTEGA VENETA'}, {'id':2,'brand_name':'BURBERRY'}, {'id':3,'brand_name':'버버리'}]
        for q in ('bur','BUR','Bur'):
            self.assertEqual(search(brands,q)[0]['brand_name'], 'BURBERRY')
        self.assertEqual(search(brands,'VENETA')[0]['brand_name'], 'BOTTEGA VENETA')
        self.assertEqual(normalize('  Burberry  '), 'BURBERRY')
