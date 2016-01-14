-- Table definitions for the tournament project.

\c tournament;

DROP VIEW IF EXISTS CountPlayersByTournament;
DROP VIEW IF EXISTS StatsByTournament;
DROP VIEW IF EXISTS Opponents;

DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Tournaments;


CREATE TABLE Tournaments
(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(250) NOT NULL
);


CREATE TABLE Players
(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(250) NOT NULL,
    Tournament_Id SERIAL REFERENCES Tournaments(Id)
);


CREATE TABLE Matches
(
    Player1_Id SERIAL REFERENCES Players(Id),
    Player2_Id SERIAL REFERENCES Players(Id),
    Result INTEGER NOT NULL,
    PRIMARY KEY (Player1_Id, Player2_Id)
);


CREATE VIEW CountPlayersByTournament AS
    SELECT
        T.Id AS Tournament_Id,
        COUNT (P.Id) AS totalPlayers
    FROM Tournaments AS T
    LEFT JOIN Players AS P
        ON P.tournament_id=T.ID
    GROUP BY T.Id;


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


CREATE VIEW Opponents AS
    SELECT
        P.Tournament_Id AS Tournament_Id,
        P.Id AS Player1_Id,
        P.Name AS Player1Name,
        OP.Id AS Player2_Id,
        OP.Name AS Player2Name,
        SUM(CASE
            WHEN
                s.player1_id = s.player2_id -- a bye is considered a win
                OR ((s.player1_id = p.id OR s.player1_id = op.id) AND s.result = 1)
                OR ((s.player2_id = p.id OR s.player2_id = op.id) AND s.result = 2) THEN 2
            WHEN (s.player1_id <> s.player2_id) AND s.result = 0 THEN 1
            ELSE 0
        END) AS TotalScore
    FROM Players AS P
    JOIN Players OP
        ON P.Id <= OP.Id AND OP.Tournament_Id = P.Tournament_Id
    LEFT JOIN Matches AS S
        ON (S.Player1_Id = P.Id OR S.Player2_Id = P.Id)
            OR (S.Player1_Id = OP.Id OR S.Player2_Id = OP.Id)
    WHERE ((P.Id = S.Player1_Id AND OP.id = S.Player2_Id)=False OR S.Result IS NULL)
    GROUP BY P.Tournament_Id, P.id, OP.id
    ORDER BY
        Tournament_Id,
        TotalScore DESC,
        Player1_Id,
        Player2_Id;
