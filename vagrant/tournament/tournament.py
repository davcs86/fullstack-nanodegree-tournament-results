#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname='tournament'")


def deleteTournaments():
    deleteMatches()
    deletePlayers()
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Tournaments")
    conn.commit()
    conn.close()


def registerTournament(tournamentName):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO Tournaments (Name) VALUES (%s)", [tournamentName])
    conn.commit()
    c = conn.cursor()
    c.execute("SELECT currval(pg_get_serial_sequence('Tournaments','id'))")
    newTournamentId = c.fetchone()[0]
    conn.close()
    return newTournamentId


def countTournaments():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Tournaments")
    totalTournaments = c.fetchone()[0]
    conn.commit()
    conn.close()
    return totalTournaments


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Matches")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    deleteMatches()
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Players")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Players")
    totalPlayers = c.fetchone()[0]
    conn.commit()
    conn.close()
    return totalPlayers


def registerPlayerInTournament(tournamentId, playerName):
    """Adds a player to the tournament database.
    Args:
      playerName: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO Players (Name, Tournament_Id) VALUES (%s, %s)",
              [playerName, tournamentId])
    conn.commit()
    c = conn.cursor()
    c.execute("SELECT currval(pg_get_serial_sequence('Players','id'))")
    newPlayerInTournamentId = c.fetchone()[0]
    conn.close()
    return newPlayerInTournamentId


def countPlayersInTournament(tournamentId):
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT totalPlayers FROM CountPlayersByTournament
                WHERE Tournament_Id='%s'""", [tournamentId])
    totalPlayersInTournament = c.fetchone()[0]
    conn.close()
    return totalPlayersInTournament


def deletePlayersInTournament(tournamentId):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM Players WHERE Tournament_Id=%s", [tournamentId])
    conn.commit()
    conn.close()


def playerStandings(tournamentId):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT Player_Id, PlayerName, Wins, Matches
                FROM StatsByTournament WHERE Tournament_Id='%s'""",
              [tournamentId])
    playerStandings = c.fetchall()
    conn.close()
    return playerStandings


def reportMatch(player1Id, player2Id, result):
    """Records the outcome of a single match between two players.
    Args:
      player1Id:  the id number of the player #1
      player2Id:  the id number of the player #2
      result: result of the match (0=draw, 1=Player1 won, 2=Player2 won)
    """
    if player1Id == player2Id:
        """ A bye game, store it as draw in the DB """
        result = 0
    else:
        minId = min(player1Id, player2Id)
        if (player2Id == minId):
            """ invert the players' ids, in order to complain P1Id < p2Id
                this makes work the UNIQUE constraint of the table Matches"""
            player2Id = player1Id
            player1Id = minId
            """ Exchange result when it's not a draw """
            if (result != 0):
                result = 2 if (result == 1) else 1
    conn = connect()
    c = conn.cursor()
    c.execute("""INSERT INTO Matches (Player1_Id, Player2_Id, Result)
                VALUES (%s, %s, %s)""", [player1Id, player2Id, result])
    conn.commit()
    conn.close()


def swissPairings(tournamentId):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
    """ Based on the non-repeated and still possible pairings
        returned by the Opponents view """
    c.execute("""SELECT Player1_Id, Player1Name, Player2_Id, Player2Name
                FROM Opponents WHERE Tournament_Id='%s'""",
              [tournamentId])
    unplayedPairs = c.fetchall()
    """ Get if there's odd number of players in that tournament """
    c.execute("""SELECT (totalPlayers%%2=1) AS odd
                FROM CountPlayersByTournament WHERE Tournament_Id='%s'""",
              [tournamentId])
    isOddPlayers = c.fetchone()[0]
    swissPairs = []
    foundPlayers = []
    if isOddPlayers:
        """ If there's a odd number of players,
            search for the lowest ranked 'bye' """
        for (p1Id, p1Name, p2Id, p2Name) in reversed(unplayedPairs):
            if p1Id == p2Id:
                bye = [p1Id, p1Name, p2Id, p2Name]
                foundPlayers.append(p1Id)
                break
    for (p1Id, p1Name, p2Id, p2Name) in unplayedPairs:
        """ Find the unique pairs """
        if (p1Id != p2Id and
           (p1Id not in foundPlayers and p2Id not in foundPlayers)):
            swissPairs.append([p1Id, p1Name, p2Id, p2Name])
            foundPlayers.append(p1Id)
            foundPlayers.append(p2Id)
    if isOddPlayers:
        """ Append the 'bye' to the pairs """
        swissPairs.append(bye)
    conn.commit()
    conn.close()
    return swissPairs
