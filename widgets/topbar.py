# -*- coding: utf-8 -*-
from vi import html5

from vi.network import NetworkService, DeferredCall
from vi.i18n import translate
from vi.config import conf
from vi.widgets.task import TaskSelectWidget
from vi.priorityqueue import toplevelActionSelector
from vi.framework.components.button import Button
from vi.embedsvg import embedsvg
from vi.framework.components.icon import Icon
from vi.pane import Pane
from vi.widgets.edit import EditWidget
from vi.log import LogButton

class TopBarWidget(html5.Header):
	"""
		Provides the top-bar of VI
	"""
	def __init__(self):
		super(TopBarWidget,self ).__init__()

		self["class"] = "vi-topbar bar"

		self.sinkEvent("onClick")

		self.fromHTML("""
			<div class="vi-tb-left bar-group bar-group--left" [name]="topbarLeft">
				<div class="vi-tb-logo" [name]="topbarLogo"></div>
				<h1 class="vi-tb-title" [name]="moduleH1"></h1>
				<div class="item" [name]="moduleContainer">
					<div [name]="modulImg"></div>
					<div class="item-content" [name]="moduleName"></div>
				</div>
			</div>
			<nav class="vi-tb-right bar-group bar-group--right" [name]="topbarRight">
				<div class="input-group input-group--bar" [name]="iconnav">
				</div>
			</nav>
		""")

		svg = embedsvg.get("logos-vi")
		if svg:
			self.topbarLogo.element.innerHTML = svg + self.topbarLogo.element.innerHTML

		DeferredCall(self.setTitle, _delay=500)

	def invoke(self):
		self.iconnav.removeAllChildren()

		newBtn = html5.A()
		newBtn["href"] = "https://www.viur.is"
		newBtn["target"] = "_blank"
		newBtn.addClass("btn")
		svg = embedsvg.get("icons-ribbon")
		if svg:
			newBtn.element.innerHTML = svg + newBtn.element.innerHTML
		newBtn.appendChild(translate("vi.topbar.newbtn"))
		#self.iconnav.appendChild(newBtn)

		newMarker = html5.Span()
		newMarker.addClass("marker")
		newMarker.appendChild(translate("vi.topbar.new"))
		newBtn.appendChild(newMarker)

		for icon in conf["toplevelactions"]:
			widget = toplevelActionSelector.select(icon)
			# register log Button as Loghandler
			if widget == LogButton:
				conf["mainWindow"].logWdg = widget()
				self.iconnav.appendChild(conf["mainWindow"].logWdg)
			elif widget:
				self.iconnav.appendChild(widget())



	def setTitle(self, title=None):
		self.moduleH1.removeAllChildren()

		if title is None:
			title = conf.get("vi.name")

		if title:
			self.moduleH1.appendChild(html5.TextNode(html5.utils.unescape(title)))

	def onClick(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.moduleH1):
			conf["mainWindow"].switchFullscreen(not conf["mainWindow"].isFullscreen())

	def setCurrentModulDescr(self, descr = "", iconURL=None, iconClasses=None, path=None):
		self.moduleName.removeAllChildren()
		descr = html5.utils.unescape(descr)
		self.moduleName.appendChild(html5.TextNode(descr))

		self.modulImg.removeAllChildren()
		self.modulImg.appendChild( Icon(descr, iconURL) )

		conf["theApp"].setTitle(descr)

		if path:
			conf[ "theApp" ].setPath( path )

class UserState(html5.Div):
	def __init__(self, *args, **kwargs):
		super( UserState, self ).__init__(*args, **kwargs)

		self[ "class" ] = [ "popout-opener", "popout-anchor", "popout--sw" ]

		self.btn = Button( icon = "icons-user", className = "btn btn--topbar btn--user" )
		self.appendChild( self.btn )

		self.sinkEvent( "onClick" )

		popout = html5.Div()
		popout[ "class" ] = [ "popout" ]
		self.popoutlist = html5.Div()
		self.popoutlist[ "class" ] = [ "list" ]

		popout.appendChild( self.popoutlist )
		self.appendChild( popout )


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

		aitem = html5.Div()
		aitem[ "class" ] = [ "item", "has-hover", "item--small" ]
		# userinfo
		usrinfo = html5.Div()
		usermail = html5.Span()
		usermail.appendChild( html5.TextNode( user[ "name" ] ) )
		aitem.appendChild( usermail )
		self.popoutlist.appendChild( aitem )

		self["title"] = user["name"]
		self.currentUser = user["key"] or None
		self.addClass("vi-tb-accountmgnt")
		try:
			self.btn["text"] = "%s. %s" % (user["firstname"][0], user["lastname"])
		except:
			self.btn["text"] = user["name"]

	@staticmethod
	def canHandle( action ):
		return action == "userstate"

	def onClick( self, sender=None ):
		#load user module if not already loaded
		if not "user" in conf["modules"].keys():
			conf["modules"].update(
				{"user": {"handler": "list",
			              "name": "Benutzer"}
			    })

		self.openEdit( self.currentUser )

	def openEdit(self, key):
		apane = Pane(
			translate("Edit"),
			closeable=True,
			iconClasses=["module_%s" % "user", "apptype_list", "action_edit"],
			collapseable=True
		)

		conf["mainWindow"].addPane(apane)
		edwg = EditWidget("user", EditWidget.appList, key=key)

		actions = edwg.actionbar.getActions()
		actions.append("cancel.close")
		edwg.actionbar.setActions(actions, widget=edwg)

		apane.addWidget(edwg)

		conf["mainWindow"].focusPane(apane)
toplevelActionSelector.insert( 0, UserState.canHandle, UserState )

class Tasks(Button):
	def __init__(self, *args, **kwargs):
		super(Tasks, self).__init__(icon="icons-settings", *args, **kwargs)
		self.sinkEvent("onClick")
		self.hide()
		self.addClass("btn vi-tb-tasks")
		self.appendChild(html5.TextNode(translate("System")))

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

class Logout(Button):
	def __init__(self, *args, **kwargs):
		super(Logout,self).__init__(icon="icons-logout", *args, **kwargs)
		self.addClass("btn vi-tb-logout")
		self.appendChild(html5.TextNode(translate("Logout")))
		self.sinkEvent("onClick")

	def onClick(self, event):
		html5.ext.YesNoDialog(
			translate("Möchten Sie {vi.name} wirklich beenden?\n"
			          "Alle nicht gespeicherten Einträge gehen dabei verloren!",
			          **conf),
			title=translate("Logout"),
			yesCallback=lambda *args, **kwargs: self.logout()
		)
		event.stopPropagation()
		event.preventDefault()

	def logout( self ):
		conf[ "theApp" ].logout()

	@staticmethod
	def canHandle( action ):
		return action == "logout"
toplevelActionSelector.insert( 0, Logout.canHandle, Logout )

#FIXME: Put Message Center in Iconnav. The message center will be a popout in the topbar.
