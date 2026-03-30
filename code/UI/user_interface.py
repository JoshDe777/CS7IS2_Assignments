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
		self.current_scale = default_scale

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
		self.p1_symbol = UI_Text(game=game, text="o", font_color="blue", pos = Vector2(90, last_y) + self.pos, font_size=20)
		last_y += 40
		self.p1_input = UI_Dropdown(game=game, pos=Vector2(0, last_y) + self.pos, size=Vector2(175, 50), options=options, on_select=self.update_p1_agent_type)
		last_y += 20
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)

		# player 2 type selector
		last_y += 15
		self.p2_text = UI_Text(game=game, text=f"Player 2:", font_color="black", pos=Vector2(0, last_y) + self.pos, font_size=15)
		self.p2_symbol = UI_Text(game=game, text="x", font_color="red", pos = Vector2(90, last_y) + self.pos, font_size=20)
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

	def update_p1_agent_type(self, _, agent_type):
		if self.game.ttt.running:
			print("Can't change agent type whilst playing!")
			return

		print(f"Active p1 agent type: {agent_type} (Not implemented unless Human).")
		# self.game.set_ttt_agent(1, agent_type)

	def update_p2_agent_type(self, _, agent_type):
		if self.game.ttt.running:
			print("Can't change agent type whilst playing!")
			return

		print(f"Active p2 agent type: {agent_type} (Not implemented unless Human).")
		# self.game.set_ttt_agent(2, agent_type)

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

		self.pos = Vector2(125, 360)
		self.panel = UI_Panel(game, self.pos, Vector2(200, 600), "white")
		last_y = -285
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
		self.start_bfs_button = UI_Button(game=game, buttonText="Start A* (Euclidean)", rect=Rect(0, 0, 175, 30), on_press_action=self.start_Astar_1)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start A* (Manhattan)", rect=Rect(0, 0, 175, 30), on_press_action=self.start_Astar_2)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start MDP Value Iteration", rect=Rect(0, 0, 175, 30), on_press_action=self.start_MDP_Val)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 35
		self.start_bfs_button = UI_Button(game=game, buttonText="Start MDP Policy Iteration", rect=Rect(0, 0, 175, 30), on_press_action=self.start_MDP_Pol)
		self.start_bfs_button.set_position(self.pos + Vector2(0, last_y))
		last_y += 15
		self.separator2 = UI_Text(game=game, text="---------------------------------------------", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.markov_discount = UI_Text(game=game, text=f"MDP Discount Factor = {self.mdp_discount:.2f}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.discount_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=0.0, max_val=1.0, value=self.mdp_discount, on_slide_callback=self.update_mdp_discount)
		last_y += 15
		self.markov_living_reward = UI_Text(game=game, text=f"MDP Living Reward = {self.mdp_living_reward:.2f}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.living_reward_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=-2.0, max_val=2.0, value=self.mdp_living_reward, on_slide_callback=self.update_mdp_living_reward)
		last_y += 15
		self.markov_iters = UI_Text(game=game, text=f"MDP Iterations = {int(self.mdp_iters)}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.living_iter_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=0, max_val=500, value=int(self.mdp_iters), on_slide_callback=self.update_it_count)
		last_y += 15
		self.markov_threshold = UI_Text(game=game, text=f"MDP Delta Threshold = {self.mdp_th:.4f}", font_color="black", pos=Vector2(0, last_y) + self.pos)
		last_y += 15
		self.living_th_slider = UI_Slider(game=game, pos=Vector2(0, last_y) + self.pos, width=150, min_val=0.0, max_val=0.2, value=int(self.mdp_th), on_slide_callback=self.update_threshold)


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
		self.set_search_legend()

	def start_DFS(self):
		self.activeSolver = "DFS"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()
		self.set_search_legend()

	def start_Astar_1(self):
		self.activeSolver = "A_Star_1"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()
		self.set_search_legend()

	def start_Astar_2(self):
		self.activeSolver = "A_Star_2"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()
		self.set_search_legend()

	def start_MDP_Val(self):
		self.activeSolver = "MDP_Value"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()
		self.set_mdp_legend()

	def start_MDP_Pol(self):
		self.activeSolver = "MDP_Policy"
		self.game.solvers[self.activeSolver].start()
		self.update_active_solver_text_UI()
		self.set_mdp_policy_legend()

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

	def update_mdp_discount(self, val):
		self.mdp_discount = val
		self.game.solvers["MDP_Value"].set_discount(val)
		self.markov_discount.set_text(f"MDP Discount Factor = {self.mdp_discount:.2f}")

	def update_mdp_living_reward(self, val):
		self.mdp_living_reward = val
		self.game.solvers["MDP_Value"].set_living_reward(val)
		self.markov_living_reward.set_text(f"MDP Living Reward = {self.mdp_living_reward:.2f}")

	def update_it_count(self, val):
		self.mdp_iters = int(val)
		self.game.solvers["MDP_Value"].set_max_iters(int(val))
		self.markov_iters.set_text(f"MDP Iterations = {int(self.mdp_iters)}")

	def update_threshold(self, val):
		self.mdp_th = val
		self.game.solvers["MDP_Value"].set_threshold(val)
		self.markov_threshold.set_text(f"MDP Delta Threshold = {self.mdp_th:.4f}")

	def set_search_legend(self):
		self.legend1.set_text(f"dark blue = explored")
		self.legend2.set_text(f"light blue = exploration edge")

	def set_mdp_legend(self):
		self.legend1.set_text(f"green---------black----------red")
		self.legend2.set_text(f"+X--------------0------------ -X")

	def set_mdp_policy_legend(self):
		self.legend1.set_text(f"up: beige <-> down: olive green")
		self.legend2.set_text(f"left: red <-> right: light blue")
