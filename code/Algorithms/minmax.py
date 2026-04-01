class MinMax_Default:
	def __init__(self, game):
		self.game = game
		self.state = game.grid.copy()

	def update_state(self):
		self.state = self.game.grid.copy()

	def evaluate(state, depth, is_max):
		pass