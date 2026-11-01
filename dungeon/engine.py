import streamlit as st

from dungeon.levels import DUNGEON_LEVELS

RULES_VERSION = 3
LEVEL_POINTS = 10
HINT_COST = 5


def fresh_state():
    return {
        "score": 0,
        "current_level": 0,
        "current_challenge": 0,
        "hints_left": 2,
        "victory": False,
        "level_total": len(DUNGEON_LEVELS),
        "rules_version": RULES_VERSION,
    }


def init_game_state():
    state = st.session_state.get("game_state")
    if (
        not state
        or "hints_left" not in state
        or state.get("level_total") != len(DUNGEON_LEVELS)
        or state.get("rules_version") != RULES_VERSION
    ):
        st.session_state.game_state = fresh_state()


def reset_game():
    st.session_state.game_state = fresh_state()


def advance_challenge():
    state = st.session_state.game_state
    level = DUNGEON_LEVELS[state["current_level"]]
    state["current_challenge"] += 1
    finished_level = state["current_challenge"] >= len(level["challenges"])
    if finished_level:
        state["score"] += LEVEL_POINTS
        state["current_level"] += 1
        state["current_challenge"] = 0
        if state["current_level"] >= len(DUNGEON_LEVELS):
            state["victory"] = True
    return finished_level


def use_hint():
    state = st.session_state.game_state
    if state["hints_left"] <= 0:
        return False
    state["hints_left"] -= 1
    state["score"] -= HINT_COST
    return True
