import html5
from network import NetworkService, DeferredCall
from config import conf
from i18n import translate
from datetime import datetime, timedelta

class UserLogoutMsg( html5.ext.Popup):
	pollInterval = 120 # We query the server once a minute
	checkIntervall = 1000*5 # We test if the system has been suspended every 5 seconds

	def __init__(self, *args, **kwargs):
		super( UserLogoutMsg, self ).__init__( title=translate("Session terminated"), *args, **kwargs )
		self["class"].append("userloggendoutmsg")
		self.isCurrentlyFailed = False
		self.isInitialTest = True
		self.loginWindow = None
		self.lastChecked = datetime.now()
		self.lbl = html5.Label(translate("Your session was terminated by our server. Perhaps your computer fall asleep and broke connection?\n Please relogin to continue your mission."))
		self.appendChild(self.lbl)
		self.appendChild(html5.ext.Button(translate("Refresh"), callback=self.startPolling) )
		self.appendChild( html5.ext.Button(translate("Login"), callback=self.showLoginWindow) )
		setInterval = eval("window.setInterval")
		setInterval( self.checkForSuspendResume, self.checkIntervall )
		self.hideMessage()

	def hideMessage(self):
		"""
			Make this popup invisible
		"""
		self.parent()["style"]["display"]="none"
		self.isCurrentlyFailed = False

	def showMessage(self):
		"""
			Show this popup
		"""
		self.parent()["style"]["display"]="block"
		self.isCurrentlyFailed = True

	def showLoginWindow(self, *args, **kwargs ):
		"""
			Open the login-window sothat the user can sign in again
		"""
		self.closeLoginWindow()
		newWindow = eval("window.open")
		self.loginWindow = newWindow("/vi/user/login", "loginwindow", "width=800,height=600,status=yes,scrollbars=yes,resizable=yes")
		self.loginWindow.focus()

	def closeLoginWindow(self, *args, **kwargs ):
		return #Due to a bug in chrome, we either a) cannot close the window or b) crash the browser
		if self.loginWindow:
			self.closeLoginWindow()
			self.loginWindow = None
			try:
				self.closeLoginWindow()
			except:
				pass

	def checkForSuspendResume(self,*args, **kwargs):
		"""
			Test if at least self.pollIntervall seconds have passed and query the server if
		"""
		if ((datetime.now()-self.lastChecked).seconds>self.pollInterval) or self.isCurrentlyFailed:
			self.lastChecked = datetime.now()
			self.startPolling()

	def startPolling(self, *args, **kwargs ):
		"""
			Start querying the server
		"""
		NetworkService.request( None, "/vi/user/view/self", successHandler=self.onUserTestSuccess,failureHandler=self.onUserTestFail, cacheable=False )

	def onUserTestSuccess(self,req):
		"""
			We received a response from the server
		"""
		self.isInitialTest = False
		try:
			data = NetworkService.decode(req)
		except:
			self.showMessage()
			return
		if self.isCurrentlyFailed:
			if conf["currentUser"]!=None and conf["currentUser"]["id"]==data["values"]["id"]:
				self.hideMessage()
				self.closeLoginWindow()

	def onUserTestFail(self,text, ns):
		"""
			Error retrieving the current user response from the server
		"""
		if self.isInitialTest:
			eval("window.top.preventViUnloading = false;")
			eval("window.top.location = '/vi'")
		self.showMessage()





