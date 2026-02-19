"""Fair matching algorithm for pairing participants."""


class FairMatcher:
    """Pairs participants fairly using a round-robin algorithm."""

    def __init__(self, participants):
        if len(participants) < 2:
            raise ValueError("At least 2 participants are required.")
        self.participants = list(participants)

    def generate_round(self):
        """Generate one round of pairings using the circle method."""
        players = self.participants[:]
        if len(players) % 2 != 0:
            players.append(None)  # bye

        n = len(players)
        fixed = players[0]
        rotating = players[1:]
        pairs = []

        for i in range(n - 1):
            current = [fixed] + rotating
            round_pairs = []
            for j in range(n // 2):
                p1, p2 = current[j], current[n - 1 - j]
                if p1 is not None and p2 is not None:
                    round_pairs.append((p1, p2))
            pairs.append(round_pairs)
            rotating = [rotating[-1]] + rotating[:-1]

        return pairs
