#-*- coding: utf-8 -*-
from . import html5

from . import network
from . import utils
from . import sidebarwidgets
from . import exception

from .login import LoginScreen
from .admin import AdminScreen
from .config import conf
from .i18n import translate
from . import i18n

class Application(html5.Div):
	def __init__(self):
		super(Application, self).__init__()
		self.addClass("vi-application")
		conf["theApp"] = self

		# Main Screens
		self.loginScreen = None
		self.adminScreen = None

		self.startup()

	def startup(self, *args, **kwargs):


		if conf["core.version"] is None:
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
		conf["core.version"] = network.NetworkService.decode(req)

		if ((conf["core.version"][0] >= 0                              # check version?
			#and (conf["core.version"][0] != conf["vi.version"][0]     # major version mismatch (disabled)
		     and (conf["core.version"][0] not in [2, conf["vi.version"][0]]# major version mismatch (used currently!)
				or (conf["core.version"][0] == 3 and conf["core.version"][1] > conf["vi.version"][1])))): # minor version mismatch

			params = {
				"core.version": ".".join(str(x) for x in conf["core.version"]),
				"vi.version": ".".join(str(x) for x in conf["vi.version"]),
			}

			html5.ext.Alert(
				translate("ViUR-core (v{core.version}) is incompatible to this Vi (v{vi.version}).", **params)
					+ "\n" + translate("There may be a lack on functionality.")
					+ "\n" + translate("Please update either your server or Vi!"),
				title=translate("Version mismatch"),
				okCallback=self.startup,
				okLabel=translate("Continue at your own risk")
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

		if self.adminScreen:
			self.adminScreen.reset()
			self.adminScreen.hide()

		self.loginScreen.invoke(logout=logout)

	def admin(self):
		if self.loginScreen:
			self.loginScreen.hide()

		self.startup()

	def logout(self):
		self.login(logout=True)

	def setTitle(self, title = None):
		if title:
			title = [title]
		else:
			title = []

		addendum = conf.get("vi.name")
		if addendum:
			title.append(addendum)

		html5.document.title = conf["vi.title.delimiter"].join(title)

	def setPath(self, path = ""):
		hash = html5.window.location.hash
		if "?" in hash and not "?" in path:
			hash = hash.split("?", 1)[1]
			if hash:
				hash = "?" + hash

		else:
			hash = ""

		html5.window.location.hash = path + hash

def start():

	# Configure vi as network render prefix
	network.NetworkService.prefix = "/vi"
	network.NetworkService.host = ""
	conf["currentLanguage"] = i18n.getLanguage()
	conf["indexeddb"] = utils.indexeddb("vi-cache")

	# Application
	app = Application()
	html5.Body().appendChild(app)
