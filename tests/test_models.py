"""Tests for model classes."""

import unittest
import uuid

from runthroughlinehackathor.action_selection.action_list import action_list
from runthroughlinehackathor.action_selection.random_events_list import (
    random_events,
)
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State


class TestParameters(unittest.TestCase):
    """Test cases for Parameters model."""

    def test_parameters_creation(self):
        """Test creating a Parameters instance."""
        params = Parameters(career=10, relations=20, health=30, money=40)
        self.assertEqual(params.career, 10)
        self.assertEqual(params.relations, 20)
        self.assertEqual(params.health, 30)
        self.assertEqual(params.money, 40)

    def test_parameters_addition(self):
        """Test adding two Parameters instances."""
        params1 = Parameters(career=10, relations=20, health=30, money=40)
        params2 = Parameters(career=5, relations=10, health=15, money=20)
        result = params1 + params2
        self.assertEqual(result.career, 15)
        self.assertEqual(result.relations, 30)
        self.assertEqual(result.health, 45)
        self.assertEqual(result.money, 60)

    def test_parameters_addition_with_negative_values(self):
        """Test adding Parameters with negative values."""
        params1 = Parameters(career=10, relations=20, health=30, money=40)
        params2 = Parameters(career=-5, relations=-10, health=-15, money=-20)
        result = params1 + params2
        self.assertEqual(result.career, 5)
        self.assertEqual(result.relations, 10)
        self.assertEqual(result.health, 15)
        self.assertEqual(result.money, 20)

    def test_parameters_addition_with_zero_values(self):
        """Test adding Parameters with zero values."""
        params1 = Parameters(career=10, relations=20, health=30, money=40)
        params2 = Parameters(career=0, relations=0, health=0, money=0)
        result = params1 + params2
        self.assertEqual(result.career, 10)
        self.assertEqual(result.relations, 20)
        self.assertEqual(result.health, 30)
        self.assertEqual(result.money, 40)


class TestAction(unittest.TestCase):
    """Test cases for Action model using action_list values."""

    def test_action_from_action_list(self):
        """Test that actions from action_list are valid."""
        self.assertGreater(len(action_list), 0)
        for action in action_list:
            self.assertIsInstance(action, Action)
            self.assertIsInstance(action.name, str)
            self.assertIsInstance(action.type, ActionType)
            self.assertGreater(action.time_cost, 0)
            self.assertLessEqual(action.time_cost, 5)
            self.assertIsInstance(action.is_unique, bool)
            self.assertIsInstance(action.parameter_change, Parameters)

    def test_action_allowed_stages(self):
        """Test that action allowed_stages are valid Stage values."""
        for action in action_list:
            for stage in action.allowed_stages:
                self.assertIn(stage, [Stage.FIRST, Stage.SECOND, Stage.THIRD])

    def test_action_types_exist(self):
        """Test that all ActionTypes are represented in action_list."""
        action_types = {action.type for action in action_list}
        self.assertEqual(len(action_types), len(ActionType))

    def test_unique_actions_exist(self):
        """Test that some unique actions exist in action_list."""
        unique_actions = [action for action in action_list if action.is_unique]
        self.assertGreater(len(unique_actions), 0)

    def test_non_unique_actions_exist(self):
        """Test that some non-unique actions exist in action_list."""
        non_unique_actions = [
            action for action in action_list if not action.is_unique
        ]
        self.assertGreater(len(non_unique_actions), 0)


class TestRandomEvent(unittest.TestCase):
    """Test cases for RandomEvent model using random_events values."""

    def test_random_events_from_list(self):
        """Test that random events from random_events_list are valid."""
        self.assertGreater(len(random_events), 0)
        for event in random_events:
            self.assertIsInstance(event.name, str)
            self.assertIsInstance(event.description, str)
            self.assertEqual(len(event.reactions), 2)

    def test_random_event_reactions_have_parameter_changes(self):
        """Test that reactions in random events have parameter changes."""
        for event in random_events:
            for reaction in event.reactions:
                self.assertIsInstance(reaction.parameter_change, Parameters)
                self.assertIsInstance(reaction.description, str)


class TestState(unittest.TestCase):
    """Test cases for State model."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_id = uuid.uuid4()
        self.test_params = Parameters(
            career=20, relations=20, health=100, money=20
        )
        self.test_action = action_list[0]
        self.test_random_event = random_events[0]

    def test_state_creation(self):
        """Test creating a State instance."""
        state = State(
            id=self.test_id,
            parameters=self.test_params,
            history=[],
            turn_description="Test description",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test Player",
            goal="Test goal",
            big_actions=[],
            small_actions=[],
            random_event=self.test_random_event,
            stage_summary=None,
        )
        self.assertEqual(state.id, self.test_id)
        self.assertEqual(state.parameters, self.test_params)
        self.assertEqual(len(state.history), 0)
        self.assertEqual(state.current_stage, Stage.FIRST)
        self.assertEqual(state.game_turn, 0)
        self.assertEqual(state.gender, Gender.MALE)

    def test_state_age_computation(self):
        """Test age computation from game_turn."""
        from runthroughlinehackathor.settings import settings

        state = State(
            id=self.test_id,
            parameters=self.test_params,
            history=[],
            turn_description="Test description",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test Player",
            goal="Test goal",
            big_actions=[],
            small_actions=[],
            random_event=self.test_random_event,
            stage_summary=None,
        )
        expected_age = 0 * settings.years_per_turn + settings.initial_age
        self.assertEqual(state.age, expected_age)

    def test_state_age_computation_multiple_turns(self):
        """Test age computation after multiple turns."""
        from runthroughlinehackathor.settings import settings

        state = State(
            id=self.test_id,
            parameters=self.test_params,
            history=[],
            turn_description="Test description",
            current_stage=Stage.FIRST,
            game_turn=5,
            gender=Gender.FEMALE,
            name="Test Player",
            goal="Test goal",
            big_actions=[],
            small_actions=[],
            random_event=self.test_random_event,
            stage_summary=None,
        )
        expected_age = 5 * settings.years_per_turn + settings.initial_age
        self.assertEqual(state.age, expected_age)

    def test_state_history_with_actions(self):
        """Test state history can contain actions."""
        state = State(
            id=self.test_id,
            parameters=self.test_params,
            history=[self.test_action],
            turn_description="Test description",
            current_stage=Stage.FIRST,
            game_turn=1,
            gender=Gender.MALE,
            name="Test Player",
            goal="Test goal",
            big_actions=[],
            small_actions=[],
            random_event=self.test_random_event,
            stage_summary=None,
        )
        self.assertEqual(len(state.history), 1)
        self.assertEqual(state.history[0], self.test_action)

    def test_state_is_game_finished_default(self):
        """Test that is_game_finished defaults to False."""
        state = State(
            id=self.test_id,
            parameters=self.test_params,
            history=[],
            turn_description="Test description",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test Player",
            goal="Test goal",
            big_actions=[],
            small_actions=[],
            random_event=self.test_random_event,
            stage_summary=None,
        )
        self.assertFalse(state.is_game_finished)


if __name__ == "__main__":
    unittest.main()
