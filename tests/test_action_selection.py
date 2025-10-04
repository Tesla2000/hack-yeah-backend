"""Tests for action selection logic."""

import unittest

from runthroughlinehackathor.action_selection.select_actions import (
    select_actions,
)
from runthroughlinehackathor.models.parameters import Parameters
from runthroughlinehackathor.models.stage import Stage


class TestCanAddAction(unittest.IsolatedAsyncioTestCase):
    """Test cases for action selection constraints."""

    async def test_action_selection(self):
        await select_actions(
            [],
            Stage.FIRST,
            Parameters(career=0, relations=0, health=0, money=0),
        )
