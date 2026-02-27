from game import Game

# default values
window_size = (1280, 720)
default_lab_dims = (10, 10)
default_seed = -1

if __name__ == "__main__":
	print("Hello World!")
	game = Game("AI Assignment 1", window_size, default_lab_dims, default_seed)
	game.run()
