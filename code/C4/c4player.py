from event import Event

class C4_Player:
	player_id = 0
	symbol = ['x', 'o']
	symbol_colors = ["red", "yellow"]

	def __init__(self, game):
		self.id = C4_Player.player_id
		C4_Player.player_id += 1

		self.marker = C4_Player.symbol[self.id if self.id < 2 else 1]
		self.color = C4_Player.symbol_colors[self.id if self.id < 2 else 1]
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
