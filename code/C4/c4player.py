from Algorithms.minmax import MinMax_Default, MinMax_AB_Pruning
from Algorithms.rl import DQN_RL, Tabular_QRL
from C4.utils import C4_determine_winner, C4_assess_partial_state
from event import Event
from pygame import Vector2
import random

cardinal_dirs = [
	Vector2(-1, 1), 
	Vector2(0, 1), 
	Vector2(1, 1), 
	Vector2(1, 0)
]

class C4_Player:
	player_id = 0
	symbol = ['x', 'o']
	symbol_colors = ["red", "yellow"]

	def get_other_marker(marker):
		"""utility function to get the opponent's marker"""
		return C4_Player.symbol[0] if C4_Player.symbol[1] == marker else C4_Player.symbol[1]

	def __init__(self, game, team):
		self.id = C4_Player.player_id
		C4_Player.player_id += 1

		self.marker = C4_Player.symbol[team-1]
		self.color = C4_Player.symbol_colors[team-1]
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
			self.game.c4.add_to_slot(tile_id)

	def start_turn(self):
		self.turn = True

	def update(self):
		if not self.turn or not self.game.c4.running:
			return
		
		self.place_tile(self.choose_next_move(self.game.c4.grid))

	def end_turn(self):
		self.turn = False

	def choose_next_move(self, state):
		pass

	def invalidate(self):
		self.game.update.remove_listener(self.update)


class C4_Baseline_Player(C4_Player):
	WEIGHTS = {
		"CAN_WIN": 10,
		"BLOCK_OPP": 9,
		"LINE": 2			# multiplies by length! -> max val = 6 (or 8 but that's CAN_WIN/BLOCK_OPP)
	}

	def __init__(self, game, team):
		super().__init__(game, team)


	def choose_next_move(self, state):
		n_placeable = 0
		placeable_cols = []

		# find placeable columns
		for i in range(7):
			if len(state[i]) < 6:
				n_placeable += 1
				placeable_cols.append(i)

		# no decision to make if no placeable tiles.
		if n_placeable == 0:
			return

		if n_placeable == 1:
			self.place_tile(placeable_cols[0])

		max_val = ([-1], -float('inf'))
		for j in placeable_cols:
			val = self.eval_tile(state, j)
			
			#print(f"Column {j} got a value of {val}!")
			if val > max_val[1]:
				max_val = ([j], val)
				continue

			if val == max_val[1]:
				max_val[0].append(j)
		
		chosen_tile = max_val[0] if len(max_val) == 1 else random.choice(max_val[0])
		return chosen_tile

	def eval_tile(self, state, idx):
		#print(f"--------------------------- Start Eval Col {idx} ---------------------------")
		team = self.marker

		def eval(_dir):
			#print(f"Eval Dir ({_dir.x}, {_dir.y})")
			own_streak = 0
			opp_streak = 0
			n = len(state[idx])
			i = 1
			streak = 0
			
			x = int(idx + _dir.x)
			y = int(n + _dir.y)

			# skip fwd pass if accessing invalid tile
			if (x >= 0 and x < len(state)) and (y >= 0 and y < len(state[x])):
				next_marker = state[x][y]

				# establish pass ownership (if evaluating own line or opponent's)
				# works because no empty marker :D
				ownership = team if next_marker == team else next_marker

				# auto-break if already evaluating a winning streak
				while not streak >= 3:
					# x, y = (idx, n) + i * _dir
					x = int(idx + i * _dir.x)
					y = int(n + i * _dir.y)

					# if x, y invalid exit fwd pass
					if x < 0 or x >= len(state):
						break
					if y < 0 or y >= len(state[x]):
						break

					# if [x, y] != pass owner exit fwd pass
					if state[x][y] != ownership:
						break

					# else streak += 1 and continue (i += 1)
					streak += 1
					i += 1

				# assign the streak to its rightful credit claimant
				if ownership == team:
					own_streak += streak
				else:
					opp_streak += streak
				streak = 0

				#print(f"Forward pass:\n- own_streak={own_streak},\n- opp_streak={opp_streak}")

			# reset i & establish back pass ownership
			i = 1
			x = int(idx - _dir.x)
			y = int(n - _dir.y)

			# skip backward pass if accessing invalid tile
			if (x >= 0 and x < len(state)) and (y >= 0 and y < len(state[x])):
				next_marker = state[x][y]

				# establish pass ownership (if evaluating own line or opponent's)
				# works because no empty marker :D
				ownership = team if next_marker == team else next_marker

				while not streak >= 3:
				# backward pass:
					# x, y = (idx, n) - i * _dir
					x = int(idx - i * _dir.x)
					y = int(n - i * _dir.y)

					#print(f"({x},{y})")

					# if x, y invalid exit back pass
					if x < 0 or x >= len(state):
						break
					if y < 0 or y >= len(state[x]):
						break

					#print(f"Ownership matching: {state[x][y]} vs {ownership}")

					# if [x, y] != team exit back pass
					if state[x][y] != ownership:
						break

					# else streak += 1 and continue (i += 1)
					streak += 1
					i += 1
					
				if ownership == team:
					own_streak += streak
				else:
					opp_streak += streak
				streak = 0
				#print(f"Backward pass (owner: {ownership}):\n- own_streak={own_streak},\n- opp_streak={opp_streak}")
				
			return (own_streak >= 3, opp_streak >= 3, own_streak)

		# init with dummy values in case empty. 
		# Any credible run will overwrite those without being affected.
		results = [(False, False, 0)]
		for _dir in cardinal_dirs:
			results.append(eval(_dir))

		# if can win in any direction do so
		can_win = True in [i[0] for i in results]
		# if can block in any direction do so
		can_block = True in [i[1] for i in results]
		# save longest possible line including potentially placed token here.
		line = max([i[2] for i in results]) + 1
		
		#print(f"--------------------------- End Eval Col {idx} ---------------------------")

		# special returns if can immediately win or block opponent from winning next round
		if can_win:
			return C4_Baseline_Player.WEIGHTS["CAN_WIN"]
		if can_block:
			return C4_Baseline_Player.WEIGHTS["BLOCK_OPP"]
		
		# otherwise return weight scaled by largest potential line
		return line * C4_Baseline_Player.WEIGHTS["LINE"]

class C4_MinMax_Player(C4_Player):
	depth = 5

	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# mirror desirable states with (own tokens, empty tokens) in any given sequence of 4 grid spaces.
	PARTIAL_WEIGHTS = {
		(4, 0): 100,
		(2, 2): 2,
		(3, 1): 5
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state):
		return MinMax_Default.evaluate(
			game="C4",
			state=state,
			team=self.marker,
			opponent=C4_Player.get_other_marker(self.marker),
			max_depth=C4_MinMax_Player.depth,
			utility_func=self.eval_state
		)

	def eval_state(self, state, terminal):
		n_empty = sum([1 for x in state if len(x) < 6])
		# if leaf state (no more moves after) evaluate whether the state is a win or loss
		if terminal:
			winner = C4_determine_winner(state)
			return C4_MinMax_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else C4_MinMax_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else C4_MinMax_Player.TERMINAL_WEIGHTS["LOSE"]

		return C4_assess_partial_state(state, self.marker, C4_MinMax_Player.PARTIAL_WEIGHTS)

class C4_Pruned_MinMax_Player(C4_Player):
	depth = 5

	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# mirror desirable states with (own tokens, empty tokens) in any given sequence of 4 grid spaces.
	PARTIAL_WEIGHTS = {
		(4, 0): 100,
		(2, 2): 2,
		(3, 1): 5
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state):
		return MinMax_AB_Pruning.evaluate(
			game="C4",
			state=state,
			team=self.marker,
			opponent=C4_Player.get_other_marker(self.marker),
			max_depth=C4_Pruned_MinMax_Player.depth,
			utility_func=self.eval_state
		)

	def eval_state(self, state, terminal):
		# if leaf state (no more moves after) evaluate whether the state is a win or loss
		if terminal:
			winner = C4_determine_winner(state)
			return C4_Pruned_MinMax_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else C4_Pruned_MinMax_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else C4_Pruned_MinMax_Player.TERMINAL_WEIGHTS["LOSE"]

		return C4_assess_partial_state(state, self.marker, C4_Pruned_MinMax_Player.PARTIAL_WEIGHTS)

	def end_turn(self):
		super().end_turn()
		print(f"Pruned {MinMax_AB_Pruning.get_n_pruned()} states!")


class C4_TQRL_Player(C4_Player):
	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# mirror desirable states with (own tokens, empty tokens) in any given sequence of 4 grid spaces.
	PARTIAL_WEIGHTS = {
		(4, 0): 100,
		(2, 2): 2,
		(3, 1): 5
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state):
		return Tabular_QRL.evaluate(
			game="C4",
			state=state,
			team=self.marker,
			utility_func=self.eval_state
		)

	def eval_state(self, state, terminal):
		# if leaf state (no more moves after) evaluate whether the state is a win or loss
		if terminal:
			winner = C4_determine_winner(state)
			return C4_TQRL_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else C4_TQRL_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else C4_TQRL_Player.TERMINAL_WEIGHTS["LOSE"]

		return C4_assess_partial_state(state, self.marker, C4_TQRL_Player.PARTIAL_WEIGHTS)


class C4_DQL_Player(C4_Player):
	TERMINAL_WEIGHTS = {
		"WIN": 100,
		"BASE": 0,
		"LOSE": -100
	}

	# mirror desirable states with (own tokens, empty tokens) in any given sequence of 4 grid spaces.
	PARTIAL_WEIGHTS = {
		(4, 0): 100,
		(2, 2): 2,
		(3, 1): 5
	}

	def __init__(self, game, team):
		super().__init__(game, team)

	def choose_next_move(self, state):
		return DQN_RL.evaluate(
			game="C4",
			state=state,
			team=self.marker,
			utility_func=self.eval_state
		)

	def eval_state(self, state, terminal):
		# if leaf state (no more moves after) evaluate whether the state is a win or loss
		if terminal:
			winner = C4_determine_winner(state)
			return C4_DQL_Player.TERMINAL_WEIGHTS["BASE"] if winner is None \
				else C4_DQL_Player.TERMINAL_WEIGHTS["WIN"] if winner == self.marker \
				else C4_DQL_Player.TERMINAL_WEIGHTS["LOSE"]

		return C4_assess_partial_state(state, self.marker, C4_DQL_Player.PARTIAL_WEIGHTS)
