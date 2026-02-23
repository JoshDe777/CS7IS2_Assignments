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

	def is_valid(self, pos: Vector2, grid: list) -> bool:
		in_grid = pos.x >= 0 and pos.y >= 0 and pos.x < self.size[0] and pos.y < self.size[1]
		return in_grid

	def build_labyrinth(self):
		# establish a random goal point within the maze
		grid = [[0 for _ in range(self.size[1])] for _ in range(self.size[0])]
		self.goal = Vector2(randint(0, self.size[0]-1), randint(0, self.size[1]-1))
		goal_tile = Tile(pos=self.goal, color=type_to_color("goal"))
		self.labyrinth.append(goal_tile)

		self.start = self.goal
		# poll a random start position until start != goal
		while self.start == self.goal:
			self.start = Vector2(randint(0, self.size[0]-1), randint(0, self.size[1]-1))

		self.random_walk(self.start, grid)
		while(not self.is_sufficiently_explored(grid, 1.0)):
			unvisited_cells = self.get_unexplored_tiles(grid)
			cell_index = randint(0, len(unvisited_cells) - 1)
			self.random_walk(unvisited_cells[cell_index], grid)

		print(f"Generated Maze with {len(self.labyrinth)} tiles! (dimensions {self.size[0]}x{self.size[1]})")

	def random_walk(self, start_pos: Vector2, grid: list):
		# loop-erased Wilson walk.
		current_path = []
		visited = {}

		current_path.append(start_pos)
		current = start_pos
		walk_iterations_counter = 0

		while not self.is_in_labyrinth(current):
			walk_iterations_counter += 1
			print(f"Entering iteration {walk_iterations_counter}.")

			neighbours = []
			for _dir in cardinal_directions:
				n = current + _dir
				if(self.is_valid(n, grid)):
					neighbours.append(n)

			next_pos = neighbours[randint(0, len(neighbours) - 1)]
			current = next_pos

			# loop erasure; Truncate paths when reaching a tile already visited in the random walk.
			key = (int(current.x), int(current.y))
			if key in visited:
				loop_start = visited[key]
				current_path = current_path[:loop_start+1]

				visited = {(int(coords.x), int(coords.y)): index for index, coords in enumerate(current_path)}
			else:
				visited[key] = len(current_path)
				current_path.append(next_pos)

			end = current


		print(f"Exiting Random Walk with {len(current_path)} nodes.\n----------")

		last = self.get_tile_at(end)
		for pos in reversed(current_path):
			grid[int(pos.x)][int(pos.y)] = 1

			# get tile at pos.
			tile = self.get_tile_at(pos)

			if tile == last: 
				continue

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
