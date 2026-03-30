from Solvers.solver import Solver
from Labyrinth.tile import Tile

class A_Star_Solver(Solver):
	def __init__(self, game, euclidean: bool):
		super().__init__(game, "A_Star_1" if euclidean else "A_Star_2")
		self.euclidean = euclidean

	def start(self):
		super().start()
		self.edge_tiles = set()
		self.edge_tiles.add(self.root)
		self.root.data[self.type].is_root = True
		self.root.data[self.type].set_dist(0)
		self.root.data[self.type].set_score(self.calculate_score(self.root, 0))

	def select_next(self) -> Tile:
		if len(self.edge_tiles) == 0:
			return None

		next_tile = None
		lowest_score = 10000000

		for tile in self.edge_tiles:
			if tile.data[self.type].score < lowest_score:
				lowest_score = tile.data[self.type].score
				next_tile = tile

		return next_tile

	def calculate_score(self, tile: Tile, cost_to_tile: float):
		return cost_to_tile + tile.data[self.type].heuristic(tile.pos, self.goal.pos)

	def update(self):
		if not self.running:
			return

		if self.exited:
			self.tile.mark_on_path(self.type)
			self.tile = self.tile.data[self.type].pred
			if self.tile is None:
				self.pause()
		else:
			self.frameCount += 1

		if len(self.edge_tiles) > 0 and not self.exited:
			current = self.select_next()
			self.edge_tiles.remove(current)

			# data collection
			self.tileCount += 1
			self.maxDist = max(current.data[self.type].dist, self.maxDist)

			if current == self.goal:
				self.on_goal_reach(self.goal)
				return

			# dist is not set for A* hence -1 to debug for invalid values otherwise.
			current.mark_explored(_type=self.type, dist=-1)

			for n in current.neighbours:
				# ignore tiles already processed
				if n.data[self.type].explored:
					continue

				# constant edge cost of 1 in any direction.
				cost_to_next = current.data[self.type].dist + 1
				n_score = self.calculate_score(n, cost_to_next)

				# add tile to processing list if the neighbour's A* Score is lower than its existing score.
				if n_score < n.data[self.type].score:
					n.data[self.type].set_dist(cost_to_next)
					n.data[self.type].set_score(n_score)
					n.mark_edge(_type=self.type, pred=current)

					self.edge_tiles.add(n)
