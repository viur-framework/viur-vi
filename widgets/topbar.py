# -*- coding: utf-8 -*-
import html5
from network import NetworkService, DeferredCall
from i18n import translate
from config import conf
from widgets.task import TaskSelectWidget
from priorityqueue import toplevelActionSelector

class TopBarWidget(html5.Header):
	"""
		Provides the top-bar of VI
	"""
	def __init__(self):
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__()

		self["class"] = "vi_topbar"
		anav=html5.Nav()
		anav["class"].append("iconnav")
		self.iconnav=html5.Ul()

		#self.logoContainer = html5.Div()
		#self.logoContainer["class"].append("logo")
		#self.appendChild( self.logoContainer )

		self.sinkEvent("onClick")

		self.modulH1 = html5.H1()
		self.modulH1._setClass("module")
		self.appendChild(self.modulH1)

		self.modulContainer = html5.Div()
		self.modulContainer["class"].append("currentmodul")
		self.appendChild( self.modulContainer )

		self.modulImg = html5.Label()
		self.modulContainer.appendChild(self.modulImg)

		self.moduleName = html5.Span()
		self.modulContainer.appendChild( self.moduleName )

		anav.appendChild(self.iconnav)
		self.appendChild(anav)

		DeferredCall(self.setTitle, _delay=500)

	def invoke(self):
		self.iconnav.removeAllChildren()

		for icon in conf["toplevelactions"]:
			widget = toplevelActionSelector.select(icon)
			if widget:
				self.iconnav.appendChild(widget())

	def setTitle(self):
		title = conf.get("vi.name")
		if title:
			self.modulH1.appendChild(html5.TextNode(html5.utils.unescape(title)))

	def onClick(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.modulH1):
			conf["mainWindow"].switchFullscreen(not conf["mainWindow"].isFullscreen())

	def setCurrentModulDescr(self, descr = "", iconURL=None, iconClasses=None):
		for c in self.modulImg._children[:]:
			self.modulImg.removeChild(c)
		for c in self.moduleName._children[:]:
			self.moduleName.removeChild( c )
		for c in self.modulImg["class"]:
			self.modulImg["class"].remove(c)

		descr = html5.utils.unescape(descr)
		self.moduleName.appendChild(html5.TextNode(descr))

		if iconURL is not None:
			img = html5.Img()
			img["src"] = iconURL
			self.modulImg.appendChild(img)

		if iconClasses is not None:
			for cls in iconClasses:
				self.modulImg["class"].append( cls )

		conf["theApp"].setTitle(descr)

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
		aa["title"] = user[ "name" ]
		aa["class"].append("icon accountmgnt")
		aa.appendChild( html5.TextNode( user[ "name" ] ) )
		self.appendChild(aa)

	@staticmethod
	def canHandle( action ):
		return action == "userstate"

toplevelActionSelector.insert( 0, UserState.canHandle, UserState )


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
			NetworkService.request( None, "/vi/_tasks/list",
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

	@staticmethod
	def canHandle( action ):
		return action == "tasks"

toplevelActionSelector.insert( 0, Tasks.canHandle, Tasks )


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
		conf["theApp"].logout()

	@staticmethod
	def canHandle( action ):
		return action == "logout"

toplevelActionSelector.insert( 0, Logout.canHandle, Logout )
