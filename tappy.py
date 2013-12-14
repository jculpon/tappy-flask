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

if __name__ == '__main__':
    app.run()
