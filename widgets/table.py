import html5
from event import EventDispatcher
from html5.keycodes import *

class SelectTable( html5.Table ):
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
		super(SelectTable,self).__init__(*args,**kwargs)
		#Events
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.sinkEvent( "onClick", "onDblClick", "onMouseMove", "onMouseDown", "onMouseUp", "onKeyDown", "onKeyUp", "onMouseOut")
		self["tabindex"] = 1
		self._selectedRows = [] # List of row-indexes currently selected
		self._currentRow = None # Rowindex of the cursor row
		self._isMouseDown = False # Tracks status of the left mouse button
		self._isCtlPressed = False # Tracks status of the ctrl key
		self._ctlStartRow = None # Stores the row where a multi-selection (using the ctrl key) started
		self._selectionChangedListener = [] # All objects getting informed when the selection changes
		self._selectionActivatedListeners = [] # All objects getting informed when items are selected
		self._cursorMovedListeners = [] # All objects getting informed when the cursor moves
		self.setHeader(["a","b","c"])

	def onAttach(self):
		super(SelectTable, self).onAttach()
		self.focus()

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
		self.head.element.innerHTML = tmp

	def getTrByIndex(self, idx):
		"""
			Retrives the TR element by the given row number
			@param idx: Rownumber to retrive the tr of
			@type idx: int
			@returns HTMLTableRowElement
		"""
		for c in self.body._children:
			if idx <= 0:
				return( c )
			idx -= c["rowspan"]
		return( None )

	def getIndexByTr(self,tr):
		"""
			Returns the rowNumber for the given tr element or None if
			the given tr element is invalid.
			@param tr: A HTMLTableRowElement of this table
			@type tr: HTMLTableRowElement
			@returns int or None
		"""
		idx = 0
		for c in self.body._children:
			if c.element == tr:
				return( idx )
			idx += c["rowspan"]
		return( idx )

	def _rowForEvent(self, event ):
		"""
			Determines the row number for the given event
		"""
		tc = event.srcElement
		if tc is None:
			return( None )
		tr = tc.parentElement
		while( tr.parentElement is not None ):
			if tr.parentElement == self.body.element:
				return( tr )
			tr = tr.parentElement
		return( None )

	def onMouseDown(self, event):
		tr = self._rowForEvent( event )
		if tr is None:
			return
		if self._isCtlPressed and tr:
			row = self.getIndexByTr(tr)
			if row in self._selectedRows:
				self.removeSelectedRow( row )
			else:
				self.addSelectedRow( row )
			event.preventDefault()
		elif tr:
			self._isMouseDown = True
			self.setCursorRow( self.getIndexByTr(tr) )
			event.preventDefault()
		self.focus()

	def onMouseOut(self, event):
		self._isMouseDown = False

	def onMouseUp(self, event):
		self._isMouseDown = False

	def onMouseMove(self, event):
		if self._isMouseDown:
			tr = self._rowForEvent( event )
			if tr is None:
				return
			self.addSelectedRow( self.getIndexByTr(tr) )
			event.preventDefault()

	def onKeyDown(self, event):
		if isArrowDown(event.keyCode): #Arrow down
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
		elif isArrowUp(event.keyCode): #Arrow up
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
		elif isReturn(event.keyCode): # Return
			if len( self._selectedRows )>0:
				self.selectionActivatedEvent.fire( self, self._selectedRows )
				event.preventDefault()
				return
			if self._currentRow is not None:
				self.selectionActivatedEvent.fire( self, [self._currentRow] )
				event.preventDefault()
				return
		elif isSingleSelectionKey( event.keyCode ): #Ctrl
			self._isCtlPressed = True
			self._ctlStartRow = self._currentRow or 0

	def onKeyUp(self, event):
		if isSingleSelectionKey( event.keyCode ):
			self._isCtlPressed = False
			self._ctlStartRow = None

	def onDblClick(self, event):
		if self._currentRow is not None:
			self.selectionActivatedEvent.fire( self, [self._currentRow] )
		event.preventDefault()

	def addSelectedRow(self, row):
		"""
			Marks a row as selected
		"""
		if row in self._selectedRows:
			return
		self._selectedRows.append( row )
		self.getTrByIndex(row)["class"].append("is_selected")
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
		self.getTrByIndex(row)["class"].remove("is_selected")
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
			self.getTrByIndex(newRow)["class"].append("is_selected")
		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def setCursorRow(self, row, removeExistingSelection=True ):
		"""
			Move the cursor to row 'row'.
			If removeExistingSelection is True, the current selection (if any) is invalidated.
		"""
		if self._currentRow is not None:
			self.getTrByIndex(self._currentRow)["class"].remove("is_focused")
		self._currentRow = row
		self.getTrByIndex(self._currentRow)["class"].append("is_focused")
		self.cursorMovedEvent.fire( self, row )
		if removeExistingSelection:
			for row in self._selectedRows[:]:
				self.removeSelectedRow( row )
			self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def getCurrentSelection(self):
		"""
			Returns a list of currently selected row-numbers
			@returns: List
		"""
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

class DataTable( html5.Div ):
	"""
		Provides kind of MVC on top of SelectTable.
	"""

	def __init__( self, *args, **kwargs ):
		super( DataTable, self ).__init__( )
		self.table = SelectTable()
		self.appendChild(self.table)
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
		self["style"]["overflow"] = "scroll"
		self.recalcHeight()
		self.sinkEvent("onScroll")


	def recalcHeight(self, *args, **kwargs):
		self["style"]["max-height"] = "%spx" % (int(eval("window.top.innerHeight"))-280)

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
		if "is_loading" in self.table["class"]:
			self.table["class"].remove("is_loading")

	def onCursorMoved(self, table, row):
		"""
			Ensure the table scrolls according to the position of its cursor
		"""
		tr = table.getTrByIndex( row )
		if tr is None:
			return
		return #FIXME
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
		if "is_loading" in self.table["class"]:
			self.table["class"].remove("is_loading")
		self.testIfNextBatchNeededImmediately()

	def extend(self, objList):
		"""
			Adds multiple rows at once.
			Much faster than calling add() multiple times.
		"""
		self.table.prepareGrid( len(objList), len(self._shownFields) )
		for obj in objList:
			obj["_uniqeIndex"] = self._modelIdx
			self._modelIdx += 1
			self._model.append( obj )
			self._renderObject( obj, tableIsPrepared=True )
			self._isAjaxLoading = False
			if "is_loading" in self.table["class"]:
				self.table["class"].remove("is_loading")
		self.testIfNextBatchNeededImmediately()

	def testIfNextBatchNeededImmediately(self):
		"""
			Test if we display enough entries so that our contents are scrollable.
			Otherwise, we'll never request a second batch
		"""
		sumHeight = 0
		for c in self.table._children:
			if "clientHeight" in dir(c.element):
				sumHeight += c.element.clientHeight
			else:
				print( c )
		if not sumHeight>int(self["style"]["max-height"][:-2]) and not self._isAjaxLoading:
			if self._dataProvider:
				self._isAjaxLoading = True
				if not "is_loading" in self.table["class"]:
					self.table["class"].append("is_loading")
				self._dataProvider.onNextBatchNeeded()


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
		if not keepModel:
			self._model = []

	def _renderObject(self, obj, tableIsPrepared=False):
		"""
			Renders the object to into the table.
			Does nothing if the list of _shownFields is empty.
			@param obj: Dictionary of values for this row
			@type obj: dict
		"""
		if not self._shownFields:
			return
		rowIdx = self._model.index(obj)
		if not tableIsPrepared:
			self.table.prepareCol( rowIdx, len(self._shownFields)-1 )
		cellIdx = 0
		for field in self._shownFields:
			if field in self._cellRender.keys():
				lbl = self._cellRender[ field ].render( obj, field )
			elif field in obj.keys():
				lbl = html5.Label(obj[field])
			else:
				lbl = html5.Label("...")
			self.table["cell"][rowIdx][cellIdx] = lbl
			cellIdx += 1

	def rebuildTable(self):
		"""
			Rebuilds the entire table.
			Useful if something fundamental changed (ie. the cell renderer or the list of visible fields)
		"""
		self.clear( keepModel=True )
		self.table.prepareGrid( len(self._model), len(self._shownFields))
		for obj in self._model:
			self._renderObject( obj, tableIsPrepared=True )

	def setShownFields(self,fields):
		"""
			Sets the list of _shownFields.
			This causes the whole table to be rebuild.
			Be careful if calling this function often on a large table!
			@param fields: List of model-keys which will be displayed.
			@type fields: list
		"""
		self._shownFields = fields
		self.rebuildTable()

	def onScroll(self, event):
		"""
			Check if we got a scroll event and need to fetch another set of rows from our dataProvider
		"""
		self.recalcHeight()
		if (self.element.scrollTop+self.element.clientHeight)>=self.element.scrollHeight and not self._isAjaxLoading:
			if self._dataProvider:
				self._isAjaxLoading = True
				if not "is_loading" in self.table["class"]:
					self.table["class"].append("is_loading")
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
		if not self._model or not rows:
			return( [] )
		return( [ self._model[x] for x in rows ] )

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

	def setCellRenders(self, renders ):
		"""
			Like setCellRender, but sets multiple renders at one.
			Much faster than calling setCellRender repeatedly.
		"""
		assert isinstance( renders, dict )
		for field, render in renders.items():
			if render is None:
				if field in self._cellRender.keys():
					del self._cellRender[ field ]
			else:
				assert "render" in dir(render), "The render must provide a 'render' method"
				self._cellRender[ field ] = render
		self.rebuildTable()

	def activateCurrentSelection(self):
		"""
			Emits the selectionActivated event if there's currently a selection

		"""
		selection = self.getCurrentSelection()
		if len( selection )>0:
			self.selectionActivatedEvent.fire( self, selection )

