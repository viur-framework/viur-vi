#-*- coding: utf-8 -*-

import pyjd
import html5

from login import LoginScreen
from admin import AdminScreen
from config import conf

try:
	import vi_plugins
except ImportError:
	pass


class Application(html5.Div):
	def __init__(self):
		super(Application, self).__init__()
		self["class"].append("vi-application")
		conf["theApp"] = self

		# Main Screens
		self.loginScreen = LoginScreen(self)
		self.adminScreen = None

		self.loginScreen.invoke()

	def onLogin(self):
		if not self.adminScreen:
			self.adminScreen = AdminScreen(self)

		self.adminScreen.invoke()

	def onLogout(self):
		self.removeChild(self.adminScreen)
		conf["mainWindow"] = self.adminScreen = None

		self.loginScreen.invoke(logout=True)

if __name__ == '__main__':
	pyjd.setup("public/main.html")

	app = Application()
	html5.Body().appendChild(app)

	pyjd.run()
