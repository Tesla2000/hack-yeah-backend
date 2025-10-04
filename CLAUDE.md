# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

**Start the FastAPI server:**
```bash
python -m runthroughlinehackathor.main
# or
uvicorn runthroughlinehackathor.main:app --reload
```

## Project Setup

- **Python version**: 3.12+
- **Build system**: Poetry (pyproject.toml)
- **Key dependencies**:
  - FastAPI + Uvicorn for API server
  - LangChain + LangChain-OpenAI for LLM integration
  - Pydantic Settings for configuration

## Architecture Overview

This is a turn-based life simulation game API built with FastAPI. The core game loop involves:

1. **State Management**: In-memory storage of game states (runthroughlinehackathor/models/state.py)
2. **Action Selection**: LLM-weighted action selection system (runthroughlinehackathor/action_selection/)
3. **State Updates**: Applying chosen actions and updating game state (runthroughlinehackathor/state_update/)

### Core Game Mechanics

**State System** (runthroughlinehackathor/models/state.py):
- Each state tracks 4 parameters: health, career, relations, money
- State includes: history of actions/events, turn descriptions, current phase (1-3), game turn counter, gender, goal
- Age is computed from game turns (age = game_turn * years_per_turn + initial_age)

**Action Selection Flow** (runthroughlinehackathor/action_selection/select_actions.py):
- Uses GPT-4o-mini to assign weights (1-10) to actions based on current state and history
- Weighted random selection ensures variety while respecting game constraints:
  - Total of 8 actions per turn (configurable via settings.n_actions)
  - Mix of 3 big actions (time_cost > 3) and 5 small actions (time_cost ≤ 3)
  - All 4 action types (health, career, relations, money) must be represented
  - Unique actions can only appear once in history

**Time Constraint System**:
- Each action has a time_cost (1-5 units)
- Total time per turn is 10 units (settings.time_pre_turn)
- Unused time converts to health: health += remaining_time * settings.health_per_time_spent

**State Update Flow** (runthroughlinehackathor/state_update/update_state.py):
1. Apply each chosen action to state (update_state.py calls apply_action.py)
2. Action application: append to history, add parameter_change to current parameters
3. Calculate remaining time and convert to health bonus

### API Endpoints

**POST /create-new-game**
- Input: `{gender: "MALE"|"FEMALE", goal: str}`
- Creates new game state with initial parameters (health=100, others=20)
- Returns: State object with UUID

**POST /next-turn**
- Input: `{state_id: UUID, chosen_actions: Action[]}`
- Validates state exists, applies actions, updates state
- Returns: Updated state object

### Configuration System

Settings loaded from `.env` file via Pydantic Settings (runthroughlinehackathor/settings.py):
- Game balance: `n_actions`, `time_pre_turn`, `health_per_time_spent`
- Action constraints: `n_big_actions`, `n_small_actions`, `small_action_max_cost`
- Initial values: `initial_health`, `initial_other_parameters`, `initial_age`, `years_per_turn`

### Key Model Relationships

- **ActionBase** (abstract): name, description, parameter_change
  - **Action**: extends ActionBase with type, time_cost, is_unique flag
  - **Reaction**: extends ActionBase (triggered responses)
- **Parameters**: health, career, relations, money (supports addition via `__add__`)
- **HistoryElement**: Union of Action, RandomEvent, or Reaction
