import pygame
from pygame import Rect, Surface, Vector2

from Solvers.tile_data import BFS_Data, DFS_Data

ON_BEST_PATH_COLOR = "chartreuse2"
EXPLORED_COLOR = "blue3"
VISITED_COLOR = "cadetblue2"
EDGE_COLOR = "darkslategray2"

class Tile:
	tileDim = 45
	
	def __init__(self, pos: Vector2, color: str):
		self.pos = pos
		self.neighbours = []
		self.pathTiles = []
		self.baseColor = color
		self.color = color
		self.data = {
			"BFS": BFS_Data(),
			"DFS": DFS_Data()
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

	def reset(self, _type: str):
		self.color = self.baseColor
		self.data[_type].reset()

	def mark_edge(self, _type: str, pred):
		self.color = EDGE_COLOR if self.baseColor == "white" else self.baseColor
		# case BFS & DFS:
		self.data[_type].set_pred(pred)

		if _type == "BFS":
			self.data[_type].explore()
		elif _type == "DFS":
			# visualization correction for DFS which can re-mark already explored tiles.
			if self.data[_type].explored:
				self.color = EXPLORED_COLOR if self.baseColor == "white" else self.baseColor

	def mark_visited(self, _type: str):
		self.color = VISITED_COLOR if self.baseColor == "white" else self.baseColor

	def mark_explored(self, _type: str, dist):
		self.color = EXPLORED_COLOR if self.baseColor == "white" else self.baseColor
		# case both BFS & DFS!
		self.data[_type].set_dist(dist)
		if _type == "DFS":
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