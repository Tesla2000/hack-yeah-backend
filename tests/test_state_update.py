"""Tests for state update logic."""

import unittest
import uuid

from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_increment import StateIncrement
from runthroughlinehackathor.state_update.update_state import update_state


class TestApplyAction(unittest.TestCase):
    """Test cases for applying actions to state."""

    def setUp(self):
        """Set up test state."""
        self.state = State(
            id=uuid.uuid4(),
            parameters=Parameters(
                health=100, career=20, relations=20, money=20
            ),
            history=[],
            turn_descriptions=["Initial state"],
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            goal="Test goal",
        )

    def test_apply_action_updates_parameters(self):
        """Test that applying an action updates parameters correctly."""
        action = Action(
            name="Study",
            description="Study for exam",
            image_url="https://example.com/study.jpg",
            parameter_change=Parameters(
                health=-5, career=15, relations=0, money=0
            ),
            type=ActionType.CAREER,
            time_cost=3,
        )

        apply_action(self.state, action)

        self.assertEqual(self.state.parameters.health, 95)
        self.assertEqual(self.state.parameters.career, 35)
        self.assertEqual(len(self.state.history), 1)
        self.assertEqual(self.state.history[0], action)

    def test_apply_multiple_actions(self):
        """Test applying multiple actions sequentially."""
        action1 = Action(
            name="Exercise",
            description="Go to gym",
            image_url="https://example.com/gym.jpg",
            parameter_change=Parameters(
                health=10, career=0, relations=0, money=-5
            ),
            type=ActionType.HEALTH,
            time_cost=2,
        )
        action2 = Action(
            name="Network",
            description="Attend networking event",
            image_url="https://example.com/network.jpg",
            parameter_change=Parameters(
                health=0, career=5, relations=10, money=0
            ),
            type=ActionType.RELATIONS,
            time_cost=3,
        )

        apply_action(self.state, action1)
        apply_action(self.state, action2)

        self.assertEqual(self.state.parameters.health, 110)
        self.assertEqual(self.state.parameters.career, 25)
        self.assertEqual(self.state.parameters.relations, 30)
        self.assertEqual(self.state.parameters.money, 15)
        self.assertEqual(len(self.state.history), 2)


class TestUpdateState(unittest.TestCase):
    """Test cases for full state update logic."""

    def setUp(self):
        """Set up test state."""
        self.state = State(
            id=uuid.uuid4(),
            parameters=Parameters(
                health=100, career=20, relations=20, money=20
            ),
            history=[],
            turn_descriptions=["Initial state"],
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            goal="Test goal",
        )

    def test_update_state_with_remaining_time_bonus(self):
        """Test that remaining time converts to health bonus."""
        action = Action(
            name="Quick task",
            description="Do a quick task",
            image_url="https://example.com/task.jpg",
            parameter_change=Parameters(
                health=0, career=10, relations=0, money=0
            ),
            type=ActionType.CAREER,
            time_cost=3,
        )

        state_increment = StateIncrement(
            state_id=self.state.id, chosen_actions=[action]
        )

        update_state(self.state, state_increment)

        # Health should be: 100 (initial) + 0 (action) + 7 (remaining time: 10-3)
        self.assertEqual(self.state.parameters.health, 107)
        self.assertEqual(self.state.parameters.career, 30)

    def test_update_state_with_multiple_actions(self):
        """Test state update with multiple actions consuming all time."""
        actions = [
            Action(
                name=f"Action {i}",
                description=f"Description {i}",
                image_url=f"https://example.com/action{i}.jpg",
                parameter_change=Parameters(
                    health=0, career=2, relations=0, money=0
                ),
                type=ActionType.CAREER,
                time_cost=2,
            )
            for i in range(5)
        ]

        state_increment = StateIncrement(
            state_id=self.state.id, chosen_actions=actions
        )

        update_state(self.state, state_increment)

        # Total time: 5 actions * 2 = 10, remaining = 0
        self.assertEqual(self.state.parameters.health, 100)
        self.assertEqual(self.state.parameters.career, 30)
        self.assertEqual(len(self.state.history), 5)


if __name__ == "__main__":
    unittest.main()
