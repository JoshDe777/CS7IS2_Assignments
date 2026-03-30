import pygame
from pygame import Surface, Vector2

class Connect4:

	box_color = "black"
	bound_width = 2
	marker_fill = 0.9

	def __init__(self, game, worldOffset, player1, player2):
		self.scale = 100 * Vector2(1, 1)
		self.enabled = False
		self.game = game
		# 7x6 grid; 
		self.grid = [
			[],
			[],
			[],
			[],
			[],
			[],
			[]
		]
		self.rect_grid = [
			[],
			[],
			[],
			[],
			[],
			[],
			[]
		]
		for i in range(8):
			for j in range(7):
				self.rect_grid[i].append(
					pygame.Rect(
						worldOffset.x + (i - 3) * self.scale.x,
						worldOffset.y + (j - 2.5) * self.scale.y,
						self.scale.x,
						self.scale.y,
					)
				)

	def enable(self):
		self.enabled = True
	
	def disable(self):
		self.enable = False

	def add_to_slot(self, idx):
		if idx > 7:
			return

		idx -= 1
		if len(self.grid[idx]) == 6:
			print("Column is already full!")

	def draw_tiles(self, window: Surface, worldOffset: Vector2):
		if not self.enabled:
			return

		for col in range(8):
			for row in range(7):
				rect = self.rect_grid[col][row]
				pygame.draw.rect(window, (col * 36, row * 42, 255), rect)
				pygame.draw.rect(window, self.box_color, rect, self.bound_width)

				return

				padding = 1 - self.marker_fill
				pad_x = self.scale.x * padding
				pad_y = self.scale.y * padding
				inner = rect.inflate(-pad_x * 2, -pad_y * 2)

				marker = None if row >= len(self.grid[col]) else self.grid[col][row] 
				if marker is None:
					pygame.draw.circle(window, "gray", inner.center, int(min(inner.width, inner.height) / 2))
					continue

				color = self.p1.color if marker == 'x' else self.p2.color if marker == 'o' else "gray"
				pygame.draw.circle(window, color, inner.center, int(min(inner.width, inner.height) / 2))