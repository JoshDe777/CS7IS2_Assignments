import pygame
from pygame import Surface, Vector2
from C4.c4player import C4_Player, C4_Baseline_Player
from event import Event

cardinal_dirs = [
	Vector2(-1, 1), 
	Vector2(0, 1), 
	Vector2(1, 1), 
	Vector2(1, 0)
]

class Connect4:

	box_color = "black"
	bound_width = 2
	marker_fill = 0.9

	type_dict = {
		"Human": C4_Player,
		"Baseline": C4_Baseline_Player
	}

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
		for i in range(7):
			for j in range(7):
				self.rect_grid[i].append(
					pygame.Rect(
						worldOffset.x + (i - 3) * self.scale.x,
						worldOffset.y + (-j + 2.5) * self.scale.y,
						self.scale.x if j < 6 else 0.8 * self.scale.x,
						self.scale.y if j < 6 else 0.8 * self.scale.y
					)
				)

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

	def set_player(self, idx, player_type):
		if player_type not in self.type_dict.keys():
			print(f"Invalid Connect 4 player type '{player_type}'!")
			return

		if idx == 1:
			self.p1 = Connect4.type_dict[player_type](self.game, 1)
		elif idx == 2:
			self.p2 = Connect4.type_dict[player_type](self.game, 2)
		else:
			print("Invalid player number! Please use numbers 1 or 2!")

	def start(self):
		self.reset()
		self.running = True
		self.start_turn(self.p1)

	def reset(self):
		self.grid = [
			[],
			[],
			[],
			[],
			[],
			[],
			[]
		]
		self.running = False
		self.active_player = self.p1

	def start_turn(self, player):
		self.active_player.on_turn_end.invoke()
		self.active_player = player
		self.on_turn_change.invoke(self.active_player.name)
		self.active_player.on_turn_start.invoke()

	def add_to_slot(self, idx):
		print(f"Placing tile at row {idx}.")

		if idx > 6:
			return

		if len(self.grid[idx]) == 6:
			print("Column is already full!")
			return

		self.grid[idx].append(self.active_player.marker)

		winner = self.eval_winner(idx)
		if winner is not None:
			self.on_win(winner)
			return

		self.start_turn(self.p1 if self.active_player != self.p1 else self.p2)

	def is_grid_full(self):
		for col in self.grid:
			if len(col) < 6:
				return False

		return True

	def eval_winner(self, idx: int) -> str:
		# check if exists tile in every cardinal direction and search until marker is either empty or not own.
		# if len == 4 declare winner else none
		# if grid full declare draw
		n = len(self.grid[idx]) - 1
		team = self.grid[idx][n]
		streak = 0

		for _dir in cardinal_dirs:
			streak = 0
			i = 0
			# forward pass:
			while not streak >= 4:
				# x, y = (idx, n) + i * _dir
				x = int(idx + i * _dir.x)
				y = int(n + i * _dir.y)

				# if x, y invalid exit fwd pass
				if x < 0 or x >= len(self.grid):
					break
				if y < 0 or y >= len(self.grid[x]):
					break

				# if [x, y] != team exit fwd pass
				if self.grid[x][y] != team:
					break

				# else streak += 1 and continue (i += 1)
				streak += 1
				i += 1

			# reset i (to 1 not 0 because otherwise counts newly placed token twice)
			i = 1

			while not streak >= 4:
			# backward pass:
				# x, y = (idx, n) - i * _dir
				x = int(idx - i * _dir.x)
				y = int(n - i * _dir.y)

				# if x, y invalid exit back pass
				if x < 0 or x >= len(self.grid):
					break
				if y < 0 or y >= len(self.grid[x]):
					break

				# if [x, y] != team exit back pass
				if self.grid[x][y] != team:
					break

				# else streak += 1 and continue (i += 1)
				streak += 1
				i += 1

			# exit check if there's a winner
			if streak >= 4:
				break

		if not streak >= 4:
			return None if not self.is_grid_full() else "Draw"

		return self.p1.name if team == self.p1.marker else self.p2.name

	def on_win(self, winner):
		self.running = False
		self.on_game_end.invoke(winner)

	def get_input(self, events):
		if not self.running or not self.enabled:
			return

		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN and not getattr(event, 'consumed', False):
				for idx in range(len(self.rect_grid)):
					rect = self.rect_grid[idx][6]
					if rect.collidepoint(event.pos):
						self.add_to_slot(idx)

	def draw_arrow(self, window: Surface, rect: pygame.Rect, color):
		cx = rect.centerx
		top = rect.top
		bot = rect.bottom
    
		shaft_w = rect.width * 0.3    # width of the vertical shaft
		head_w  = rect.width * 0.75   # width of the arrowhead base
		split   = rect.top + rect.height * 0.5  # where shaft ends and head begins

		points = [
			(cx - shaft_w / 2, top),       # shaft top-left
			(cx + shaft_w / 2, top),       # shaft top-right
			(cx + shaft_w / 2, split),     # shaft bottom-right
			(cx + head_w  / 2, split),     # head top-right
			(cx,               bot),       # arrow tip
			(cx - head_w  / 2, split),     # head top-left
			(cx - shaft_w / 2, split),     # shaft bottom-left
		]
		pygame.draw.polygon(window, color, points)

	def draw_tiles(self, window: Surface, worldOffset: Vector2):
		if not self.enabled:
			return

		for col in range(7):
			for row in range(6):
				rect = self.rect_grid[col][row]
				pygame.draw.rect(window, "dodgerblue2", rect)
				pygame.draw.rect(window, self.box_color, rect, self.bound_width)

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

			self.draw_arrow(window, self.rect_grid[col][6], "green")
