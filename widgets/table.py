import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui import Event
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Panel import Panel
from pyjamas import DOM
import time
import json
from network import NetworkService
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.Focus import FocusMixin
from pyjamas.ui.FocusWidget import FocusWidget
import pygwt
from pyjamas.Timer import Timer
from event import EventDispatcher

def addClass( elem, cls):
	cls = cls.lower()
	classes = DOM.getElemAttribute( elem, "class" )
	if not classes:
		tmpCls = []
	else:
		tmpCls = classes.lower().split(" ")
	if not cls in tmpCls:
		tmpCls.append( cls )
	DOM.setElemAttribute( elem, "class", " ".join(tmpCls))

def removeClass(elem, cls):
	cls = cls.lower()
	classes = DOM.getElemAttribute( elem, "class" )
	if not classes:
		tmpCls = []
	else:
		tmpCls = classes.lower().split(" ")
	if cls in tmpCls:
		tmpCls.remove( cls )
	DOM.setElemAttribute( elem, "class", " ".join(tmpCls))


class SelectTable( FlexTable, FocusWidget ):
	"""
		Provides an Html-Table which allows selecting rows.
		Parent widgets can register for certain events:

			- selectionChanged: called if the current _multi_ selection changes. (Ie the user
				holds ctrl and clicks a row). The selection might contain no, one or multiple rows.
				Its also called if the cursor moves. Its called if the user simply double
				clicks a row. So its possible to recive a selectionActivated event without an
				selectionChanged Event.
			- selectionActivated: called if a selection is activated, ie. a row is double-clicked or Return
			 	is pressed.
			- cursorMoved: called when the currently active row changes. The user can select the current row
				with a single click or by moving the cursor up and down using the arrow keys.
	"""
	def __init__(self,*args,**kwargs):
		FlexTable.__init__(self,*args,**kwargs)
		FocusWidget.__init__(self, self.getElement(), *args,**kwargs)
		#super(Table,self).__init__(*args,**kwargs)
		#Events
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.headElem = DOM.createElement("thead")
		DOM.appendChild( self.element, self.headElem )
		self.sinkEvents(Event.ONCLICK | Event.ONDBLCLICK | Event.ONMOUSEMOVE | Event.ONMOUSEDOWN | Event.ONMOUSEUP | Event.ONKEYPRESS)
		self.setTabIndex(1)
		DOM.setElemAttribute( self.getElement(), "height", "50px")
		self._selectedRows = [] # List of row-indexes currently selected
		self._currentRow = None # Rowindex of the cursor row
		self._isMouseDown = False # Tracks status of the left mouse button
		self._isCtlPressed = False # Tracks status of the ctrl key
		self._ctlStartRow = None # Stores the row where a multi-selection (using the ctrl key) started
		self._selectionChangedListener = [] # All objects getting informed when the selection changes
		self._selectionActivatedListeners = [] # All objects getting informed when items are selected
		self._cursorMovedListeners = [] # All objects getting informed when the cursor moves
		self.setHeader(["a","b","c"])

	def setHeader(self, headers):
		"""
			Sets the table-headers to 'headers'
			@param headers: List of strings
			@type headers: list
		"""
		tmp = "<tr>"
		for h in headers:
			tmp += "<th>%s</th>" % h
		tmp += "</tr>"
		self.headElem.innerHTML = tmp

	def getTrByIndex(self, idx):
		"""
			Retrives the TR element by the given row number
			@param idx: Rownumber to retrive the tr of
			@type idx: int
			@returns HTMLTableRowElement
		"""
		body = self.getBodyElement()
		currChild = DOM.getFirstChild( body )
		lastChild = DOM.getLastChild( body )
		while( idx > 0 ):
			if currChild == lastChild:
				return( None )
			currChild = DOM.getNextSibling( currChild )
			idx -= 1
		return( currChild )

	def getIndexByTr(self,tr):
		"""
			Returns the rowNumber for the given tr element or None if
			the given tr element is invalid.
			@param tr: A HTMLTableRowElement of this table
			@type tr: HTMLTableRowElement
			@returns int or None
		"""
		body = DOM.getParent(tr)
		row = DOM.getChildIndex(body, tr)
		print("INDEX IS", row)
		return( row )

	def _rowForEvent(self, event ):
		"""
			Determines the row number for the given event
		"""
		tc = self.getEventTargetCell( event )
		if tc is None:
			return( None )
		tr = DOM.getParent( tc )
		return( tr )

	def onBrowserEvent(self, event):
		super(SelectTable,self).onBrowserEvent( event )
		#print( event )
		#print( dir( event ))
		eventType = DOM.eventGetType(event)
		if eventType == "mousedown":
			tr = self._rowForEvent( event )
			if tr is None:
				return
			if self._isCtlPressed and tr:
				row = self.getIndexByTr(tr)
				if row in self._selectedRows:
					self.removeSelectedRow( row )
				else:
					self.addSelectedRow( row )
				self.setFocus( True )
				event.preventDefault()
			elif tr:
				self._isMouseDown = True
				self.setCursorRow( self.getIndexByTr(tr) )
				self.setFocus( True )
				event.preventDefault()
		elif eventType == "mouseup":
			self._isMouseDown = False
		elif eventType == "mousemove":
			if self._isMouseDown:
				tr = self._rowForEvent( event )
				if tr is None:
					return
				self.addSelectedRow( self.getIndexByTr(tr) )
				event.preventDefault()
		elif eventType == "keydown":
			if DOM.eventGetKeyCode(event)==40: #Arrow down
				if self._currentRow is None:
					self.setCursorRow(0)
				else:
					if self._isCtlPressed:
						if self._ctlStartRow > self._currentRow:
							self.removeSelectedRow( self._currentRow )
						else:
							self.addSelectedRow( self._currentRow )
							if self._currentRow+1 < self.getRowCount():
								self.addSelectedRow( self._currentRow+1 )
					if self._currentRow+1 < self.getRowCount():
						self.setCursorRow(self._currentRow+1, removeExistingSelection=(not self._isCtlPressed))
				event.preventDefault()
			elif DOM.eventGetKeyCode(event)==38: #Arrow up
				if self._currentRow is None:
					self.setCursorRow(0)
				else:
					if self._isCtlPressed: #Check if we extend a selection
						if self._ctlStartRow < self._currentRow:
							self.removeSelectedRow( self._currentRow )
						else:
							self.addSelectedRow( self._currentRow )
							if self._currentRow>0:
								self.addSelectedRow( self._currentRow-1 )
					if self._currentRow>0: #Move the cursor if possible
						self.setCursorRow(self._currentRow-1, removeExistingSelection=(not self._isCtlPressed))
				event.preventDefault()
			elif DOM.eventGetKeyCode(event)==13: # Return
				if len( self._selectedRows )>0:
					self.selectionActivatedEvent.fire( self, self._selectedRows )
					event.preventDefault()
					return
				if self._currentRow is not None:
					self.selectionActivatedEvent.fire( self, [self._currentRow] )
					event.preventDefault()
					return
			elif DOM.eventGetKeyCode(event)==17:
				self._isCtlPressed = True
				self._ctlStartRow = self._currentRow or 0
		elif eventType == "keyup" and DOM.eventGetKeyCode(event)==17:
			self._isCtlPressed = False
			self._ctlStartRow = None
		elif eventType == "dblclick":
			if self._currentRow is not None:
				self.selectionActivatedEvent.fire( self, [self._currentRow] )
			event.preventDefault()
		#print( eventType )

	def addSelectedRow(self, row):
		"""
			Marks a row as selected
		"""
		if row in self._selectedRows:
			return
		self._selectedRows.append( row )
		addClass(self.getTrByIndex(row),"is_selected")
		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )
		print("Currently selected rows: %s" % str(self._selectedRows))

	def removeSelectedRow(self, row):
		"""
			Removes 'row' from the current selection (if any)
			@param row: Number of the row to unselect
			@type row: int
		"""
		if not row in self._selectedRows:
			return
		self._selectedRows.remove( row )
		removeClass(self.getTrByIndex(row),"is_selected")
		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def selectRow(self, newRow ):
		"""
			Sets the current selection to 'row'.
			Any previous selection is removed.
			@param newRow: Number of the row to select
			@type newRow: int
		"""
		self.setCursorRow( newRow )
		for row in self._selectedRows[:]:
			if row!=newRow:
				self.removeSelectedRow( row )
		if not newRow in self._selectedRows:
			self._selectedRows.append( newRow )
			addClass(self.getTrByIndex(newRow),"is_selected")
		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def setCursorRow(self, row, removeExistingSelection=True ):
		"""
			Move the cursor to row 'row'.
			If removeExistingSelection is True, the current selection (if any) is invalidated.
		"""
		if self._currentRow is not None:
			removeClass(self.getTrByIndex(self._currentRow),"is_focused")
		self._currentRow = row
		addClass(self.getTrByIndex(self._currentRow),"is_focused")
		self.cursorMovedEvent.fire( self, row )
		if removeExistingSelection:
			for row in self._selectedRows[:]:
				self.removeSelectedRow( row )
			self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def getCurrentSelection(self):
		if self._selectedRows:
			return( self._selectedRows[:])
		elif self._currentRow is not None:
			return( [self._currentRow ])
		else:
			return( None )

	def clear(self):
		"""
			Hook the clear() method so we can reset some internal states, too
		"""
		super(SelectTable, self).clear()
		self._currentRow = None
		self._selectedRows = []

	def removeRow(self, row):
		"""
			Hook the removeRow method so we can reset some internal states, too
		"""
		if row in self._selectedRows:
			self._selectedRows.remove( row )
			self.selectionChangedEvent.fire( self )
		if self._currentRow == row:
			self._currentRow = None
			self.cursorMovedEvent.fire( self )
		super( SelectTable, self ).removeRow( row )

class DataTable(FocusWidget):
	"""
		Provides kind of MVC on top of SelectTable.
	"""

	def __init__( self, *args, **kwargs ):
		self.element = DOM.createDiv()
		super( DataTable, self ).__init__( self.element )
		self.table = SelectTable()
		DOM.appendChild(self.element, self.table.element )
		self.table.onAttach()
		self.sinkEvents(Event.ONSCROLL)
		self.setStyleAttribute("height","300px")
		self.setStyleAttribute("overflow","scroll")
		self._model = [] # List of values where displaying right now
		self._shownFields = [] # List of keys we display from the model
		self._modelIdx = 0 # Internal counter to distinguish between 2 rows with identical data
		self._isAjaxLoading = False # Determines if we already requested the next batch of rows
		self._dataProvider = None # Which object to call if we need more data
		self._cellRender = {} # Map of renders for a given field
		# We re-emit some events with custom parameters
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.table.selectionChangedEvent.register( self )
		self.table.selectionActivatedEvent.register( self )
		#Proxy some events and functions of the original table
		for f in ["cursorMovedEvent","setHeader"]:
			setattr( self, f, getattr(self.table,f))
		self.cursorMovedEvent.register( self )

	def setDataProvider(self,obj):
		"""
			Register's 'obj' as the provider for this table.
			It must provide a onNextBatchNeeded function, which must fetch and
			feed new rows using add() or reset the dataProvider to None if no more
			rows are available.
			Notice: If the bottom of the table is reached, onNextBatchNeeded will only be called once.
			No further calls will be made until add() or setDataProvider() has been called afterwards.
		"""
		assert obj==None or "onNextBatchNeeded" in dir(obj),"The dataProvider must provide a 'onNextBatchNeeded' function"
		self._dataProvider = obj
		self._isAjaxLoading = False

	def onCursorMoved(self, table, row):
		"""
			Ensure the table scrolls according to the position of its cursor
		"""
		tr = table.getTrByIndex( row )
		if tr is None:
			return
		if self.element.scrollTop>tr.offsetTop:
			self.element.scrollTop = tr.offsetTop
		elif self.element.scrollTop+self.element.clientHeight<tr.offsetTop:
			self.element.scrollTop = tr.offsetTop+tr.clientHeight-self.element.clientHeight

	def getRowCount(self):
		"""
			Returns the total amount of rows currently known.
			@returns: int
		"""
		return( len( self._model ))


	def add(self, obj):
		"""
			Adds an row to the model
			@param obj: Dictionary of values for this row
			@type obj: dict
		"""
		obj["_uniqeIndex"] = self._modelIdx
		self._modelIdx += 1
		self._model.append( obj )
		self._renderObject( obj )
		self._isAjaxLoading = False

	def remove(self, objOrIndex):
		"""
			Removes 'obj' from the table.
			'obj' may be an row-index or an object recieved by any eventListener.
			It _cannot_ be any original object passed to 'add' - it _must_ be recived by an eventListener!
		"""
		if isinstance( objOrIndex, dict ):
			assert objOrIndex in self._model, "Cannot remove unknown object from Table"
			objOrIndex = self._model.index( objOrIndex )
		if isinstance( objOrIndex, int ):
			assert objOrIndex>0 and objOrIndex<len(self._model), "Modelindex out of range"
			self._model.remove( self._model[objOrIndex] )
			self.table.removeRow( objOrIndex )
		else:
			raise TypeError("Expected int or dict, got %s" % str(type(objOrIndex)))

	def clear(self, keepModel=False):
		"""
			Flushes the whole table.
		"""
		self.table.clear()
		while( self.table.getRowCount()>0 ):
			self.table.removeRow(0)
		if not keepModel:
			self._model = []

	def _renderObject(self, obj):
		"""
			Renders the object to into the table.
			Does nothing if the list of _shownFields is empty.
			@param obj: Dictionary of values for this row
			@type obj: dict
		"""
		if not self._shownFields:
			return
		rowIdx = self._model.index(obj)
		self.table.prepareRow( rowIdx )
		cellIdx = 0
		for field in self._shownFields:
			if field in self._cellRender.keys():
				lbl = self._cellRender[ field ].render( obj, field )
			elif field in obj.keys():
				lbl = Label(obj[field])
			else:
				lbl = Label("...")
			self.table.add( lbl, rowIdx, cellIdx )
			cellIdx += 1

	def rebuildTable(self):
		"""
			Rebuilds the entire table.
			Useful if something fundamental changed (ie. the cell renderer or the list of visible fields)
		"""

		self.clear( keepModel=True )
		for obj in self._model:
			self._renderObject( obj )

	def setShownFields(self,fields):
		"""
			Sets the list of _shownFields.
			This causes the whole table to be rebuild.
			Be carefull if calling this function often on a large table!
			@param fields: List of model-keys which will be displayed.
			@type fields: list
		"""
		self._shownFields = fields
		self.rebuildTable()

	def onBrowserEvent(self, event):
		"""
			Check if we got a scroll event and need to fetch another set of rows from our dataProvider
		"""
		eventType = DOM.eventGetType(event)
		if eventType!="scroll":
			return
		if (self.element.scrollTop+self.element.clientHeight)>=self.element.scrollHeight and not self._isAjaxLoading:
			if self._dataProvider:
				self._isAjaxLoading = True
				self._dataProvider.onNextBatchNeeded()


	def onSelectionChanged( self, table, rows ):
		"""
			Re-emit the event. Maps row-numbers to actual models.
		"""
		vals = [ self._model[x] for x in rows]
		self.selectionChangedEvent.fire( self, vals )

	def onSelectionActivated( self, table, rows ):
		"""
			Re-emit the event. Maps row-numbers to actual models.
		"""
		vals = [ self._model[x] for x in rows]
		self.selectionActivatedEvent.fire( self, vals )

	def getCurrentSelection(self):
		"""
			Override the getCurrentSelection method to
			yield actual models, not row-numbers.
		"""
		rows = self.table.getCurrentSelection()
		return( [ self._model[x] for x in rows] )

	def setCellRender(self, field, render):
		"""
			Sets the render for cells of 'field' to render.
			A cell render receives the data for a given cell and returns
			the appropriate widget to display that data for the table.
		"""
		if render is None:
			if field in self._cellRender.keys():
				del self._cellRender[ field ]
		else:
			assert "render" in dir(render), "The render must provide a 'render' method"
			self._cellRender[ field ] = render
		self.rebuildTable()