# -*- coding: utf-8 -*-
"""
    Tappy Terror Tests
    ------------------

    Tests Tappy Terror

    :license: MIT; details in LICENSE
"""
from __future__ import unicode_literals

import tappy
import unittest
import json
import random

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

        wrong_json_format = self.app.post(
            '/amd/push',
            data=json.dumps({'a': 'b'}),
            content_type='application/json'
        )
        self.assertEqual(wrong_json_format.status_code, 422)

        well_formed = self.app.post(
            '/amd/push',
            data=json.dumps([{'user':'user1', 'x': 1, 'y': 2, 'z': 3}]),
            content_type='application/json'
        )
        self.assertEqual(well_formed.status_code, 200)
        decoded = json.loads(well_formed.data)
        self.assertIsInstance(decoded['snapshot_id'], int)
        
        wrong_content_type = self.app.post(
            '/amd/push',
            data=json.dumps([{'user':'user1', 'x': 1, 'y': 2, 'z': 3}])
        )
        self.assertEqual(wrong_content_type.status_code, 200)
        decoded = json.loads(wrong_content_type.data)
        self.assertIsInstance(decoded['snapshot_id'], int)

class TappyTerrorGameTestCase(unittest.TestCase):
    def get_location_dump(filter=None, value=None):
        """Dummy list of user updates
        """
        return [
            {"user": "user10",
             "team": "blue",
             "area": "NOC"},
            {"user": "user30",
             "team": "red",
             "area": "NOC"},
            {"user": "user31",
             "team": "green",
             "area": "NOC"},
            {"user": "user11",
             "team": "red",
             "area": "Core Staff Area"},
            {"user": "user12",
             "team": "green",
             "area": random.choice(tappy.floor_list.keys())},
            {"user": "user13",
             "team": "green",
             "area": random.choice(tappy.floor_list.keys())},
            {"user": "user14",
             "team": "yellow",
             "area": random.choice(tappy.floor_list.keys())},
            {"user": "user15",
             "team": "yellow",
             "area": random.choice(tappy.floor_list.keys()),
             "button": True},
            {"user": "user32",
             "team": "yellow",
             "area": "NOC",
             "button": True},
        ]

    def test_start_game(self):
        game = tappy.TappyTerrorGame()
        game.tick()

    def test_position_update_changes_active(self):
        game = tappy.TappyTerrorGame()
        # Equivelent to asserting that there are no active players
        self.assertFalse(game.active_players)

        user_updates = self.get_location_dump()
        no_button_updates = [x for x in user_updates if not x.get('button')]
        button_updates = [x for x in user_updates if x.get('button')]
        inactive_users = [x['user'] for x in no_button_updates]
        expected_active_users = [x['user'] for x in button_updates]
        # update without buttons shouldn't make users appear
        game.update_player_positions(no_button_updates)
        self.assertFalse(game.active_players)

        # now update all of them
        game.update_player_positions(user_updates)
        self.members_correct(game.active_players, expected_active_users, inactive_users)

        # performing another update without any button folks shouldn't
        # make the button folks leave active
        game.update_player_positions(no_button_updates)
        self.members_correct(game.active_players, expected_active_users, inactive_users)

        # updating just the button folks shouldn't change anything
        game.update_player_positions(button_updates)
        self.members_correct(game.active_players, expected_active_users, inactive_users)

        # make a few random users toggle their button, make sure update works
        random_users = random.sample(user_updates, 3)
        for user in random_users:
            if user.get('button'):
                user['button'] = False
            else:
                user['button'] = True
                inactive_users.remove(user['user'])
                expected_active_users.append(user['user'])

        game.update_player_positions(user_updates)
        self.members_correct(game.active_players, expected_active_users, inactive_users)

        # confirm that our assumptions survive a round trip
        mem_db = tappy.connect_memory_db()
        tappy.create_game_db(mem_db)
        game.snapshot_to_db(mem_db)
        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertEquals(game.active_players, roundtrip.active_players)

    def members_correct(self, target, present, absent):
        """Asserts that target contains elements of present but not absent.

        Asserts that all elements of present are in the target list and none
        of the elements of absent are in the target list. 
        
        Params:
        - target: the target list
        - present: sequence of items that must be in target
        - absent: sequence of items that must not be in target
        """
        # NOTE: This is a quick implementation of this, not a performant one
        for p in present:
            self.assertIn(p, target)
        for a in absent:
            self.assertNotIn(a, target)

    def test_snapshot(self):
        mem_db = tappy.connect_memory_db()
        tappy.create_game_db(mem_db)
        
        empty_game = tappy.TappyTerrorGame()
        snapshot_id = empty_game.snapshot_to_db(mem_db)
        db_snapshot_id = mem_db.execute('SELECT id FROM game_snapshots ORDER BY update_time DESC LIMIT 1').fetchone()[0]
        self.assertEqual(snapshot_id, db_snapshot_id)

        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertIsInstance(roundtrip, tappy.TappyTerrorGame)

        self.assertEqual(empty_game.game_board.keys(), roundtrip.game_board.keys())
        self.assertEqual(empty_game.game_board, roundtrip.game_board)
        self.assertEqual(empty_game.active_players, roundtrip.active_players)
        self.assertEqual(empty_game.team_points, roundtrip.team_points)

        full_game = tappy.TappyTerrorGame()
        full_game.tick()
        self.assertNotEqual(empty_game, full_game)
        db_snapshot_id = mem_db.execute('SELECT id FROM game_snapshots ORDER BY update_time DESC LIMIT 1').fetchone()[0]
        self.assertEqual(snapshot_id, db_snapshot_id)
        snapshot_id = full_game.snapshot_to_db(mem_db)
        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertEqual(full_game.game_board, roundtrip.game_board)
        self.assertEqual(full_game.active_players, roundtrip.active_players)
        self.assertEqual(full_game.team_points, roundtrip.team_points)

    def test_team_control(self):
        game = tappy.TappyTerrorGame()

        user_updates = self.get_location_dump()
        self.assertIsNone(game.game_board[user_updates[0]['area']].team)

        # we expect the first player in the update at each location to 
        # take control of that location, so make a map of area -> conroller
        expected_teams = {}
        for user in user_updates:
            if user['area'] not in expected_teams:
                expected_teams[user['area']] = set([user['team']])
            else:
                expected_teams[user['area']].add(user['team'])

        game.update_player_positions(user_updates)
        for user in user_updates:
            self.assertIsNotNone(game.game_board[user['area']].team)
            self.assertIn(
                game.game_board[user['area']].team,
                expected_teams[user['area']]
            )

    def test_assign_teams(self):
        game = tappy.TappyTerrorGame()
        user_updates = self.get_location_dump()
        for user in user_updates:
            user['team'] = None
            game._assign_team(user)
        
        assigned_teams = {user['user']: user['team'] for user in user_updates}
        for user in user_updates:
            user['team'] = None
        game.update_player_positions(user_updates)

        for (user_id, player) in game.active_players.items():
            self.assertEqual(player.team, assigned_teams[player.amd_user_id])

        mem_db = tappy.connect_memory_db()
        tappy.create_game_db(mem_db)
        game.snapshot_to_db(mem_db)
        roundtrip = tappy.TappyTerrorGame.load_from_snapshot(mem_db)
        self.assertEqual(game.active_players, roundtrip.active_players)

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
