import csv, os, time

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
		
		self.start_time = time.perf_counter()
		self.labsize = int(self.game.labyrinth.size[0]) * int(self.game.labyrinth.size[1])
		self.csv_save_path = f"Data/runs_{self.labsize}.csv"
		fields = ["Solver Algorithm", "Labyrinth Dimensions [px*px]", "Solution Depth [units]", "Runtime [s]", "Maze Coverage [%]", "Tile Efficiency [units]", "Max Explored Depth [units]"]
		if not os.path.exists(self.csv_save_path):
			with open(self.csv_save_path, 'w') as f:
				writer = csv.writer(f)
				writer.writerow(fields)

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
		dims = f"{int(self.game.labyrinth.size[0])}x{int(self.game.labyrinth.size[1])}"
		self.end_time = time.perf_counter()
		elapsed_time = f"{(self.end_time - self.start_time):.3f}s"
		maze_coverage = f"{(100 * self.tileCount / self.labsize):.2f}%"
		tile_efficiency = f"{(self.tileCount / goal_tile.data[self.type].dist):.4f}"

		
		# algorithm type; labyrinth dimensions; solution depth; runtime; maze coverage; tile efficiency; max depth
		csv_entry = [self.type, dims, goal_tile.data[self.type].dist, elapsed_time, maze_coverage, tile_efficiency, self.maxDist]
		with open(self.csv_save_path, 'a', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(csv_entry)

		self.exited = True
		self.tile = goal_tile
