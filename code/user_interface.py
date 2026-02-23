from pygame import Vector2
from UI.uielement import UI_Button, UI_Panel, UI_Text, UI_Slider, UI_InputInt

class LabyrinthInterface:
	def __init__(self, game):
		self.pos = Vector2(0, 0)
		self.panel = UI_Panel(game, Vector2(1100, 300), Vector2(200, 400), "white")
		self.header = UI_Text(game=game, text="Joshua's Labyrinth", font_color="black", pos=Vector2(1100, 100))