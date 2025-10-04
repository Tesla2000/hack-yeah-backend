"""Tests for action selection logic."""

import unittest

from runthroughlinehackathor.action_selection.select_actions import (
    _can_add_action,
)
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.settings import settings


class TestCanAddAction(unittest.TestCase):
    """Test cases for action selection constraints."""

    def setUp(self):
        """Set up test actions."""
        self.small_action_health = Action(
            name="Small Health",
            description="Small health action",
            image_url="https://example.com/small_health.jpg",
            parameter_change=Parameters(
                health=5, career=0, relations=0, money=0
            ),
            type=ActionType.HEALTH,
            time_cost=2,
        )
        self.small_action_career = Action(
            name="Small Career",
            description="Small career action",
            image_url="https://example.com/small_career.jpg",
            parameter_change=Parameters(
                health=0, career=5, relations=0, money=0
            ),
            type=ActionType.CAREER,
            time_cost=3,
        )
        self.big_action_health = Action(
            name="Big Health",
            description="Big health action",
            image_url="https://example.com/big_health.jpg",
            parameter_change=Parameters(
                health=15, career=0, relations=0, money=0
            ),
            type=ActionType.HEALTH,
            time_cost=5,
        )
        self.big_action_relations = Action(
            name="Big Relations",
            description="Big relations action",
            image_url="https://example.com/big_relations.jpg",
            parameter_change=Parameters(
                health=0, career=0, relations=15, money=0
            ),
            type=ActionType.RELATIONS,
            time_cost=4,
        )
        self.action_money = Action(
            name="Money Action",
            description="Money action",
            image_url="https://example.com/money.jpg",
            parameter_change=Parameters(
                health=0, career=0, relations=0, money=10
            ),
            type=ActionType.MONEY,
            time_cost=3,
        )

    def test_cannot_add_duplicate_action(self):
        """Test that the same action cannot be added twice."""
        chosen = [self.small_action_health]
        result = _can_add_action(self.small_action_health, chosen)
        self.assertFalse(result)

    def test_can_add_different_action(self):
        """Test that different actions can be added."""
        chosen = [self.small_action_health]
        result = _can_add_action(self.small_action_career, chosen)
        self.assertTrue(result)

    def test_cannot_exceed_small_actions_limit(self):
        """Test that we cannot exceed the small actions limit."""
        # Create 5 small actions (the limit according to settings.n_small_actions)
        small_actions = [
            Action(
                name=f"Small {i}",
                description=f"Small action {i}",
                image_url=f"https://example.com/small{i}.jpg",
                parameter_change=Parameters(
                    health=1, career=1, relations=1, money=1
                ),
                type=[
                    ActionType.HEALTH,
                    ActionType.CAREER,
                    ActionType.RELATIONS,
                    ActionType.MONEY,
                ][
                    i % 4
                ],  # Rotate through types
                time_cost=2,
            )
            for i in range(settings.n_small_actions)
        ]

        # Try to add one more small action
        new_small_action = Action(
            name="Extra Small",
            description="One too many",
            image_url="https://example.com/extra.jpg",
            parameter_change=Parameters(
                health=1, career=0, relations=0, money=0
            ),
            type=ActionType.HEALTH,
            time_cost=2,
        )

        result = _can_add_action(new_small_action, small_actions)
        self.assertFalse(result)

    def test_cannot_exceed_big_actions_limit(self):
        """Test that we cannot exceed the big actions limit."""
        # Create 3 big actions (the limit according to settings.n_big_actions)
        big_actions = [
            Action(
                name=f"Big {i}",
                description=f"Big action {i}",
                image_url=f"https://example.com/big{i}.jpg",
                parameter_change=Parameters(
                    health=10, career=10, relations=10, money=10
                ),
                type=[
                    ActionType.HEALTH,
                    ActionType.CAREER,
                    ActionType.RELATIONS,
                    ActionType.MONEY,
                ][i % 4],
                time_cost=5,
            )
            for i in range(settings.n_big_actions)
        ]

        # Try to add one more big action
        new_big_action = Action(
            name="Extra Big",
            description="One too many",
            image_url="https://example.com/extra_big.jpg",
            parameter_change=Parameters(
                health=10, career=0, relations=0, money=0
            ),
            type=ActionType.HEALTH,
            time_cost=5,
        )

        result = _can_add_action(new_big_action, big_actions)
        self.assertFalse(result)

    def test_must_have_all_action_types(self):
        """Test that all action types must be represented."""
        # Create 7 actions all of type HEALTH (missing other types)
        chosen = [
            Action(
                name=f"Health {i}",
                description=f"Health action {i}",
                image_url=f"https://example.com/health{i}.jpg",
                parameter_change=Parameters(
                    health=5, career=0, relations=0, money=0
                ),
                type=ActionType.HEALTH,
                time_cost=2 if i < 5 else 4,
            )
            for i in range(7)
        ]

        # Try to add another HEALTH action when we need other types
        another_health = Action(
            name="More Health",
            description="Another health action",
            image_url="https://example.com/more_health.jpg",
            parameter_change=Parameters(
                health=5, career=0, relations=0, money=0
            ),
            type=ActionType.HEALTH,
            time_cost=2,
        )

        result = _can_add_action(another_health, chosen)
        # Should return False because we need other types and only have 1 slot left
        self.assertFalse(result)

    def test_valid_mix_of_actions(self):
        """Test a valid mix of small and big actions with all types."""
        chosen = [
            # 2 big actions
            self.big_action_health,
            self.big_action_relations,
            # 3 small actions
            self.small_action_health,
            self.small_action_career,
            self.action_money,
        ]

        # Adding another small action of different type should work
        new_small = Action(
            name="Small Relations",
            description="Small relations action",
            image_url="https://example.com/small_relations.jpg",
            parameter_change=Parameters(
                health=0, career=0, relations=5, money=0
            ),
            type=ActionType.RELATIONS,
            time_cost=2,
        )

        result = _can_add_action(new_small, chosen)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
