-- Table definitions for the tournament project.

\c tournament;

DROP VIEW CountTournaments;
DROP VIEW CountPlayers;
DROP VIEW CountPlayersByTournament;
DROP VIEW Opponents;
DROP VIEW StatsByTournament;
DROP VIEW StatsByPlayer;
DROP TABLE Matches;
DROP TABLE Players;
DROP TABLE Tournaments;

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

CREATE VIEW CountTournaments AS SELECT COUNT(*) FROM Tournaments;
CREATE VIEW CountPlayers AS SELECT COUNT(*) FROM Players;
CREATE VIEW CountPlayersByTournament AS
    SELECT
        T.Id AS Tournament_Id,
        CASE WHEN P.preTotal IS NULL THEN 0 ELSE P.preTotal END AS totalPlayers
    FROM Tournaments AS T
    LEFT JOIN (
        SELECT
            COUNT(SP.Id) AS preTotal,
            SP.Tournament_Id
        FROM Players AS SP
        GROUP BY SP.Tournament_Id ) AS P
    ON P.Tournament_Id = T.Id;

CREATE VIEW StatsByPlayer AS
    SELECT
        P.Id AS Player_Id,
        SUM(CASE WHEN (M.Player1_Id=M.Player2_Id OR (M.Player1_Id=P.Id AND M.Result=1) OR (M.Player2_Id=P.Id AND M.Result=2)) THEN 1 ELSE 0 END) AS Wins,
        SUM(CASE WHEN (M.Player1_Id<>M.Player2_Id OR (M.Player1_Id=P.Id AND M.Result=2) OR (M.Player2_Id=P.Id AND M.Result=1)) THEN 1 ELSE 0 END) AS Loses,
        SUM(CASE WHEN (M.Player1_Id<>M.Player2_Id AND M.Result=0) THEN 1 ELSE 0 END) AS Draws,
        SUM(CASE WHEN (M.Player1_Id<>M.Player2_Id) THEN 1 ELSE 0 END) AS numMatches
    FROM Players AS P
    JOIN Matches AS M
        ON M.Player1_Id=P.Id OR M.Player2_Id=P.Id
    GROUP BY P.Id;

CREATE VIEW StatsByTournament AS
    SELECT
        T.Id AS Tournament_Id,
        P.Id AS Player_Id,
        P.Name AS PlayerName,
        CASE WHEN S.Wins IS NULL THEN 0 ELSE S.Wins END AS Wins,
        CASE WHEN S.Loses IS NULL THEN 0 ELSE S.Loses END AS Loses,
        CASE WHEN S.Draws IS NULL THEN 0 ELSE S.Draws END AS Draws,
        (Wins*2)+(Draws*1) AS Score,
        CASE WHEN S.numMatches IS NULL THEN 0 ELSE S.numMatches END AS Matches
    FROM Tournaments AS T
    JOIN Players AS P
        ON P.Tournament_Id = T.Id
    LEFT JOIN StatsByPlayer AS S
        ON S.Player_Id=P.Id
    ORDER BY Tournament_Id ASC, Wins DESC, Score DESC, Player_Id ASC;


CREATE VIEW Opponents AS
    SELECT
        T.Id AS Tournament_Id,
        P.Id AS Player1_Id,
        P.Name AS Player1Name,
        SP.Wins AS Player1Wins,
        SP.Score AS Player1Score,
        OP.Id AS Player2_Id,
        OP.Name AS Player2Name,
        SOP.Wins AS Player2Wins,
        SOP.Score AS Player2Score,
        CASE WHEN M.Result IS NULL THEN FALSE ELSE TRUE END AS AlreadyPlayed
    FROM Tournaments AS T
    JOIN Players AS P
        ON P.Tournament_Id = T.Id
    CROSS JOIN Players OP
    LEFT JOIN Matches AS M
        ON OP.Tournament_Id=P.Tournament_Id
            AND ((P.Id=M.Player1_Id AND OP.Id=M.Player2_Id)
                OR (OP.Id=M.Player1_Id AND P.Id=M.Player2_Id))
    LEFT JOIN StatsByTournament AS SP
        ON SP.Player_Id=P.Id
    LEFT JOIN StatsByTournament AS SOP
        ON SOP.Player_Id=OP.Id
    ORDER BY
        Tournament_Id ASC,
        Player1Wins DESC,
        Player2Wins DESC,
        Player1Score DESC,
        Player2Score DESC;
