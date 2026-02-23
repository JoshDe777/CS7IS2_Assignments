import pygame
from event import Event
from labyrinth_generator import Labyrinth

class Game:
	def __init__(self, name: str, display_size: tuple, labyrinth_size: pygame.Vector2):
		self.name = name
		self.running = True
		self.deltaTime = 0.0
		self.size = display_size
		self.worldToScreen = pygame.Vector2(display_size[0] / 2, display_size[1] / 2)
		self.labyrinth_size = labyrinth_size
		self.update = Event()
		self.beforeUpdate = Event()
		self.afterUpdate = Event()

	def onBeforeUpdate(self):
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
		self.beforeUpdate.invoke()
		self.window.fill(color="azure4")

	def request_close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))

	def draw(self):
		self.afterUpdate.invoke(self.window, self.worldToScreen)
		pygame.display.flip()

	def onShutdown(self):
		print("Exiting game.")
		pygame.quit()

	def run(self):
		pygame.init()
		self.window = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		self.labyrinth = Labyrinth(size=self.labyrinth_size, game=self, worldOffset=pygame.Vector2(0, 0))
		while self.running:
			self.onBeforeUpdate()
			self.update.invoke()

			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.request_close()

			self.draw()
			self.deltaTime = self.clock.tick(60) / 1000

		self.onShutdown()