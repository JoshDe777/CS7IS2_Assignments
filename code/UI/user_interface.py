from pygame import Vector2, Rect
from UI.uielement import UI_Button, UI_InputField, UI_Text, UI_Slider, UI_Panel, UI_Dropdown

# notes to self:
# - min y-distance to new text element, slider: 15
# - min y-distance to new button: button height

default_scale = 45
default_width = 10
default_height = 10
options = ["Human", "Baseline", "MinMax", "MinMax-AB", "Tabular QRL", "DQN-RL"]

class TicTacToeInterface:
	def __init__(self, game):
		self.game = game
		game.ttt.on_game_end.add_listener(self.display_winner)
		game.ttt.on_turn_change.add_listener(self.update_game_state)
		self.active_p1_type = 0
		self.active_p2_type = 0

		self.pos = Vector2(1155, 360)
		self.panel = UI_Panel(game, self.pos, Vector2(200, 400), "white")
		last_y = -185
		self.header = UI_Text(game=game, text="Tic Tac Toe!", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.game_state = UI_Text(game=game, text=f"Waiting for game start!", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		last_y += 40
		self.start_button = UI_Button(game=game, buttonText="Start Game!", rect=Rect(0, 0, 175, 50), on_press_action=self.start_game)
		self.start_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 20
		self.separator1 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# player 1 type selector
		last_y += 15
		self.p1_text = UI_Text(game=game, text=f"Player 1:", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		self.p1_symbol = UI_Text(game=game, text="x", font_color="red", pos = Vector2(90, last_y) + self.pos, font_size=20)
		last_y += 40
		self.p1_input = UI_Dropdown(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 50), options=options, on_select=self.update_p1_agent_type)
		last_y += 20
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# player 2 type selector
		last_y += 15
		self.p2_text = UI_Text(game=game, text=f"Player 2:", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		self.p2_symbol = UI_Text(game=game, text="o", font_color="blue", pos = Vector2(90, last_y) + self.pos, font_size=20)
		last_y += 40
		self.p2_input = UI_Dropdown(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 50), options=options, on_select=self.update_p2_agent_type)
		last_y += 20
		self.separator3 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# transition to connect 4
		last_y += 40
		self.c4_button = UI_Button(game=game, buttonText="Play Connect 4", rect=Rect(0, 0, 175, 50), on_press_action=self.move_to_c4)
		self.c4_button.set_position(self.pos + Vector2(0, last_y))

	def start_game(self):
		if not self.game.ttt.running:
			print("Starting game!")
			self.game.ttt.start()

	def update_game_state(self, activePlayer: str):
		self.game_state.set_text(f"{activePlayer}'s turn!")

	def display_winner(self, winner):
		text = ""
		if winner == "Draw":
			text = "No winner!"
		else:
			text = f"{winner} wins!"
		self.game_state.set_text(text)

	def update_p1_agent_type(self, idx, agent_type):
		if self.game.ttt.running:
			self.p1_input.set_selected(self.active_p1_type)
			print("Can't change agent type whilst playing!")
			return
		
		self.active_p1_type = idx
		self.game.set_TTT_agent(1, agent_type)

	def update_p2_agent_type(self, idx, agent_type):
		if self.game.ttt.running:
			self.p2_input.set_selected(self.active_p2_type)
			print("Can't change agent type whilst playing!")
			return
		
		self.active_p2_type = idx
		self.game.set_TTT_agent(2, agent_type)

	def move_to_c4(self):
		self.game.close_TTT()
		self.game.open_c4()

	def enable(self):
		self.panel.enable()
		self.header.enable()
		self.game_state.enable()
		self.start_button.enable()
		self.separator1.enable()
		self.p1_text.enable()
		self.p1_symbol.enable()
		self.p1_input.enable()
		self.separator2.enable()
		self.p2_text.enable()
		self.p2_symbol.enable()
		self.p2_input.enable()
		self.separator3.enable()
		self.c4_button.enable()

	def disable(self):
		self.panel.disable()
		self.header.disable()
		self.game_state.disable()
		self.start_button.disable()
		self.separator1.disable()
		self.p1_text.disable()
		self.p1_symbol.disable()
		self.p1_input.disable()
		self.separator2.disable()
		self.p2_text.disable()
		self.p2_symbol.disable()
		self.p2_input.disable()
		self.separator3.disable()
		self.c4_button.disable()


# TODO before testing C4!
class Connect4Interface:
	def __init__(self, game):
		self.game = game
		game.c4.on_game_end.add_listener(self.display_winner)
		game.c4.on_turn_change.add_listener(self.update_game_state)
		self.active_p1_type = 0
		self.active_p2_type = 0

		self.pos = Vector2(1155, 360)
		self.panel = UI_Panel(game, self.pos, Vector2(200, 400), "white")
		last_y = -185
		self.header = UI_Text(game=game, text="Connect 4!", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.game_state = UI_Text(game=game, text=f"Waiting for game start!", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		last_y += 40
		self.start_button = UI_Button(game=game, buttonText="Start Game!", rect=Rect(0, 0, 175, 50), on_press_action=self.start_game)
		self.start_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 20
		self.separator1 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# player 1 type selector
		last_y += 15
		self.p1_text = UI_Text(game=game, text=f"Player 1:", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		self.p1_symbol = UI_Text(game=game, text="o", font_color="red", pos = Vector2(90, last_y) + self.pos, font_size=20)
		last_y += 40
		self.p1_input = UI_Dropdown(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 50), options=options, on_select=self.update_p1_agent_type)
		last_y += 20
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# player 2 type selector
		last_y += 15
		self.p2_text = UI_Text(game=game, text=f"Player 2:", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		self.p2_symbol = UI_Text(game=game, text="o", font_color="yellow", pos = Vector2(90, last_y) + self.pos, font_size=20)
		last_y += 40
		self.p2_input = UI_Dropdown(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 50), options=options, on_select=self.update_p2_agent_type)
		last_y += 20
		self.separator3 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# transition to tic tac toe
		last_y += 40
		self.ttt_button = UI_Button(game=game, buttonText="Play Tic Tac Toe", rect=Rect(0, 0, 175, 50), on_press_action=self.move_to_ttt)
		self.ttt_button.set_position(self.pos + Vector2(0, last_y))


	def enable(self):
		self.panel.enable()
		self.header.enable()
		self.game_state.enable()
		self.start_button.enable()
		self.separator1.enable()
		self.p1_text.enable()
		self.p1_symbol.enable()
		self.p1_input.enable()
		self.separator2.enable()
		self.p2_text.enable()
		self.p2_symbol.enable()
		self.p2_input.enable()
		self.separator3.enable()
		self.ttt_button.enable()

	def disable(self):
		self.panel.disable()
		self.header.disable()
		self.game_state.disable()
		self.start_button.disable()
		self.separator1.disable()
		self.p1_text.disable()
		self.p1_symbol.disable()
		self.p1_input.disable()
		self.separator2.disable()
		self.p2_text.disable()
		self.p2_symbol.disable()
		self.p2_input.disable()
		self.separator3.disable()
		self.ttt_button.disable()

	def update_game_state(self, activePlayer: str):
		self.game_state.set_text(f"{activePlayer}'s turn!")

	def display_winner(self, winner):
		text = ""
		if winner == "Draw":
			text = "No winner!"
		else:
			text = f"{winner} wins!"
		self.game_state.set_text(text)

	def start_game(self):
		self.game.c4.start()

	def update_p1_agent_type(self, idx, agent_type):
		if self.game.c4.running:
			self.p1_input.set_selected(self.active_p1_type)
			print("Can't change agent type whilst playing!")
			return

		self.active_p1_type = idx
		self.game.set_C4_agent(1, agent_type)

	def update_p2_agent_type(self, idx, agent_type):
		if self.game.c4.running:
			self.p2_input.set_selected(self.active_p2_type)
			print("Can't change agent type whilst playing!")
			return
		
		self.active_p2_type = idx
		self.game.set_C4_agent(2, agent_type)

	def move_to_ttt(self):
		self.game.close_c4()
		self.game.open_TTT()
