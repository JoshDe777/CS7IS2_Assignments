from Solvers.markov_solver import Markov_Solver

class MDP_Value(Markov_Solver):
	def __init__(self, game):
		super().__init__(game, "MDP_Value")

	def set_discount(self, new_discount):
		self.discount = new_discount

	def set_living_reward(self, new_reward):
		self.living_reward = new_reward

	def set_max_iters(self, k):
		self.max_iters = k

	def set_goal_reward(self, new_reward):
		self.manual_rewards = True
		self.goal_reward = new_reward

	def set_threshold(self, th):
		self.delta_threshold = th

	def update(self):
		if not self.running:
			return

		if self.exited:
			self.root.reset(self.type)
			self.goal.reset(self.type)
			self.pause()
			return
		else:
			self.frameCount += 1

		# states = any tile
		# actions = move {up, right, down, left}
		# reward: On enter goal: n(tiles) / labyrinth width (50x50 => 2500 / 50 = 50)
		# transition function => 1.0 (fully deterministic)
		# all tiles initialized with a V(s) = 0.0 except goal tile with V(s) = reward

		# for each state / tile in the maze - done using a BFS from the goal tile.
		val_dict = {}

		tile_counter = 0

		for tile in self.game.labyrinth.labyrinth:
			tile.reset(self.type, markov_reset=False)

			max_qval = -1000000000000000.0
			tile_counter += 1

			for n in tile.neighbours:
				# get q value => neighbour.reward + discount * neighbour.value
				reward = self.goal_reward if n == self.goal else self.living_reward
				qval = reward + self.discount * n.data[self.type].get_value()
				# overwrite if better than existing.
				max_qval = max(max_qval, qval)

			val_dict[tile] = max_qval

		total_disparity = 0
		disparity_exit = True
		for tile, val in val_dict.items():
			disp = abs(tile.data[self.type].get_value() - val)
			total_disparity += disp

			disparity_exit = disparity_exit and disp < self.delta_threshold
			tile.data[self.type].set_value(val)
			tile.set_markov_color(val)

		self.disparities.append(f"{(total_disparity / tile_counter):.4f}")

		# exit if average disparity <= threshold.
		self.tileCount += tile_counter
		if self.frameCount >= self.max_iters or disparity_exit:
			self.on_goal_reach(self.goal)
