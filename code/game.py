import pygame

class Game:
	def __init__(self, name: str, display_size: tuple):
		self.name = name
		self.running = True
		self.deltaTime = 0.0
		self.size = display_size

	def onBeforeUpdate(self):
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False

		self.window.fill(color="black")

	def request_close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))

	def draw(self):
		pygame.display.flip()

	def onShutdown(self):
		print("Exiting game.")
		pygame.quit()

	def run(self):
		pygame.init()
		self.window = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		while self.running:
			self.onBeforeUpdate()

			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.request_close()

			self.draw()
			self.deltaTime = self.clock.tick(60) / 1000

		self.onShutdown()