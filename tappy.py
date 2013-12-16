# -*- coding: utf-8 -*-
"""
    Tappy Terror
    ------------

    Simple gamelike toy based on HOPE's OpenAMD project

    :license: MIT; details in LICENSE
"""

from PIL import Image, ImageDraw
from contextlib import closing
import time
import os
import errno
import random
import shelve
import sqlite3
import datetime

# Flask setup
from flask import Flask, render_template

app = Flask(__name__)

# Dev settings
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='Not so secret dev key'
))
# Override dev settings from the TAPPY_SETTINGS envvar if present
app.config.from_envvar('TAPPY_SETTINGS', silent=True)

@app.route('/')
@app.route('/game')
def game_index():
    """Render the current state of the game for the web"""
    s = shelve.open('TappyData.dat')
    gb = s['gameboard']
    ap = s['activeplayers']
    tp = s['teampoints']
    s.close()

    return render_template('game.html')

# End Flask setup


# Helpers for getting game state ready for the web
def draw_board_image(game_board, rooms):
    """Draws an image representing the current state of the game

    game_board - dict(name -> loc)
    rooms - equiv to floor_list
    """
    im = Image.new ('RGBA', (1157,1098), (0,0,0,0)) #Create a blank image
    draw = ImageDraw.Draw(im) #create a draw object

    for name, loc in game_board.items() :
        if rooms[name].poly_type == 'rect':
            draw.rectangle(rooms[name].vertices, fill=loc.team, outline="black")
        elif rooms[name].poly_type == 'poly':
            draw.polygon(rooms[name].vertices, fill=loc.team, outline="black")

    img_dir = os.path.join(app.static_folder, 'boards')

    # make sure the boards img dir exists - without this im.save() will raise
    # if we haven't made the dir yet.
    # Note that this construction avoids a subtle race condition in the
    # naive "if the dir doesn't exist, make it" code. In python >=3.2, we
    # can just use os.makedirs(path, exist_ok=True), which does essentially
    # this.
    try:
        os.makedirs(img_dir)
    except OSError:
        if not os.path.isdir(img_dir):
            raise

    now_gmt = time.gmtime()    
    filename = 'tappymap-%s.png' % (
        time.strftime('%Y-%m-%d-%H-%M-%S', now_gmt)
    )
        
    im.save(os.path.join(img_dir, filename))
    symlink_with_overwrite(os.path.join(img_dir, filename),
                           os.path.join(app.static_folder, 'latest.png'))

def symlink_with_overwrite(src, dst):
    """Create a symlink at dst pointing to src, overwriting dst if possible

    Like os.symlink(src, dst), but if the link fails to be created due to a
    file already exisitng at dst, tries to delete the file and make the link.
    Can still raise an OSError with e.errno == EEXIST if another process
    creates dst after this function deletes it.
    """
    try:
        os.symlink(src, dst)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
        # symlink already exists, kill it and relink. We could theoretically
        # lose a race here between the delete and create. If so, we just have
        # to bail.
        os.remove(dst)
        os.symlink(src, dst)

def connect_memory_db():
    """Connect to an in-memory SQLite db
    """
    return sqlite3.connect(':memory:')

def create_game_db(db):
    """Create the db schema for tappy terror from the given schema file
    """
    with open('schema.sql') as f:
        db.cursor().executescript(f.read())
    with open('hope.sql') as f:
        db.cursor().executescript(f.read())
    db.commit()

# Game config
# These constants are the variables that control all the
# game logic -  how often the board resets, mobs spawn and how many points
# you get for killing mobs and holding territory.
# For now they are hard coded in but I would like them to be read in from a file
# where we can change them
# Maximum number of mobs that can be spawned in a given location
max_mobs_in_loc = 25

# Number of mobs spawned in a location by default
initial_mob_count = 1

#points_per_control_tick - points for holding a territory per minute
points_per_control_tick = 30.0


# Game logic
class TappyTerrorGame(object):
    """Main thread equivelent for Tappy Terror

    Initializes data structures and manages game updates."""
    def __init__(self):
        self.game_board = {}
        self.active_players = {}
        self.team_points = {"red": 0, "blue": 0, "yellow": 0, "green": 0}
        self._initialize_game_board()

    def _initialize_game_board(self):
        for name in floor_list.keys():
            self.game_board[name] = Location(name, floor_list[name])

    def tick(self):
        self._update_game_board()
        self._update_mobs()
        self._shelve_data()

    def _update_game_board(self):
        """Update the game board based on the latest player location dump.

        Stuff not done right:
        1. if locations overlap, the current implementation will count
           players that lie within the overlap as being in both regions.
        2. The team flag updates are currently unsafe.
        3. Really, this sould be triggered by the updates coming in rather than
           us polling.
        """
        # this is the super-naive way to do this, but we don't have many
        # locations so n^2 will be good enough for now.

        # dict of bounding_box -> {"team_name": count}
        team_counts = {} 

        # probably a more elegant way to do this but it gets the job done
        for area_name, loc in self.game_board.items():
            team_counts[area_name] = dict([(t,0) for t in self.team_points])

        #Get the location dump of where all the players are
        players = get_location_dump()
    
        # tally up the number of players on each team in each location
        for p in players:
            for n, l in self.game_board.items():
                if p["area"] == n:
                    team_counts[n][p["team"]] += 1

        # update locations's teams with the new owners
        for name, team_count in team_counts.items():
            # not sure that this method is always going to do what we want
            # in the case of ties on the player counts, but it'll do something
            # consistently at least :)
            top_team = max(team_count, key=team_count.get)
            # giving away locations when *nobody* is there is a bit mean; let
            # the old team keep it in that case
            if team_count[top_team] != 0:
                self.game_board[name].team = top_team

        #Draw the image of the current gameboard
        draw_board_image(self.game_board, floor_list) 

    def _update_mobs(self):
        """increase mob count in any location that already has a mob
        """
        for name, loc in self.game_board.items():
            assert loc.mob_count >= 0, "weirdness: negative mob count"
            if loc.has_mobs:
                loc.spawn_mob()

    def _shelve_data(self):
        s = shelve.open('TappyData.dat')
        s['gameboard'] = self.game_board
        s['activeplayers'] = self.active_players
        s['teampoints'] = self.team_points
        s.close()
    
    def snapshot_to_db(self, db):
        """Snapshot the game state to the given database

        Writes a snapshot of the game state to the given sqlite3 database.
        The database is assumed to have the correct schema etc.
        
        Params:
        - db: a connected sqlite3 database
        """
        if not isinstance(db, sqlite3.Connection):
            raise TypeError('db is not a sqlite3 connection')
        
        # Creates a transaction that rolls back on failure and
        # commits at the end of the block. See 
        # http://docs.python.org/2/library/sqlite3.html#using-the-connection-as-a-context-manager
        with db:
            #actual db writes go here
            #insert snapshot time and get snapshot id for subsequent stuff
            now = datetime.datetime.utcnow()
            now_milliseconds = (
                time.mktime(now.timetuple())*1000 + now.microsecond / 1000
            )
            result = db.execute(
                'INSERT INTO game_snapshots(update_time) VALUES (?)',
                [now_milliseconds]
            )
            update_id = result.lastrowid
            #_snapshot_game_board(db)
            db.executemany(
                'INSERT INTO location_ephemera'
                '(snapshot_id, location_id, controlling_team_id, mob_count)'
                'VALUES (?, '
                        '(SELECT id FROM locations WHERE name=?), '
                        '(SELECT id FROM teams WHERE name=?), '
                        '?)',
                ((update_id, l.name, l.team, l.mob_count)
                 for l in self.game_board.values())
            )
            #_snapshot_team_points(db)
            db.executemany(
                'INSERT INTO team_ephemera(snapshot_id, team_id, score) '
                'VALUES (?, (SELECT id FROM teams WHERE name=?), ?)',
                ((update_id, k, v) for (k,v) in self.team_points.items())
            )
            #_snapshot_active_players(db)
            db.executemany(
                'INSERT OR REPLACE INTO '
                'players(id, amd_user_id, display_name) '
                'VALUES (?, ?, ?)',
                ((x['id'], x['amd_user_id'], x['display_name'])
                 for x in self.active_players)
            )

    @staticmethod
    def load_from_snapshot(db):
        """Construct a new game instance from the given database

        Params:
        - db: a connected sqlite3 database
        """
        if not isinstance(db, sqlite3.Connection):
            raise TypeError('db is not a sqlite3 connection')
        
        with db:
            game = TappyTerrorGame()

            result = db.execute('SELECT id FROM game_snapshots ORDER BY update_time DESC LIMIT 1')
            snapshot_id = result.fetchone()[0]

            teams_result = db.execute(
                'SELECT teams.id, teams.color, teams.name, te.score '
                'FROM team_ephemera AS te JOIN teams ON teams.id = te.team_id '
                'WHERE te.snapshot_id = ?',
                [snapshot_id]
            )
            team_id_to_name = {}
            for team_row in teams_result.fetchall():
                (id, color, name, score) = team_row
                game.team_points[name] = score
                team_id_to_name[id] = name
            
            #_snapshot_game_board(db)
            locations_result = db.execute(
                'SELECT l.name, l.bounds_list_id, '
                'le.controlling_team_id, le.mob_count '
                'FROM location_ephemera AS le '
                'INNER JOIN locations AS l ON le.location_id = l.id '
                'WHERE le.snapshot_id = ?',
                [snapshot_id]
            )
            bounds_ids = []
            bounds_id_to_name = {}
            for location_row in locations_result.fetchall():
                (name, bounds_id, team_id, mob_count) = location_row
                # make the location without bounds for now, will fetch all
                # bounds and update the locations in a subsequent query
                team = team_id_to_name.get(team_id)
                game.game_board[name] = Location(
                    name, None, team, mob_count
                )
                bounds_ids.append(bounds_id)
                bounds_id_to_name[bounds_id] = name
            bounds_results = db.execute(
                'SELECT v.x, v.y, v.list_id, t.name '
                'FROM bounds_vertices AS v '
                'INNER JOIN bounds_vertex_lists AS l ON l.id = v.list_id '
                'INNER JOIN bounds_types AS t ON l.bounds_type = t.id '
                'WHERE v.list_id IN (%s) '
                'ORDER BY v.list_id, v.list_rank ' % (', '.join('?' for x in bounds_ids)),
                bounds_ids
            )
            vertex_lists = {}
            list_id_to_bounds_type = {}
            for vertex_row in bounds_results:
                (x, y, list_id, bounds_type) = vertex_row
                if list_id not in vertex_lists:
                    vertex_lists[list_id] = [(x, y)]
                    list_id_to_bounds_type[list_id] = bounds_type
                else:
                    assert list_id_to_bounds_type[list_id] == bounds_type
                    vertex_lists[list_id].append((x, y))
            for list_id in vertex_lists:
                p = Polygon(
                    list_id_to_bounds_type[list_id],
                    vertex_lists[list_id]
                )
                game.game_board[bounds_id_to_name[list_id]].bounds = p
                

            #_snapshot_active_players(db)
            players_result = db.execute(
                'SELECT id, amd_user_id, display_name FROM players'
            )
            for player_row in players_result.fetchall():
                (id, amd_user_id, display_name) = player_row
                player = {
                    'id': id,
                    'amd_user_id': amd_user_id,
                    'display_name': display_name
                }
                game.active_players.append(player)
            
            return game

def get_location_dump(filter=None, value=None):
    """Dummy implementation of get_location_dump for testing
    """
    return [{"user": "10", "team": "blue", "area": "NOC"},
            {"user": "11", "team": "red", "area": "Core Staff Area"},
            {"user": "12", "team": "green", "area": random.choice(floor_list.keys())},
            {"user": "13", "team": "green", "area": random.choice(floor_list.keys())},
            {"user": "14", "team": "yellow", "area": random.choice(floor_list.keys())}]

class Location(object):
    """Handles all information for locations in Tappy Terror

    Currently just a holder for team and mob count info
    """

    def __init__(self,
                 location_name,
                 location_bounds,
                 controlling_team=None,
                 mob_count=initial_mob_count):
        """Make a location.
        
        Arguments:
        - `location_name`: name of the location
        - `location_bounds`: Polygon definining the bounds
        - `team`: The team that currently owns this Location
        - `mob_count`: Number of mobs in the Location
        """
        if location_name is None:
            raise ValueError('Locations must be named')
        if location_bounds is not None and not isinstance(location_bounds, Polygon):
            raise TypeError('bounds must be a tappy.Polygon object')
        self.name = location_name
        self.bounds = location_bounds
        self.team = controlling_team
        self.mob_count = mob_count

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Location):
            return False

        return ((self.name == other.name)
                and (self.team == other.team)
                and (self.bounds.poly_type == other.bounds.poly_type)
                and (self.bounds.vertices == other.bounds.vertices)
                and (self.mob_count == other.mob_count))

    def __neq__(self, other):
        return not (self == other)

    def __hash__(self):
        seed = 0x34567
        return (seed ^ hash(self.name) ^ hash(self.team)
                ^ hash(self.bounds.poly_type) ^ hash(self.bounds.vertices)
                ^ hash(self.mob_count))
    
    def spawn_mob(self, count=1):
        """Spawn a mob in this location
        
        Arguments:
        - `count`: Number of mobs to spawn. defaults to 1
        """
        updated_count = self.mob_count + count
        if updated_count > max_mobs_in_loc:
            updated_count = max_mobs_in_loc
        self.mob_count = updated_count

    def remove_mob(self, count=1):
        """Remove a mob from this location
        
        Arguments:
        - `count`: Number of mobs to spawn. defaults to 1
        """
        updated_count = self.mob_count - count
        if updated_count < 0:
            updated_count = 0
        self.mob_count = updated_count

    def has_mobs(self):
        """Returns true if and only if the location has mobs in it
        """
        return self.mob_count > 0
        
    def score(self):
        """Return the score earned for this territory by the controlling team
        """
        return points_per_control_tick

class Polygon (object):
    """Polygon stores the bounds for rooms.

    Polygon defines boundaries in terms of vertex lists. A vertex list is a
    plain old python list containing tuples representing x,y coordinates.

    There are two types of bounds, which differ in how they treat their list
    of verticies:
    - `rect` defines a rectangle and treats the first and second entries of the
       verticies list the upper left and lower right corners of the rectancgle:
       [(upper_left_x, upper_left_y), (lower_right_x, lower_right_y)]
       Other elements in the vertex list are ignored

    - `poly` defines a generic polygon giving in terms of vertexes listed
       in clockwise order from the top left. then clockwise around. The
       polygon has the edges:
            verticies[0] -> verticies[1]
            verticies[1] -> verticies[2]
            ...
            verticies[n-1] -> verticies[n]
            verticies[n] -> verticies[0]
    """
    def __init__ (self, poly_type, vertices) :
        self.poly_type = poly_type
        self.vertices = vertices

floor_list = {}
"""Floor_list stores all of the different zones on the mezanine level
it is a dictionary keyed to the zones name and holds the type and vertices
of the polygon bounding the zone

The Origin of the room is at the top left corner"""

floor_list["Hammock Zone"] = Polygon('rect',
    [(0,0),(354,76)]
)
floor_list["Low Power Zone"] = Polygon('rect',
    [(0,76),(354,161)]
)
floor_list["Art Space 2"] = Polygon('rect',
    [(0,162),(152,252)]
)
floor_list["Interview Area"] = Polygon('rect',
    [(0,234),(82,324)]
)
floor_list["Keynote Bullpen"] = Polygon('rect',
    [(0,326),(82,473)]
)
floor_list["Stairs to Lobby"] = Polygon('rect',
    [(82,250),(348,389)]
)
floor_list["NOC"] = Polygon('rect',
    [(84,414),(272,466)]
)
floor_list["Core Staff Area"] = Polygon('rect',
    [(88,462),(268,594)]
)
floor_list["NOC NOC"] = Polygon('rect', 
    [(273,513),(288,537)]
)
floor_list["Security Center"] = Polygon('rect', 
    [(273,513),(371,653)]
)
floor_list["AMD Work Area"] = Polygon('rect', 
    [(0,600),(176,660)]
)
floor_list["AV Stream Work Area"] = Polygon('rect',
    [(180,590),(270,660)]
)
floor_list["Ethernet Tables"] = Polygon('rect',
    [(0,658),(175,738)]
)
floor_list["Project Telephreak"] = Polygon('rect',
    [(175,658),(285,738)]
)
floor_list["Art Space 1"] = Polygon('poly',
    [(0,736),(352,736),(352,990),(85,990),(85,825),(0,825)]
)
floor_list["Segway Track"] = Polygon('poly',
    [(0,830),(80,830),(80,995),(585,995),(585,1070),(0,1070)]
)
floor_list["Info Desk"] = Polygon('rect',
    [(368,732),(460,814)]
)
floor_list["Radio Statler"] = Polygon('rect',
    [(363,816),(457,904)]
)
floor_list["Volunteer Lounge"] = Polygon('rect', 
    [(453,746),(592,819)]
)
floor_list["Radio/News Work Area"] = Polygon('rect', 
    [(460,816),(592,940)]
)
floor_list["Walkway North"] = Polygon('poly', 
    [(350,0),(510,0),(510,66),(445,66),(445,400),(350, 400)]
)
floor_list["untitled 1"] = Polygon('rect', 
    [(450,76),(513,132)]
)
floor_list["Walkway South"] = Polygon('poly', 
    [(350, 400),(445,400),(445, 645),(645,645),(645,333),(700,333),(700,715),(290,715),(290,655),(350,655)]
)
floor_list["Vendor Tables"] = Polygon('rect', 
    [(440,330),(640,646)]
)
floor_list["Vintage Computer Demo"] = Polygon('rect', 
    [(600, 740),(799,874)]
)
floor_list["Lock Picking Zone"] = Polygon('rect', 
    [(600,864),(700,988)]
)
floor_list["Video Temple and Simulcast"] = Polygon('rect',
    [(704,865),(980,1000)]
)
floor_list["CTF"] = Polygon('rect', 
    [(592,993),(972,1105)]
)
floor_list["General Demo Area"] = Polygon('rect', 
    [(702, 727),(965,851)]
)
floor_list["Hackerspace and Hardware Hacking Village"] = Polygon('rect', 
    [(700,430),(970,650)]
)
floor_list["General Store"] = Polygon('rect', 
    [(700,328),(975,423)]
)
floor_list["Village Ops Center"] = Polygon('rect', 
    [(973,332),(1061,658)]
)

if __name__ == '__main__':
    app.run()
