import random
from Solvers.markov_solver import Markov_Solver

class MDP_Policy(Markov_Solver):
	def __init__(self, game):
		super().__init__(game, "MDP_Policy")

	def start(self):
		super().start()
		self.goal.SetPolicy(None)
		self.evaluated = False
		self.improved = False

		for tile in self.game.labyrinth.labyrinth:
			if tile == self.goal:
				continue

			tile.SetPolicy(random.choice(tile.neighbours))

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


		########## Policy Evaluation ##########
		if not self.evaluated:

			val_dict = {}
			for tile in self.game.labyrinth.labyrinth:
				if tile == self.goal:
					continue

				policy_tile = tile.data[self.type].get_policy()
				reward = self.goal_reward if tile == self.goal else self.living_reward
				val_dict[tile] = reward + self.discount * policy_tile.data[self.type].get_value()
				
			disparity_exit = True

			for tile, val in val_dict.items():
				disp = abs(tile.data[self.type].get_value() - val)

				disparity_exit = disparity_exit and disp < self.delta_threshold
				tile.data[self.type].set_value(val)
				tile.set_markov_color(val)

			if disparity_exit:
				self.evaluated = True
				print("Starting Policy Improvement.")

			return

		########## Policy Improvement ##########
		policy_stability_exit = False
		
		policy_stability_exit = True
		for tile in self.game.labyrinth.labyrinth:
			best_policy = None
			best_value = -1000000000.0

			for n in tile.neighbours:
				reward = self.goal_reward if n == self.goal else self.living_reward
				value = reward + self.discount * n.data[self.type].get_value()
				if value > best_value:
					best_value = value
					best_policy = n

			if best_policy != tile.data[self.type].get_policy():
				tile.SetPolicy(best_policy)
				policy_stability_exit = False
			else:
				tile.set_policy_color()

		if policy_stability_exit:
			self.on_goal_reach(self.goal)
		else:
			self.evaluated = False
			print("Starting Evaluation")
