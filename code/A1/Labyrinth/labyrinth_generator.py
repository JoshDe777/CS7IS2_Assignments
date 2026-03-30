import random
from pygame import Surface, Vector2
from Labyrinth.tile import Tile

cardinal_directions = [
	Vector2(0, 1),		# North
	Vector2(1, 0),		# East
	Vector2(0, -1),		# South
	Vector2(-1, 0)		# West
]
"""An array containing vectors representing the four carinal directions in order: NORTH - EAST - SOUTH - WEST (clockwise from north)"""

def type_to_color(_type: str) -> str:
	"""
	Assigns a tile color based on tile type.\n
	Goal tiles get 'green',
	Start/Root tiles get 'yellow',
	default return value is 'white'

	@returns:
		a string representing the color as supported by pygame (https://www.pygame.org/docs/ref/color_list.html)
	"""
	if _type is None:
		return "white"

	return "indigo" if _type == "goal" else \
		"orchid2" if _type == "start" else \
		"white"

class Labyrinth:
	"""
	Object representing a Labyrinth created by Joshua O'Donnell using a Wilson Loop-Erased Walk algorithm.

	Stores all labyrinth tiles accessible by tile coordinates, the ability to regenerate a maze based on a custom or random seed, 
	and data access for UI and Solvers alike.
	"""
	def __init__(self, size: Vector2, game, worldOffset, seed=-1):
		self.size = size
		self.seed = seed
		self.labyrinth = []
		self.worldOffset = worldOffset
		self.pos_offset = Vector2(int(-self.size[0] / 2), int(-self.size[1] / 2))
		self.build_labyrinth()
		game.afterUpdate.add_listener(self.draw_labyrinth)

#region UI Accessor Functions
	def regenerate(self):
		"""Regenerates a labyrinth from scratch using the active seed and dimensions."""
		self.labyrinth = []
		self.pos_offset = Vector2(int(-self.size[0] / 2), int(-self.size[1] / 2))
		self.build_labyrinth()


	def set_seed(self, seed: int=-1):
		"""Gives the labyrinth generator a seed for its random chooser. 
		if seed = -1 (default) a random seed is generated at the next generation."""
		self.seed = seed


	def get_seed(self):
		"""Returns the active labyrinth seed as an integer (I think...?)."""
		return self.seed
	

	def set_size(self, width: int=None, height: int=None):
		"""
		Sets the labyrinth's dimension values to width x height. 
		New dimensions must be integers, any deviation will be rounded to an integer if not blocked by type settings.
		Ignoring one dimension (width or height == None) will retain the current value for that dimension.
		"""
		current = self.size
		self.size = (
			int(width) if width is not None else current[0], 
			int(height) if height is not None else current[1]
		)
#endregion

#region Solver Accessor Functions
	def reset(self, _type: str):
		"""Reset all tile data for the maze."""
		for tile in self.labyrinth:
			if tile is not None:
				tile.reset(_type, markov_reset=True)


	def get_root(self):
		"""Get the tile from which the solver is to start."""
		return self.get_tile_at(self.start)


	def get_goal(self):
		"""Get the tile towards which the solver is to go."""
		return self.get_tile_at(self.goal)
#endregion

#region Labyrinth Generation Helpers
	def is_sufficiently_explored(self, grid: list, percent: float) -> bool:
		"""
		Determines whether enough tiles of the labyrinth have been generate to fulfill the generation conditions.
		/!\\ Not enforced, but setting percent values > 1.0 will lead to infinite generation, unless the grid is larger than the labyrinth's expected dimensions
		
		@returns:
			bool: representing whether the amount of tiles explored in the grid is >= percent * width * height.
		"""
		_sum = 0
		for dim in grid:
			for tile in dim:
				_sum += tile

		return _sum >= (percent * self.size[0] * self.size[1])


	def get_unexplored_tiles(self, grid: list) -> list:
		"""
		Get the grid-space coordinates of all tiles in the grid that haven't been marked as explored (val == 0) in a list.
		"""
		res = []
		wLen, hLen = len(grid), len(grid[0])
		for i in range(wLen):
			for j in range(hLen):
				if grid[i][j] == 0:
					res.append(Vector2(i, j))

		return res


	def is_valid(self, pos: Vector2, grid: list) -> bool:
		"""Checks whether a given coordinate is valid (within the labyrinths's bounds, i.e. each coord > 0 and <= expected width (x) or height (y))"""
		in_grid = pos.x >= 0 and pos.y >= 0 and pos.x < self.size[0] and pos.y < self.size[1]
		return in_grid


	def is_in_labyrinth(self, pos: Vector2) -> bool:
		"""Checks whether there is already an existing tile at the given (grid-space) coord in the labyrinth."""
		for tile in self.labyrinth:
			if tile.pos == pos:
				return True

		return False


	def get_tile_at(self, pos: Vector2):
		"""Returns the tile at the given coordinate if any is found, or None otherwise."""
		for tile in self.labyrinth:
			if tile.pos == pos:
				return tile

		return None
#endregion

	def build_labyrinth(self):
		"""
		Executes the generation process for the labyrinth:
		- Generate a seed if requested (seed == -1)
		- Compute random, differring start and goal positions (min labyrinth size 2x2 !)
		- Does random walks from random, unexplored tiles until every tile of the maze is explored.
		"""
		# establish a random goal point within the maze
		self.seed = self.seed if self.seed != -1 else random.randrange(1_000_000)
		self.rnd = random.Random(self.seed)
		grid = [[0 for _ in range(self.size[1])] for _ in range(self.size[0])]
		self.goal = Vector2(self.rnd.randint(0, self.size[0]-1), self.rnd.randint(0, self.size[1]-1))
		goal_tile = Tile(pos=self.goal, color=type_to_color("goal"))
		self.labyrinth.append(goal_tile)

		self.start = self.goal
		# poll a random start position until start != goal, unless there's only one tile (1x1=1)
		while self.start == self.goal or (self.size[0] * self.size[1] == 1):
			self.start = Vector2(self.rnd.randint(0, self.size[0]-1), self.rnd.randint(0, self.size[1]-1))

		while(not self.is_sufficiently_explored(grid, 1.0)):
			unvisited_cells = self.get_unexplored_tiles(grid)
			cell_index = self.rnd.randint(0, len(unvisited_cells) - 1)
			self.random_walk(unvisited_cells[cell_index], grid)


	def random_walk(self, start_pos: Vector2, grid: list):
		"""
		Performs a loop-erased random (Wilson) walk from the given start position.
		/!\\ Requires at least one tile already in the labyrinth 'marked' as generated (member of self.labyrinth list)

		Process description:
		- "walks" in a random cardinal direction (no diagonal movement) until reaching a tile that has already been added to the maze.
		- if it reaches a tile that is already part of the current path, 
		'forgets' all tiles explored since the last time that tile was explored to avoid loops.
		- At the end of the walk, generate all retained tiles and connect them as neighbours between themselves.
		"""
		# loop-erased Wilson walk.
		current_path = []
		visited = {}

		current_path.append(start_pos)
		current = start_pos

		while not self.is_in_labyrinth(current):

			neighbours = []
			for _dir in cardinal_directions:
				n = current + _dir
				if(self.is_valid(n, grid)):
					neighbours.append(n)

			next_pos = neighbours[self.rnd.randint(0, len(neighbours) - 1)]
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


	def draw_labyrinth(self, screen: Surface, worldOffset: Vector2):
		"""Instruct the pygame system to display the labyrinth on screen."""
		if not self.labyrinth or len(self.labyrinth) == 0:
			return

		for tile in self.labyrinth:
			if tile is not None:
				tile.draw(screen, worldOffset, self.pos_offset)
