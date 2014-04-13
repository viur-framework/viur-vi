import html5
from network import NetworkService, DeferredCall
from config import conf
from i18n import translate
class UserLogoutMsg( html5.ext.Popup):
	checkInterval = 1000*60*5
	def __init__(self, *args, **kwargs):
		super( UserLogoutMsg, self ).__init__( title=translate("user is logged out"), *args, **kwargs )
		self["class"].append("userloggendoutmsg")
		self.lbl = html5.Label(translate("Your session was terminated by our server. Perhaps your computer fall asleep and broke connection?\n Please relogin to continue your mission."))
		self.appendChild(self.lbl)

		refreshBtn = html5.ext.Button(translate("refresh"), callback=self.doRecheckUserAvaiable)
		self.appendChild(refreshBtn)

		applyBtn = html5.ext.Button(translate("Login"), callback=self.doApply)
		self.appendChild(applyBtn)
		self.parent()["style"]["display"]="none"
		DeferredCall(self.testUserTick,_delay=self.checkInterval)

	def doApply(self, *args, **kwargs):
		eval("""var fenster = window.open("/vi/user/login", "fenster1", "width=800,height=600,status=yes,scrollbars=yes,resizable=yes");""")
		#eval("""fenster.onload(function () { document.getElementById("CoreWindow").dispatchEvent(new Event('UserTryedToLogin'))});""")
		#eval("""fenster.onclose(function () { document.getElementById("CoreWindow").dispatchEvent(new Event('UserTryedToLogin'))});""")
		eval("""fenster.focus();""")

	def doRefresh(self,*args,**kwargs):
		#eval("window.onbeforeunload=None;")
		print("REFRESH !!")
		eval("window.onbeforeunload = void(0);")
		eval("window.top.location.href='/vi';")

	def doRecheckUserAvaiable(self, *args, **kwargs):
		if (self.parent()["style"]["display"]=="block"):
			if conf["currentUser"]!=None:
				self.parent()["style"]["display"]="none"
				conf["mainWindow"].log("success",translate("relogin success :-)"))

	def testUserAvaiable(self):
		NetworkService.request( None, "/vi/user/view/self", successHandler=self.onUserTestSuccess,failureHandler=self.onUserTestFail, cacheable=False )

	def testUserTick(self):
		self.testUserAvaiable()
		DeferredCall(self.testUserTick,_delay=self.checkInterval)

	def onUserTestSuccess(self,req):
		data = NetworkService.decode(req)
		#print ("keep Alive!")
		if (self.parent()["style"]["display"]=="block"):
			eval("""fenster.close();""")
			if conf["currentUser"]!=None and conf["currentUser"]["id"]==data["values"]["id"]:
				self.parent()["style"]["display"]="none"
				conf["mainWindow"].log("success",translate("relogin success :-)"))
			else:
				if conf["currentUser"]!=None and data["values"]!=None:
					self.lbl.element.innerHTML=translate("The user you choose to login differs from the user vi started with.\nolduser: {user} \nnewuser: {newuser}",user=conf["currentUser"]["name"],newuser=data["values"]["name"])
					applyBtn = html5.ext.Button(translate("refresh"), callback=self.doRefresh)
				else:
					self.doRefresh()
					#self.lbl=html5.Label("please ")
	def onUserTestFail(self,text, ns):
		self.parent()["style"]["display"]="block"
