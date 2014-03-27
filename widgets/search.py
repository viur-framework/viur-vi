import html5
from html5.keycodes import isReturn
from event import EventDispatcher
from i18n import translate
class Search( html5.Div ):
	def __init__(self, *args, **kwargs):
		super( Search, self ).__init__( *args, **kwargs )
		self.startSearchEvent = EventDispatcher("startSearch")
		self["class"].append("search")
		lblSearch = html5.Span()
		lblSearch.appendChild( html5.TextNode("Search"))
		self.appendChild( lblSearch )
		self.searchInput = html5.Input()
		self.searchInput["type"] = "text"
		self.appendChild(self.searchInput)
		self.btn = html5.ext.Button(translate("Search"), callback=self.doSearch)
		self.appendChild(self.btn)
		self.sinkEvent("onKeyDown")

	def doSearch(self, *args, **kwargs):
		self.startSearchEvent.fire(self.searchInput["value"] or None)
		if not "is_loading" in self.btn["class"]:
			self.btn["class"].append("is_loading")

	def onKeyDown(self, event):
		if isReturn(event.keyCode):
			self.doSearch()
			event.preventDefault()
			event.stopPropagation()

	def resetLoadingState(self):
		if "is_loading" in self.btn["class"]:
			self.btn["class"].remove("is_loading")