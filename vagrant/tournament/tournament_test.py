#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteTournaments():
    deleteTournaments()
    print "1. Old tournaments can be deleted"


def testDeleteMatches():
    deleteMatches()
    print "2. Old matches can be deleted"


def testDeletePlayers():
    deleteMatches()
    deletePlayers()
    print "3. Player records can be deleted"


def testCountTournaments():
    deleteTournaments()
    c = countTournaments()
    if c == '0':
        raise TypeError(
            "countTournaments() should return numeric zero, not string '0'")
    if c != 0:
        raise ValueError("After deleting, countTournaments should return zero")
    print "4. After deleting, countTournaments() returns zero"


def testRegisterTournament():
    deleteTournaments()
    registerTournament("Tournament #1")
    c = countTournaments()
    if c != 1:
        raise ValueError(
            "After one tournament registers, countTournaments() should be 1")
    print "5. After registering a tournament, countTournaments() returns 1"


def testRegisterCountDeleteTournaments():
    deleteTournaments()
    registerTournament("Tournament #1")
    registerTournament("Tournament #2")
    registerTournament("Tournament #3")
    registerTournament("Tournament #4")
    c = countTournaments()
    if c != 4:
        raise ValueError(
            "After registering four tournaments, countTournaments should be 4")
    deleteTournaments()
    c = countTournaments()
    if c != 0:
        raise ValueError("After deleting, countTournaments should return zero")
    print "6. Tournaments can be registered and deleted"


def testRegisterPlayerInTournament():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Chandra Nalaar")
    c = countPlayersInTournament(t)
    if c != 1:
        raise ValueError("After one player registers,"
                         "countPlayersInTournament() should be 1")
    print ("7. After registering a player in a tournament,"
           "countPlayersInTournament() returns 1")


def testRegisterCountDeletePlayersInTournament():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Markov Chaney")
    registerPlayerInTournament(t, "Joe Malik")
    registerPlayerInTournament(t, "Mao Tsu-hsi")
    registerPlayerInTournament(t, "Atlanta Hope")
    c = countPlayersInTournament(t)
    if c != 4:
        raise ValueError("After registering four players in a tournament,"
                         "countPlayersInTournament() should be 4")
    deletePlayersInTournament(t)
    c = countPlayersInTournament(t)
    if c != 0:
        raise ValueError("After deleting, countPlayersInTournament()"
                         "should return zero")
    print "8. Players in tournaments can be registered and deleted"


def testStandingsBeforeMatches():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Melpomene Murray")
    registerPlayerInTournament(t, "Randy Schwartz")
    standings = playerStandings(t)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before"
                         "they have played any matches")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError(
                "Registered players' names should appear in standings,"
                "even if they have no matches played")
    print "9. Newly registered players appear in the standings with no matches"


def testOddStandingsBeforeMatches():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Melpomene Murray")
    registerPlayerInTournament(t, "Randy Schwartz")
    registerPlayerInTournament(t, "Odd Player")
    standings = playerStandings(t)
    if len(standings) < 3:
        raise ValueError("Players should appear in playerStandings even before"
                         "they have played any matches")
    elif len(standings) > 3:
        raise ValueError("Only registered players should appear in standings")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns")
    [(id1, name1, wins1, matches1),
     (id2, name2, wins2, matches2),
     (id3, name3, wins3, matches3)] = standings
    if (matches1 != 0 or matches2 != 0 or matches3 != 0 or
       wins1 != 0 or wins2 != 0 or wins3 != 0):
            raise ValueError(
                "Newly registered players should have no matches or wins.")
    if (set([name1, name2, name3]) !=
       set(["Melpomene Murray", "Randy Schwartz", "Odd Player"])):
            raise ValueError(
                "Registered players' names should appear in standings,"
                "even if they have no matches played")
    print "10. New registered players appear in the standings with no matches"


def testReportMatches():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Bruno Walton")
    registerPlayerInTournament(t, "Boots O'Neal")
    registerPlayerInTournament(t, "Cathy Burton")
    registerPlayerInTournament(t, "Diane Grant")
    standings = playerStandings(t)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4, 1)
    standings = playerStandings(t)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded")
    print "11. After a match, players have updated standings"


def testPairings():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Twilight Sparkle")
    registerPlayerInTournament(t, "Fluttershy")
    registerPlayerInTournament(t, "Applejack")
    registerPlayerInTournament(t, "Pinkie Pie")
    standings = playerStandings(t)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4, 1)
    pairings = swissPairings(t)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired")
    print "12. After one match, players with one win are paired"


def testOddPairings():
    deleteTournaments()
    t = registerTournament("Tournament #1")
    registerPlayerInTournament(t, "Twilight Sparkle")
    registerPlayerInTournament(t, "Fluttershy")
    registerPlayerInTournament(t, "Applejack")
    registerPlayerInTournament(t, "Pinkie Pie")
    registerPlayerInTournament(t, "Odd Player")
    standings = playerStandings(t)
    [id1, id2, id3, id4, id5] = [row[0] for row in standings]
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4, 1)
    reportMatch(id5, id5, 0)
    standings = playerStandings(t)
    pairings = swissPairings(t)
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return three pairs")
    [(pid1, pname1, pid2, pname2),
        (pid3, pname3, pid4, pname4),
        (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set([frozenset([id1, id3]),
                        frozenset([id2, id5]),
                        frozenset([id4, id4])])
    actual_pairs = set([frozenset([pid1, pid2]),
                        frozenset([pid3, pid4]),
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with higher wins should be paired")
    print "13. After one match, players with higher wins are paired"


if __name__ == '__main__':
    testDeleteTournaments()
    testDeleteMatches()
    testDeletePlayers()
    testCountTournaments()
    testRegisterTournament()
    testRegisterCountDeleteTournaments()
    testRegisterPlayerInTournament()
    testRegisterCountDeletePlayersInTournament()
    testStandingsBeforeMatches()
    testOddStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testOddPairings()
    deleteTournaments()
    print "Success!  All tests pass!"
