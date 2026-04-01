from event import Event
from pygame import Vector2

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
		self.game.place_tile(tile_id, self.marker)

	def start_turn(self):
		self.turn = True

	def update(self):
		pass

	def end_turn(self):
		self.turn = False


class C4_Baseline_Player(C4_Player):
	WEIGHTS = {
		"CAN_WIN": 10,
		"BLOCK_OPP": 9,
		"LINE": 2,			# multiplies by length! -> max val = 6 (or 8 but that's CAN_WIN)
		"MAX_NEIGHBOURS": 4,
		"NONE": 1
	}

	def __init__(self, game, team):
		super().__init__(self, game, team)

	def update(self):
		if not self.turn or not self.game.c4.running:
			return

		self.eval_state

	def eval_state(self):
		# for every column:
			# forward & backward pass of values -> can_win, line_length
			# both from own and opponent POV	-> block
		pass
		

	def eval_tile(self, state, idx):
		team = self.marker
		for _dir in cardinal_dirs:
			streak = 0
			i = 0
			# forward pass:
			while not streak >= 4:
				# x, y = (idx, n) + i * _dir
				x = int(idx + i * _dir.x)
				y = int(n + i * _dir.y)

				# if x, y invalid exit fwd pass
				if x < 0 or x >= len(self.grid):
					break
				if y < 0 or y >= len(self.grid[x]):
					break

				# if [x, y] != team exit fwd pass
				if self.grid[x][y] != team:
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
				if x < 0 or x >= len(self.grid):
					break
				if y < 0 or y >= len(self.grid[x]):
					break

				# if [x, y] != team exit back pass
				if self.grid[x][y] != team:
					break

				# else streak += 1 and continue (i += 1)
				streak += 1
				i += 1

			# exit check if there's a winner
			if streak >= 4:
				break
