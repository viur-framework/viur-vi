# -*- coding: utf-8 -*-
import html5
from config import conf
from widgets.search import Search
from priorityqueue import extendedSearchWidgetSelector
from pane import Pane
from i18n import translate
import utils



class CompoundFilter( html5.Div ):
	def __init__(self, view, module, embed=False, *args, **kwargs ):
		super( CompoundFilter, self ).__init__( *args, **kwargs)

		self["class"].append("compoundfilter")
		self.view = view
		self.module = module
		self.embed = embed

		if embed:
			self["class"].append("embed")
			self["class"].append("expanded")
		else:
			self["class"].append("standalone")
			self["class"].append("collapsed")

		if "name" in view.keys():
			h2 = html5.H2()
			h2.appendChild( html5.TextNode( view["name"] ) )
			self.appendChild( h2 )

		self.extendedFilters = []

		for extension in (view["extendedFilters"] if "extendedFilters" in view.keys() else []):
			wdg = extendedSearchWidgetSelector.select( extension, view, module)

			if wdg is not None:
				container = html5.Div()
				container["class"].append("extendedfilter")
				wdg = wdg( extension, view, module )
				container.appendChild( wdg )
				self.appendChild( container )
				self.extendedFilters.append( wdg )
				wdg.filterChangedEvent.register( self )
		#btn = html5.ext.Button("Apply", self.reevaluate)
		#self.appendChild( btn )

	def onFilterChanged(self, *args, **kwargs):
		self.reevaluate()

	def reevaluate(self, *args, **kwargs ):
		if "filter" in self.view.keys():
			filter = self.view["filter"].copy()
		else:
			filter = {}

		for extension in self.extendedFilters:
			filter = extension.updateFilter( filter )

		if self.embed:
			self.parent().setFilter( filter, -1, "" )
		else:
			self.parent().applyFilter( filter, -1, translate( "Extended Search" ) )

	def focus(self):
		for extension in self.extendedFilters:
			if ( "focus" in dir( extension )
			     and callable( extension.focus ) ):
				extension.focus()

class FilterSelector( html5.Div ):
	def __init__(self, module, *args, **kwargs ):
		"""
		:param module: The name of the module for which this filter is created for
		:param args:
		:param kwargs:
		:return:
		"""
		super( FilterSelector, self ).__init__( *args, **kwargs )
		self.module = module
		self.currentTarget = None
		self.defaultFilter = True
		self.sinkEvent("onClick")

	def onClick(self, event):
		"""
		Handle event on filter selection (fold current active filter, expand selected filter and execute, if possible)
		:param event:
		:return:
		"""
		nextTarget = self.currentTarget
		for c in self._children:
			if c == self.currentTarget and not html5.utils.doesEventHitWidgetOrChildren(event, c):
				c["class"].append("collapsed")
				c["class"].remove("expanded")
				if nextTarget==self.currentTarget: #Did not change yet
					nextTarget = None
			elif c != self.currentTarget and html5.utils.doesEventHitWidgetOrChildren(event, c):
				c["class"].remove("collapsed")
				c["class"].append("expanded")
				nextTarget = c

		if self.currentTarget != nextTarget:
			self.defaultFilter = False
			self.currentTarget = nextTarget

			if "reevaluate" in dir( nextTarget ):
				nextTarget.reevaluate()

		if ("focus" in dir(self.currentTarget)
			and callable(self.currentTarget.focus)):
			self.currentTarget.focus()

	def onAttach(self):
		super(FilterSelector, self).onAttach()

		activeFilter = self.parent().parent().filterID
		isSearchDisabled=False

		if self.module in conf["modules"].keys():
			modulConfig = conf["modules"][self.module]
			if "views" in modulConfig.keys() and modulConfig["views"]:
				for view in modulConfig["views"]:
					self.appendChild( CompoundFilter( view, self.module ) )
			if "disabledFunctions" in modulConfig.keys() and modulConfig[ "disabledFunctions" ] and "fulltext-search" in modulConfig[ "disabledFunctions" ]:
				isSearchDisabled = True

		if not isSearchDisabled:
			self.search = Search()
			self.search["class"].append("collapsed")
			self.appendChild(self.search)
			self.search.startSearchEvent.register( self )

	def onDetach(self):
		if not self.defaultFilter:
			self.onStartSearch()

		super(FilterSelector, self).onDetach()

	def onStartSearch(self, searchTxt = None):
		self.defaultFilter = not searchTxt

		if self.module in conf["modules"].keys():
			modulConfig = conf["modules"][self.module]
			if "filter" in modulConfig.keys():
				filter = modulConfig["filter"]
			else:
				filter = {}

			if searchTxt:
				filter["search"] = searchTxt
				self.applyFilter( filter, -1, translate("Fulltext search: {token}", token=searchTxt) )
			else:
				if "search" in filter.keys():
					filter.pop("search", None )

				self.applyFilter( filter, -1, "" )

	def setView(self, btn):
		self.applyFilter( btn.destView["filter"], btn.destView["__id"], btn.destView["name"]  )

	def applyFilter(self, filter, filterID, filterName):
		self.parent().parent().setFilter( filter, filterID, filterName )
