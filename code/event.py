class Event:
	def __init__(self):
		self.listeners = []

	def add_listener(self, fn):
		self.listeners.append(fn)
		return fn

	def remove_listener(self, handle):
		self.listeners.remove(handle)

	def reset(self):
		self.listeners.clear()

	def invoke(self, *args, **kwargs):
		if len(self.listeners) == 0:
			return

		for fn in self.listeners:
			fn(*args, **kwargs)