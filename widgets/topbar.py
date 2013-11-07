import pyjd # this is dummy in pyjs.
import html5
from network import NetworkService

class TopBarWidget( html5.Div ):
	def __init__(self):
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__( )
		self["class"] = "vi_topbar"
		NetworkService.request( "user", "view/self", successHandler=self.onDD, cacheable=False )
		#HTTPRequest().asyncGet("/admin/user/view/self", self)
		#self.nav.setParent( self )
		#self.element.appendChild( self.nav )

		#h1 = DOM.createElement("h1")
		#h1.innerText = "ViAppName"
		#DOM.appendChild( self.element, h1 )
		#self.nav = DOM.createElement("nav")
		#self.nav.setAttribute("class","iconnav")
		#DOM.appendChild( self.element, self.nav )
		#self.ul = DOM.createElement("ul")
		#DOM.appendChild( self.nav, self.ul )
		#self.add( self.nav )
		#FocusWidget.__init__(self, self.element)

	def onDD(self, req):
		print("onDD")
		data = NetworkService.decode(req)
		nameLi = html5.Li()
		nameLi.element.innerHTML = "<a href=\"#\" title=\"{'accountmanagement'}\" class=\"icon accountmgnt\">%s</a>" % data["values"]["name"]
		self.appendChild( nameLi )

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