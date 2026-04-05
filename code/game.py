import pygame
from C4.connect4 import Connect4
from C4.c4player import C4_Player
from TTT.tictactoe import TicTacToe
from TTT.tttplayer import TTT_Player
from UI.user_interface import Connect4Interface, TicTacToeInterface
from event import Event

class Game:
	def __init__(self, name: str, display_size: tuple):
		self.name = name
		self.running = True
		self.deltaTime = 0.0
		self.size = display_size
		pygame.font.init()
		self.worldToScreen = pygame.Vector2(display_size[0] / 2, display_size[1] / 2)
		self.update = Event()
		self.beforeUpdate = Event()
		self.afterUpdate = Event()
		self.postDraw = Event()
		self.eventPoller = Event()

		# A3 exclusive
		self.active_game = None

		# Tic Tac Toe
		self.ttt_p1 = TTT_Player(self, 1)
		self.ttt_p2 = TTT_Player(self, 2)
		self.ttt = TicTacToe(self, self.worldToScreen, self.ttt_p1, self.ttt_p2)
		self.ttt_ui = TicTacToeInterface(game=self)

		# Connect 4
		self.c4_p1 = C4_Player(self, 1)
		self.c4_p2 = C4_Player(self, 2)
		self.c4 = Connect4(self, self.worldToScreen, self.c4_p1, self.c4_p2)
		self.c4_ui = Connect4Interface(game=self)
		

	def onBeforeUpdate(self):
		events = pygame.event.get()
		for event in events:
			event.consumed = False
			if event.type == pygame.QUIT:
				self.running = False

		self.eventPoller.invoke(events)
		self.beforeUpdate.invoke()
		self.window.fill(color="azure4")

	def request_close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))

	def draw(self):
		self.afterUpdate.invoke(self.window, self.worldToScreen)
		self.postDraw.invoke(self.window, self.worldToScreen)
		pygame.display.flip()

	def onShutdown(self):
		print("Exiting game.")
		pygame.font.quit()
		pygame.quit()

	def run(self):
		pygame.init()
		self.window = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		self.close_c4()
		self.open_TTT()

		while self.running:
			self.onBeforeUpdate()
			self.update.invoke()

			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.request_close()

			self.draw()
			self.deltaTime = self.clock.tick(60) / 1000

		self.onShutdown()

	# A3 exclusive
	def open_TTT(self):
		if self.active_game == self.ttt:
			return

		self.active_game = self.ttt
		self.ttt.enable()
		self.ttt_ui.enable()

	def close_TTT(self):
		if self.active_game != self.ttt:
			return

		if self.active_game == self.ttt:
			self.active_game = None
		self.ttt.reset()
		self.ttt.disable()
		self.ttt_ui.disable()

	def set_TTT_agent(self, idx, _type):
		if self.active_game == self.ttt:
			self.ttt.set_player(idx, _type)

	def open_c4(self):
		if self.active_game == self.c4:
			return

		self.active_game = self.c4
		self.c4.enable()
		self.c4_ui.enable()

	def close_c4(self):
		if self.active_game != self.c4:
			return

		if self.active_game == self.c4:
			self.active_game = None
		self.c4.reset()
		self.c4.disable()
		self.c4_ui.disable()

	def set_C4_agent(self, idx, _type):
		if self.active_game == self.c4:
			self.c4.set_player(idx, _type)
