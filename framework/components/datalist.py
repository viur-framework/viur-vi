# -*- coding: utf-8 -*-
from ... import html5
from ...embedsvg import embedsvg
from vi.framework.utils import DeferredCall
from vi.framework.components.button import Button
from vi.i18n import translate


class Datalist(html5.Div):

	def __init__(self,name,*args, **kwargs):
		super().__init__(*args,**kwargs)
		self.input = html5.Input()
		self.input.element.setAttribute("list", name ) #fixme ["list"] = name does not work
		self.input.addClass("input ignt-input")
		self.appendChild(self.input)

		self.datalist = html5.Datalist()
		self.datalist["id"] = name
		self.appendChild(self.datalist)

		self.sinkEvent("onInput")

	def onInput(self, event):
		print(event.target)
		print("FJFJFJFJFJFJFJ")


class AutocompleteList(html5.Div):

	def __init__(self,inputId, *args, **kwargs):
		super().__init__( *args, **kwargs )
		self.holdactive = False
		self.currentSelection = None

		self.input = html5.Input()
		self.input.addClass( "input ignt-input" )
		self["style"]["position"] = "relative"
		self.appendChild( self.input )

		self._suggestionContainer = html5.Div()
		self._suggestionContainer["style"]["position"] = "absolute"
		self._suggestionContainer["style"]["background-color"] = "white"
		self._suggestionContainer.hide()

		self.suggestionList = html5.Ul()
		self.suggestionList.addClass("list")
		self._suggestionContainer.appendChild(self.suggestionList)

		self.moreEntries = Button(translate("mehr laden"))
		#self._suggestionContainer.appendChild(self.moreEntries)
		self.appendChild(self._suggestionContainer)

		DeferredCall(self.updateContainer, _delay = 1)
		self.sinkEvent("onClick")
		self.sinkEvent("onFocusOut")
		self.sinkEvent("onInput")


	def onInput(self, event):
		self.currentSelection=None
		self.holdactive = True
		self._suggestionContainer.show()
		val = self.input["value"]
		self._dataProvider.setFilter({"search":val})
		self.loadData()

		if not val:
			self.holdactive = False
		self._dataProvider.selectionupdate()

	def setDataProvider( self,obj ):
		assert obj == None or "onNextBatchNeeded" in dir( obj ), \
			"The dataProvider must provide a 'onNextBatchNeeded' function"
		self._dataProvider = obj
		self.loadData()

	def loadData( self ):
		if not self._dataProvider:
			self.emptyList()
			return 0
		self._dataProvider.onNextBatchNeeded()

	def emptyList( self ):
		self.moreEntries.hide()
		self.clearSuggestionList()
		emptyMessage = html5.Li()
		emptyMessage.addClass( "item has-hover item--small" )
		emptyMessage["data"]["value"] = None
		emptyMessage.appendChild( html5.TextNode( translate( "No Item" ) ) )
		self.suggestionList.appendChild( emptyMessage )

	def clearSuggestionList( self ):
		self.suggestionList.removeAllChildren()

	def appendListItem( self, item ):
		self.moreEntries.show()
		self.suggestionList.appendChild(item)

	def updateContainer( self ):
		print("UPDATE")
		inputPos = self.input.element.getBoundingClientRect()
		print(inputPos.right)
		print(inputPos.left)
		print("%spx" % (inputPos.right - inputPos.left))
		self._suggestionContainer[ "style" ][ "width" ] = "%spx" % (inputPos.right - inputPos.left)
		self._suggestionContainer[ "style" ][ "z-index" ] = 9999
		self._suggestionContainer[ "style" ][ "box-shadow" ] = "0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 3px 1px -2px rgba(0, 0, 0, 0.12), 0 1px 5px 0 rgba(0, 0, 0, 0.2)"
		self._suggestionContainer[ "style" ][ "max-height" ] = "255px"
		self._suggestionContainer[ "style" ][ "overflow-y" ] = "auto"
		self._suggestionContainer[ "style" ][ "overflow" ] = "hidden"

	def setSelection( self,targetElement ):
		print("SETSELECTION")

		entry = [x for x in self.suggestionList.children() if x.element == targetElement]
		if entry:
			entry = entry[0]
		else:
			self.currentSelection = None
			return 0

		if not entry["data"]["value"]:
			self.currentSelection = None
			return 0

		data = self._dataProvider.dataList[entry["data"]["value"]]
		print(data)
		self.input["value"] = entry.element.innerHTML
		self.currentSelection = data
		self._dataProvider.selectionupdate()


	def disableSuggestion( self,force=False ):

		if not self.holdactive or force:
			self._suggestionContainer.hide()

	def onFocusOut(self, event):
		DeferredCall(self.disableSuggestion,_delay = 200)
		DeferredCall( self.disableSuggestion,force=True, _delay = 10000 )

	def onClick(self, event):
		if event.target == self.input.element: #click on Input
			self._suggestionContainer.show()
			self.holdactive = False
		elif event.target.parentElement == self.suggestionList.element: #selected list
			self.setSelection(event.target)
			self.disableSuggestion()
			self.holdactive = False
		elif event.target in [self.suggestionList.element,self.element,self._suggestionContainer.element] or \
				event.target.parentElement in [self.suggestionList.element,self.element,self._suggestionContainer.element]:
			self.holdactive = True
		else:
			self.holdactive = False
