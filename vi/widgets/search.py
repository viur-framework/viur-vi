# -*- coding: utf-8 -*-
from flare import html5
from flare.button import Button
from flare.input import Input
from flare.event import EventDispatcher
from flare.i18n import translate
from flare.icons import SvgIcon,Icon


class Search(html5.Div):
	def __init__(self, *args, **kwargs):
		super(Search, self).__init__(*args, **kwargs)
		self.startSearchEvent = EventDispatcher("startSearch")

		self.addClass( "vi-search" )

		self.headWidget = html5.Div()
		self.headWidget.addClass("header")
		filterImage = html5.Div()
		filterImage.addClass( "item-image" )
		self.headWidget.appendChild( filterImage )
		filterImage.appendChild( Icon( "icon-search" ) )

		self.searchLbl = html5.H2()
		self.searchLbl.appendChild(html5.TextNode(translate("Fulltext search")))
		self.searchLbl.addClass("vi-search-label item-content")
		self.headWidget.appendChild(self.searchLbl)

		self.bodyWidget = html5.Div()
		self.bodyWidget.addClass( "searchbody" )
		self.searchInput = Input()
		self.searchInput["type"] = "text"
		self.bodyWidget.appendChild(self.searchInput)
		self.btn = Button(translate("Search"), callback=self.doSearch)
		self.bodyWidget.appendChild(self.btn)


		self.appendChild(self.headWidget)
		self.appendChild(self.bodyWidget)

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
