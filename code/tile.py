from typing_extensions import runtime
import pygame
from pygame import Rect, Surface, Vector2


class Tile:
	tileDim = 45
	
	def __init__(self, pos: Vector2, color: str):
		self.pos = pos
		self.neighbours = []
		self.pathTiles = []
		self.color = color

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