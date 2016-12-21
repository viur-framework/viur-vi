#-*- coding: utf-8 -*-
import html5, i18n, pyjd, network

from login import LoginScreen
from admin import AdminScreen
from config import conf
from i18n import translate

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

	def startup(self, *args, **kwargs):


		if conf["server.version"] is None:
			network.NetworkService.request(None, "/vi/getVersion",
			                               successHandler=self.getVersionSuccess,
			                               failureHandler=self.startupFailure,
			                               cacheable=True)
		else:
			network.NetworkService.request(None, "/vi/config",
			                                successHandler=self.getConfigSuccess,
											failureHandler=self.startupFailure,
	                                        cacheable=True)

	def getVersionSuccess(self, req):
		conf["server.version"] = network.NetworkService.decode(req)

		if ((conf["server.version"][0] >= 0                             # check version?
			and conf["server.version"][0] != conf["vi.version"][0]      # major version mismatch
			or conf["server.version"][1] > conf["vi.version"][1])):     # minor version mismatch

			params = {
				"server.version": ".".join(str(x) for x in conf["server.version"]),
				"vi.version": ".".join(str(x) for x in conf["vi.version"]),
			}

			conf["server.version"] = None

			html5.ext.Alert(
				translate("The ViUR server (v{server.version}) is incompatible to this Vi (v{vi.version}).", **params)
					+ "\n" + translate("Please update either your server or Vi!"),
				title=translate("Version mismatch"),
				okCallback=self.startup,
				okLabel=translate("Retry")
			)

			return

		self.startup()

	def getConfigSuccess(self, req):
		conf["mainConfig"] = network.NetworkService.decode(req)

		if not self.adminScreen:
			self.adminScreen = AdminScreen()

		self.adminScreen.invoke()

	def startupFailure(self, req, err):
		if err in [403, 401]:
			self.login()
		else:
			html5.ext.Alert(
				translate("The connection to the server could not be correctly established."),
				title=translate("Communication error"),
				okCallback=self.startup,
				okLabel=translate("Retry")
			)

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
