import html5
from network import NetworkService

class TopBarWidget( html5.Header ):
	def __init__(self):
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__( )
		self["class"] = "vi_topbar"
		anav=html5.Nav()
		anav["class"].append("iconnav")
		self.iconnav=html5.Ul()
		self.iconnav.appendChild(DashBoard())
		self.iconnav.appendChild(MyFiles())
		self.iconnav.appendChild(Settings())
		self.iconnav.appendChild(UserState())
		self.iconnav.appendChild(Logout())
		anav.appendChild(self.iconnav)
		self.appendChild(anav)


class UserState(html5.Li):
	def __init__(self):
		super(UserState,self).__init__()

		NetworkService.request( "user", "view/self", successHandler=self.onCurrentUserAvaiable, cacheable=False )

	def onCurrentUserAvaiable(self, req):
		data = NetworkService.decode(req)
		aa=html5.A()
		aa["title"]=str(data["values"])
		aa["class"].append("icon accountmgnt")
		aa.appendChild(html5.TextNode(data["values"]["name"]))
		self.appendChild(aa)

class DashBoard(html5.Li):
	def __init__(self):
		super(DashBoard,self).__init__()
		aa=html5.A()
		aa["class"].append("icon dashboard")
		aa.appendChild(html5.TextNode("Dashboard"))
		self.appendChild(aa)

class MyFiles(html5.Li):
	def __init__(self):
		super(MyFiles,self).__init__()
		aa=html5.A()
		aa["class"].append("icon myfiles")
		aa.appendChild(html5.TextNode("My Files"))
		self.appendChild(aa)

class Settings(html5.Li):
	def __init__(self):
		super(Settings,self).__init__()
		aa=html5.A()
		aa["class"].append("icon settings")
		aa.appendChild(html5.TextNode("Settings"))
		self.appendChild(aa)

class Logout(html5.Li):
	def __init__(self):
		super(Logout,self).__init__()
		##NetworkService.request( "skey", "", successHandler=self.onSkeyAvaiable, cacheable=False )

	##def onSkeyAvaiable(self, req):
		aa=html5.A()
		aa["class"].append("icon logout")
		aa.appendChild(html5.TextNode("Logout"))
		self.appendChild(aa)