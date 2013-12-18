# -*- coding: utf-8 -*-
"""
    Tappy Terror Tests
    ------------------

    Tests Tappy Terror

    :license: MIT; details in LICENSE
"""

import tappy
import unittest
import json

class TappyTerrorWebTestCase(unittest.TestCase):
    def setUp(self):
        tappy.app.config['TESTING'] = True
        self.app = tappy.app.test_client()
        
    def test_index_renders(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_draw_board_image(self):
        dummy_game_board = {}
        for name in tappy.floor_list.keys():
            dummy_game_board[name] = tappy.Location(
                name,
                tappy.floor_list[name]
            )
        # TODO currently this writes to:
        # tappy.app.static/boards/tappymap-yyyy-mm-dd-HH-MM-SS.png
        # and really that should be mocked out or something to avoid the
        # file write while testing
        tappy.draw_board_image(dummy_game_board, tappy.floor_list)

    def test_location_push(self):
        no_data = self.app.post('/amd/push')
        self.assertEqual(no_data.status_code, 400)

        malformed_data = self.app.post(
            '/amd/push',
            data='{"a":',
            content_type='application/json'
        )
        self.assertEqual(no_data.status_code, 400)

        wrong_content_type = self.app.post(
            '/amd/push',
            data=json.dumps({'a': 'b'})
        )
        self.assertEqual(wrong_content_type.status_code, 200)
        decoded = json.loads(wrong_content_type.data)
        self.assertEqual(u'failure', decoded['status'])

        wrong_json_format = self.app.post(
            '/amd/push',
            data=json.dumps({'a': 'b'}),
            content_type='application/json'
        )
        self.assertEqual(wrong_json_format.status_code, 200)
        decoded = json.loads(wrong_json_format.data)
        self.assertEqual(u'failure', decoded['status'])

        well_formed = self.app.post(
            '/amd/push',
            data=json.dumps([{'user':'user1', 'x': 1, 'y': 2, 'z': 3}]),
            content_type='application/json'
        )
        self.assertEqual(well_formed.status_code, 200)
        decoded = json.loads(well_formed.data)
        self.assertEqual(u'ok', decoded['status'])

class TappyTerrorGameTestCase(unittest.TestCase):
    def test_start_game(self):
        game = tappy.TappyTerrorGame()
        game.tick()

    def test_snapshot(self):
        mem_db = tappy.connect_memory_db()
        tappy.create_game_db(mem_db)
        
        empty_game = tappy.TappyTerrorGame()
        empty_game.snapshot_to_db(mem_db)
        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertIsInstance(roundtrip, tappy.TappyTerrorGame)

        self.assertEqual(empty_game.game_board.keys(), roundtrip.game_board.keys())
        self.assertDictEqual(empty_game.game_board, roundtrip.game_board)
        self.assertDictEqual(empty_game.active_players, roundtrip.active_players)
        self.assertDictEqual(empty_game.team_points, roundtrip.team_points)

        full_game = tappy.TappyTerrorGame()
        full_game.tick()
        self.assertNotEqual(empty_game, full_game)
        full_game.snapshot_to_db(mem_db)
        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertDictEqual(full_game.game_board, roundtrip.game_board)
        self.assertDictEqual(full_game.active_players, roundtrip.active_players)
        self.assertDictEqual(full_game.team_points, roundtrip.team_points)


class LocationTestCase(unittest.TestCase):
    def test_mob_spawn(self):
        loc = tappy.Location(
            'name',
            tappy.Polygon('rect', [(0,0), (1,1)]),
            'some team',
            0
        )
        loc.spawn_mob()
        self.assertTrue(loc.has_mobs())
        self.assertGreater(loc.mob_count, 0)

        # Spawning more than max mobs should only ever result in max mobs
        loc.spawn_mob(tappy.max_mobs_in_loc + 1)
        self.assertTrue(loc.has_mobs())
        self.assertEqual(loc.mob_count, tappy.max_mobs_in_loc)

    def test_remove_mob(self):
        loc = tappy.Location(
            'name',
            tappy.Polygon('rect', [(0,0), (1,1)]),
            'some team',
            tappy.max_mobs_in_loc
        )
        self.assertTrue(loc.has_mobs())
        loc.remove_mob(1)
        self.assertEquals(loc.mob_count, tappy.max_mobs_in_loc - 1)
        # mob count should never be negative
        loc.remove_mob(tappy.max_mobs_in_loc)
        self.assertEquals(loc.mob_count, 0)

    def test_location_equals(self):
        lhs_rect = tappy.Location(
            'name',
            tappy.Polygon('rect', [(0,0), (1,1)]),
            'some team',
            tappy.max_mobs_in_loc
        )
        self.assertEquals(lhs_rect, lhs_rect)

        rhs_rect = tappy.Location(
            'name',
            tappy.Polygon('rect', [(0,0), (1,1)]),
            'some team',
            tappy.max_mobs_in_loc
        )
        self.assertEquals(lhs_rect, rhs_rect)
        self.assertEquals(rhs_rect, lhs_rect)

        poly = tappy.Location(
            'name',
            tappy.Polygon('poly', [(0,0), (1, 0), (0, 1)]),
            'some team',
            tappy.max_mobs_in_loc
        )
        self.assertEquals(poly, poly)
        self.assertNotEqual(lhs_rect, poly)
        self.assertNotEqual(rhs_rect, poly)
        self.assertNotEqual(poly, lhs_rect)
        self.assertNotEqual(poly, rhs_rect)
        
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
