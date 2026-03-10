from Solvers.solver import Solver, csv, os, time
from Labyrinth.tile import Tile

class Markov_Solver(Solver):
	run_id = 37

	def __init__(self, game, _type):
		super().__init__(game, _type)
		self.manual_rewards = False
		self.max_iters = 1000
		# markov properties
		self.delta_threshold = 0.01
		self.discount = 0.93
		self.living_reward = -1.0
		self.goal_reward = 1

	def start(self):
		"""Instruct the solver to start running."""
		self.root = self.game.labyrinth.get_root()
		self.goal = self.game.labyrinth.get_goal()
		self.running = True
		self.tile = None
		self.disparities = []
		
		self.start_time = time.perf_counter()
		self.labsize = int(self.game.labyrinth.size[0]) * int(self.game.labyrinth.size[1])

		# goal tile initialization
		self.goal_reward = self.goal_reward if self.manual_rewards else self.labsize / self.game.labyrinth.size[0]
		Tile.max_tile_val = self.goal_reward
		self.goal.data[self.type].set_value(self.goal_reward)

		self.csv_save_path = f"Data/markov_runs_{self.labsize}.csv"
		fields = ["Solver Algorithm", "Labyrinth Dimensions [px*px]", "Discount", "Living Reward", "Runtime [s]", "Convergence iterations", "Max. Iterations"]
		if not os.path.exists(self.csv_save_path):
			with open(self.csv_save_path, 'w') as f:
				writer = csv.writer(f)
				writer.writerow(fields)

	def on_goal_reach(self, goal_tile):
		# Solver Algorithm, Labyrinth Dimensions [px*px], Runtime [s], n(iterations) to convergence, max n(iterations)
		dims = f"{int(self.game.labyrinth.size[0])}x{int(self.game.labyrinth.size[1])}"
		self.end_time = time.perf_counter()
		elapsed_time = f"{(self.end_time - self.start_time):.3f}s"

		csv_entry = [self.type, dims, self.discount, self.living_reward, elapsed_time, self.frameCount, self.max_iters]

		with open(self.csv_save_path, 'a', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(csv_entry)

		self.exited = True
		self.tile = goal_tile

		self.disparities_save_path = f"Data/markov_disparities_{self.labsize}.csv"
		fields = ["Run ID", "Solver Algorithm", "Labyrinth Dimensions [px*px]", "Iteration", "Disparity"]

		entries = []
		it_count = 0
		for i in self.disparities:
			entries.append([self.run_id, self.type, dims, it_count, i])
			it_count += 1

		if not os.path.exists(self.disparities_save_path):
			with open(self.disparities_save_path, 'w', newline='') as f:
				writer = csv.writer(f)
				writer.writerow(fields)
				writer.writerows(entries)
		else:
			with open(self.disparities_save_path, 'a', newline='') as f:
				writer = csv.writer(f)
				writer.writerows(entries)

		print(f"Last run ID: {self.run_id}")
		self.run_id += 1
