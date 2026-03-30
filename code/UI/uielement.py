import pygame
from pygame import Surface, Vector2
from pygame.math import clamp

class UI_Element:
	def __init__(self, game):
		self.enabled = True
		game.eventPoller.add_listener(self.get_input)
		game.afterUpdate.add_listener(self.draw)

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False

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
		if not self.enabled:
			return

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
		if not self.enabled:
			return

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
		if not self.enabled:
			return

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
		if not self.enabled:
			return

		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
				self.callback()

	def draw(self, window: Surface, worldOffset: Vector2):
		if not self.enabled:
			return

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
		if not self.enabled:
			return

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
		if not self.enabled:
			return

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
		if not self.enabled:
			return

		color = self.active_color if self.active else self.bg_color
		pygame.draw.rect(window, color, self.rect)

		txt_surface = self.font.render(self.text, True, self.text_color)
		window.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

class UI_Dropdown(UI_Element):
	def __init__(self, game, pos: Vector2, size: Vector2, options: list[str], on_select=None, initial_index=0):
		super().__init__(game)
		game.postDraw.add_listener(self.draw_dropdown)

		self.rect = pygame.Rect(pos.x - size.x / 2, pos.y - size.y / 2, size.x, size.y)
		self.options = options
		self.selected = initial_index
		self.open = False
		self.on_select = on_select

		self.bg_color       = "cornsilk4"
		self.hover_color    = "lightskyblue"
		self.text_color     = "black"
		self.outline_color  = "black"
		self.font           = pygame.font.SysFont(None, 20)

		self._hovered = -1  # index of option currently hovered, -1 = none

    # ── option rects are derived on the fly so they always match self.rect ──

	def _option_rect(self, i: int) -> pygame.Rect:
		return pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height,
							self.rect.width, self.rect.height)

	def get_selected(self) -> str:
		return self.options[self.selected]

	def set_selected(self, index: int):
		self.selected = index

    # ── input ───────────────────────────────────────────────────────────────

	def get_input(self, events):
		if not self.enabled:
			return

		for event in events:

			if event.type == pygame.MOUSEBUTTONDOWN:
				if self.rect.collidepoint(event.pos):
					self.open = not self.open

				elif self.open:
					for i in range(len(self.options)):
						if self._option_rect(i).collidepoint(event.pos):
							self.selected = i
							if self.on_select:
								self.on_select(i, self.options[i])
							break
					self.open = False  # close on any outside click too

			if event.type == pygame.MOUSEMOTION and self.open:
				self._hovered = -1
				for i in range(len(self.options)):
					if self._option_rect(i).collidepoint(event.pos):
						self._hovered = i
						break

    # ── draw ────────────────────────────────────────────────────────────────

	def draw(self, window: Surface, worldOffset: Vector2):
		if not self.enabled:
			return

		# Header button
		pygame.draw.rect(window, self.bg_color, self.rect)
		pygame.draw.rect(window, self.outline_color, self.rect, 1)

		label = self.font.render(self.options[self.selected], True, self.text_color)
		window.blit(label, label.get_rect(center=self.rect.center))

		# Arrow indicator
		arrow = "^" if self.open else "v"
		arrow_surf = self.font.render(arrow, True, self.text_color)
		window.blit(arrow_surf, arrow_surf.get_rect(centery=self.rect.centery, right=self.rect.right - 6))

	def draw_dropdown(self, window: Surface, worldOffset: Vector2):
		if not self.open or not self.enabled:
			return

		# Drop-down list
		for i, option in enumerate(self.options):
			r = self._option_rect(i)
			color = self.hover_color if i == self._hovered else self.bg_color
			pygame.draw.rect(window, color, r)
			pygame.draw.rect(window, self.outline_color, r, 1)

			opt_label = self.font.render(option, True, self.text_color)
			window.blit(opt_label, opt_label.get_rect(center=r.center))

