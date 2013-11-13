import html5
from network import NetworkService

class TopBarWidget( html5.Div ):
	def __init__(self):
		#DOM.setAttribute( self.element, "class", "vi_topbar")
		super(TopBarWidget,self ).__init__( )
		self["class"] = "vi_topbar"
		NetworkService.request( "user", "view/self", successHandler=self.onCurrentUserAvaiable, cacheable=False )

	def onCurrentUserAvaiable(self, req):
		data = NetworkService.decode(req)
		nameLi = html5.Li()
		nameLi.element.innerHTML = "<a href=\"#\" title=\"{'accountmanagement'}\" class=\"icon accountmgnt\">%s</a>" % data["values"]["name"]
		self.appendChild( nameLi )


