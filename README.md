tappy-flask
===========

Port of The Next HOPE OpenAMD game/toy Tappy Terror to Flask.


History
-------
Tappy Terror is a small game that was thrown together during [The Next HOPE](http://thenexthope.org). It was intended to show off some interesting things that could be done with the real-time tracking of attendees at HOPE. As such, it was primarily intended as a demonstration, not a polished or pretty game.

Originally Tappy Terror was built on top of web.py. I've ported it to [Flask](http://flask.pocoo.org/) here as one part learning exercise and one part to move the code to something that is easier to get up and running quickly. The idea is that this project could show someone how to get a nice and simple webapp off the ground without too much effort.

The game was originally designed with the help of my friends Megan Myers and Sam Calabrese. The core of the idea came from a discussion about the possibility of using the flow of attendees as an environmental characteristic. The goal of the game was to take control of various areas of the conference by clearing out invading forces and claiming areas once they were free of enemies. Every attendee would be assigned a team based on their badge ID, and could play both for individual and team score. Individuals scored by clearing out enemies by pressing a button on their badge while in areas marked as containing enemies. Teams scored by gaining control of territory without any enemies in it, and could gain control of any area by having more team members in at that location than any other team.

Credits
-------

This project was based on discussions with the OpenAMD team for [The Next HOPE](http://thenexthope.org).

TODOs
-----
- Getting started documentation
- Style the index pages
- Determine if OpenAMD data still exists
- Pump for location data
