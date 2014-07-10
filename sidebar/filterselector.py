import html5
from config import conf
from widgets.search import Search
from widgets.list import ListWidget
from priorityqueue import extendedSearchWidgetSelector
from pane import Pane
from i18n import translate


class CompoundFilter( html5.Div ):
	def __init__(self, view, modul, *args, **kwargs ):
		super( CompoundFilter, self ).__init__( *args, **kwargs)
		self["class"].append("compoundfilter")
		self.view = view
		self.modul = modul
		if "name" in view.keys():
			h2 = html5.H2()
			h2.appendChild( html5.TextNode( view["name"] ) )
			self.appendChild( h2 )
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
		self.parent().applyFilter( filter, -1, "Erweiterte Suche" )



class FilterSelector( html5.Div ):
	def __init__(self, modul, *args, **kwargs ):
		super( FilterSelector, self ).__init__( *args, **kwargs )
		self.modul = modul

	def onAttach(self):
		super( FilterSelector, self ).onAttach()
		activeFilter = self.parent().parent().filterID
		if self.modul in conf["modules"].keys():
			modulConfig = conf["modules"][self.modul]
			if "views" in modulConfig.keys() and modulConfig["views"]:
				for view in modulConfig["views"]:
					if "extendedFilters" in view.keys() and view["extendedFilters"] and view["__id"] == activeFilter:
						self.appendChild( CompoundFilter( view, self.modul ) )
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
		if not searchTxt:
			return
		if self.modul in conf["modules"].keys():
			modulConfig = conf["modules"][self.modul]
			if "filter" in modulConfig.keys():
				filter = modulConfig["filter"]
			else:
				filter = {}
			filter["search"] = searchTxt
			self.applyFilter( filter, -1, translate("Fulltext search: {token}", token=searchTxt) )


	def setView(self, btn):
		self.applyFilter( btn.destView["filter"], btn.destView["__id"], btn.destView["name"]  )


	def applyFilter(self, filter, filterID, filterName):
		if self.parent().parent().filterID == filterID or self.parent().parent().isSelector:
			self.parent().parent().setFilter( filter, filterID, filterName )
			self.parent().parent().sideBar.setWidget( type(self)( self.modul ) )
		else:
			filterIcon = None
			if self.modul in conf["modules"].keys() and conf["modules"][ self.modul ] and \
			   "views" in conf["modules"][ self.modul ].keys() and conf["modules"][ self.modul ]["views"]:
				for v in conf["modules"][ self.modul ]["views"]:
					if v["__id"] == filterID:
						if "icon" in v.keys() and v["icon"]:
							filterIcon = v["icon"]
						break
			p = Pane( filterName, iconURL=filterIcon, closeable=True )
			conf["mainWindow"].stackPane( p )
			## FIXME
			l = ListWidget( self.parent().parent().modul, columns=self.parent().parent().columns, isSelector=False,
					filter=filter, filterID=filterID, filterDescr=filterName )
			p.addWidget( l )
			p.focus()
			l.sideBar.setWidget( FilterSelector( self.modul ) )
			self.parent().parent().sideBar.setWidget( None )


