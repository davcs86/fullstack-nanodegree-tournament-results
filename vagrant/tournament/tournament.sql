-- Table definitions for the tournament project.

\c tournament;

-- Drop current items in database

DROP VIEW IF EXISTS CountPlayersByTournament;
DROP VIEW IF EXISTS StatsByTournament;
DROP VIEW IF EXISTS Opponents;

DROP INDEX IF EXISTS M1;
DROP INDEX IF EXISTS M2;
DROP INDEX IF EXISTS M3;
DROP TABLE IF EXISTS Matches;

DROP INDEX IF EXISTS P1;
DROP INDEX IF EXISTS P2;
DROP TABLE IF EXISTS Players;

DROP INDEX IF EXISTS T1;
DROP TABLE IF EXISTS Tournaments;

-- Where the tournaments are stored
CREATE TABLE Tournaments
(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(250) NOT NULL
);
CREATE INDEX T1 ON Tournaments USING btree(Id);

-- Where the players are stored with their respective tournament
CREATE TABLE Players
(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(250) NOT NULL,
    Tournament_Id SERIAL REFERENCES Tournaments(Id)
);
CREATE INDEX P1 ON Players USING btree(Id);
CREATE INDEX P2 ON Players USING btree(Tournament_id);

-- Where the results of a match is stored
CREATE TABLE Matches
(
    Player1_Id SERIAL REFERENCES Players(Id),
    Player2_Id SERIAL REFERENCES Players(Id),
    Result INTEGER NOT NULL,
    -- UNIQUE constraint avoids insert the same match result more than once
    UNIQUE (Player1_Id, Player2_Id)
);
CREATE INDEX M1 ON Matches USING btree (Player1_Id);
CREATE INDEX M2 ON Matches USING btree (Player2_Id);
CREATE INDEX M3 ON Matches USING btree (Result);


CREATE VIEW CountPlayersByTournament AS
    SELECT
        T.Id AS Tournament_Id,
        COUNT (P.Id) AS totalPlayers
    FROM Tournaments AS T
    LEFT JOIN Players AS P
        ON P.tournament_id=T.ID
    GROUP BY T.Id;

-- Counts the wins, loses and draws of players in a tournament.
-- Based on the Result column from the table Matches
CREATE VIEW StatsByTournament AS
    SELECT
        P.Tournament_Id AS Tournament_Id,
        P.Id AS Player_Id,
        P.Name AS PlayerName,
        SUM(
            CASE
                WHEN (M.Player1_Id=M.Player2_Id
                    OR (M.Player1_Id=P.Id AND M.Result=1)
                    OR (M.Player2_Id=P.Id AND M.Result=2)) THEN 1
                ELSE 0
            END) AS Wins,
        SUM(
            CASE
                WHEN (M.Player1_Id<>M.Player2_Id
                    OR (M.Player1_Id=P.Id AND M.Result=2)
                    OR (M.Player2_Id=P.Id AND M.Result=1)) THEN 1
                ELSE 0
            END) AS Loses,
        SUM(
            CASE
                WHEN (M.Player1_Id<>M.Player2_Id AND M.Result=0) THEN 1
                ELSE 0
            END) AS Draws,
        COUNT(M.Result) AS Matches
    FROM Players AS P
    LEFT JOIN Matches AS M
        ON M.Player1_Id=P.Id OR M.Player2_Id=P.Id
    GROUP BY P.Id
    ORDER BY
        Wins DESC,
        Player_Id;

-- Creates the non-repeated and still possible pairings based on the following conditions:
-- **** Takes not repeated pairs:    P.Id <= OP.Id
--
--      i.e. for 4 players, takes these as possible pairs
--         A  B  C  D
--      A  *  -  -  -
--      B  *  *  -  -
--      C  *  *  *  -
--      D  *  *  *  *
--
-- **** Same tournament:            OP.Tournament_Id = P.Tournament_Id
--
-- **** Haven't play yet:           M.Result IS NULL -- never played at all
--                                  (P.Id = M.Player1_Id AND OP.id = M.Player2_Id)=False -- played with others
--
-- **** Ranks the pairs by score:   2 points by win (or bye) and 1 point for draw
CREATE VIEW Opponents AS
    SELECT
        P.Tournament_Id AS Tournament_Id,
        P.Id AS Player1_Id,
        P.Name AS Player1Name,
        OP.Id AS Player2_Id,
        OP.Name AS Player2Name,
        SUM(CASE
            WHEN
                M.Player1_Id = M.Player2_Id -- a bye is considered a win
                OR ((M.Player1_Id = P.Id OR M.Player1_Id = OP.Id) AND M.Result = 1)
                OR ((M.Player2_Id = P.Id OR M.Player2_Id = OP.Id) AND M.Result = 2) THEN 2
            WHEN (M.Player1_Id <> M.Player2_Id) AND M.Result = 0 THEN 1
            ELSE 0
        END) AS TotalScore
    FROM Players AS P
    JOIN Players OP
        ON P.Id <= OP.Id AND OP.Tournament_Id = P.Tournament_Id
    LEFT JOIN Matches AS M
        ON (M.Player1_Id = P.Id OR M.Player2_Id = P.Id)
            OR (M.Player1_Id = OP.Id OR M.Player2_Id = OP.Id)
    WHERE ((P.Id = M.Player1_Id AND OP.id = M.Player2_Id)=False OR M.Result IS NULL)
    GROUP BY P.id, OP.id
    ORDER BY
        TotalScore DESC,
        Player1_Id,
        Player2_Id;
