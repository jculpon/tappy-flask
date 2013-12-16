-- We mostly care about the *latest* update but it'd be nice to have
-- state snapshots for every update we do so that we can replay the game
-- or otherwise do fancy stuff as we desire.
-- I think we should have a db like this:
--   update_id, update_timestamp
-- which stores the last update. If we support multiple games in one db,
-- we should add a game_id to that table
-- Mutable state components of the game should always have an update_id
-- so that fetching all the state we need is something like:
-- fetch_location_details(update_id), fetch_players(update_id), fetch_teams(update_id)

-- If we update once/min over the course of three days we have:
-- 24 hours/day * 3 days * 60 min/hour * 1 update/min = 4320 state snapshots
-- That shouldn't be too bad to just do them naively...
DROP TABLE IF EXISTS game_snapshots;
CREATE TABLE game_snapshots (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       update_time INTEGER
);
DROP INDEX IF EXISTS snapshot_time_idx;
CREATE UNIQUE INDEX snapshot_time_idx ON game_snapshots(update_time);

DROP TABLE IF EXISTS teams;
CREATE TABLE teams (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       color TEXT NOT NULL,
       name TEXT UNIQUE NOT NULL
);
-- could index by name if we have a lot of teams, current plans for only ~4

DROP TABLE IF EXISTS team_ephemera;
CREATE TABLE team_ephemera (
       snapshot_id NOT NULL,
       team_id NOT NULL,
       score INTEGER NOT NULL default 0,
       PRIMARY KEY (snapshot_id, team_id),
       FOREIGN KEY(snapshot_id) REFERENCES game_snapshots(id),
       FOREIGN KEY(team_id) REFERENCES teams(id)
); -- add WITHOUT ROWID if using sqlite >=3.8.2

DROP TABLE IF EXISTS bounds_types;
CREATE TABLE bounds_types (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT UNIQUE NOT NULL
);
INSERT INTO bounds_types(name) VALUES ('rect'), ('poly');

DROP TABLE IF EXISTS bounds_vertex_lists;
CREATE TABLE bounds_vertex_lists (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       bounds_type INTEGER NOT NULL,
       FOREIGN KEY(bounds_type) REFERENCES bounds_types(id)
);

DROP TABLE IF EXISTS bounds_vertices;
CREATE TABLE bounds_vertices (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       x INTEGER NOT NULL,
       y INTEGER NOT NULL,
       list_id INTEGER NOT NULL,
       list_rank INTEGER NOT NULL,
       FOREIGN KEY(list_id) REFERENCES bounds_vertex_lists(id)
);
DROP INDEX IF EXISTS vertex_list_idx;
CREATE INDEX vertex_list_idx ON bounds_vertices(list_id, list_rank);

DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT UNIQUE NOT NULL,
       bounds_list_id INTEGER NOT NULL,
       FOREIGN KEY(bounds_list_id) REFERENCES bounds_vertex_lists(id)
);

DROP TABLE IF EXISTS location_ephemera;
CREATE TABLE location_ephemera (
       location_id INTEGER NOT NULL,
       snapshot_id INTEGER NOT NULL,
       controlling_team_id INTEGER,
       mob_count INTEGER NOT NULL default 0,
       PRIMARY KEY(snapshot_id, location_id),
       FOREIGN KEY(location_id) REFERENCES locations(id),
       FOREIGN KEY(snapshot_id) REFERENCES game_snapshots(id),
       FOREIGN KEY(controlling_team_id) REFERENCES teams(id)
); -- add WITHOUT ROWID if using sqlite >=3.8.2

DROP TABLE IF EXISTS players;
CREATE TABLE players (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       amd_user_id INTEGER UNIQUE NOT NULL,
       display_name TEXT
);
DROP INDEX IF EXISTS player_amd_idx;
CREATE UNIQUE INDEX player_amd_idx ON players(amd_user_id);
