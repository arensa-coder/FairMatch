"""Tests for FairMatcher."""
import pytest
from fairmatch import FairMatcher


def test_basic_pairing():
    matcher = FairMatcher(["Alice", "Bob", "Charlie", "Dave"])
    rounds = matcher.generate_round()
    assert len(rounds) == 3  # n-1 rounds for 4 players


def test_each_pair_appears_once():
    participants = ["A", "B", "C", "D"]
    matcher = FairMatcher(participants)
    rounds = matcher.generate_round()
    all_pairs = [pair for round_ in rounds for pair in round_]
    pair_set = set(frozenset(p) for p in all_pairs)
    assert len(pair_set) == len(all_pairs)  # no duplicate pairings


def test_minimum_participants():
    matcher = FairMatcher(["A", "B"])
    rounds = matcher.generate_round()
    assert rounds == [[("A", "B")]]


def test_too_few_participants():
    with pytest.raises(ValueError):
        FairMatcher(["Solo"])


def test_odd_number_of_participants():
    matcher = FairMatcher(["A", "B", "C"])
    rounds = matcher.generate_round()
    assert len(rounds) > 0
