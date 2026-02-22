def calculate_score(total_time_seconds, commits):
    base = 100
    speed_bonus = 10 if total_time_seconds < 300 else 0
    penalty = max(0, commits - 20) * 2
    final = base + speed_bonus - penalty
    return {
        "base": base,
        "speed_bonus": speed_bonus,
        "penalty": penalty,
        "final": final,
    }
