import pygame
from pygame import Surface, Vector2
from pygame.math import clamp

class UI_Element:
	def __init__(self, game):
		game.eventPoller.add_listener(self.get_input)
		game.afterUpdate.add_listener(self.draw)

	def get_input(self, events):
		pass

	def draw(self, window: Surface, worldOffset: Vector2):
		pass


class UI_Text(UI_Element):
	def __init__(self, game, text: str, pos: Vector2, font_color="white", font_size = 20):
		super().__init__(game)
		self.text = text
		self.screen_pos = pos
		self.font_color = font_color
		self.font_size = font_size
		self.font = pygame.font.SysFont(None, font_size)

	def draw(self, window: Surface, worldOffset: Vector2):
		surf = self.font.render(self.text, True, self.font_color)
		window.blit(surf, self.screen_pos - Vector2(surf.get_width() / 2, 0))

	def set_text(self, text: str):
		self.text = text


class UI_Slider(UI_Element):
	def __init__(self, game, pos: Vector2, width: float, min_val: float, max_val: float, value: float, on_slide_callback, on_release_callback=None):
		super().__init__(game)
		self.rect = pygame.Rect(pos.x - (width / 2), pos.y, width, 10)
		self.min = min_val
		self.max = max_val
		self.value = value
		self.active = False
		self.sliderColor = "black"
		self.fillColor = "gray"
		self.sliderSize = 6
		self.slide_callback = on_slide_callback
		self.release_callback = on_release_callback

	def set_slider_colour(self, colour: str):
		self.sliderColor = colour

	def set_fill_colour(self, colour: str):
		self.fillColor = colour

	def set_min(self, min_val: float):
		self.min = min_val

	def set_max(self, max_val: float):
		self.max = max_val

	def set_value(self, val: float):
		self.value = val

	def get_value(self) -> float:
		return self.value

	def get_input(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				self.active = True
			if event.type == pygame.MOUSEBUTTONUP and self.active:
				self.active = False
				if self.release_callback is not None:
					self.release_callback(self.value)

			if event.type == pygame.MOUSEMOTION and self.active:
				# get x position relative to the slider progression.
				progress = clamp((event.pos[0] - self.rect.x) / self.rect.w, 0.0, 1.0)
				self.value = self.min + progress * (self.max - self.min)
				if self.slide_callback is not None:
					self.slide_callback(self.value)

	def draw(self, window: Surface, worldOffset: Vector2):
		pygame.draw.rect(window, self.fillColor, self.rect)
		progress = self.rect.x + (self.value - self.min)/(self.max-self.min)*self.rect.w
		pygame.draw.circle(window, self.sliderColor, (int(progress), self.rect.y + 5), self.sliderSize)


class UI_Button(UI_Element):
	def __init__(self, game, buttonText: str, rect, on_press_action):
		super().__init__(game)
		self.text = buttonText
		self.rect = pygame.Rect(rect)
		self.callback = on_press_action
		self.colour = "cornsilk4"
		self.font_colour = "black"
		self.font = pygame.font.SysFont(None, 20)

	def set_position(self, pos: Vector2):
		dims = Vector2(self.rect.width, self.rect.height)
		self.rect = pygame.Rect(pos.x - (dims.x / 2), pos.y - (dims.y / 2), dims.x, dims.y)

	def set_text(self, text: str):
		self.text = text

	def set_button_color(self, colour: str):
		self.colour = colour

	def set_text_colour(self, colour: str):
		self.font_colour = colour

	def get_input(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				self.callback()

	def draw(self, window: Surface, worldOffset: Vector2):
		pygame.draw.rect(window, self.colour, self.rect)
		label = self.font.render(self.text, True, self.font_colour)
		window.blit(label, label.get_rect(center=self.rect.center))


class UI_Panel(UI_Element):
	def __init__(self, game, pos: Vector2, size: Vector2, colour: str):
		super().__init__(game)
		self.pos = pos
		self.size = size
		self.colour = colour

	def set_colour(self, colour: str):
		self.colour = colour

	def draw(self, window, worldOffset):
		rect = pygame.Rect(self.pos.x - (self.size.x / 2), self.pos.y - (self.size.y / 2), self.size.x, self.size.y)
		pygame.draw.rect(window, self.colour, rect)

class UI_InputField(UI_Element):
	def __init__(self, game, pos: Vector2, size: Vector2, on_submit=None, initial_text=""):
		super().__init__(game)

		self.rect = pygame.Rect(
			pos.x - size.x/2,
			pos.y - size.y/2,
			size.x,
			size.y
		)

		self.text = initial_text
		self.active = False
		self.font = pygame.font.SysFont(None, 20)

		self.bg_color = "white"
		self.text_color = "black"
		self.active_color = "lightskyblue"

		self.on_submit = on_submit

	def get_input(self, events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				# activate if clicked
				self.active = self.rect.collidepoint(event.pos)

			if not self.active:
				continue

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					if self.on_submit:
						# convert to int if possible
						try:
							value = int(self.text)
						except:
							value = None
						self.on_submit(value)

				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]

				else:
					# allow only digits
					if event.unicode.isdigit():
						self.text += event.unicode

	def set_text(self, text: str):
		self.text = text

	def draw(self, window: Surface, worldOffset: Vector2):
		color = self.active_color if self.active else self.bg_color
		pygame.draw.rect(window, color, self.rect)

		txt_surface = self.font.render(self.text, True, self.text_color)
		window.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
