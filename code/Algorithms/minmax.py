from copy import deepcopy
from C4.utils import C4_apply_move, C4_format_state, C4_get_available_moves, C4_is_terminal
from TTT.utils import TTT_get_available_moves, TTT_apply_move, TTT_format_state, TTT_is_terminal

class MinMax_Algos:
	def __init__(self, get_moves, apply_move, is_terminal, copy_state_func=None):
		self.get_moves = get_moves
		self.apply_move = apply_move
		self.is_terminal = is_terminal
		self.copy_state = copy_state_func if copy_state_func is not None else (lambda s: s.copy())

class MinMax_Default:
	TTT = MinMax_Algos(
		get_moves=TTT_get_available_moves, 
		apply_move=TTT_apply_move, 
		is_terminal=TTT_is_terminal
	)
	# deepcopy because .copy() keeps sublists persistent -> breaks C4 game.
	C4 = MinMax_Algos(
		get_moves=C4_get_available_moves, 
		apply_move=C4_apply_move, 
		copy_state_func=lambda s: deepcopy(s), 
		is_terminal=C4_is_terminal
	)

	max_depth = 5

	game_dict = {
		"TTT": TTT,
		"C4": C4
	}

	def evaluate(game,
			state, 
			team, 
			opponent, 
			max_depth,
			utility_func
		):
		"""
		Does a full run of MinMax considering (many) parameters:
		- game: the game MinMax is to be used for [options: TTT, C4; anything else will result in errors!]
		- state: the game's current state
		- team: the marker of the player whose turn is being evaluated
		- opponent: the opposing player's marker
		- max_depth: the maximum depth of the simulation tree
		- utility_func: a function taking in a state as input returning a utility value.

		(parameters all included in static function to not need to rewrite specifically for tic tac toe or connect 4 separately :D)
		"""
		game = MinMax_Default.game_dict.get(game, None)
		MinMax_Default.max_depth = max_depth

		base_moves = game.get_moves(state)
		# early exit if no valid moves.
		if len(base_moves) == 0:
			return -1

		best_util = -float('inf')
		best_move = base_moves[0]

		# depth-first search from each child state
		for idx in base_moves:
			new_state = game.apply_move(game.copy_state(state), idx, team)

			_score = MinMax_Default.min_run(game, new_state, markers=(team, opponent), depth=1, utility_func=utility_func)

			if _score > best_util:
				best_util = _score
				best_move = idx

		return best_move

	def max_run(game, state, markers, depth, utility_func, alpha=None, beta=None):
		if game.is_terminal(state) or depth >= MinMax_Default.max_depth:
			return utility_func(state, game.is_terminal(state))

		best_score = -10000
		for move in game.get_moves(state):
			new_state = game.apply_move(game.copy_state(state), move, markers[0])
			score = MinMax_Default.min_run(game=game, state=new_state, markers=markers, depth=depth+1, utility_func=utility_func)

			if score > best_score:
				best_score = score

		return best_score

	def min_run(game, state, markers, depth, utility_func, alpha=None, beta=None):
		if game.is_terminal(state) or depth >= MinMax_Default.max_depth:
			return utility_func(state, game.is_terminal(state))

		best_score = 10000
		for move in game.get_moves(state):
			new_state = game.apply_move(game.copy_state(state), move, markers[1])
			score = MinMax_Default.max_run(game=game, state=new_state, markers=markers, depth=depth+1, utility_func=utility_func)

			if score < best_score:
				best_score = score

		return best_score

class MinMax_AB_Pruning(MinMax_Default):
	pruned_count = 0

	def max_run(game, state, markers, depth, utility_func, alpha=10000, beta=-10000):
		if game.is_terminal(state) or depth >= MinMax_AB_Pruning.max_depth:
			return utility_func(state, game.is_terminal(state))

		best_score = -10000
		for move in game.get_moves(state):
			new_state = game.apply_move(game.copy_state(state), move, markers[0])
			score = MinMax_AB_Pruning.min_run(game=game, state=new_state, markers=markers, depth=depth+1, utility_func=utility_func)

			if score > best_score:
				best_score = score

				# alpha-beta pruning; if score higher than min-pruned value, ignore and exit from node; 
				if best_score > beta:
					MinMax_AB_Pruning.pruned_count += 1
					return best_score

				# otherwise update alpha upwards if applicable
				alpha = max(alpha, best_score)

		return best_score

	def min_run(game, state, markers, depth, utility_func, alpha=None, beta=None):
		if game.is_terminal(state) or depth >= MinMax_AB_Pruning.max_depth:
			return utility_func(state, game.is_terminal(state))

		best_score = 10000
		for move in game.get_moves(state):
			new_state = game.apply_move(game.copy_state(state), move, markers[1])
			score = MinMax_AB_Pruning.max_run(game=game, state=new_state, markers=markers, depth=depth+1, utility_func=utility_func)

			if score < best_score:
				best_score = score
				# alpha-beta pruning; if score lower than max-pruned value, ignore and exit from node; 
				if best_score < alpha:
					MinMax_AB_Pruning.pruned_count += 1
					return best_score
				
				# otherwise update beta downwards if applicable
				beta = min(beta, best_score)

		return best_score

	def get_n_pruned():
		return MinMax_AB_Pruning.pruned_count

	def reset_pruned_count():
		MinMax_AB_Pruning.pruned_count = 0
