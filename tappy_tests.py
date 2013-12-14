# -*- coding: utf-8 -*-
"""
    Tappy Terror Tests
    ------------------

    Tests Tappy Terror

    :license: MIT; details in LICENSE
"""

import tappy
import unittest

class TappyTerrorWebTestCase(unittest.TestCase):
    def setUp(self):
        tappy.app.config['TESTING'] = True
        self.app = tappy.app.test_client()
        
    def test_index_renders(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

class LocationTestCase(unittest.TestCase):
    def test_mob_spawn(self):
        loc = tappy.Location('some team', 0)
        loc.spawn_mob()
        self.assertTrue(loc.has_mobs())
        self.assertGreater(loc.mob_count, 0)

        # Spawning more than max mobs should only ever result in max mobs
        loc.spawn_mob(tappy.max_mobs_in_loc + 1)
        self.assertTrue(loc.has_mobs())
        self.assertEqual(loc.mob_count, tappy.max_mobs_in_loc)

    def test_remove_mob(self):
        loc = tappy.Location('some team', tappy.max_mobs_in_loc)
        self.assertTrue(loc.has_mobs())
        loc.remove_mob(1)
        self.assertEquals(loc.mob_count, tappy.max_mobs_in_loc - 1)
        # mob count should never be negative
        loc.remove_mob(tappy.max_mobs_in_loc)
        self.assertEquals(loc.mob_count, 0)

if __name__ == '__main__':
    unittest.main()
