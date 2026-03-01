import pygame
from pygame import Rect, Surface, Vector2, Color
from pygame.math import clamp

from Solvers.tile_data import AStarData, BFS_Data, DFS_Data, MarkovValueData

ON_BEST_PATH_COLOR = Color("chartreuse2")
EXPLORED_COLOR = Color("blue3")
EDGE_COLOR = Color("cadetblue2")

class Tile:
	tileDim = 45
	max_tile_val = 1.0
	
	def __init__(self, pos: Vector2, color: str):
		self.pos = pos
		self.neighbours = []
		self.pathTiles = []
		self.baseColor = color
		self.color = color
		self.data = {
			"BFS": BFS_Data(),
			"DFS": DFS_Data(),
			"A_Star_1": AStarData(euclidean=True),
			"A_Star_2": AStarData(euclidean=False),
			"MDP_Value": MarkovValueData()
		}

	def AddNeighbour(self, tile):
		if self == tile:
			raise RuntimeError("Attempting to add own object as a neighbour!")

		self.neighbours.append(tile)
		_dir = (Vector2(tile.pos) - self.pos).normalize()
		self.pathTiles.append(_dir)

	def IsNeighbour(self, pos: Vector2):
		for tile in self.neighbours:
			if tile.pos == pos:
				return True

		return False

	def set_scale(new_scale: float):
		Tile.tileDim = new_scale

	def reset(self, _type: str, markov_reset: bool = False):
		self.color = self.baseColor
		self.data[_type].reset()

		if markov_reset and _type in ["MDP_Value", "MDP_Policy"]:
			self.data[_type].full_reset()

	def set_markov_color(self, _type: str, m_val: float):
		# set tile color to red if at maximum negative value, green if positive maximum value. Black if m_val = 0.
		self.max_tile_val = max(m_val, self.max_tile_val)
		val_normalized = clamp(m_val / self.max_tile_val, -1, 1)
		self.color = Color(int(max(0, -val_normalized) * 255), int(max(0, val_normalized) * 255), 0, 255)

	def mark_edge(self, _type: str, pred):
		self.color = EDGE_COLOR if self.baseColor == "white" else self.baseColor
		# case BFS & DFS:
		self.data[_type].set_pred(pred)

		if _type in ["BFS", "MDP_Value", "MDP_Policy"]:
			self.data[_type].explore()

	def mark_explored(self, _type: str, dist):
		self.color = EXPLORED_COLOR if self.baseColor == "white" else self.baseColor

		# case both BFS & DFS but not A*!
		if _type not in ["A_Star_1", "A_Star_2"]:
			self.data[_type].set_dist(dist)

		if _type in ["DFS", "A_Star_1", "A_Star_2"]:
			self.data[_type].explore()


	def mark_on_path(self, _type: str):
		self.color = ON_BEST_PATH_COLOR if self.baseColor == "white" else self.baseColor

	def draw(self, screen: Surface, worldOffset: Vector2, grid_offset: Vector2):
		pygame.draw.rect(screen, self.color, Rect(
			worldOffset.x + self.tileDim * (self.pos.x + grid_offset.x - 0.5),
			worldOffset.y + self.tileDim * (self.pos.y + grid_offset.y + 0.5),
			self.tileDim/3, self.tileDim/3
		))

		for tile in self.pathTiles:
			tile_border_offset = 0.9 * tile
			pygame.draw.rect(screen, self.color, Rect(
				worldOffset.x + self.tileDim * (self.pos.x + grid_offset.x + tile_border_offset.x / 3 - 0.5), 
				worldOffset.y + self.tileDim * (self.pos.y + grid_offset.y + tile_border_offset.y / 3 + 0.5), 
				self.tileDim/3, self.tileDim/3
			))

	def __eq__(self, other):
		if not isinstance(other, Tile):
			return False

		return self.pos == other.pos

	def __hash__(self):
		return hash((int(self.pos.x), int(self.pos.y)))