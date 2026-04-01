from event import Event
import random

neighbours = {
	0: [3, 6, 1, 2, 4, 8, None, None],
	1: [4, 7, 0, 2, None, None, None, None],
	2: [5, 8, 0, 1, 4, 6, None, None],
	3: [0, 6, 4, 5, None, None, None, None],
	4: [1, 7, 3, 5, 0, 8, 2, 6],
	5: [2, 8, 3, 4, None, None, None, None],
	6: [0, 3, 7, 8, 2, 4, None, None],
	7: [1, 4, 6, 8, None, None, None, None],
	8: [2, 5, 6, 7, 0, 4, None, None]
}
"""
2x top-down, 2x left-right, 4x diagonal (null x4 if invalid)
"""

direct_neighbours = {
	0 : [1, 4, 3],
	1: [0, 3, 4, 5, 2],
	2: [1, 4, 5],
	3: [0, 1, 4, 6, 7],
	4: [0, 1, 2, 3, 5, 6, 7, 8],
	5: [2, 1, 4, 7, 8],
	6: [3, 4, 7],
	7: [6, 3, 4, 5, 8],
	8: [5, 4, 7]
}

class TTT_Player:
	player_id = 0
	symbol = ['x', 'o']
	symbol_colors = ["red", "blue"]

	def __init__(self, game, team):
		self.id = TTT_Player.player_id
		TTT_Player.player_id += 1

		self.marker = TTT_Player.symbol[team - 1]
		self.color = TTT_Player.symbol_colors[team - 1]
		self.game = game
		self.name = f"Player {team}"
		self.turn = False

		self.on_turn_start = Event()
		self.on_turn_start.add_listener(self.start_turn)
		self.on_turn_end = Event()
		self.on_turn_end.add_listener(self.end_turn)
		self.game.update.add_listener(self.update)

	def place_tile(self, tile_id):
		if self.turn:
			print(f"{self.name} chose tile {tile_id}")
			self.game.ttt.place_tile(tile_id)

	def update(self):
		pass

	def start_turn(self):
		self.turn = True

	def end_turn(self):
		self.turn = False

class TTT_Baseline_Player(TTT_Player):
	WEIGHTS = {
		"CAN_WIN": 10,
		"BLOCK_OPP": 9,
		"LINE": 5,
		"MAX_NEIGHBOURS": 4,
		"NONE": 1
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def update(self):
		if not self.turn or not self.game.ttt.running:
			return

		self.eval_state()

	def eval_state(self):
		state = self.game.ttt.grid
		n_empty = 0
		empty_indices = []

		# find all empty tiles.
		for i, marker in enumerate(state):
			if marker == 'e':
				# count & reference index (tile to place)
				n_empty += 1
				empty_indices.append(i)

		# no decision to make if no tiles to place.
		if n_empty == 0:
			return

		# if only one move to make, place a tile at the empty one.
		if n_empty == 1:
			self.place_tile(empty_indices[0])

		# store best state
		max_val = ([-1], -float('inf'))
		for j in empty_indices:
			val = self.eval_tile(state, j)
			#print(f"Tile {j} got a value of {val}")
			if val > max_val[1]:
				max_val = ([j], val)
				continue
			# add index to list if equal value (to choose randomly)
			if val == max_val[1]:
				max_val[0].append(j)

		# if only one chosen tile, 
		chosen_tile = max_val[0] if len(max_val) == 1 else random.choice(max_val[0])
		self.place_tile(chosen_tile)

	def eval_tile(self, state, idx):
		# return an invalid value if invalid tile.
		if not idx in neighbours.keys():
			return -float('inf')

		n = neighbours[idx]

		n_empty_neighbours = [state[x] == 'e' for x in direct_neighbours[idx]].count(True)

		# evaluate a given direction.
		def eval(n_0, n_1, team):
			# invalidate the check if any neighbour is invalid
			if n_0 is None or n_1 is None:
				return (False, False, False)

			win = state[n_0] == state[n_1] == team
			block = (state[n_0] == state[n_1] != team) and (state[n_0] == state[n_1] != 'e')	# opponent can win if both tiles not own marker nor empty
			line = (state[n_0] == team and state[n_1] == 'e') or (state[n_0] == 'e' and state[n_1] == team)

			return (win, block, line)

		r_w1, r_b1, r_l1 = eval(n[0], n[1], self.marker)
		r_w2, r_b2, r_l2 = eval(n[2], n[3], self.marker)
		r_w3, r_b3, r_l3 = eval(n[4], n[5], self.marker)
		r_w4, r_b4, r_l4 = eval(n[6], n[7], self.marker)
		
		# if any line expresses the trait, it should pass to the eval.
		can_win = r_w1 or r_w2 or r_w3 or r_w4
		opponent_can_win = r_b1 or r_b2 or r_b3 or r_b4
		forms_line = r_l1 or r_l2 or r_l3 or r_l4

		# want highest value if:
		# a) can win
		if can_win:
			return TTT_Baseline_Player.WEIGHTS["CAN_WIN"]
		# b) directly stops opponent from winning
		if opponent_can_win:
			return TTT_Baseline_Player.WEIGHTS["BLOCK_OPP"]
		# c) places a line of markers
		if forms_line:
			return TTT_Baseline_Player.WEIGHTS["LINE"]
		# d) n_neighbours
		if n_empty_neighbours > 0:
			return TTT_Baseline_Player.WEIGHTS["MAX_NEIGHBOURS"]

		# return token value if no advantage to playing this tile.
		return TTT_Baseline_Player.WEIGHTS["NONE"]


