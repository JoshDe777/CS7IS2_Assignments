import math
from pygame import Vector2

class TileData:
	def __init__(self):
		self.dist = float("inf")
		self.pred = None
		self.explored = False

	def set_dist(self, newDist):
		self.dist = newDist

	def explore(self):
		self.explored = True

	def set_pred(self, pred, overwrite: bool=False):
		self.pred = pred if self.pred == None or overwrite else self.pred

	def reset(self):
		self.dist = float("inf")
		self.pred = None
		self.explored = False


class BFS_Data(TileData):
	def __init__(self):
		super().__init__()
		

	def reset(self):
		super().reset()


class DFS_Data(TileData):
	def __init__(self):
		super().__init__()
		self.is_root = False

	def set_pred(self, pred, _: bool=True):
		# no pred if root & no overwrite
		super().set_pred(None if self.is_root else pred, False)

	def reset(self):
		super().reset()
		

class AStarData(TileData):
	# dist = cost to tile
	def __init__(self, euclidean: bool=True):
		super().__init__()
		self.euclidean = euclidean
		self.score = float("inf")
		self.is_root = False

	def heuristic(self, pos: Vector2, goalPos: Vector2):
		"""Automatically determines the heuristic based on the solver's type. Defaults to Euclidean distance."""
		return self.heuristic_1(pos, goalPos) if self.euclidean else self.heuristic_2(pos, goalPos)

	def heuristic_1(self, pos: Vector2, goalPos: Vector2):
		"""Euclidean Distance Heuristic: |goalPos - pos|"""
		return (goalPos - pos).magnitude()

	def heuristic_2(self, pos: Vector2, goalPos: Vector2):
		"""Manhattan Distance Heuristic: (goalPos.x - pos.x) + (goalPos.y - pos.y)"""
		return math.fabs((goalPos.x - pos.x) + (goalPos.y - pos.y))

	def set_pred(self, pred, _: bool=True):
		# no pred if root but overwrite predecessor if necessary.
		super().set_pred(None if self.is_root else pred, True)

	def set_score(self, score: float) -> bool:
		"""
		Overwrites the current score if it's better (lower) than the existing value.
		"""
		self.score = min(score, self.score)

	def reset(self):
		super().reset()
		self.score = float("inf")


class MarkovValueData(TileData):
	def __init__(self):
		super().__init__()
		self.value = 0.0

	def get_value(self) -> float:
		return self.value

	def set_value(self, value):
		self.value = value

	def full_reset(self):
		# extra reset in case also needs to reset markov values
		self.reset()
		self.value = 0.0


class MarkovPolicyData(TileData):
	pass
		