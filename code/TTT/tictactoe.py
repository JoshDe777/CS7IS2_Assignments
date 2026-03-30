from re import S
from pygame import Surface, Vector2	
import pygame

from event import Event

class TicTacToe:
	neighbours = {
		0: [3, 6, 1, 2, 4, 8, None, None],
		1: [4, 7, 0, 2, None, None, None, None],
		2: [5, 8, 0, 1, 4, 6, None, None],
		3: [0, 6, 4, 5, None, None, None, None],
		4: [1, 7, 3, 5, 0, 8, 2, 6],
		5: [2, 8, 3, 4, None, None, None, None],
		6: [0, 3, 7, 8, 2, 4, None, None],
		7: [1, 4, 6, 8, None, None, None, None],
		8: [2, 5, 6, 7, 0, 4, None, None]
	}
	"""
	2x top-down, 2x left-right, 4x diagonal (null x4 if invalid)
	"""

	grid_to_index = [
		[0, 1, 2],
		[3, 4, 5],
		[6, 7, 8]
	]

	box_color = "black"
	bound_width = 2
	marker_fill = 0.9

	def __init__(self, game, worldOffset, player1, player2):
		self.scale = 100 * Vector2(1, 1)
		self.enabled = False
		self.game = game
		self.grid = [
			"e", "e", "e", 
			"e", "e", "e", 
			"e", "e", "e"
		]

		self.rect_grid = [
			pygame.Rect(
				worldOffset.x - self.scale.x,
				worldOffset.y - self.scale.y,
				self.scale.x,
				self.scale.y,
			), 
			pygame.Rect(
				worldOffset.x,
				worldOffset.y - self.scale.y,
				self.scale.x,
				self.scale.y,
			),
			pygame.Rect(
				worldOffset.x + self.scale.x,
				worldOffset.y - self.scale.y,
				self.scale.x,
				self.scale.y,
			),
			pygame.Rect(
				worldOffset.x - self.scale.x,
				worldOffset.y,
				self.scale.x,
				self.scale.y,
			), 
			pygame.Rect(
				worldOffset.x,
				worldOffset.y,
				self.scale.x,
				self.scale.y,
			),
			pygame.Rect(
				worldOffset.x + self.scale.x,
				worldOffset.y,
				self.scale.x,
				self.scale.y,
			),
			pygame.Rect(
				worldOffset.x - self.scale.x,
				worldOffset.y + self.scale.y,
				self.scale.x,
				self.scale.y,
			), 
			pygame.Rect(
				worldOffset.x,
				worldOffset.y + self.scale.y,
				self.scale.x,
				self.scale.y,
			),
			pygame.Rect(
				worldOffset.x + self.scale.x,
				worldOffset.y + self.scale.y,
				self.scale.x,
				self.scale.y,
			)
		]

		self.p1 = player1
		self.p2 = player2
		self.running = False
		self.active_player = self.p1

		self.on_game_end = Event()
		self.on_turn_change = Event()

		self.game.eventPoller.add_listener(self.get_input)
		self.game.afterUpdate.add_listener(self.draw_tiles)

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False

	def set_player(self, idx, player):
		if idx == 1:
			self.p1 = player
			player.name = "Player 1"
		elif idx == 2:
			self.p2 = player
			player.name = "Player 2"
		else:
			print("Invalid player number! Please use numbers 1 or 2!")

	def start(self):
		self.running = True
		self.start_turn(self.p1)

	def start_turn(self, player):
		self.active_player.on_turn_end.invoke()
		self.active_player = player
		self.on_turn_change.invoke(self.active_player.name)
		player.on_turn_start.invoke()

	def reset(self):
		self.grid = [
			"e", "e", "e", 
			"e", "e", "e", 
			"e", "e", "e"
		]
		self.running = False
		self.active_player = self.p1

	def get_input(self, events):
		# don't react if game hasn't started.
		if not self.running or not self.enabled:
			return

		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				for i in range(len(self.rect_grid)):
					rect = self.rect_grid[i]
					if rect.collidepoint(event.pos):
						self.place_tile(i)

	def eval_winner(self, grid_index: int) -> str:
		"""
		Inspects the current game state to determine whether there is a winner.
		Returns none if the grid is neither full nor contains 3 consecutive markers of the same type.
		Assumes the current grid_index is not 'e' (empty).
		"""
		has_winner = False
		n = self.neighbours.get(grid_index, None)
		if not n:
			print(f"Invalid Grid ID ({grid_index})")
			return None

		# vertical:
		has_winner = self.grid[grid_index] == self.grid[n[0]] == self.grid[n[1]]
		# horizontal
		has_winner = has_winner or (self.grid[grid_index] == self.grid[n[2]] == self.grid[n[3]])
		# diagonal
		if n[4] is not None:
			has_winner = has_winner or (self.grid[grid_index] == self.grid[n[4]] == self.grid[n[5]])
			# case middle box, needs diagonal check both ways
			if n[6] is not None:
				has_winner = has_winner or (self.grid[grid_index] == self.grid[n[6]] == self.grid[n[7]])


		if has_winner:
			self.running = False
			return self.p1.name if self.grid[grid_index] == self.p1.marker else self.p2.name

		# if full grid, declare draw
		if self.grid.count('e') == 0:
			self.running = False
			return "Draw"
		else:
			return None

	def place_tile(self, grid_index: int):
		if grid_index < 0 or grid_index > 8:
			print(f"[ERROR] Invalid grid index ({grid_index})!")
			return

		if self.grid[grid_index] != 'e':
			print("[DENIED] Attempting to place a marker in already occupied tile.")
			return

		self.grid[grid_index] = self.active_player.marker

		winner = self.eval_winner(grid_index)
		if winner is not None:
			self.on_win(winner)
			return

		# update turn
		self.start_turn(self.p1 if self.active_player != self.p1 else self.p2)

	def draw_tiles(self, window: Surface, worldOffset: Vector2):
		if not self.enabled:
			return

		#print("----------------------------------------")
		for row in range(3):
			for column in range(3):
				#print(f"Drawing box at grid pos ({row},{column})")
				# ── Bounding box ──────────────────────────────────────────────
				idx = self.grid_to_index[row][column]
				rect = self.rect_grid[idx]
				pygame.draw.rect(window, self.box_color, rect, self.bound_width)

				# ── Marker ────────────────────────────────────────────────────
				marker = self.grid[idx]
				if marker is None or marker == 'e':
					continue

				padding = 1 - self.marker_fill
				pad_x = self.scale.x * padding
				pad_y = self.scale.y * padding
				inner = rect.inflate(-pad_x * 2, -pad_y * 2)   # shrink inward

				if marker == 'x':
					pygame.draw.line(window, self.p1.color, inner.topleft, inner.bottomright, self.bound_width + 1)
					pygame.draw.line(window, self.p1.color, inner.topright, inner.bottomleft, self.bound_width + 1)
				elif marker == 'o':
					pygame.draw.circle(window, self.p2.color, inner.center, int(min(inner.width, inner.height) / 2), self.bound_width + 1)

	def on_win(self, winner):
		self.on_game_end.invoke(winner)
		if winner == "Draw":
			print(f"The match ends in a draw!")
		else:
			print(f"{winner} wins!")

		self.reset()
