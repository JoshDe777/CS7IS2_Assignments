from Algorithms.minmax import MinMax_Default, MinMax_AB_Pruning
from Algorithms.rl import DQN_RL, Tabular_QRL
from TTT.utils import TTT_assess_partial_state, TTT_determine_winner, TTT_format_state, TTT_get_available_moves
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
"""A list of pointers to tiles considered direct neighbours of a given tile."""

class TTT_Player:
	"""Base Tic Tac Toe controller. Base class meant for use by Human players, with virtual setup functions for AI controllers.."""

	#region static members
	player_id = 0
	"""[static] player ID field that auto-increments. Kinda useless but eh."""

	symbol = ['x', 'o']
	"""[static] Available symbols to differentiate player 1 from player 2."""

	symbol_colors = ["red", "blue"]
	"""[static] Available colors to differentiate player 1 from player 2."""

	def get_other_marker(marker):
		"""utility function to get the opponent's marker"""
		return TTT_Player.symbol[0] if TTT_Player.symbol[1] == marker else TTT_Player.symbol[1]
	#endregion

	#region core
	def __init__(self, game, team):
		self.name = f"Player {team}"
		"""Player name for display purposes."""
		self.id = TTT_Player.player_id
		"""The player's unique ID. Useless feature initially used to map teams but broken."""
		TTT_Player.player_id += 1

		self.marker = TTT_Player.symbol[team - 1]
		"""The player's marker. Shouldn't be the same as the other player's ideally."""
		self.color = TTT_Player.symbol_colors[team - 1]
		"""The player's color. Shouldn't be the same as the other player's but only for visualization so not too bad if so."""
		self.game = game
		"""A reference to the Game class to reference the tic tac toe environment indirectly."""
		self.turn = False
		"""A bool indicating whether it's a player's turn or not."""

		self.on_turn_start = Event()
		"""Event invoked whenever a player's turn starts."""
		self.on_turn_start.add_listener(self.start_turn)

		self.on_turn_end = Event()
		"""Event invoked whenever a player's turn ends."""
		self.on_turn_end.add_listener(self.end_turn)

		self.game.update.add_listener(self.update)
		"""Flags the game to update the player (mostly for the AI controllers :D)."""

	def start_turn(self):
		"""Starts a player's turn. (Added to on_turn_start event)"""
		self.turn = True

	def end_turn(self):
		"""Closes a player's turn. (Added to on_turn_end event)"""
		self.turn = False

	def place_tile(self, tile_id):
		"""Attempts to place the player's marker on the given tile."""
		if self.turn and tile_id in range(0, 9):
			self.game.ttt.place_tile(tile_id)

	def update(self):
		"""
		Called every frame unless out of turn or tic tac toe game disabled.
		DO NOT EDIT in child behaviours, will get rid of the early exit otherwise.
		"""
		if not self.turn or not self.game.ttt.running:
			return

		self.place_tile(self.choose_next_move(self.game.ttt.grid))

	def invalidate(self):
		self.game.update.remove_listener(self.update)
		self.on_turn_start.reset()
		self.on_turn_end.reset()
	#endregion

	#region controller templates
	def choose_next_move(self, state) -> int:
		"""
		virtual function for the controllers to implement.
		selects and returns the tile index chosen for the agent's move.
		"""
		return -1
	#endregion


class TTT_Baseline_Player(TTT_Player):
	"""Baseline Tic Tac Toe controller. Will always win or block if able/needed, otherwise always tries to form a line of markers."""

	#region static members
	WEIGHTS = {
		"CAN_WIN": 10,
		"BLOCK_OPP": 9,
		"LINE": 5,
		"MAX_NEIGHBOURS": 1,		# scales with n(neighbours) -> max = 8 (middle on 1st turn)!
	}
	"""
	A default set of weights for tic tac toe games. Adjusted to return in order of priority:
	- has the direct opportunity to win (CAN_WIN) - absolute highest weight
	- has to block opponent to stop them from winning (BLOCK_OPP) - 2nd highest weight (if can both win and block should choose to win, but should block in any other scenario)
	- can form a line of 2 markers (LINE)
	- has a few empty neighbours -> scales with n(neighbours) => bias in 1st move; will always pick middle (8*MAX_NEIGHBOURS), after that it'll usually find the other scenarios
	"""

	def get_utility(can_win: bool, can_block: bool, forms_line: bool, n_neighbours: int):
		"""
		Wrapper function to get the base utility of a given state based on certain params:
		- can_win: "can the agent win immediately?"
		- can_block: "does the agent need to block their opponent to avoid losing?"
		- forms_line: "does the move set the agent up for a best-case win in the next turn?"
		- n_neighbours: "how many empty neighbouring tiles are there around the newly placed marker?"
		"""
		# a) can win
		if can_win:
			return TTT_Baseline_Player.WEIGHTS["CAN_WIN"]
		# b) directly stops opponent from winning
		if can_block:
			return TTT_Baseline_Player.WEIGHTS["BLOCK_OPP"]
		# c) places a line of markers
		if forms_line:
			return TTT_Baseline_Player.WEIGHTS["LINE"]
		# d) n_neighbours
		if n_neighbours > 0:
			return n_neighbours * TTT_Baseline_Player.WEIGHTS["MAX_NEIGHBOURS"]
		return 0
	#endregion
	
	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state) -> int:
		"""Evaluates the current state/direct next moves for the baseline parameters and takes a random pick of the best-valued moves."""
		eval_results = self.eval_state(state)

		if len(eval_results) == 0:
			print("[Baseline] No moves to choose from!")
			return -1

		if len(eval_results) == 1:
			return eval_results[0][0]

		max_val = ([-1], -float('inf'))

		for j, val in eval_results:
			if val is None:
				continue

			#print(f"Tile {j} got a value of {val}")
			if val > max_val[1]:
				max_val = ([j], val)
				continue
			# add index to list if equal value (to choose randomly)
			if val == max_val[1]:
				max_val[0].append(j)

		return max_val[0][0] if len(max_val[0]) == 1 else random.choice(max_val[0])

	def eval_state(self, state):
		"""Template function to evaluate a game state."""
		empty_indices = TTT_get_available_moves(state)
		n_empty = len(empty_indices)

		# no decision to make if no tiles to place.
		if n_empty == 0:
			return []

		# return list of available states paired with utility values.
		eval_ = []
		for j in empty_indices:
			eval_.append((j, self.eval_move(state, j)))

		# if more than one chosen tile, choose randomly
		return eval_

	def eval_move(self, state, idx):
		"""Assesses the direct aftermath of a tentative move, returning a score on how good the move is (defined in TTT_Player.WEIGHTS)"""
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
		return TTT_Baseline_Player.get_utility(can_win, opponent_can_win, forms_line, n_empty_neighbours)
		

class TTT_MinMax_Player(TTT_Player):
	"""Tic Tac Toe MinMax controller (no pruning)"""

	depth = 5
	"""[static] The maximum min-max depth the algorithm is to incur."""

	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# any scenario not in weights -> 0
	PARTIAL_WEIGHTS = {
		(1, 0): 1,
		(2, 0): 10,
		(0, 1): -1,
		(0, 2): -10
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state) -> int:
		"""Runs the minmax algorithm [delegated to MinMax_Default class for reuse in connect 4] to choose the next move."""

		return MinMax_Default.evaluate(
			game="TTT", 
			state=state, 
			team=self.marker, 
			opponent=TTT_Player.get_other_marker(self.marker),
			max_depth=TTT_MinMax_Player.depth,
			utility_func=self.eval_state)

	def eval_state(self, state, terminal):
		"""
		Overwritten utility function!
		Considers case 'full grid' (dead-end state) -> WIN = 10, DRAW = 0, LOSE = -10
		and case 'partial grid' (intermediate state) -> FORMS_LINE = 5, MUST_BLOCK = -7, BASE = 0
		"""
		# if leaf state (no more moves after) evaluate whether the state is a win or a loss
		if terminal:
			winner = TTT_determine_winner(state)
			return TTT_MinMax_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else TTT_MinMax_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else TTT_MinMax_Player.TERMINAL_WEIGHTS["LOSE"]

		return TTT_assess_partial_state(state, self.marker, TTT_MinMax_Player.PARTIAL_WEIGHTS)


class TTT_Pruned_MinMax_Player(TTT_Player):
	"""Tic Tac Toe MinMax controller (with pruning)"""

	depth = 5
	"""[static] The maximum min-max depth the algorithm is to incur."""

	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# any scenario not in weights -> 0
	PARTIAL_WEIGHTS = {
		(1, 0): 1,
		(2, 0): 10,
		(0, 1): -1,
		(0, 2): -10
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state) -> int:
		"""Runs the minmax algorithm [delegated to MinMax_Default class for reuse in connect 4] to choose the next move."""

		return MinMax_AB_Pruning.evaluate(
			game="TTT", 
			state=state, 
			team=self.marker, 
			opponent=TTT_Player.get_other_marker(self.marker),
			max_depth=TTT_Pruned_MinMax_Player.depth,
			utility_func=self.eval_state)

	def eval_state(self, state, terminal):
		"""
		Overwritten utility function!
		Considers case 'full grid' (dead-end state) -> WIN = 10, DRAW = 0, LOSE = -10
		and case 'partial grid' (intermediate state) -> FORMS_LINE = 5, MUST_BLOCK = -7, BASE = 0
		"""
		# if leaf state (no more moves after) evaluate whether the state is a win or a loss
		if terminal:
			winner = TTT_determine_winner(state)
			return TTT_Pruned_MinMax_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else TTT_Pruned_MinMax_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else TTT_Pruned_MinMax_Player.TERMINAL_WEIGHTS["LOSE"]

		return TTT_assess_partial_state(state, self.marker, TTT_Pruned_MinMax_Player.PARTIAL_WEIGHTS)

	def end_turn(self):
		super().end_turn()
		print(f"Pruned {MinMax_AB_Pruning.get_n_pruned()} states!")
		MinMax_AB_Pruning.reset_pruned_count()


class TTT_TQRL_Player(TTT_Player):

	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# any scenario not in weights -> 0
	PARTIAL_WEIGHTS = {
		(1, 0): 1,
		(2, 0): 10,
		(0, 1): -1,
		(0, 2): -10
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state) -> int:
		"""Runs the minmax algorithm [delegated to MinMax_Default class for reuse in connect 4] to choose the next move."""

		return Tabular_QRL.evaluate(
			game="TTT", 
			state=state, 
			team=self.marker,
			utility_func=self.eval_state)

	def eval_state(self, state, terminal):
		"""
		Overwritten utility function!
		Considers case 'full grid' (dead-end state) -> WIN = 10, DRAW = 0, LOSE = -10
		and case 'partial grid' (intermediate state) -> FORMS_LINE = 5, MUST_BLOCK = -7, BASE = 0
		"""
		# if leaf state (no more moves after) evaluate whether the state is a win or a loss
		if terminal:
			winner = TTT_determine_winner(state)
			return TTT_TQRL_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else TTT_TQRL_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else TTT_TQRL_Player.TERMINAL_WEIGHTS["LOSE"]

		return TTT_assess_partial_state(state, self.marker, TTT_TQRL_Player.PARTIAL_WEIGHTS)


class TTT_DQL_Player(TTT_Player):
	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# any scenario not in weights -> 0
	PARTIAL_WEIGHTS = {
		(1, 0): 1,
		(2, 0): 10,
		(0, 1): -1,
		(0, 2): -10
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state) -> int:
		"""Runs the minmax algorithm [delegated to MinMax_Default class for reuse in connect 4] to choose the next move."""

		return DQN_RL.evaluate(
			game="TTT", 
			state=state, 
			team=self.marker,
			utility_func=self.eval_state)

	def eval_state(self, state, terminal):
		"""
		Overwritten utility function!
		Considers case 'full grid' (dead-end state) -> WIN = 10, DRAW = 0, LOSE = -10
		and case 'partial grid' (intermediate state) -> FORMS_LINE = 5, MUST_BLOCK = -7, BASE = 0
		"""
		# if leaf state (no more moves after) evaluate whether the state is a win or a loss
		if terminal:
			winner = TTT_determine_winner(state)
			return TTT_DQL_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else TTT_DQL_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else TTT_DQL_Player.TERMINAL_WEIGHTS["LOSE"]

		return TTT_assess_partial_state(state, self.marker, TTT_DQL_Player.PARTIAL_WEIGHTS)
