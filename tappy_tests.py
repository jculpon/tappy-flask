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

class PolygonTestCase(unittest.TestCase):
    # Incredibly lame tests for now because we basically did no validation
    # or any sanity checking on the polygon class originally, so there's no
    # real behavior to test with it.
    def test_rect(self):
        r = tappy.Polygon('rect', [(0, 0), (3, 4)])

    def test_poly(self):
        p = tappy.Polygon('poly',
            [(0,736), (352,736),(352,990),(85,990),(85,825),(0,825)]
        )

if __name__ == '__main__':
    unittest.main()
