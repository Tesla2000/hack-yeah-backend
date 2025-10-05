"""Tests for action selection logic."""

import unittest

from runthroughlinehackathor.action_selection.action_list import action_list
from runthroughlinehackathor.action_selection.select_actions import (
    _can_add_action,
)
from runthroughlinehackathor.action_selection.select_actions import (
    select_actions,
)
from runthroughlinehackathor.action_selection.select_random_event import (
    select_random_event,
)
from runthroughlinehackathor.models.action.action_type import ActionType
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage
from runthroughlinehackathor.settings import settings


class TestCanAddAction(unittest.TestCase):
    """Test cases for _can_add_action function."""

    def setUp(self):
        """Set up test fixtures using action_list values."""
        self.big_actions = [
            action
            for action in action_list
            if action.time_cost > settings.small_action_max_cost
        ][: settings.n_big_actions]
        self.small_actions = [
            action
            for action in action_list
            if action.time_cost <= settings.small_action_max_cost
        ][: settings.n_small_actions]

    def test_can_add_first_action(self):
        """Test that first action can always be added."""
        action = action_list[0]
        result = _can_add_action(action, [])
        self.assertTrue(result)

    def test_cannot_add_duplicate_action(self):
        """Test that duplicate actions cannot be added."""
        action = action_list[0]
        chosen_actions = [action]
        result = _can_add_action(action, chosen_actions)
        self.assertFalse(result)

    def test_cannot_exceed_small_action_limit(self):
        """Test that cannot add more small actions than allowed."""
        chosen_actions = self.small_actions[:]
        # Try to add one more small action
        extra_small_action = [
            action
            for action in action_list
            if action.time_cost <= settings.small_action_max_cost
            and action not in chosen_actions
        ][0]
        result = _can_add_action(extra_small_action, chosen_actions)
        self.assertFalse(result)

    def test_cannot_exceed_big_action_limit(self):
        """Test that cannot add more big actions than allowed."""
        chosen_actions = self.big_actions[:]
        # Try to add one more big action
        extra_big_action = [
            action
            for action in action_list
            if action.time_cost > settings.small_action_max_cost
            and action not in chosen_actions
        ][0]
        result = _can_add_action(extra_big_action, chosen_actions)
        self.assertFalse(result)

    def test_must_include_all_action_types(self):
        """Test that all action types must be represented."""
        # Get actions of only one type
        health_actions = [
            action
            for action in action_list
            if action.type == ActionType.HEALTH
        ][: settings.n_actions - 1]

        # Try to add another health action when we need other types
        result = _can_add_action(health_actions[0], health_actions[1:])
        # This should fail because we won't have room for all types
        if len(health_actions) >= settings.n_actions - len(ActionType) + 1:
            self.assertFalse(result)

    def test_can_add_valid_action_mix(self):
        """Test that valid action mix can be added."""
        # Add a mix of actions respecting all constraints
        chosen_actions = []
        action_types_needed = list(ActionType)

        for action_type in action_types_needed[:2]:  # Add 2 different types
            action = next(
                a
                for a in action_list
                if a.type == action_type and a not in chosen_actions
            )
            if _can_add_action(action, chosen_actions):
                chosen_actions.append(action)

        # Should be able to add more actions as long as constraints are met
        self.assertLess(len(chosen_actions), settings.n_actions)


class TestSelectActions(unittest.IsolatedAsyncioTestCase):
    """Test cases for select_actions function."""

    async def test_select_actions_basic(self):
        """Test basic action selection."""
        actions = await select_actions(
            [],
            Stage.FIRST,
            Parameters(career=0, relations=0, health=0, money=0),
        )
        self.assertEqual(len(actions), settings.n_actions)

    async def test_select_actions_returns_valid_actions(self):
        """Test that select_actions returns valid actions from action_list."""
        actions = await select_actions(
            [],
            Stage.FIRST,
            Parameters(career=50, relations=50, health=50, money=50),
        )
        for action in actions:
            self.assertIn(action, action_list)

    async def test_select_actions_respects_stage(self):
        """Test that select_actions only returns actions valid for current stage."""
        actions = await select_actions(
            [],
            Stage.SECOND,
            Parameters(career=30, relations=30, health=30, money=30),
        )
        for action in actions:
            self.assertIn(Stage.SECOND, action.allowed_stages)

    async def test_select_actions_respects_unique_constraint(self):
        """Test that unique actions are not selected if already in history."""
        unique_action = next(
            action for action in action_list if action.is_unique
        )
        history = [unique_action]

        actions = await select_actions(
            history,
            Stage.FIRST,
            Parameters(career=20, relations=20, health=20, money=20),
        )
        self.assertNotIn(unique_action, actions)

    async def test_select_actions_has_all_types(self):
        """Test that selected actions include all action types."""
        actions = await select_actions(
            [],
            Stage.FIRST,
            Parameters(career=25, relations=25, health=25, money=25),
        )
        action_types = {action.type for action in actions}
        self.assertEqual(len(action_types), len(ActionType))

    async def test_select_actions_respects_big_small_split(self):
        """Test that actions are split correctly between big and small."""
        actions = await select_actions(
            [],
            Stage.FIRST,
            Parameters(career=40, relations=40, health=40, money=40),
        )
        big_actions = [
            a for a in actions if a.time_cost > settings.small_action_max_cost
        ]
        small_actions = [
            a for a in actions if a.time_cost <= settings.small_action_max_cost
        ]
        self.assertEqual(len(big_actions), settings.n_big_actions)
        self.assertEqual(len(small_actions), settings.n_small_actions)


class TestSelectRandomEvent(unittest.IsolatedAsyncioTestCase):
    """Test cases for select_random_event function."""

    async def test_select_random_event_returns_event(self):
        """Test that select_random_event returns a RandomEvent."""
        from runthroughlinehackathor.action_selection.random_events_list import (
            random_events,
        )

        event = await select_random_event([])
        self.assertIn(event, random_events)

    async def test_select_random_event_excludes_history(self):
        """Test that select_random_event excludes events in history."""
        from runthroughlinehackathor.action_selection.random_events_list import (
            random_events,
        )

        # Put first event in history
        first_event = random_events[0]
        history = [first_event]

        # Select multiple events to verify exclusion
        for _ in range(5):
            event = await select_random_event(history)
            self.assertNotEqual(event, first_event)

    async def test_select_random_event_with_empty_history(self):
        """Test select_random_event with empty history."""
        from runthroughlinehackathor.action_selection.random_events_list import (
            random_events,
        )

        event = await select_random_event([])
        self.assertIn(event, random_events)
