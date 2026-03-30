from event import Event

class TTT_Player:
	player_id = 0
	symbol = ['x', 'o']
	symbol_colors = ["red", "blue"]

	def __init__(self, game):
		self.id = TTT_Player.player_id
		TTT_Player.player_id += 1

		self.marker = TTT_Player.symbol[self.id if self.id < 2 else 1]
		self.color = TTT_Player.symbol_colors[self.id if self.id < 2 else 1]
		self.game = game
		self.name = f"Player {self.id + 1}"
		self.turn = False

		self.on_turn_start = Event()
		self.on_turn_start.add_listener(self.start_turn)
		self.on_turn_end = Event()
		self.on_turn_end.add_listener(self.end_turn)

	def place_tile(self, tile_id):
		self.game.place_tile(tile_id, self.marker)

	def start_turn(self):
		self.turn = True

	def end_turn(self):
		self.turn = False
