from pygame import Vector2, Rect
from UI.uielement import UI_Button, UI_InputField, UI_Text, UI_Slider, UI_Panel
from tile import Tile

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

		self.pos = Vector2(1162, 360)
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
