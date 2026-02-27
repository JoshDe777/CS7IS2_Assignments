from Solvers.solver import Solver

class DFS_Solver(Solver):
	def __init__(self, game):
		super().__init__(game, "DFS")
		self.stack = []

	def start(self):
		super().start()
		self.root.data["DFS"].is_root = True
		self.stack.append(self.root)

	def update(self):
		if not self.running:
			return

		if self.exited and self.tile is not None:
			self.tile.mark_on_path(self.type)
			self.tile = self.tile.data[self.type].pred
			if self.tile is None:
				self.pause()
		else:
			self.frameCount += 1

		if not len(self.stack) == 0:
			self.tileCount += 1
			tile = self.stack.pop()
			# do nothing if current tile is already explored
			if not tile.data[self.type].explored:
				# distance = 0 if no predecessor (root) otherwise predecessor's dist + 1
				dist = 0 if tile.data[self.type].pred is None \
					else tile.data[self.type].pred.data[self.type].dist + 1

				# overwrite max depth if greater than current value.
				self.maxDist = self.maxDist if dist <= self.maxDist else dist
				
				# mark the current tile as explored & save depth value.
				tile.mark_explored(self.type, dist)

				if tile == self.goal:
					self.on_goal_reach(tile)
					return

				# for every neighbour
				for n in tile.neighbours:
					n.mark_edge(self.type, tile)
					self.stack.append(n)

			else:
				tile.mark_explored(self.type, tile.data[self.type].dist)
			return


	def reset(self):
		super().reset()
		self.stack = []
