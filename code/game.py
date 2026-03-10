import pygame
from Solvers.astar_solver import A_Star_Solver
from Solvers.bfs_solver import BFS_Solver
from Solvers.dfs_solver import DFS_Solver
from Solvers.mdp_policy_solver import MDP_Policy
from Solvers.mdp_value_solver import MDP_Value
from event import Event
from Labyrinth.labyrinth_generator import Labyrinth
from UI.user_interface import LabyrinthInterface, SolverInterface

class Game:
	def __init__(self, name: str, display_size: tuple, labyrinth_size: pygame.Vector2, labyrinth_seed: int):
		self.name = name
		self.running = True
		self.deltaTime = 0.0
		self.size = display_size
		pygame.font.init()
		self.worldToScreen = pygame.Vector2(display_size[0] / 2, display_size[1] / 2)
		self.labyrinth_size = labyrinth_size
		self.labyrinth_seed = labyrinth_seed
		self.update = Event()
		self.beforeUpdate = Event()
		self.afterUpdate = Event()
		self.eventPoller = Event()

		self.solvers = {
			"BFS": BFS_Solver(self),
			"DFS": DFS_Solver(self),
			"A_Star_1": A_Star_Solver(self, euclidean=True),
			"A_Star_2": A_Star_Solver(self, euclidean=False),
			"MDP_Value": MDP_Value(self),
			"MDP_Policy": MDP_Policy(self)
		}

	def onBeforeUpdate(self):
		events = pygame.event.get()
		for event in events:
				if event.type == pygame.QUIT:
					self.running = False
		self.eventPoller.invoke(events)
		self.beforeUpdate.invoke()
		self.window.fill(color="azure4")

	def request_close(self):
		pygame.event.post(pygame.event.Event(pygame.QUIT))

	def draw(self):
		self.afterUpdate.invoke(self.window, self.worldToScreen)
		pygame.display.flip()

	def onShutdown(self):
		print("Exiting game.")
		pygame.font.quit()
		pygame.quit()

	def run(self):
		pygame.init()
		self.window = pygame.display.set_mode(self.size)
		self.clock = pygame.time.Clock()
		self.labyrinth = Labyrinth(size=self.labyrinth_size, game=self, worldOffset=pygame.Vector2(0, 0), seed=self.labyrinth_seed)
		self.ui = LabyrinthInterface(self)
		self.solver_ui = SolverInterface(self)

		while self.running:
			self.onBeforeUpdate()
			self.update.invoke()

			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				self.request_close()

			self.draw()
			self.deltaTime = self.clock.tick(60) / 1000

		self.onShutdown()