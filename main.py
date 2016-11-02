#-*- coding: utf-8 -*-
import html5, i18n, pyjd, network

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
		self.loginScreen = None
		self.adminScreen = None

		self.startup()

	def startup(self):
		network.NetworkService.request(None, "/vi/config",
		                                successHandler=self.startupSuccess,
										failureHandler=self.startupFailure,
                                        cacheable=True)

	def startupSuccess(self, req):
		conf["mainConfig"] = network.NetworkService.decode(req)

		if not self.adminScreen:
			self.adminScreen = AdminScreen()

		self.adminScreen.invoke()

	def startupFailure(self, req, err):
		if err in [403, 401]:
			self.login()
		else:
			alert("startupFailure TODO")

	def login(self, logout=False):
		if not self.loginScreen:
			self.loginScreen = LoginScreen()

		self.loginScreen.invoke(logout=logout)

	def admin(self):
		if self.loginScreen:
			self.loginScreen.hide()

		self.startup()

	def logout(self):
		self.adminScreen.remove()
		conf["mainWindow"] = self.adminScreen = None
		self.login(logout=True)

if __name__ == '__main__':
	pyjd.setup("public/main.html")

	# Configure vi as network render prefix
	network.NetworkService.prefix = "/vi"
	conf["currentlanguage"] = i18n.getLanguage()

	# Application
	app = Application()
	html5.Body().appendChild(app)

	pyjd.run()
