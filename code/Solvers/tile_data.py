

class TileData:
	def __init__(self):
		self.dist = 1000000000
		self.pred = None
		self.explored = False

	def set_dist(self, newDist):
		self.dist = newDist

	def explore(self):
		self.explored = True

	def set_pred(self, pred, overwrite: bool=False):
		self.pred = pred if self.pred == None or overwrite else self.pred

	def reset(self):
		self.dist = 1000000000
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
		