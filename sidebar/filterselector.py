import html5
from config import conf
from widgets.search import Search
from priorityqueue import extendedSearchWidgetSelector


class CompoundFilter( html5.Div ):
	def __init__(self, view, modul, *args, **kwargs ):
		super( CompoundFilter, self ).__init__( *args, **kwargs)
		self.view = view
		self.modul = modul
		self.extendedFilters = []
		for extension in view["extendedFilters"]:
			wdg = extendedSearchWidgetSelector.select( extension, view, modul)
			if wdg is not None:
				container = html5.Div()
				container["class"].append("extendedfilter")
				wdg = wdg( extension, view, modul )
				container.appendChild( wdg )
				self.appendChild( container )
				self.extendedFilters.append( wdg )
				wdg.filterChangedEvent.register( self )
		#btn = html5.ext.Button("Apply", self.reevaluate)
		#self.appendChild( btn )

	def onFilterChanged(self, *args, **kwargs):
		self.reevaluate()

	def reevaluate(self, *args, **kwargs ):
		filter = self.view["filter"].copy()
		for extension in self.extendedFilters:
			filter = extension.updateFilter( filter )
		self.parent().applyFilter( filter )


class FilterSelector( html5.Div ):
	def __init__(self, modul, *args, **kwargs ):
		super( FilterSelector, self ).__init__( *args, **kwargs )
		self.modul = modul
		if modul in conf["modules"].keys():
			modulConfig = conf["modules"][modul]
			if "views" in modulConfig.keys() and modulConfig["views"]:
				for view in modulConfig["views"]:
					if "extendedFilters" in view.keys() and view["extendedFilters"]:
						self.appendChild( CompoundFilter( view, modul ) )
					else:
						btn = html5.ext.Button( callback=self.setView )
						btn.destView = view
						if "icon" in view.keys() and view["icon"]:
							img = html5.Img()
							img["src"] = view["icon"]
							btn.appendChild(img)
						btn.appendChild( html5.TextNode(view["name"]))
						self.appendChild( btn )
		self.search = Search()
		self.appendChild(self.search)
		self.search.startSearchEvent.register( self )


	def onStartSearch(self, searchTxt):
		filter = self.parent().parent().getFilter()
		if searchTxt:
			filter["search"] = searchTxt
		else:
			if "search" in filter.keys():
				del filter["search"]
		self.applyFilter( filter )


	def setView(self, btn):
		print("SETTING VIEW", btn.destView)
		self.applyFilter( btn.destView["filter"] )


	def applyFilter(self, filter):
		self.parent().parent().setFilter( filter )
		self.parent().parent().sideBar.setWidget( None )

