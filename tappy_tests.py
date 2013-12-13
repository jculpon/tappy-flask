# -*- coding: utf-8 -*-
"""
    Tappy Terror Tests
    ------------------

    Tests Tappy Terror

    :license: MIT; details in LICENSE
"""

import tappy
import unittest

class TappyTerrorTestCase(unittest.TestCase):
    def setUp(self):
        tappy.app.config['TESTING'] = True
        self.app = tappy.app.test_client()
        
    def test_index_renders(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

if __name__ == '__main__':
    unittest.main()
