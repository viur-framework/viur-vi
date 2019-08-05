# -*- coding: utf-8 -*-
import html5
from .config import conf

class Screen(html5.Div):
	"""
	This is the screen superclass.

	It represents a basic screen and its functionality.
	"""

	def __init__(self, *args, **kwargs):
		super(Screen, self).__init__(*args, **kwargs)
		self.addClass("vi-screen")

		conf["theApp"].appendChild(self)
		self.hide()

	def lock(self):
		self.addClass("is-loading")

	def unlock(self):
		self.removeClass("is-loading")

	def invoke(self):
		"""Is called to show the screen"""
		print("Invoke: %s" % self.__class__.__name__)

	def remove(self):
		"""Remove the screen from its parent"""
		if self.parent():
			self.parent().removeChild(self)

	def setTitle(self, title = None):
		if title is None:
			title = self.__class__.__name__

		conf["theApp"].setTitle(title)
