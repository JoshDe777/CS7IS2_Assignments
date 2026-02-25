from pygame import Vector2, Rect
from UI.uielement import UI_Button, UI_InputField, UI_Text, UI_Slider, UI_Panel
from Labyrinth.tile import Tile

# notes to self:
# - min y-distance to new text element, slider: 15
# - min y-distance to new button: button height

default_scale = 45
default_width = 10
default_height = 10

class LabyrinthInterface:
	def __init__(self, game):
		self.game = game
		game.afterUpdate.add_listener(self.update_seed_text)
		self.current_scale = default_scale
		self.current_width = default_width
		self.current_height = default_height
		self.labyrinth_seed = game.labyrinth.get_seed()

		self.pos = Vector2(1155, 360)
		self.panel = UI_Panel(game, self.pos, Vector2(200, 400), "white")
		last_y = -185
		self.header = UI_Text(game=game, text="Joshua's Labyrinth", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.seed_text = UI_Text(game=game, text=f"seed: {self.labyrinth_seed}", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		last_y += 30
		self.seed_input = UI_InputField(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 25), on_submit=self.regen_maze_seeded, initial_text=str(self.labyrinth_seed))
		last_y += 15
		self.separator1 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		last_y += 15
		self.legend_label = UI_Text(game=game, text=f"Color Legend:", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.legend1 = UI_Text(game=game, text=f"yellow = start", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.legend2 = UI_Text(game=game, text=f"green = goal", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)
		
		# labyrinth scale slider
		last_y += 15
		self.scale_desc = UI_Text(game=game, text=f"labyrinth scale : {self.current_scale}%", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.scale_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=5, max_val=100, value=self.current_scale, on_slide_callback=self.adjust_scale)
		last_y += 15
		self.separator3 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)
		
		# button: regenerate maze
		last_y += 40
		self.regen_button = UI_Button(game=game, buttonText="Generate Random Maze", rect=Rect(0, 0, 175, 50), on_press_action=self.regen_maze)
		self.regen_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 25
		self.separator4 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# input fields: maze size
		last_y += 15
		self.scale_setter_text = UI_Text(game=game, text="Maze Dimensions:", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.scale_setter_text2 = UI_Text(game=game, text="(changes automatically make a new maze!)", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=14)
		last_y += 25
		self.scale_x_text = UI_Text(game=game, text=f"width={self.current_width}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.x_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=2, max_val=50, value=self.current_width, on_slide_callback=self.adjust_width, on_release_callback=self.regen_maze_discard)
		last_y += 15
		self.scale_y_text = UI_Text(game=game, text=f"height={self.current_height}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.y_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=2, max_val=50, value=self.current_height, on_slide_callback=self.adjust_height, on_release_callback=self.regen_maze_discard)

		# preset buttons for largest and 10x10 (default) maze
		last_y += 40
		self.ten_scale_button = UI_Button(game=game, buttonText="10x10 Scale", rect=Rect(0, 0, 75, 25), on_press_action=self.preset_10_10)
		self.ten_scale_button.set_position(self.pos + Vector2(-50, last_y))
		self.fifty_scale_button = UI_Button(game=game, buttonText="50x50 Scale", rect=Rect(0, 0, 75, 25), on_press_action=self.preset_50_50)
		self.fifty_scale_button.set_position(self.pos + Vector2(50, last_y))


	def update_seed_text(self, _, __):
		self.labyrinth_seed = self.game.labyrinth.get_seed()
		self.seed_text.set_text(f"seed: {self.labyrinth_seed}")

	def regen_maze(self):
		self.game.labyrinth.set_seed()
		self.game.labyrinth.regenerate()
		self.labyrinth_seed = self.game.labyrinth.get_seed()
		self.seed_input.set_text(str(self.labyrinth_seed))

	def regen_maze_seeded(self, seed):
		self.game.labyrinth.set_seed(seed)
		self.game.labyrinth.regenerate()

	def regen_maze_discard(self, _):
		self.game.labyrinth.regenerate()

	def adjust_scale(self, new_scale):
		Tile.set_scale(new_scale)
		self.current_scale = new_scale
		self.scale_desc.set_text(f"labyrinth scale : {self.current_scale:.2f}%")

	def adjust_width(self, new_width):
		if self.current_width == int(new_width):
			return

		self.current_width = int(new_width)
		self.game.labyrinth.set_size(new_width, None)
		self.scale_x_text.set_text(f"width={self.current_width}")

	def adjust_height(self, new_height):
		if self.current_height == int(new_height):
			return

		self.current_height = int(new_height)
		self.game.labyrinth.set_size(None, new_height)
		self.scale_y_text.set_text(f"height={self.current_height}")

	def preset_50_50(self):
		new_scale = 14.0
		Tile.set_scale(new_scale)
		self.current_scale = new_scale
		self.scale_desc.set_text(f"labyrinth scale : {self.current_scale:.2f}%")
		self.scale_slider.set_value(new_scale)

	def preset_10_10(self):
		new_scale = 70.0
		Tile.set_scale(new_scale)
		self.current_scale = new_scale
		self.scale_desc.set_text(f"labyrinth scale : {self.current_scale:.2f}%")
		self.scale_slider.set_value(new_scale)

class SolverInterface:
	def __init__(self, game):
		self.game = game
		self.activeSolver = None

		self.pos = Vector2(125, 360)
		self.panel = UI_Panel(game, self.pos, Vector2(200, 400), "white")
		last_y = -185
		self.header = UI_Text(game=game, text="Solvers:", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.activeSolverText = UI_Text(game=game, text=f"Active Solver: {'None' if self.activeSolver is None else self.activeSolver}", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=18)

		# play & pause buttons
		last_y += 40
		self.ten_scale_button = UI_Button(game=game, buttonText="Pause", rect=Rect(0, 0, 75, 25), on_press_action=self.pause_solver)
		self.ten_scale_button.set_position(self.pos + Vector2(-50, last_y))
		self.fifty_scale_button = UI_Button(game=game, buttonText="Resume", rect=Rect(0, 0, 75, 25), on_press_action=self.resume_solver)
		self.fifty_scale_button.set_position(self.pos + Vector2(50, last_y))
		last_y += 15
		self.separator1 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		last_y += 15
		self.legend_label = UI_Text(game=game, text=f"Color Legend:", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.legend1 = UI_Text(game=game, text=f"dark blue = explored", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.legend2 = UI_Text(game=game, text=f"light blue = exploration edge", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		last_y += 35
		self.reset_solver_button = UI_Button(game=game, buttonText="Reset Exploration.", rect=Rect(0, 0, 175, 30), on_press_action=self.reset_solver)
		self.reset_solver_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start BFS", rect=Rect(0, 0, 175, 30), on_press_action=self.start_BFS)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start DFS", rect=Rect(0, 0, 175, 30), on_press_action=self.start_DFS)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start A* 1", rect=Rect(0, 0, 175, 30), on_press_action=self.start_Astar_1)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start A* 2", rect=Rect(0, 0, 175, 30), on_press_action=self.start_Astar_2)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start MDP Value Iteration", rect=Rect(0, 0, 175, 30), on_press_action=self.start_MDP_Val)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start MDP Policy Iteration", rect=Rect(0, 0, 175, 30), on_press_action=self.start_MDP_Pol)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))

	def reset_solver(self):
		if self.activeSolver is None:
			return

		self.game.solvers[self.activeSolver].reset()
		self.activeSolver = None
		self.update_active_solver_text_UI()

	def start_BFS(self):
		self.activeSolver = "BFS"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()

	def start_DFS(self):
		self.activeSolver = "DFS"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()

	def start_Astar_1(self):
		print("Not implemented!")

	def start_Astar_2(self):
		print("Not implemented!")

	def start_MDP_Val(self):
		print("Not implemented!")

	def start_MDP_Pol(self):
		print("Not implemented!")

	def pause_solver(self):
		if self.activeSolver is None:
			return

		self.game.solvers[self.activeSolver].pause()
		self.activeSolverText.set_text(f"Active Solver: {'None' if self.activeSolver is None else self.activeSolver} (paused)")

	def resume_solver(self):
		if self.activeSolver is None:
			return

		self.game.solvers[self.activeSolver].resume()
		self.update_active_solver_text_UI()

	def update_active_solver_text_UI(self):
		self.activeSolverText.set_text(f"Active Solver: {'None' if self.activeSolver is None else self.activeSolver}")
