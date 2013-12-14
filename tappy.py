# -*- coding: utf-8 -*-
"""
    Tappy Terror
    ------------

    Simple gamelike toy based on HOPE's OpenAMD project

    :license: MIT; details in LICENSE
"""

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
    return render_template('game.html')

# End Flask setup

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


# Game logic    
class Location(object):
    """Handles all information for locations in Tappy Terror

    Currently just a holder for team and mob count info
    """

    def __init__(self, team=None, mob_count=initial_mob_count):
        """Make a location.
        
        Arguments:
        - `team`: The team that currently owns this Location
        - `mob_count`: Number of mobs in the Location
        """
        self.team = team
        self.mob_count = mob_count
    
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
