# internal imports
from Solvers.solver import Solver


class BFS_Solver(Solver):
	def __init__(self, game):
		super().__init__(game, "BFS")
		self.queue = []


	def start(self):
		super().start()
		self.root.mark_edge(self.type, None)
		self.root.mark_explored(self.type, 0)
		self.queue.append(self.root)


	def update(self):
		if not self.running:
			return

		if self.exited and self.tile is not None:
			self.tile.mark_on_path(self.type)
			self.tile = self.tile.data[self.type].pred
		else:
			self.frameCount += 1


		if not len(self.queue) == 0 and not self.exited:
			self.tileCount += 1
			# take the first item from the priority queue (closest to root node)
			tile = self.queue.pop(0)
			# get previous tile's distance. If root tile.predecessor == None -> 0, otherwise get tile dist.
			dist = 0 if tile.data[self.type].pred is None else tile.data[self.type].pred.data[self.type].dist + 1
			self.maxDist = self.maxDist if dist <= self.maxDist else dist

			tile.mark_explored(self.type, dist)

			# if reaches goal state, exit successfully
			if tile == self.goal:
				self.on_goal_reach(tile)
				return

			for n in tile.neighbours:
				# skip neighbour if already explored
				if n.data[self.type].explored:
					continue

				# mark the tile for exploration (marked as 'edge') & set current tile as its predecessor.
				n.mark_edge(self.type, tile)
				self.queue.append(n)
			return

		# exit w/o success if no more tiles to explore.

		if self.tile is None:
			self.pause()


	def reset(self):
		super().reset()
		self.queue = []
