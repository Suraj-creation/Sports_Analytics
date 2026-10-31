"""Doubles partner service order, separate from team rally-point scoring.

Opening server/receiver must be supplied explicitly. A new game requires a new
selection; neither court side nor tracker numbering determines the serving pair.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DoublesServiceOrder:
    teams: dict[str, tuple[str, str]]
    right: dict[str, str]
    score: dict[str, int]
    serving_team: str

    @classmethod
    def seed(
        cls, teams: dict[str, tuple[str, str]], server: str, receiver: str, score: dict[str, int]
    ) -> DoublesServiceOrder:
        if (
            set(teams) != {"P1", "P2"}
            or any(len(pair) != 2 for pair in teams.values())
            or len(set(person for pair in teams.values() for person in pair)) != 4
            or any(not isinstance(person, str) or not person for pair in teams.values() for person in pair)
            or set(score) != {"P1", "P2"}
            or any(type(value) is not int or not 0 <= value <= 30 for value in score.values())
        ):
            raise ValueError("four distinct team members and valid team points required")
        serving = next((slot for slot, pair in teams.items() if server in pair), None)
        receiving = next((slot for slot, pair in teams.items() if receiver in pair), None)
        if serving is None or receiving is None or serving == receiving:
            raise ValueError("server and receiver must belong to opposing teams")
        right = {}
        for slot, person in ((serving, server), (receiving, receiver)):
            partner = next(member for member in teams[slot] if member != person)
            right[slot] = person if score[serving] % 2 == 0 else partner
        return cls({slot: tuple(pair) for slot, pair in teams.items()}, right, dict(score), serving)

    @property
    def court(self) -> str:
        return "right" if self.score[self.serving_team] % 2 == 0 else "left"

    def occupant(self, slot: str) -> str:
        return (
            self.right[slot]
            if self.court == "right"
            else next(person for person in self.teams[slot] if person != self.right[slot])
        )

    @property
    def server(self) -> str:
        return self.occupant(self.serving_team)

    @property
    def receiver(self) -> str:
        return self.occupant("P2" if self.serving_team == "P1" else "P1")

    def point(self, winner: str) -> DoublesServiceOrder:
        if winner not in self.teams or self.score[winner] >= 30:
            raise ValueError("valid next rally winner required")
        score, right = dict(self.score), dict(self.right)
        score[winner] += 1
        if winner == self.serving_team:
            right[winner] = next(person for person in self.teams[winner] if person != right[winner])
        return DoublesServiceOrder(self.teams, right, score, winner)

    def to_public(self) -> dict:
        return {
            "status": "known",
            "server_participant_id": self.server,
            "receiver_participant_id": self.receiver,
            "serving_team": self.serving_team,
            "service_court": self.court,
            "score": dict(self.score),
            "right_court_occupants": dict(self.right),
        }
