# -*- coding: utf-8 -*-
import html5
from network import NetworkService
from i18n import translate
from config import conf
from widgets.task import TaskSelectWidget

class TopBarWidget( html5.Header ):

	def getConf(self):
		NetworkService.request( None, "/admin/config", successHandler=self.onCompletion,
					failureHandler=self.onError, cacheable=True )

	def onCompletion(self, req):
		data = NetworkService.decode(req)
		if "configuration" in data.keys() and isinstance( data["configuration"], dict):
			if "vi.name" in data["configuration"].keys():
				self.modulH1.appendChild(html5.TextNode(data["configuration"]["vi.name"]))
			#self.logoContainer["style"]["background-image"]="url('"+data["configuration"]["vi.logo"]+"')"
	def onError(self, req, code):
		print("ONERROR")

	"""
		Provides the top-bar of VI
	"""
	def __init__(self):
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__( )
		self["class"] = "vi_topbar"
		anav=html5.Nav()
		anav["class"].append("iconnav")
		self.iconnav=html5.Ul()

		#self.logoContainer = html5.Div()
		#self.logoContainer["class"].append("logo")
		#self.appendChild( self.logoContainer )

		self.modulH1 = html5.H1()
		self.modulH1._setClass("beta")
		self.appendChild(self.modulH1)


		self.modulContainer = html5.Div()
		self.modulContainer["class"].append("currentmodul")
		self.appendChild( self.modulContainer )
		self.modulImg = html5.Label()
		self.modulContainer.appendChild(self.modulImg)
		self.modulName = html5.Span()
		self.modulContainer.appendChild( self.modulName )
		#self.iconnav.appendChild(DashBoard())
		#self.iconnav.appendChild(MyFiles())
		#self.iconnav.appendChild(Settings())
		self.iconnav.appendChild(Tasks())
		self.iconnav.appendChild(UserState())
		self.iconnav.appendChild(Logout())
		anav.appendChild(self.iconnav)
		self.appendChild(anav)
		self.getConf()

	def setCurrentModulDescr(self, descr, iconURL=None, iconClasses=None):
		for c in self.modulImg._children[:]:
			self.modulImg.removeChild(c)
		for c in self.modulName._children[:]:
			self.modulName.removeChild( c )
		for c in self.modulImg["class"]:
			self.modulImg["class"].remove(c)
		self.modulName.appendChild( html5.TextNode(descr))
		if iconURL is not None:
			img = html5.Img()
			img["src"] = iconURL
			self.modulImg.appendChild(img)
		if iconClasses is not None:
			for cls in iconClasses:
				self.modulImg["class"].append( cls )

		eval("top.document.title='"+descr+"'")

class UserState(html5.Li):
	def __init__(self):
		super(UserState,self).__init__()
		self.update()

	def onCurrentUserAvailable(self, req):
		data = NetworkService.decode( req )
		conf[ "currentUser" ] = data[ "values" ]
		self.update()

	def update(self):
		user = conf.get( "currentUser" )
		if not user:
			NetworkService.request( "user", "view/self",
			                        successHandler=self.onCurrentUserAvailable,
			                        cacheable=False )
			return

		aa = html5.A()
		aa["title"] = str( user )
		aa["class"].append("icon accountmgnt")
		aa.appendChild( html5.TextNode( user[ "name" ] ) )
		self.appendChild(aa)

class Tasks(html5.Li):
	def __init__(self):
		super(Tasks, self).__init__()
		self.sinkEvent("onClick")
		self.hide()

		a = html5.A()
		a[ "class" ].append( "icon tasks" )
		a.appendChild( html5.TextNode( translate( "Tasks" ) ) )
		self.appendChild( a )

		if not conf[ "tasks" ][ "server" ]:
			NetworkService.request( None, "/admin/_tasks/list",
		        successHandler=self.onTaskListAvailable,
		        cacheable=False )

		self.update()

	def onTaskListAvailable(self, req):
		data = NetworkService.decode(req)
		if not "skellist" in data.keys() or not data[ "skellist" ]:
			conf[ "tasks" ][ "server" ] = []
			self.hide()
			return

		conf[ "tasks" ][ "server" ] = data[ "skellist" ]

	def onTaskListFailure(self):
		self.hide()

	def onCurrentUserAvailable(self, req):
		data = NetworkService.decode( req )
		conf[ "currentUser" ] = data[ "values" ]
		self.update()

	def update(self):
		user = conf.get( "currentUser" )
		if not user:
			NetworkService.request( "user", "view/self",
			                        successHandler=self.onCurrentUserAvailable,
			                        cacheable=False )
			return

		if "root" in user[ "access" ]:
			self.show()

	def onClick(self, event ):
		TaskSelectWidget()

class DashBoard(html5.Li):
	def __init__(self):
		super(DashBoard,self).__init__()
		aa=html5.A()
		aa["class"].append("icon dashboard")
		aa.appendChild(html5.TextNode(translate("Dashboard")))
		self.appendChild(aa)

class MyFiles(html5.Li):
	def __init__(self):
		super(MyFiles,self).__init__()
		aa=html5.A()
		aa["class"].append("icon myfiles")
		aa.appendChild(html5.TextNode(translate("My Files")))
		self.appendChild(aa)

class Settings(html5.Li):
	def __init__(self):
		super(Settings,self).__init__()
		aa=html5.A()
		aa["class"].append("icon settings")
		aa.appendChild(html5.TextNode(translate("Settings")))
		self.appendChild(aa)

class Logout(html5.Li):
	def __init__(self):
		super(Logout,self).__init__()
		aa=html5.A()
		aa["class"].append("icon logout")
		aa.appendChild(html5.TextNode(translate("Logout")))
		self.appendChild(aa)
		self.sinkEvent("onClick")

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()
		NetworkService.request( "skey", "", successHandler=self.onSkeyAvaiable, cacheable=False )

	def onSkeyAvaiable(self, req):
		skey = NetworkService.decode( req )
		assert not "\"" in skey
		eval("""window.top.location.href = "/vi/user/logout?skey="""+skey+"""&";""")