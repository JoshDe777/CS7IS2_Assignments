from pygame import Vector2

cardinal_dirs = [
	Vector2(-1, 1), 
	Vector2(0, 1), 
	Vector2(1, 1), 
	Vector2(1, 0)
]

def C4_get_available_moves(state: list[list]) -> list[int]:
	return [i for i, col in enumerate(state) if len(col) < 6]

def C4_apply_move(state: list[list], idx: int, marker: str) -> list[list]:
	if len(state[idx]) < 6:
		state[idx].append(marker)
		
	return state

def C4_is_grid_full(state) -> bool:
	for col, _ in enumerate(state):
		# exit with not full if any column has less than 6 tokens
		if len(state[col]) < 6:
			return False

	# if no column triggered an early exit, state considered complete.
	return True

def C4_determine_winner(state) -> str:
	# check if exists tile in every cardinal direction and search until marker is either empty or not own.
	# if len == 4 declare winner else none
	# if grid full declare draw

	# only really need to check the top chip of every state since that's the only place a token will ever be placed 
	# -> smaller change surface
	for idx, _ in enumerate(state):
		n = len(state[idx]) - 1
		# if empty column, not worth investigating
		if n < 0:
			continue

		team = state[idx][n]
		streak = 0

		for _dir in cardinal_dirs:
			streak = 0
			i = 0
			# forward pass:
			while not streak >= 4:
				# x, y = (idx, n) + i * _dir
				x = int(idx + i * _dir.x)
				y = int(n + i * _dir.y)

				# if x, y invalid exit fwd pass
				if x < 0 or x >= len(state):
					break
				if y < 0 or y >= len(state[x]):
					break

				# if [x, y] != team exit fwd pass
				if state[x][y] != team:
					break

				# else streak += 1 and continue (i += 1)
				streak += 1
				i += 1

			# reset i (to 1 not 0 because otherwise counts newly placed token twice)
			i = 1

			while not streak >= 4:
			# backward pass:
				# x, y = (idx, n) - i * _dir
				x = int(idx - i * _dir.x)
				y = int(n - i * _dir.y)

				# if x, y invalid exit back pass
				if x < 0 or x >= len(state):
					break
				if y < 0 or y >= len(state[x]):
					break

				# if [x, y] != team exit back pass
				if state[x][y] != team:
					break

				# else streak += 1 and continue (i += 1)
				streak += 1
				i += 1

			# exit check if there's a winner
			if streak >= 4:
				break

		if not streak >= 4:
			return 'e' if not C4_is_grid_full(state) else None

		return team

def C4_assess_partial_state(state, team, weights) -> int:
	def _score(window, team):
		team_count = window.count(team)
		empty = window.count(None)
		opp_count = len(window) - team_count - empty

		if opp_count == 0:
			return weights.get((team_count, empty), 0)
		if team_count == 0:
			return -weights.get((opp_count, empty), 0)
		
		# if window has markers of both teams, consider window 'dead' -> no reward nor punishment.
		return 0

	def _get_cell(state, row, col):
		if col >= len(state):
			return None

		_col = state[col]
		return _col[row] if row < len(_col) else None

	def _make_windows(state):
		n_cols = 7
		n_rows = 6
		for col in range(n_cols):
			for row in range(n_rows):
				# horizontal row towards right
				if col+3 < n_cols:
					yield [_get_cell(state, row=row, col=col+i) for i in range(4)]
				# vertical up
				if row+3 < n_rows:
					yield [_get_cell(state, row=row+i, col=col) for i in range(4)]
				# diagonal right up
				if col+3 < n_cols and row+3 < n_rows:
					yield [_get_cell(state, row=row+i, col=col+i) for i in range(4)]
				# diagonal left up
				if col+3 < n_cols and row-3 < n_rows:
					yield [_get_cell(state, row=row+i, col=col-i) for i in range(4)]

	score = 0
	for window in _make_windows(state=state):
		score += _score(window, team)

	return score

def C4_is_terminal(state) -> bool:
	for col in state:
		if len(col) < 6:
			return False

	return True

def C4_format_state(state) -> str:
	return "\n".join([f"{i}: {'-'.join(s)}" for i, s in enumerate(state)])

def C4_encode_state(state: list[list[str]]) -> str:
	return ' '.join(["".join(col) for col in state]) + ' '
