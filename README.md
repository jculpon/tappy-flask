Tappy Terror
============

Tappy Terror is a game/toy/artwork built to take advantage of the [OpenAMD](http://www.openamd.org/) project's monitoring of attendee location via a network of RFID readers and RFID tags embedded in attendees' badges.

Game Overview
-------------

Tappy Terror divided The Next HOPE con space in to areas that were slowly filling with ghosts. Teams of attendees could chase off ghosts by tapping a special button on the con's badge. Chasing off ghosts scored points for both the team and the individual attendee. Additionally, if teams kept areas of the con they controlled clear of ghosts for an extended period of time, they could score additional points.

Tappy Terror uses the overall movement of attendees to divvy up different areas of convention space among a set of four color-coded teams. Territories change ownership based on who happens to be in a given part of the convention, regardless of whether or not they are actively participating in the game. Teams could try to coordinate and get more members in certain areas to take them over, but the movement of crowds from one part of the convention to another could cause the territory to shift unexpectedly. Our hope was that the ebb and flow of attendees would become an important part of the gameplay.

Getting Started
---------------

You need a recent version of Python 2.7 to run this (I use 2.7.6). It may run on Python 3.3, but it is untested. You should have [pip installed](http://www.pip-installer.org/en/latest/installing.html) to make it easier to grab the dependencies.

Grab the source and set up a new virtualenv if you desire, then use the Makefile to kick things off. Install the dependencies with:

```make deps```

and use

```make devserver```

to start a development server listening on http://127.0.0.1:5000. You can run the tests with:

```make test```

If you get an ImportError straight off, make sure you've run `make deps`.


Tech Overview
-------------

This game runs on the web using Flask. The Flask application and game logic can all be found in tappy.py. The unit tests are in tappy_tests.py. Once the server is started, you can see an overview of the current state of the game at / or /game.html. Updates to location data should be posted as JSON to /amd/push.

Game state gets snapshotted to a sqlite3 database named tappy.db after location updates; the status page reads the latest snapshot to create its overview. The schema for the database is in schema.sql, with initial team and floorplan data for the version of the game run at HOPE in hope.sql.

A small command-line tool for simulating location updates is in tools/sim.py.
python sim.py -h should give you up to date information on how to invoke it.

History
-------

Tappy Terror is a small game that was thrown together during [The Next HOPE](http://thenexthope.org). It was intended to show off some interesting things that could be done with the real-time tracking of attendees at HOPE. As such, it was primarily intended as a demonstration and gameplay experiment, not a polished or pretty game.

Originally Tappy Terror was built on top of a quite old version of web.py. I've ported it to [Flask](http://flask.pocoo.org/) here in part to move the code to something that is easier to get up and running quickly. The idea is that this project could show someone how to get a simple but dynamic webapp up quickly.

The game was originally designed with the help of my friends Megan Myers and Sam Calabrese. The core of the idea came from a discussion about the possibility of using the flow of attendees as an environmental characteristic. The goal of the game was to take control of various areas of the conference by clearing out invading forces and claiming areas once they were free of enemies. Every attendee would be assigned a team based on their badge ID, and could play both for individual and team score. Individuals scored by clearing out enemies by pressing a button on their badge while in areas marked as containing enemies. Teams scored by gaining control of territory without any enemies in it, and could gain control of any area by having more team members in at that location than any other team.

Credits
-------

Tappy Terror  was based on discussions with the OpenAMD team for [The Next HOPE](http://thenexthope.org) and was originally created by Jamie Culpon, Megan Myers, and Sam Calabrese. This version was created primarily by Jamie Culpon, but is open for patches and extensions from anyone.

Potential Improvements
----------------------

Documentation:
- Set up and convert docstrings to [sphinx](Sphinx)

Porting:
- Determine if OpenAMD data is still around despite hope.amd.net being down

Flask app:
- Confirm/fix area assessments with raw location coordinates
- More robust error handling
- API endpoints to allow clients to post individual player updates
- Python 3 compat check
- Find a nicer way to test the templates for errors than hitting them
  with a browser
- Create a db snapshot of an in progress game that would be useful to
  load into the in-memory db during tests to make the template render
  tests more releastic

Front end/website:
- Less generic styling
- Font treatment
- Confirm layouts on Chrome and Safari
- Check pages on mobile browser
- Project Info/landing page
- Navigation
- Javascript to highlight locations on mouse/tap on game page

Other tools:
- Enhance sim.py with an actual crowd simulation
- Enhance sim.py to read a file containing a bunch of updates to send
