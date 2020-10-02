# -*- coding: utf-8 -*-
from flare import html5
from flare.button import Button
from flare.input import Input
from flare.event import EventDispatcher
from vi.i18n import translate


class Search(html5.Div):
	def __init__(self, *args, **kwargs):
		super(Search, self).__init__(*args, **kwargs)
		self.startSearchEvent = EventDispatcher("startSearch")
		self.addClass("vi-search")
		self.searchLbl = html5.H2()
		self.searchLbl.appendChild(html5.TextNode(translate("Fulltext search")))
		self.searchLbl.addClass("vi-search-label")
		self.appendChild(self.searchLbl)
		self.searchInput = Input()
		self.searchInput["type"] = "text"
		self.appendChild(self.searchInput)
		self.btn = Button(translate("Search"), callback=self.doSearch)
		self.appendChild(self.btn)
		self.sinkEvent("onKeyDown")
		self.last_search = ""

	def doSearch(self, *args, **kwargs):
		if self.searchInput["value"] != self.last_search:
			if len(self.searchInput["value"]):
				self.startSearchEvent.fire(self.searchInput["value"])
			else:
				self.resetSearch()

			self.last_search = self.searchInput["value"]

	def resetSearch(self):
		self.startSearchEvent.fire(None)

	def onKeyDown(self, event):
		if html5.isReturn(event):
			self.doSearch()
			event.preventDefault()
			event.stopPropagation()

	def resetLoadingState(self):
		if "is-loading" in self.btn["class"]:
			self.btn.removeClass("is-loading")

	def reevaluate(self):
		self.doSearch()

	def focus(self):
		self.searchInput.focus()
