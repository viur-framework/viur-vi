import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui import Event
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Panel import Panel
from pyjamas import DOM
import json
from network import NetworkService

class TopBarWidget(Widget):
	def __init__(self):
		self.element = DOM.createElement("header")
		self.setStyleName( "vi_topbar")
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__( self.element)
		NetworkService.request( "user", "view/self", successHandler=self.onDD, cacheable=False )
		#HTTPRequest().asyncGet("/admin/user/view/self", self)
		#self.nav.setParent( self )
		#self.element.appendChild( self.nav )
		h1 = DOM.createElement("h1")
		h1.innerText = "ViAppName"
		DOM.appendChild( self.element, h1 )
		self.nav = DOM.createElement("nav")
		self.nav.setAttribute("class","iconnav")
		DOM.appendChild( self.element, self.nav )
		self.ul = DOM.createElement("ul")
		DOM.appendChild( self.nav, self.ul )
		#self.add( self.nav )
		#FocusWidget.__init__(self, self.element)

	def onDD(self, req):
		print("onDD")
		data = NetworkService.decode(req)
		nameLi = DOM.createElement("li")
		nameLi.innerHTML = "<a href=\"#\" title=\"{'accountmanagement'}\" class=\"icon accountmgnt\">%s</a>" % data["values"]["name"]
		DOM.appendChild( self.ul, nameLi )
		#l = Label("SUCESS")
		#RootPanel().add(l)
		#l = Label(text)
		#RootPanel().add(l)

	def onError(self, text, code):
		l = Label("FAILED")
		RootPanel().add(l)
		l = Label(code)
		RootPanel().add(l)

	def onTimeout(self, text):
		l = Label("TIMEOUT")
		RootPanel().add(l)
		l = Label(unicode(text))
		RootPanel().add(l)