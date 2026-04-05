def TTT_get_available_moves(state: list[str]) -> list[int]:
	if len(state) != 9:
		print("Invalid state!")
		return []

	return [idx for idx, marker in enumerate(state) if marker == 'e']

def TTT_apply_move(state: list[str], idx: int, marker: str) -> list[str]:
	if state[idx] == 'e':
		state[idx] = marker

	return state

LINES: list[tuple[int, int, int]] = [
	(0, 1, 2), (3, 4, 5), (6, 7, 8),
	(0, 3, 6), (1, 4, 7), (2, 5, 8),
	(0, 4, 8), (2, 4, 6)
]

def TTT_determine_winner(state) -> str:
	for line in LINES:
		if state[line[0]] != 'e' and state[line[0]] == state[line[1]] == state[line[2]]:
			return state[line[0]]

	# return e to signal unfinished game, None in case of a draw.
	return 'e' if state.count('e') > 0 else None

def TTT_assess_partial_state(state, team, weights: dict[tuple, int]) -> int:
	score = 0
	for line in LINES:
		tiles = [state[i] for i in line]
		team_count = tiles.count(team)
		opp_count = 3 - team_count - tiles.count('e')
		score += weights.get((team_count, opp_count), 0)

	return score

def TTT_is_terminal(state) -> bool:
	return state.count('e') == 0 or TTT_determine_winner(state) != 'e'

def TTT_format_state(state) -> str:
	return f"[{state[0]}-{state[1]}-{state[2]}\n{state[3]}-{state[4]}-{state[5]}\n{state[6]}-{state[7]}-{state[8]}]\n"

def TTT_encode_state(state: list[int]) -> str:
	return str(''.join(state))
