"""Tests for state update logic."""

import unittest
import uuid

from runthroughlinehackathor.action_selection.action_list import action_list
from runthroughlinehackathor.action_selection.random_events_list import (
    random_events,
)
from runthroughlinehackathor.action_selection.random_events_list import (
    reactions,
)
from runthroughlinehackathor.models.gender import Gender
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.models.state import State
from runthroughlinehackathor.settings import settings
from runthroughlinehackathor.state_update.apply_action import apply_action
from runthroughlinehackathor.state_update.state_increment import StateIncrement
from runthroughlinehackathor.state_update.update_state import update_state


class TestApplyAction(unittest.TestCase):
    """Test cases for apply_action function."""

    def setUp(self):
        """Set up test fixtures using action_list values."""
        self.test_id = uuid.uuid4()
        self.initial_params = Parameters(
            career=20, relations=20, health=100, money=20
        )
        self.test_action = action_list[0]
        self.random_event = random_events[0]

    def test_apply_action_adds_to_history(self):
        """Test that apply_action adds action to state history."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        apply_action(state, self.test_action)

        self.assertEqual(len(state.history), 1)
        self.assertEqual(state.history[0], self.test_action)

    def test_apply_action_updates_parameters(self):
        """Test that apply_action updates state parameters correctly."""
        state = State(
            id=self.test_id,
            parameters=Parameters(
                career=20, relations=20, health=100, money=20
            ),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        initial_params = state.parameters.model_copy()
        apply_action(state, self.test_action)

        expected_params = initial_params + self.test_action.parameter_change
        self.assertEqual(state.parameters, expected_params)

    def test_apply_action_multiple_times(self):
        """Test applying multiple actions sequentially."""
        state = State(
            id=self.test_id,
            parameters=Parameters(
                career=20, relations=20, health=100, money=20
            ),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action1 = action_list[0]
        action2 = action_list[1]

        apply_action(state, action1)
        apply_action(state, action2)

        self.assertEqual(len(state.history), 2)
        self.assertEqual(state.history[0], action1)
        self.assertEqual(state.history[1], action2)

    def test_apply_action_with_negative_parameter_change(self):
        """Test applying action with negative parameter changes."""
        state = State(
            id=self.test_id,
            parameters=Parameters(
                career=50, relations=50, health=100, money=50
            ),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        # Find an action with negative parameter changes if it exists
        negative_action = next(
            (
                action
                for action in action_list
                if any(
                    [
                        action.parameter_change.career < 0,
                        action.parameter_change.relations < 0,
                        action.parameter_change.health < 0,
                        action.parameter_change.money < 0,
                    ]
                )
            ),
            action_list[0],  # fallback to first action
        )

        initial_params = state.parameters.model_copy()
        apply_action(state, negative_action)

        expected_params = initial_params + negative_action.parameter_change
        self.assertEqual(state.parameters, expected_params)


class TestUpdateState(unittest.IsolatedAsyncioTestCase):
    """Test cases for update_state function."""

    def setUp(self):
        """Set up test fixtures using action_list values."""
        self.test_id = uuid.uuid4()
        self.initial_params = Parameters(
            career=20, relations=20, health=100, money=20
        )
        self.random_event = random_events[0]

    async def test_update_state_increments_game_turn(self):
        """Test that update_state increments game_turn."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        # Select actions with total time cost <= time_pre_turn
        chosen_actions = [
            action
            for action in action_list
            if action.time_cost <= settings.small_action_max_cost
        ][:2]
        action_names = [a.name for a in chosen_actions]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        self.assertEqual(state.game_turn, 1)

    async def test_update_state_applies_actions(self):
        """Test that update_state applies all chosen actions."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        chosen_actions = [action_list[0], action_list[1]]
        action_names = [a.name for a in chosen_actions]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        # History should contain actions + random_event
        self.assertGreaterEqual(len(state.history), len(chosen_actions))
        for action in chosen_actions:
            self.assertIn(action, state.history)

    async def test_update_state_adds_health_for_remaining_time(self):
        """Test that update_state adds health bonus for remaining time."""
        state = State(
            id=self.test_id,
            parameters=Parameters(
                career=20, relations=20, health=100, money=20
            ),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        # Choose actions with low time cost to leave remaining time
        chosen_actions = [
            action for action in action_list if action.time_cost == 1
        ][
            :2
        ]  # 2 actions with time_cost=1
        action_names = [a.name for a in chosen_actions]

        initial_health = state.parameters.health
        spent_time = sum(a.time_cost for a in chosen_actions)
        remaining_time = settings.time_pre_turn - spent_time

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        # Calculate expected health
        health_from_actions = sum(
            a.parameter_change.health for a in chosen_actions
        )
        expected_health = (
            initial_health
            + health_from_actions
            + remaining_time * settings.health_per_time_spent
        )

        self.assertEqual(state.parameters.health, expected_health)

    async def test_update_state_generates_new_actions(self):
        """Test that update_state generates new big and small actions."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        chosen_actions = [action_list[0], action_list[1]]
        action_names = [a.name for a in chosen_actions]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        self.assertEqual(len(state.big_actions), settings.n_big_actions)
        self.assertEqual(len(state.small_actions), settings.n_small_actions)

    async def test_update_state_assigns_random_event(self):
        """Test that update_state assigns a random event."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action_names = [action_list[0].name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        self.assertIn(state.random_event, random_events)

    async def test_update_state_adds_money_from_career(self):
        """Test that update_state adds money based on career parameter."""
        initial_career = 50
        initial_money = 100
        state = State(
            id=self.test_id,
            parameters=Parameters(
                career=initial_career,
                relations=20,
                health=100,
                money=initial_money,
            ),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=0,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        # Choose action with no money change to isolate career-to-money conversion
        action_with_no_money = next(
            (a for a in action_list if a.parameter_change.money == 0),
            action_list[0],
        )
        action_names = [action_with_no_money.name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        # Calculate expected money: initial + action change + career * coefficient
        expected_money_from_career = (
            initial_career + action_with_no_money.parameter_change.career
        ) * settings.career_to_money_coefficient
        expected_total_money = (
            initial_money
            + action_with_no_money.parameter_change.money
            + expected_money_from_career
        )

        self.assertEqual(state.parameters.money, expected_total_money)

    async def test_update_state_stage_transition_to_second(self):
        """Test that update_state transitions to second stage at correct turn."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.FIRST,
            game_turn=settings.stage_two_step - 1,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action_names = [action_list[0].name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        self.assertEqual(state.current_stage, Stage.SECOND)

    async def test_update_state_stage_transition_to_third(self):
        """Test that update_state transitions to third stage at correct turn."""
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.SECOND,
            game_turn=settings.stage_three_step - 1,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action_names = [action_list[0].name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        self.assertEqual(state.current_stage, Stage.THIRD)

    async def test_update_state_game_finished_male(self):
        """Test that game finishes when male player reaches end age."""
        # Set game_turn such that next turn will exceed end age
        turns_until_end = (
            settings.end_age[Gender.MALE] - settings.initial_age
        ) // settings.years_per_turn
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.THIRD,
            game_turn=turns_until_end - 1,
            gender=Gender.MALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action_names = [action_list[0].name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        if state.age >= settings.end_age[Gender.MALE]:
            self.assertTrue(state.is_game_finished)

    async def test_update_state_game_finished_female(self):
        """Test that game finishes when female player reaches end age."""
        # Set game_turn such that next turn will exceed end age
        turns_until_end = (
            settings.end_age[Gender.FEMALE] - settings.initial_age
        ) // settings.years_per_turn
        state = State(
            id=self.test_id,
            parameters=self.initial_params.model_copy(),
            history=[],
            turn_description="Test",
            current_stage=Stage.THIRD,
            game_turn=turns_until_end - 1,
            gender=Gender.FEMALE,
            name="Test",
            goal="Test",
            big_actions=[],
            small_actions=[],
            random_event=self.random_event,
            stage_summary=None,
        )

        action_names = [action_list[0].name]

        state_update = StateIncrement(
            state_id=self.test_id,
            chosen_action_references=action_names,
        )

        await update_state(state, state_update)

        if state.age >= settings.end_age[Gender.FEMALE]:
            self.assertTrue(state.is_game_finished)


class TestStateIncrement(unittest.TestCase):
    """Test cases for StateIncrement model."""

    def test_state_increment_creation_with_action_names(self):
        """Test creating a StateIncrement with action name references."""
        test_id = uuid.uuid4()
        action_names = [action_list[0].name, action_list[1].name]

        increment = StateIncrement(
            state_id=test_id,
            chosen_action_references=action_names,
        )

        self.assertEqual(increment.state_id, test_id)
        self.assertEqual(len(increment.chosen_actions), 2)
        # Check that actions are resolved correctly
        self.assertEqual(increment.chosen_actions[0], action_list[0])
        self.assertEqual(increment.chosen_actions[1], action_list[1])

    def test_state_increment_with_reaction_ids(self):
        """Test creating a StateIncrement with reaction ID references."""
        test_id = uuid.uuid4()
        reaction_ids = list(reactions.keys())[:2]

        increment = StateIncrement(
            state_id=test_id,
            chosen_action_references=reaction_ids,
        )

        self.assertEqual(increment.state_id, test_id)
        self.assertEqual(len(increment.chosen_actions), 2)
        # Check that reactions are resolved correctly
        self.assertEqual(
            increment.chosen_actions[0], reactions[reaction_ids[0]]
        )
        self.assertEqual(
            increment.chosen_actions[1], reactions[reaction_ids[1]]
        )

    def test_state_increment_with_mixed_references(self):
        """Test StateIncrement with both action names and reaction IDs."""
        test_id = uuid.uuid4()
        action_name = action_list[0].name
        reaction_id = list(reactions.keys())[0]

        increment = StateIncrement(
            state_id=test_id,
            chosen_action_references=[reaction_id, action_name],
        )

        self.assertEqual(increment.state_id, test_id)
        self.assertEqual(len(increment.chosen_actions), 2)
        # Reactions (ints) should be sorted before actions (strings)
        self.assertEqual(increment.chosen_actions[0], reactions[reaction_id])
        self.assertEqual(increment.chosen_actions[1], action_list[0])

    def test_state_increment_with_empty_actions(self):
        """Test creating a StateIncrement with empty actions list."""
        test_id = uuid.uuid4()

        increment = StateIncrement(
            state_id=test_id,
            chosen_action_references=[],
        )

        self.assertEqual(increment.state_id, test_id)
        self.assertEqual(len(increment.chosen_actions), 0)

    def test_chosen_actions_property_returns_tuple(self):
        """Test that chosen_actions property returns a tuple."""
        test_id = uuid.uuid4()
        action_names = [action_list[0].name]

        increment = StateIncrement(
            state_id=test_id,
            chosen_action_references=action_names,
        )

        self.assertIsInstance(increment.chosen_actions, tuple)


if __name__ == "__main__":
    unittest.main()
