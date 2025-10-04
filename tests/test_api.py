"""Tests for FastAPI endpoints."""

import unittest
import uuid

from fastapi.testclient import TestClient
from runthroughlinehackathor.auth.dependencies import users_db
from runthroughlinehackathor.main import app
from runthroughlinehackathor.main import user_states


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test client and clear state."""
        self.client = TestClient(app)
        # Clear users and states between tests
        users_db.clear()
        user_states.clear()

    def _register_and_login(
        self,
        username="testuser",
        email="test@example.com",
        password="testpass123",
    ):
        """Helper method to register a user and get an access token."""
        # Register user
        register_response = self.client.post(
            "/register",
            json={"username": username, "email": email, "password": password},
        )
        self.assertEqual(register_response.status_code, 201)

        # Login to get token
        login_response = self.client.post(
            "/token",
            data={"username": username, "password": password},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]
        return token

    def _get_auth_headers(self, token):
        """Get authorization headers with token."""
        return {"Authorization": f"Bearer {token}"}

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], "newuser")
        self.assertEqual(data["email"], "newuser@example.com")
        self.assertFalse(data["disabled"])

    def test_register_duplicate_user(self):
        """Test registering a user with duplicate username."""
        self._register_and_login("testuser", "test@example.com", "password123")

        # Try to register again with same username
        response = self.client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "password": "password456",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        """Test user login."""
        self._register_and_login("testuser", "test@example.com", "password123")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        self._register_and_login("testuser", "test@example.com", "password123")

        response = self.client.post(
            "/token",
            data={"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 401)

    def test_get_current_user(self):
        """Test getting current user info."""
        token = self._register_and_login()

        response = self.client.get(
            "/users/me",
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")

    def test_create_new_game_male(self):
        """Test creating a new game with male gender."""
        token = self._register_and_login()

        response = self.client.post(
            "/create-new-game",
            json={
                "gender": "MALE",
                "goal": "Become a successful entrepreneur",
            },
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["gender"], "MALE")
        self.assertEqual(data["goal"], "Become a successful entrepreneur")
        self.assertEqual(data["game_turn"], 0)
        self.assertEqual(data["current_phase"], 1)
        self.assertEqual(data["parameters"]["health"], 100)
        self.assertEqual(data["parameters"]["career"], 20)
        self.assertEqual(data["parameters"]["relations"], 20)
        self.assertEqual(data["parameters"]["money"], 20)

    def test_create_new_game_female(self):
        """Test creating a new game with female gender."""
        token = self._register_and_login()

        response = self.client.post(
            "/create-new-game",
            json={"gender": "FEMALE", "goal": "Travel the world"},
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["gender"], "FEMALE")
        self.assertEqual(data["goal"], "Travel the world")

    def test_create_new_game_without_auth(self):
        """Test that creating a game without auth fails."""
        response = self.client.post(
            "/create-new-game",
            json={"gender": "MALE", "goal": "Test"},
        )
        self.assertEqual(response.status_code, 401)

    def test_get_my_games(self):
        """Test getting all games for current user."""
        token = self._register_and_login()

        # Create two games
        self.client.post(
            "/create-new-game",
            json={"gender": "MALE", "goal": "Goal 1"},
            headers=self._get_auth_headers(token),
        )
        self.client.post(
            "/create-new-game",
            json={"gender": "FEMALE", "goal": "Goal 2"},
            headers=self._get_auth_headers(token),
        )

        # Get all games
        response = self.client.get(
            "/my-games",
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_next_turn_invalid_state(self):
        """Test next turn with invalid state ID."""
        token = self._register_and_login()
        fake_id = str(uuid.uuid4())

        response = self.client.post(
            "/next-turn",
            json={"state_id": fake_id, "chosen_actions": []},
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 404)

    def test_next_turn_with_actions(self):
        """Test next turn with valid actions."""
        token = self._register_and_login()

        # First create a game
        create_response = self.client.post(
            "/create-new-game",
            json={"gender": "MALE", "goal": "Test goal"},
            headers=self._get_auth_headers(token),
        )
        state_id = create_response.json()["id"]

        # Create valid action data
        action = {
            "name": "Exercise",
            "description": "Go to the gym",
            "image_url": "https://example.com/image.jpg",
            "parameter_change": {
                "health": 10,
                "career": 0,
                "relations": 0,
                "money": 0,
            },
            "type": "health",
            "time_cost": 2,
            "is_unique": False,
        }

        # Update state with action
        response = self.client.post(
            "/next-turn",
            json={"state_id": state_id, "chosen_actions": [action]},
            headers=self._get_auth_headers(token),
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Health should increase: base 100 + action 10 + remaining time (10-2)*1 = 118
        self.assertEqual(data["parameters"]["health"], 118)
        self.assertEqual(len(data["history"]), 1)

    def test_user_cannot_access_other_user_game(self):
        """Test that users can only access their own games."""
        # Create first user and game
        token1 = self._register_and_login(
            "user1", "user1@example.com", "pass1"
        )
        create_response = self.client.post(
            "/create-new-game",
            json={"gender": "MALE", "goal": "User 1 goal"},
            headers=self._get_auth_headers(token1),
        )
        state_id = create_response.json()["id"]

        # Create second user
        token2 = self._register_and_login(
            "user2", "user2@example.com", "pass2"
        )

        # Try to access first user's game
        action = {
            "name": "Exercise",
            "description": "Go to the gym",
            "image_url": "https://example.com/image.jpg",
            "parameter_change": {
                "health": 10,
                "career": 0,
                "relations": 0,
                "money": 0,
            },
            "type": "health",
            "time_cost": 2,
            "is_unique": False,
        }
        response = self.client.post(
            "/next-turn",
            json={"state_id": state_id, "chosen_actions": [action]},
            headers=self._get_auth_headers(token2),
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
