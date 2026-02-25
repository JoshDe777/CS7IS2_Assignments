class Solver:
	"""Virtual/Abstract parent class for solver algorithms."""
	def __init__(self, game, type: str):
		game.update.add_listener(self.update)
		self.running = False
		self.game = game
		self.type = type
		self.frameCount = 0
		self.tileCount = 0
		self.maxDist = -1
		self.exited = False

	def is_running(self):
		"""poll the solver's status, whether it is running or not."""
		return self.running

	def start(self):
		"""Instruct the solver to start running."""
		self.root = self.game.labyrinth.get_root()
		self.goal = self.game.labyrinth.get_goal()
		self.running = True
		self.tile = None

	def pause(self):
		"""Freeze the solver at it's current state"""
		self.running = False

	def resume(self):
		"""Resume the solver's run."""
		self.running = True

	def update(self):
		"""Update the solver/maze state."""
		if not (self.running or self.exited):
			return

		if self.tile is None:
			self.pause()
			return

		self.tile.mark_on_path()
		self.tile = self.tile.data[self.type].pred

	def abort(self):
		"""Abort an active run."""
		self.running = False
		self.reset()

	def reset(self):
		"""Reset the solver and maze's state."""
		self.running = False
		self.exited = False
		self.game.labyrinth.reset(self.type)
		self.frameCount = 0
		self.tileCount = 0
		self.maxDist = -1

	def on_goal_reach(self, goal_tile):
		print(f"Solver of type {self.type} reached Goal State!\nStats:\n" \
			f"- {self.frameCount} frames (~{(self.frameCount / 60.0):.3f}s),\n"\
			f"- {self.tileCount} tiles explored,\n"\
			f"- Solution depth: {goal_tile.data[self.type].dist},\n"\
			f"- Maximum explored depth: {self.maxDist}\n--------------------"
		)
		self.exited = True
		self.tile = goal_tile
