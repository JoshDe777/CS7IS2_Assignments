class Game:
	def __init__(self, name: str):
		self.name = name
		self.running = True

	def draw(self):
		print("New Frame")

	def onShutdown(self):
		print("Exiting game.")

	def run(self):
		while self.running:
			input_val = input("Press x to exit.\n")
			if input_val == "x":
				self.running = False

			self.draw()

		self.onShutdown()