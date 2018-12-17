# -*- coding: utf-8 -*-
import html5, embedsvg
from network import NetworkService, DeferredCall
from i18n import translate
from config import conf
from widgets.task import TaskSelectWidget
from widgets.button import Button
from priorityqueue import toplevelActionSelector

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
				<h1 class="vi-tb-title" [name]="modulH1"></h1>
				<div class="vi-tb-currentmodul item" [name]="modulContainer">
					<div class="item-image" [name]="modulImg"></div>
					<div class="item-content" [name]="moduleName"></div>
				</div>
			</div>
			<nav class="vi-tb-right bar-group bar-group--right" [name]="topbarRight">
				<div class="input-group" [name]="iconnav">
				</div>
			</nav>
		""")

		svg = embedsvg.embedsvg.get("logos-vi")
		if svg:
			self.topbarLogo.element.innerHTML = svg + self.topbarLogo.element.innerHTML

		DeferredCall(self.setTitle, _delay=500)

	def invoke(self):
		self.iconnav.removeAllChildren()

		newBtn = html5.A()
		newBtn["href"] = "https://www.viur.is"
		newBtn["target"] = "_blank"
		newBtn.addClass("btn btn--viur")
		svg = embedsvg.embedsvg.get("icons-notifications")
		if svg:
			newBtn.element.innerHTML = svg + newBtn.element.innerHTML
		newBtn.appendChild(translate("vi.topbar.newbtn"))
		self.iconnav.appendChild(newBtn)

		newMarker = html5.Span()
		newMarker.addClass("marker")
		newMarker.appendChild(translate("vi.topbar.new"))
		newBtn.appendChild(newMarker)

		for icon in conf["toplevelactions"]:
			widget = toplevelActionSelector.select(icon)
			if widget:
				self.iconnav.appendChild(widget())

	def setTitle(self):
		title = conf.get("vi.name")
		if title:
			self.modulH1.appendChild(html5.utils.unescape(title))

	def onClick(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.modulH1):
			conf["mainWindow"].switchFullscreen(not conf["mainWindow"].isFullscreen())

	def setCurrentModulDescr(self, descr = "", iconURL=None, iconClasses=None):
		for c in self.modulImg._children[:]:
			self.modulImg.removeChild(c)
		for c in self.moduleName._children[:]:
			self.moduleName.removeChild( c )
		for c in self.modulImg["class"]:
			self.modulImg.removeClass(c)

		self.modulImg.addClass("item-image")

		descr = html5.utils.unescape(descr)
		self.moduleName.appendChild(html5.TextNode(descr))

		if iconURL is not None:
			svg = embedsvg.embedsvg.get(iconURL)
			if svg:
				modulIcon = html5.I()
				modulIcon.addClass("i")
				modulIcon.element.innerHTML = svg + modulIcon.element.innerHTML
				self.modulImg.appendChild(modulIcon)
			else:
				img = html5.Img()
				img["src"] = iconURL
				self.modulImg.appendChild(img)

		if iconClasses is not None:
			for cls in iconClasses:
				self.modulImg.addClass( cls )

		conf["theApp"].setTitle(descr)

class UserState(Button):
	def __init__(self, *args, **kwargs):
		super( UserState, self ).__init__(*args, **kwargs)

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

		self["title"] = user["name"]
		self.addClass("vi-tb-accountmgnt")
		self.appendChild(html5.TextNode(user["name"]))

	@staticmethod
	def canHandle( action ):
		return action == "userstate"

toplevelActionSelector.insert( 0, UserState.canHandle, UserState )


class Tasks(Button):
	def __init__(self, *args, **kwargs):
		super(Tasks, self).__init__(icon="icons-settings", *args, **kwargs)
		self.sinkEvent("onClick")
		self.hide()
		self.addClass("btn vi-tb-tasks")
		self.appendChild(html5.TextNode(translate("vi.tasks")))

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


#FIXME: Do not logout directly: Implement a logout yes/no dialog.

class Logout(Button):
	def __init__(self, *args, **kwargs):
		super(Logout,self).__init__(icon="icons-logout", *args, **kwargs)
		self.addClass("btn vi-tb-logout")
		self.appendChild(html5.TextNode(translate("Logout")))
		self.sinkEvent("onClick")

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()
		conf["theApp"].logout()

	@staticmethod
	def canHandle( action ):
		return action == "logout"

toplevelActionSelector.insert( 0, Logout.canHandle, Logout )

#FIXME: Put Message Center in Iconnav. The message center will be a popout in the topbar.
