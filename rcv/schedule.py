from .ballot import BallotSet
from .candidate import Candidate
from .values_dict import ValuesDict


class PreferenceSchedule:
    """A reduced preference schedule"""

    def __init__(self, ballots, candidates=None):
        if candidates is None:
            names = {name for ballot, weight in ballots for name in ballot}
            candidates = {Candidate(name) for name in names}
        self.candidates = ValuesDict(
            {str(candidate): candidate for candidate in candidates}
        )
        self.distribute_ballots(ballots)
        self.total_votes = sum(candidate.total_votes for candidate in self.candidates)

    def __iter__(self):
        return self.ballots

    @property
    def ballots(self):
        for candidate in self.candidates:
            for ballot in candidate.votes:
                yield ballot

    def remove_candidate(self, removed):
        for candidate in self.candidates:
            if candidate is not removed:
                candidate.votes = candidate.votes.eliminate(removed)
        removed.votes = BallotSet()
        del self.candidates[str(removed)]

    def distribute_ballots(self, ballots):
        for ballot, weight in ballots:
            if not ballot.is_empty:
                candidate = self.candidates[ballot.top_choice]
                candidate.votes.add(ballot, weight)

    def eliminate(self, eliminated):
        self.distribute_ballots(eliminated.votes.eliminate(eliminated))
        self.remove_candidate(eliminated)

    @classmethod
    def from_dataframe(cls, df):
        """Create a preference schedule from a dataframe whose rows are ballots.
        That is, the first column is the first-ranked candidate for each ballot,
        the second is the second-ranked candidate, and so on."""
        grouped_ballots = df.groupby(list(df.columns)).size().items()

        ballots = BallotSet(grouped_ballots)

        return cls(ballots)
