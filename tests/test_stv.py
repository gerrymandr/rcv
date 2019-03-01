import pytest

from rcv.schedule import PreferenceSchedule
from rcv.stv import FractionalSTV, droop_quota, find_winners
from rcv.ballot import BallotSet
from fractions import Fraction


@pytest.fixture
def stv(ballots):
    schedule = PreferenceSchedule(ballots)
    return FractionalSTV(schedule, seats=2)


def test_find_winners(candidates):
    winners = find_winners(candidates, 20)
    assert {winner.name for winner in winners} == {"Kamala", "Amy"}

    winners = find_winners(candidates, 21)
    assert {winner.name for winner in winners} == {"Amy"}


def test_droop_quota():
    quota = droop_quota(number_of_votes=61, number_of_seats=2)
    assert quota == 21


class TestFractionalSTV:
    def test_elect(self, ballots):
        stv = FractionalSTV(ballots, seats=2, quota=droop_quota)
        winners = stv.elect()
        assert list(winners) == ["Amy", "Kamala"]

    def test_can_find_candidates_from_ballots(self, stv):
        assert len(stv.candidates) == 3
        assert set(candidate.name for candidate in stv.candidates) == {
            "Amy",
            "Elizabeth",
            "Kamala",
        }

    def test_declare_winner(self, stv):
        amy = stv.candidates["Amy"]
        kamala = stv.candidates["Kamala"]

        stv.declare_winner(amy)

        assert amy.votes.is_empty
        assert amy in stv.elected
        assert amy not in stv.candidates

        assert kamala.total_votes > 20

    def test_transferable_votes(self, stv):
        quota = stv.quota
        candidate = stv.candidates["Amy"]
        transferable = stv.transferable_votes(candidate)

        total_votes = candidate.total_votes
        surplus = total_votes - quota
        expected = BallotSet(
            [
                (("Elizabeth", "Kamala"), Fraction(20 * surplus, total_votes)),
                (("Kamala",), Fraction(5 * surplus, total_votes)),
            ]
        )

        print(expected)
        print(transferable)

        assert transferable == expected

    def test_transferable_votes_is_empty_if_less_than_quota(self, ballots):
        quota = 1000
        stv = FractionalSTV(ballots, seats=2, quota=quota)
        transferable = stv.transferable_votes(stv.candidates["Amy"])

        assert transferable.is_empty

    def test_can_pass_in_numerical_quota(self, ballots):
        stv = FractionalSTV(ballots, seats=2, quota=15)
        assert stv.quota == 15
