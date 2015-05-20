import html5
from html5.keycodes import isReturn
from event import EventDispatcher
from i18n import translate

class Search( html5.Div ):
	def __init__(self, *args, **kwargs):
		super( Search, self ).__init__( *args, **kwargs )
		self.startSearchEvent = EventDispatcher("startSearch")
		self["class"].append("search")
		lblSearch = html5.H2()
		lblSearch.appendChild( html5.TextNode(translate("Fulltext search")))
		self.appendChild( lblSearch )
		self.searchInput = html5.Input()
		self.searchInput["type"] = "text"
		self.appendChild(self.searchInput)
		self.btn = html5.ext.Button(translate("Search"), callback=self.doSearch)
		self.appendChild(self.btn)
		self.sinkEvent("onKeyDown")
		self.last_search = ""

	def doSearch(self, *args, **kwargs):
		if self.searchInput["value"] != self.last_search:
			if len( self.searchInput[ "value" ] ):
				self.startSearchEvent.fire( self.searchInput["value"] )
			else:
				self.resetSearch()

			self.last_search = self.searchInput["value"]

	def resetSearch(self):
		self.startSearchEvent.fire( None )

	def onKeyDown(self, event):
		if isReturn(event.keyCode):
			self.doSearch()
			event.preventDefault()
			event.stopPropagation()

	def resetLoadingState(self):
		if "is_loading" in self.btn["class"]:
			self.btn["class"].remove("is_loading")

	def reevaluate(self):
		self.doSearch()

	def focus(self):
		self.searchInput.focus()
