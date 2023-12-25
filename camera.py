
from numpy import clip
class Camera:

	def __init__(self, width, height):
		self.hwidth = width // 2
		self.hheight = height // 2
		self.scale = 2.0

	def set_pos(self, pos):
		# положение камеры
		self.x = pos[0]
		self.y = pos[1]

	def set_scale(self, scale):
	# масштаб камеры
		self.dest_scale = scale
		self.scale += (self.dest_scale - self.scale) * 0.3

	def transform(self, x, y):
	# экран
		return int((x - self.x) * self.scale) + self.hwidth, int((y - self.y) * self.scale) + self.hheight

	def getr(self, r):
		return r * self.scale







