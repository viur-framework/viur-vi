import logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

from .config import vi_conf
from flare import loadProjectConf
loadProjectConf(vi_conf) #prepatch flare.conf

from flare import html5
from flare.popup import Alert
from flare import network
from flare.icons import SvgIcon
from . import utils
from . import sidebarwidgets
from . import exception

from .login import LoginScreen
from .admin import AdminScreen
from .config import conf

from flare.i18n import buildTranslations,translate
from flare import i18n


class Application(html5.Div):
	def __init__(self):
		super(Application, self).__init__()
		self.addClass("vi-application")
		conf["theApp"] = self

		# Main Screens
		self.loginScreen = None
		self.adminScreen = None

		try:
			self.isFramed = bool(html5.jseval("window.top !== window.self"))
		except:
			self.isFramed = True

		self.startup()

	def startup(self, *args, **kwargs):
		if conf["core.version"] is None:
			network.NetworkService.request(None, "/vi/getVersion",
			                               successHandler=self.getVersionSuccess,
			                               failureHandler=self.startupFailure)
		else:
			network.NetworkService.request(None, "/vi/config",
			                                successHandler=self.getConfigSuccess,
											failureHandler=self.startupFailure)

	def getVersionSuccess(self, req):
		conf["core.version"] = network.NetworkService.decode(req)
		if (conf["core.version"][0] == 3                                     # enforce ViUR3
			and ((conf["core.version"][1] < conf["core.version.min"][1])
			or (conf["core.version"][1] >= conf["core.version.max"][1]))
		):

			params = {
				"core.version": ".".join(str(x) for x in conf["core.version"]),
				"vi.version": ".".join(str(x) for x in conf["vi.version"]),
				"core.version.min": ".".join(str(x) for x in conf["core.version.min"]),
				"core.version.max": ".".join(str(x) for x in conf["core.version.max"]),
			}

			Alert(
				translate("ViUR-core (v{{core.version}}) is incompatible to this Vi (v{{vi.version}}). The ViUR-core version musst be greater or equal version v{{core.version.min}} and lower than v{{core.version.max}}.", **params)
					+ "\n\n" + translate("There may be a lack on functionality.")
					+ "\n" + translate("Please update either your ViUR-core or Vi!"),
				title=translate("Version mismatch"),
				okCallback=self.startup,
				okLabel=translate("Continue at your own risk")
			)

			return

		elif conf["core.version"][0] == 2:
			Alert(
				translate("Please update your ViUR-core to ViUR 3"),
				title=translate("Legacy ViUR-Version"),
				closeable=False,
			)

			return

		self.startup()

	def getConfigSuccess(self, req):
		d = (time.time() - s)
		print( "%.5f Sek - Config and Version received" % d  )

		conf["mainConfig"] = network.NetworkService.decode(req)

		if not self.adminScreen:
			self.adminScreen = AdminScreen()

		sc = (time.time() - s)
		print( "%.5f Sek - Screen instantiated" %  sc  )

		self.adminScreen.invoke()

		scinv = (time.time() - s)
		print( "%.5f Sek - Screen invoked" % scinv  )

	def startupFailure(self, req, err):
		if err in [403, 401]:
			self.login()
		else:
			Alert(
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


def preloadIcons():
	iconList = ["icon-arrow-right",
	"icon-save",
	"icon-draggable",
	"icon-save-file",
	"icon-image-file",
	"icon-arrow-left",
	"icon-cancel",
	"icon-file-system",
	"icon-add",
	"icon-list",
	"icon-reload",
	"icon-list-item",
	"icon-hierarchy",
	"icon-edit",
	"icon-search",
	"icon-clone",
	"icon-delete",
	"icon-play",
	"icon-dashboard",
	"icon-logout",
	"icon-error",
	"icon-error-file",
	"icon-time"]

	for icon in iconList:
		SvgIcon(icon)


def start():
	buildTranslations("vi")

	# Configure vi as network render prefix
	network.NetworkService.prefix = "/vi"
	network.NetworkService.host = ""
	conf["currentLanguage"] = i18n.getLanguage()
	conf["indexeddb"] = utils.indexeddb("vi-cache")

	preloadIcons()


	# Application
	app = Application()
	html5.Body().appendChild(app)



s = None
a = None
d = None
sc = None
scinv = None
if __name__ == "vi":
	import time
	s = time.time()
	print("Start App")
	start()
	a = (time.time() - s)
	print( "%.5f Sek - Application instantiated " % a  )
