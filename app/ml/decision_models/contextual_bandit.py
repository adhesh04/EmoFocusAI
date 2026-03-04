import random
from collections import defaultdict

INTERVENTIONS = [
    "breathing_exercise",
    "break_suggestion",
    "mini_focus_task",
    "motivation_prompt",
    # "sliding_puzzle"
]

EPSILON = 0.2  # exploration rate

def select_intervention(user_stats: dict) -> str:
    """
    user_stats = {
        intervention_type: {
            "avg_reward": float,
            "count": int
        }
    }
    """

    # Exploration
    if random.random() < EPSILON:
        return random.choice(INTERVENTIONS)

    # Exploitation
    best_action = None
    best_value = float("-inf")

    for action in INTERVENTIONS:
        stats = user_stats.get(action)
        avg_reward = stats["avg_reward"] if stats else 0.0

        if avg_reward > best_value:
            best_value = avg_reward
            best_action = action

    return best_action or random.choice(INTERVENTIONS)
