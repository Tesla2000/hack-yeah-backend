"""Tests for data models and validation."""

import unittest
import uuid

from pydantic import ValidationError
from runthroughlinehackathor.models.action.action import Action
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State


class TestParameters(unittest.TestCase):
    """Test cases for Parameters model."""

    def test_parameters_creation(self):
        """Test creating valid Parameters."""
        params = Parameters(health=100, career=50, relations=30, money=40)
        self.assertEqual(params.health, 100)
        self.assertEqual(params.career, 50)
        self.assertEqual(params.relations, 30)
        self.assertEqual(params.money, 40)

    def test_parameters_addition(self):
        """Test adding two Parameters objects."""
        params1 = Parameters(health=100, career=50, relations=30, money=40)
        params2 = Parameters(health=10, career=5, relations=15, money=-10)
        result = params1 + params2
        self.assertEqual(result.health, 110)
        self.assertEqual(result.career, 55)
        self.assertEqual(result.relations, 45)
        self.assertEqual(result.money, 30)

    def test_parameters_negative_values_rejected(self):
        """Test that negative values are rejected."""
        with self.assertRaises(ValidationError):
            Parameters(health=-10, career=50, relations=30, money=40)


class TestAction(unittest.TestCase):
    """Test cases for Action model."""

    def test_action_creation(self):
        """Test creating a valid Action."""
        action = Action(
            name="Study",
            description="Study programming",
            image_url="https://example.com/study.jpg",
            parameter_change=Parameters(
                health=-5, career=15, relations=0, money=0
            ),
            type=ActionType.CAREER,
            time_cost=3,
        )
        self.assertEqual(action.name, "Study")
        self.assertEqual(action.type, ActionType.CAREER)
        self.assertEqual(action.time_cost, 3)
        self.assertFalse(action.is_unique)

    def test_action_time_cost_validation(self):
        """Test that time_cost must be between 1 and 5."""
        # time_cost = 0 should fail (PositiveInt)
        with self.assertRaises(ValidationError):
            Action(
                name="Invalid",
                description="Invalid action",
                image_url="https://example.com/invalid.jpg",
                parameter_change=Parameters(
                    health=0, career=0, relations=0, money=0
                ),
                type=ActionType.CAREER,
                time_cost=0,
            )

        # time_cost = 6 should fail (le=5 constraint)
        with self.assertRaises(ValidationError):
            Action(
                name="Invalid",
                description="Invalid action",
                image_url="https://example.com/invalid.jpg",
                parameter_change=Parameters(
                    health=0, career=0, relations=0, money=0
                ),
                type=ActionType.CAREER,
                time_cost=6,
            )

    def test_action_unique_flag(self):
        """Test unique action flag."""
        action = Action(
            name="Graduate",
            description="Graduate from university",
            image_url="https://example.com/graduate.jpg",
            parameter_change=Parameters(
                health=0, career=50, relations=10, money=0
            ),
            type=ActionType.CAREER,
            time_cost=5,
            is_unique=True,
        )
        self.assertTrue(action.is_unique)


class TestState(unittest.TestCase):
    """Test cases for State model."""

    def test_state_creation(self):
        """Test creating a valid State."""
        state = State(
            id=uuid.uuid4(),
            parameters=Parameters(
                health=100, career=20, relations=20, money=20
            ),
            history=[],
            turn_description=["Starting the game"],
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            goal="Become successful",
        )
        self.assertEqual(state.game_turn, 0)
        self.assertEqual(state.current_stage, Stage.FIRST)
        self.assertEqual(state.gender, Gender.MALE)

    def test_state_age_computation(self):
        """Test that age is computed correctly from game_turn."""
        state = State(
            id=uuid.uuid4(),
            parameters=Parameters(
                health=100, career=20, relations=20, money=20
            ),
            history=[],
            turn_description=["Turn 0"],
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            goal="Test",
        )
        # Age = game_turn * years_per_turn + initial_age
        # With defaults: 0 * 5 + 15 = 15
        self.assertEqual(state.age, 15)

        state.game_turn = 2
        # 2 * 5 + 15 = 25
        self.assertEqual(state.age, 25)

        state.game_turn = 10
        # 10 * 5 + 15 = 65
        self.assertEqual(state.age, 65)


class TestEnums(unittest.TestCase):
    """Test cases for enum types."""

    def test_gender_enum(self):
        """Test Gender enum values."""
        self.assertEqual(Gender.MALE, "MALE")
        self.assertEqual(Gender.FEMALE, "FEMALE")

    def test_phase_enum(self):
        """Test Phase enum values."""
        self.assertEqual(Stage.FIRST, 1)
        self.assertEqual(Stage.SECOND, 2)
        self.assertEqual(Stage.THIRD, 3)

    def test_action_type_enum(self):
        """Test ActionType enum values."""
        self.assertEqual(ActionType.HEALTH, "health")
        self.assertEqual(ActionType.CAREER, "career")
        self.assertEqual(ActionType.RELATIONS, "relations")
        self.assertEqual(ActionType.MONEY, "money")


if __name__ == "__main__":
    unittest.main()
