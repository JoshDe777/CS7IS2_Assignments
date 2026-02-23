from random import randint
from pygame import Surface, Vector2
from tile import Tile

cardinal_directions = [
	Vector2(0, 1),		# North
	Vector2(1, 0),		# East
	Vector2(0, -1),		# South
	Vector2(-1, 0)		# West
]

def type_to_color(_type: str):
	if _type is None:
		return "white"

	return "green" if _type == "goal" else \
		"yellow" if _type == "start" else \
		"white"

class Labyrinth:
	def __init__(self, size: Vector2, game, worldOffset):
		self.size = size
		self.labyrinth = []
		self.worldOffset = worldOffset
		self.pos_offset = Vector2(int(-self.size[0] / 2), int(-self.size[1] / 2))
		self.build_labyrinth()
		game.afterUpdate.add_listener(self.draw_labyrinth)

	def is_sufficiently_explored(self, grid: list, percent: float) -> bool:
		_sum = 0
		for dim in grid:
			for tile in dim:
				_sum += tile

		return _sum >= (percent * self.size[0] * self.size[1])

	def get_unexplored_tiles(self, grid: list) -> list:
		res = []
		wLen, hLen = len(grid), len(grid[0])
		for i in range(wLen):
			for j in range(hLen):
				if grid[i][j] == 0:
					res.append(Vector2(i, j))

		return res

	def is_valid(self, pos: Vector2, grid: list, path: list) -> bool:
		in_grid = pos.x >= 0 and pos.y >= 0 and pos.x < self.size[0] and pos.y < self.size[1]
		not_in_path = True
		for tile in path:
			if tile == pos:
				not_in_path = False
				break

		return in_grid and not_in_path

	def build_labyrinth(self):
		# establish a random goal point within the maze
		grid = [[0 for _ in range(self.size[1])] for _ in range(self.size[0])]
		self.goal = Vector2(randint(0, self.size[0]-1), randint(0, self.size[1]-1))

		self.start = self.goal
		# poll a random start position until start != goal
		while self.start == self.goal:
			self.start = Vector2(randint(0, self.size[0]-1), randint(0, self.size[1]-1))

		self.random_walk(self.goal, grid)
		self.random_walk(self.start, grid)
		while(not self.is_sufficiently_explored(grid, 1.0)):
			unvisited_cells = self.get_unexplored_tiles(grid)
			cell_index = randint(0, len(unvisited_cells) - 1)
			self.random_walk(unvisited_cells[cell_index], grid)

		print(f"Generated Maze with {len(self.labyrinth)} tiles! (dimensions {self.size[0]}x{self.size[1]})")

	def random_walk(self, start_pos: Vector2, grid: list):
		current_path = []
		grid[int(start_pos.x)][int(start_pos.y)] = 1
		current_path.append(start_pos)

		current = start_pos
		while(True):
			neighbours = []
			for _dir in cardinal_directions:
				n = current + _dir
				if(self.is_valid(n, grid, current_path)):
					neighbours.append(n)

			if len(neighbours) == 0:
				break

			next_pos = neighbours[randint(0, len(neighbours) - 1)]
			current_path.append(next_pos)
			current = next_pos

			if(self.is_in_labyrinth(current)):
				break

		last = None
		for pos in current_path:
			grid[int(pos.x)][int(pos.y)] = 1

			# get tile at pos.
			tile = self.get_tile_at(pos)

			# create new tile if none exists.
			if not tile:
				tile_type = "goal" if pos==self.goal else "start" if pos==self.start else None
				tile = Tile(pos=pos, color=type_to_color(tile_type))
				self.labyrinth.append(tile)


			if last is not None:
				tile.AddNeighbour(last)
				last.AddNeighbour(tile)

			last = tile


	def is_in_labyrinth(self, pos: Vector2) -> bool:
		for tile in self.labyrinth:
			if tile.pos == pos:
				return True

		return False

	def get_tile_at(self, pos: Vector2):
		for tile in self.labyrinth:
			if tile.pos == pos:
				return tile

		return None

	def draw_labyrinth(self, screen: Surface, worldOffset: Vector2):
		for tile in self.labyrinth:
			if tile is not None:
				tile.draw(screen, worldOffset, self.pos_offset)
