import pygame
from pygame import Surface, Vector2
from pygame.math import clamp
from enum import Enum

class UI_Element:
	def __init__(self, game):
		game.update.add_listener(self.get_input)
		game.afterUpdate.add_listener(self.draw)

	def get_input(self):
		pass

	def draw(self, window: Surface, worldOffset: Vector2):
		pass

class AnchorPos(Enum):
	TOP_LEFT = 0
	TOP = 1
	TOP_RIGHT = 2
	LEFT = 3
	CENTRE = 4
	RIGHT = 5
	BOTTOM_LEFT = 6
	BOTTOM = 7
	BOTTOM_RIGHT = 8

	def get_anchor_position(self, container_pos, container_size, element_size):
		x, y = container_pos
		w, h = container_size
		ew, eh = element_size

		if self == AnchorPos.TOP_LEFT:
			return Vector2(x, y)
		if self == AnchorPos.TOP:
			return Vector2(x + w/2 - ew/2, y)
		if self == AnchorPos.TOP_RIGHT:
			return Vector2(x + w - ew, y)

		if self == AnchorPos.LEFT:
			return Vector2(x, y + h/2 - eh/2)
		if self == AnchorPos.CENTER:
			return Vector2(x + w/2 - ew/2, y + h/2 - eh/2)
		if self == AnchorPos.RIGHT:
			return Vector2(x + w - ew, y + h/2 - eh/2)

		if self == AnchorPos.BOTTOM_LEFT:
			return Vector2(x, y + h - eh)
		if self == AnchorPos.BOTTOM:
			return Vector2(x + w/2 - ew/2, y + h - eh)
		if self == AnchorPos.BOTTOM_RIGHT:
			return Vector2(x + w - ew, y + h - eh)

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
		window.blit(surf, self.screen_pos)

	def set_text(self, text: str):
		self.text = text

class UI_Slider(UI_Element):
	def __init__(self, game, pos: Vector2, width: float, min_val: float, max_val: float, value: float):
		super().__init__(game)
		self.rect = pygame.Rect(pos.x, pos.y, width, 10)
		self.min = min_val
		self.max = max_val
		self.value = value
		self.active = False
		self.sliderColor = "black"
		self.fillColor = "gray"
		self.sliderSize = 6

	def set_slider_colour(self, colour: str):
		self.sliderColor = colour

	def set_fill_colour(self, colour: str):
		self.fillColor = colour

	def set_min(self, min_val: float):
		self.min = min_val

	def set_max(self, max_val: float):
		self.max = max_val

	def get_value(self) -> float:
		return self.value

	def get_input(self):
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				self.active = True
			if event.type == pygame.MOUSEBUTTONUP:
				self.active = False

			if event.type == pygame.MOUSEMOTION and self.active:
				# get x position relative to the slider progression.
				progress = clamp((event.pos[0] - self.rect.x) / self.rect.w, 0.0, 1.0)
				self.value = self.min + progress * (self.max - self.min)

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

	def set_text(self, text: str):
		self.text = text

	def set_button_color(self, colour: str):
		self.colour = colour

	def set_text_colour(self, colour: str):
		self.font_colour = colour

	def get_input(self):
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				self.callback()

	def draw(self, window: Surface, worldOffset: Vector2):
		pygame.draw.rect(window, self.colour, self.rect)
		label = self.font.render(self.text, antialias=True, color=self.font_colour)
		window.blit(label, label.get_rect(center=self.rect.center))

class UI_InputInt(UI_Element):
    def __init__(self, game, pos, width, value=10):
        super().__init__(game)
        self.rect = pygame.Rect(pos[0], pos[1], width, 30)
        self.value = str(value)
        self.active = False
        self.font = pygame.font.SysFont(None, 20)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)

        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif e.unicode.isdigit():
                new = self.value + e.unicode
                if 0 <= int(new) <= 50:
                    self.value = new

    def draw(self, window, worldOffset: Vector2):
        pygame.draw.rect(window, "white", self.rect, 2)
        txt = self.font.render(self.value, True, "black")
        window.blit(txt, (self.rect.x+5, self.rect.y+5))


class UI_Panel(UI_Element):
	def __init__(self, game, pos: Vector2, size: Vector2, colour: str):
		super().__init__(game)
		self.pos = pos
		self.size = size
		self.colour = colour

	def set_colour(self, colour: str):
		self.colour = colour

	def draw(self, window, worldOffset):
		rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		pygame.draw.rect(window, self.colour, rect)