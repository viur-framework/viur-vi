import pyodide
from flare import html5
from flare.button import Button
from flare.popup import Popup
from flare.network import NetworkService, DeferredCall
from vi.config import conf
from flare.i18n import translate
import pyodide
from datetime import datetime


class UserLogoutMsg(Popup):
	pollInterval = 120  # We query the server once a minute
	checkInterval = 1000 * 5  # We test if the system has been suspended every 5 seconds

	def __init__(self, *args, **kwargs):
		super(UserLogoutMsg, self).__init__(title=translate("Session terminated"), enableShortcuts=False, *args, **kwargs)
		self.addClass("userloggedoutmsg")
		self.isCurrentlyFailed = False
		self.loginWindow = None
		self.viIsActive = True
		self.lastChecked = datetime.now()
		self.lbl = html5.Label(translate("Your session was terminated by our server. "
		                                 "Perhaps your computer fall asleep and broke connection?\n"
		                                 "Please relogin to continue your mission."))
		self.popupBody.appendChild(self.lbl)
		self.popupFoot.appendChild(Button(translate("Refresh"), callback=self.startPolling))
		self.popupFoot.appendChild(Button(translate("Login"), callback=self.showLoginWindow))

		html5.document.addEventListener( "webkitvisibilitychange", self.visibilityChanged )

		setInterval = html5.window.setInterval
		self.interval = setInterval(pyodide.create_proxy(self.checkForSuspendResume), self.checkInterval)
		self.hideMessage()

	def visibilityChanged( self,e ):
		if not html5.document.webkitHidden:
			self.viIsActive = False
		else:
			self.viIsActive = True

	def stopInterval(self):
		clearInterval = html5.window.clearInterval
		clearInterval(self.interval)

	def hideMessage(self):
		"""
			Make this popup invisible
		"""
		self.parent().hide()
		self.isCurrentlyFailed = False

	def showMessage(self):
		"""
			Show this popup
		"""
		self.parent().show()
		self.isCurrentlyFailed = True

	def showLoginWindow(self, *args, **kwargs):
		"""
			Return to the login window.
		"""
		self.hideMessage()
		conf["theApp"].logout()

	def checkForSuspendResume(self, *args, **kwargs):
		"""
			Test if at least self.pollIntervall seconds have passed and query the server if
		"""
		if (not self.viIsActive):
			return

		if ((datetime.now() - self.lastChecked).seconds > self.pollInterval) or self.isCurrentlyFailed:
			self.lastChecked = datetime.now()
			self.startPolling()

	def startPolling(self, *args, **kwargs):
		"""
			Start querying the server
		"""

		NetworkService.request("user", "view/self",
		                       successHandler=self.onUserTestSuccess,
		                       failureHandler=self.onUserTestFail)

	def onUserTestSuccess(self, req):
		"""
			We received a response from the server
		"""
		try:
			data = NetworkService.decode(req)
		except:
			self.showMessage()
			return

		if self.isCurrentlyFailed:
			if conf["currentUser"] != None and conf["currentUser"]["key"] == data["values"]["key"]:
				self.hideMessage()

	def onUserTestFail(self, text, ns):
		"""
			Error retrieving the current user response from the server
		"""
		self.showMessage()
