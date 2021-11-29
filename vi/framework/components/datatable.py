# -*- coding: utf-8 -*-
from flare import html5,utils
from flare.ignite import Table
from flare.event import EventDispatcher
from flare.network import DeferredCall


class SelectTable( Table ):
	"""
		Provides an Html-Table which allows for row selections.

		Parent widgets can register for certain events:

			- selectionChanged: called if the current _multi_ selection changes. (Ie the user
				holds ctrl and clicks a row). The selection might contain no, one or multiple rows.
				Its also called if the cursor moves. Its called if the user simply double
				clicks a row. So its possible to receive a selectionActivated event without an
				selectionChanged Event.
			- selectionActivated: called if a selection is activated, ie. a row is double-clicked or Return
			 	is pressed.
			- cursorMoved: called when the currently active row changes. The user can select the current row
				with a single click or by moving the cursor up and down using the arrow keys.
	"""
	def __init__(self, checkboxes=False, indexes=False, *args, **kwargs):
		super(SelectTable,self).__init__(*args,**kwargs)

		self.addClass("vi-table", "ignt-table")

		#Events
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.cursorMovedEvent = EventDispatcher("cursorMoved")
		self.tableChangedEvent = EventDispatcher("tableChanged")

		self.sinkEvent( "onDblClick",
		                "onMouseDown",
		                "onMouseUp",
		                "onKeyDown",
		                "onKeyUp",
		                "onMouseOut",
		                "onChange" )

		self["tabindex"] = 1

		self._selectedRows = [] # List of row-indexes currently selected
		self._currentRow = None # Rowindex of the cursor row
		self._isMouseDown = False # Tracks status of the left mouse button
		self._isCtlPressed = False # Tracks status of the ctrl key
		self._isShiftPressed = False # Tracks status of the shift key
		self._ctlStartRow = None # Stores the row where a multi-selection (using the ctrl key) started
		self._selectionChangedListener = [] # All objects getting informed when the selection changes
		self._selectionActivatedListeners = [] # All objects getting informed when items are selected
		self._cursorMovedListeners = [] # All objects getting informed when the cursor moves

		self.indexes = indexes
		self.indexes_col = 0 if indexes else -1
		self.currentCols = 0 # amount of current Columns
		self._checkboxes = {} # The checkbox items per row (better to use a dict!)
		self.checkboxes = checkboxes
		self.checkboxes_col = (self.indexes_col + 1) if checkboxes else -1

	def onAttach(self):
		super(SelectTable, self).onAttach()
		self.focus()

	def setHeader(self, headers):
		"""
			Sets the table-headers to 'headers'
			:param headers: list of strings
			:type headers: list
		"""

		tr = html5.Tr()
		tr.addClass("vi-table-head-row","ignt-table-head-row")

		# Extra column for Index#s
		if self.indexes:
			th = html5.Th()
			th.addClass("vi-table-head-index", "vi-table-head-cell", "ignt-table-head-cell")
			tr.appendChild( th )

		# Extra column for checkboxes
		if self.checkboxes:
			th = html5.Th()
			th.addClass("vi-table-head-check", "vi-table-head-cell", "ignt-table-head-cell")
			tr.appendChild( th )

		# Now every title column
		for head in headers:
			th = html5.Th()
			th.addClass("vi-table-head-cell", "ignt-table-head-cell")
			th.appendChild( html5.TextNode( head ) )
			tr.appendChild( th )

		self.head.removeAllChildren()
		self.head.appendChild( tr )

	def getTrByIndex(self, idx):
		"""
			Retrieves the TR element by the given row number
			:param idx: Rownumber to retrieve the tr of
			:type idx: int
			:returns: HTMLTableRowElement
		"""
		for c in self.body._children:
			if idx <= 0:
				return c
			idx -= c["rowspan"]

		return None

	def getIndexByTr(self,tr):
		"""
			Returns the rowNumber for the given tr element or None if
			the given tr element is invalid.
			:param tr: A HTMLTableRowElement of this table
			:type tr: HTMLTableRowElement
			:returns: int or None
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
		try:
			# Chromium
			tc = event.srcElement
		except:
			# Firefox
			tc = event.target

		if tc is None:
			return( None )

		tr = tc.parentElement

		while( tr.parentElement is not None ):
			if tr.parentElement == self.body.element:
				return( tr )
			tr = tr.parentElement

		return( None )

	def onChange(self, event):
		tr = self._rowForEvent( event )
		if tr is None:
			return

		row = self.getIndexByTr( tr )

		if self.checkboxes and utils.doesEventHitWidgetOrChildren(event, self._checkboxes[row]):
			self._checkboxes[ row ][ "checked" ] = row in self._selectedRows

	def onMouseDown(self, event):
		tr = self._rowForEvent( event )

		if tr is None:
			return

		row = self.getIndexByTr( tr )

		if self._isCtlPressed:
			if row in self._selectedRows:
				for x in self._selectedRows:
					self.getTrByIndex(x).removeClass("is-focused") # remove focus
				self.removeSelectedRow( row )
			else:
				self.addSelectedRow( row )
				#self.setCursorRow(row, False) # set focus
			event.preventDefault()

		elif self._isShiftPressed:

			self.unSelectAll()
			for i in ( range(self._ctlStartRow, row+1) if self._ctlStartRow <= row else range(row, self._ctlStartRow+1) ):
				self.addSelectedRow( i )
			#self.setCursorRow(row, False) # set focus
			event.preventDefault()

		elif self.checkboxes and utils.doesEventHitWidgetOrChildren(event, self._checkboxes[row]):
			if row in self._selectedRows:
				self.removeSelectedRow( row )
			else:
				self.addSelectedRow( row )

		else:
			self._isMouseDown = True

			if self.checkboxes:
				if row in self._selectedRows:
					self.removeSelectedRow( row )
				else:
					self.addSelectedRow( row )

			self.setCursorRow(self.getIndexByTr(tr), removeExistingSelection=not self.checkboxes)

		self.focus()

	def onMouseOut(self, event):
		self._isMouseDown = False

	def onMouseUp(self, event):
		self._isMouseDown = False

	def onKeyDown(self, event):

		if html5.isArrowDown(event):  # Arrow down

			if self._currentRow is None:
				self.setCursorRow(0)

			else:
				if self._isCtlPressed or self._isShiftPressed:

					if self._ctlStartRow > self._currentRow:
						self.removeSelectedRow(self._currentRow)
					else:
						self.addSelectedRow(self._currentRow)

						if self._currentRow + 1 < self.getRowCount():
							self.addSelectedRow(self._currentRow + 1)

				if self._currentRow + 1 < self.getRowCount():
					self.setCursorRow(self._currentRow + 1,
									  removeExistingSelection=(not self._isShiftPressed and not self._isCtlPressed))

			event.preventDefault()

		elif html5.isArrowUp(event):  # Arrow up

			if self._currentRow is None:
				self.setCursorRow(0)
			else:

				if self._isCtlPressed or self._isShiftPressed:  # Check if we extend a selection
					if self._ctlStartRow < self._currentRow:
						self.removeSelectedRow(self._currentRow)
					else:
						self.addSelectedRow(self._currentRow)

						if self._currentRow > 0:
							self.addSelectedRow(self._currentRow - 1)

				if self._currentRow > 0:  # Move the cursor if possible
					self.setCursorRow(self._currentRow - 1,
									  removeExistingSelection=(not self._isShiftPressed and not self._isCtlPressed))

			event.preventDefault()

		elif html5.isReturn(event):  # Return

			if len(self._selectedRows) > 0:
				self.selectionActivatedEvent.fire(self, self._selectedRows)
				event.preventDefault()
				return

			if self._currentRow is not None:
				self.selectionActivatedEvent.fire(self, [self._currentRow])
				event.preventDefault()
				return

		elif html5.isControl(event) or html5.getKey(event) == "Meta":  # Ctrl
			self._isCtlPressed = True
			self._ctlStartRow = self._currentRow or 0
			if self._currentRow is not None:
				self.addSelectedRow(self._currentRow) # add already selected row to selection

		elif html5.isShift(event):  # Shift
			self._isShiftPressed = True
			try:
				self._ctlStartRow = self._currentRow or self._selectedRows[0] or 0
			except:
				self._ctlStartRow = 0

	def onKeyUp(self, event):
		if html5.isControl(event) or html5.getKey(event) == "Meta":
			self._isCtlPressed = False
			self._ctlStartRow = None

			# leave selection mode if there is only one row selected and return to normal focus
			if len(self._selectedRows) == 1:
				for row in self.getCurrentSelection():
					self.removeSelectedRow(row)

		elif html5.isShift(event):
			self._isShiftPressed = False
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

		tr = self.getTrByIndex( row )
		tr.addClass("is-focused")

		if self.checkboxes:
			self._checkboxes[ row ][ "checked" ] = True

		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def removeSelectedRow(self, row):
		"""
			Removes 'row' from the current selection (if any)
			:param row: Number of the row to unselect
			:type row: int
		"""
		if not row in self._selectedRows:
			return

		self._selectedRows.remove( row )

		tr = self.getTrByIndex( row )
		tr.removeClass("is-focused")

		if self.checkboxes:
			self._checkboxes[ row ][ "checked" ] = False

		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def selectRow(self, newRow ):
		"""
			Sets the current selection to 'row'.
			Any previous selection is removed.
			:param newRow: Number of the row to select
			:type newRow: int
		"""
		self.setCursorRow( newRow )

		for row in self._selectedRows[:]:
			if row!=newRow:
				self.removeSelectedRow( row )

		if not newRow in self._selectedRows:
			self._selectedRows.append( newRow )
			tr = self.getTrByIndex( newRow )
			tr.addClass("is-focused")

		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

	def setCursorRow(self, row, removeExistingSelection=True ):
		"""
			Move the cursor to row 'row'.
			If removeExistingSelection is True, the current selection (if any) is invalidated.
		"""
		if self._currentRow is not None:
			self.getTrByIndex(self._currentRow).removeClass("is-focused")

		self._currentRow = row
		if self._currentRow is not None:
			self.getTrByIndex(self._currentRow).addClass("is-focused")
			self.cursorMovedEvent.fire( self, row )

		if removeExistingSelection:
			for row in self._selectedRows[:]:
				self.removeSelectedRow( row )
			self.selectionChangedEvent.fire( self, self.getCurrentSelection() )

		DeferredCall(self.focusRow, row)

	def focusRow(self, row):
		tr = self.getTrByIndex(row)
		# fixme: Re-implement maybe later?

	def getCurrentSelection(self):
		"""
			Returns a list of currently selected row-numbers
			:returns: list
		"""
		if self._selectedRows:
			return self._selectedRows[:]
		elif self._currentRow is not None:
			return [self._currentRow]

		return None

	def clear(self):
		"""
			Hook the clear() method so we can reset some internal states, too
		"""
		super(SelectTable, self).clear()
		self._currentRow = None
		self._selectedRows = []

		self.selectionChangedEvent.fire(self, self.getCurrentSelection())
		self.tableChangedEvent.fire(self, self.getRowCount())

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

		self.tableChangedEvent.fire(self, self.getRowCount())
		super( SelectTable, self ).removeRow( row )

	def _extraCols(self):
		return int( self.checkboxes ) + int( self.indexes )

	def prepareCol(self, row, col):
		"""
		Lets hook up the original removeRow function to optionally
		provide index and checkbox columns.
		"""
		self.currentCols = col + self._extraCols() - 1
		super( SelectTable, self ).prepareCol( row, col + self._extraCols() - 1 )

		if self.checkboxes:
			checkbox = html5.Input()
			checkbox[ "type" ] = "checkbox"
			checkbox[ "class" ].append( "check" )
			checkbox[ "checked" ] = False

			self["cell"][ row ][ self.checkboxes_col ] = checkbox
			self._checkboxes[ row ] = checkbox

		if self.indexes:
			lbl = html5.Label( str( row + 1 ) )
			lbl[ "class" ].append( "index" )
			self["cell"][ row ][ self.indexes_col ] = lbl

		self.tableChangedEvent.fire(self, self.getRowCount())

	def dropTableContent(self):
		"""
		Drops content from the table, structure remains unchanged
		"""
		if not self.currentCols:
			return 0
		for row in range(0,self.getRowCount()):
			for col in range(0,self.currentCols+1):
				self.setCell(row,col,"")


	def setCell(self, row, col, val):
		"""
		Interface for self["cell"] that directs to the correct cell if extra columns are
		configured for this SelectTable.
		"""
		self[ "cell" ][ row ][ col + self._extraCols() ] = val

	def selectAll(self):
		"""
		Selects all entries of the table.
		"""
		self._selectedRows = range(0, self.getRowCount() )

		for row in self._selectedRows:
			tr = self.getTrByIndex( row )

			if not "is-focused" in tr["class"]:
				tr.addClass("is-focused")

			if self.checkboxes:
				self._checkboxes[ row ][ "checked" ] = True

		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )
		return len(self._selectedRows)

	def unSelectAll(self):
		"""
		Unselects all entries of the table.
		"""
		unsel = len(self._selectedRows)

		for row in self._selectedRows:
			tr = self.getTrByIndex( row )
			tr.removeClass("is-focused")

			if self.checkboxes:
				self._checkboxes[ row ][ "checked" ] = False

		self._selectedRows = []
		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )
		return unsel

	def invertSelection(self):
		"""
		Inverts the current selection on the whole table currently displayed.
		"""
		current = self._selectedRows[:]
		self._selectedRows = []

		for row in range(0, self.getRowCount() ):
			tr = self.getTrByIndex( row )

			if row in current:
				tr.removeClass("is-focused")
			else:
				self._selectedRows.append(row)
				tr.addClass("is-focused")

			if self.checkboxes:
				self._checkboxes[ row ][ "checked" ] = row in self._selectedRows

		self.selectionChangedEvent.fire( self, self.getCurrentSelection() )
		return len(self._selectedRows), len(current)

class DataTable( html5.Div ):

	def __init__( self, _loadOnDisplay = False, *args, **kwargs ):
		super( DataTable, self ).__init__( )
		self.table = SelectTable( *args, **kwargs )
		self.addClass("vi-datatable")
		self.appendChild(self.table)

		self._loadOnDisplay = _loadOnDisplay # Load all data content continuously when displaying

		self._model = [] # List of values we are displaying right now
		self._shownFields = [] # List of keys we display from the model
		self._modelIdx = 0 # Internal counter to distinguish between 2 rows with identical data
		self._isAjaxLoading = False # Determines if we already requested the next batch of rows
		self._dataProvider = None # Which object to call if we need more data
		self._cellRender = {} # Map of renders for a given field
		self._renderedModel = [] #save already rendered Field (used to rebuild Table if new Fields were selected
		# We re-emit some events with custom parameters
		self.selectionChangedEvent = EventDispatcher("selectionChanged")
		self.selectionActivatedEvent = EventDispatcher("selectionActivated")
		self.tableChangedEvent = EventDispatcher("tableChanged")
		self.requestingFinishedEvent = EventDispatcher("requestingFinished")

		self.table.selectionChangedEvent.register( self )
		self.table.selectionActivatedEvent.register( self )
		self.table.tableChangedEvent.register( self )

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
		assert obj==None or "onNextBatchNeeded" in dir(obj),\
			"The dataProvider must provide a 'onNextBatchNeeded' function"

		self._dataProvider = obj
		self._isAjaxLoading = False

		if "is-loading" in self.table["class"]:
			self.table.removeClass("is-loading")


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
			:returns: int
		"""
		return( len( self._model ))

	def add(self, obj):
		"""
			Adds an row to the model
			:param obj: Dictionary of values for this row
			:type obj: dict
		"""
		obj["_uniqeIndex"] = self._modelIdx
		self._modelIdx += 1
		self._model.append( obj )
		self._renderObject( obj )
		self._isAjaxLoading = False
		if "is-loading" in self.table["class"]:
			self.table.removeClass("is-loading")

	def update(self, objList, writeToModel=True):
		"""
			Adds multiple rows at once.
			Much faster than calling add() multiple times.
		"""
		#self.table.prepareGrid(len(objList), len(self._shownFields))
		self.table.fastGrid(len(objList), len(self._shownFields))
		for obj in objList:
			self._renderedModel.append( { } )
			if writeToModel:
				obj["_uniqeIndex"] = self._modelIdx
				self._modelIdx += 1
				self._model.append(obj)
			self._renderObject(obj, tableIsPrepared=True)
			self._isAjaxLoading = False
			if "is-loading" in self.table["class"]:
				self.table.removeClass("is-loading")

		self.table.tableChangedEvent.fire( self, self.getRowCount() )

	def extend(self, objList,writeToModel=True):

		self.update(objList,writeToModel=writeToModel)

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

	def _renderObject(self, obj, tableIsPrepared=False, recalculate=True):
		"""
			Renders the object to into the table.
			Does nothing if the list of _shownFields is empty.
			:param obj: Dictionary of values for this row
			:type obj: dict
		"""
		if not self._shownFields:
			return

		rowIdx = self._model.index(obj)
		cellIdx = 0

		if not tableIsPrepared:
			self.table.prepareCol( rowIdx, len( self._shownFields ) - 1 )

		for field in self._shownFields:
			if not recalculate and rowIdx<len(self._renderedModel) and field in self._renderedModel[rowIdx] and self._renderedModel[rowIdx][field]:
				lbl = self._renderedModel[rowIdx][field]
			else:
				if field in self._cellRender.keys():
					lbl = self._cellRender[field].viewWidget(obj[field])
				elif field in obj.keys():
					lbl = html5.Div(obj[field])
				else:
					lbl = html5.Div("...")
				lbl.addClass("ignt-table-content")
				self._renderedModel[rowIdx][field] = lbl

			self.table.setCell( rowIdx, cellIdx, lbl )
			cellIdx += 1

	def rebuildTable(self, recalculate=True):
		"""
			Rebuilds the entire table.
			Useful if something fundamental changed (ie. the cell renderer or the list of visible fields)
		"""
		self.clear( keepModel=True )
		#self.table.prepareGrid( len(self._model), len(self._shownFields))
		self.table.fastGrid( len(self._model), len(self._shownFields))
		for obj in self._model:
			self._renderObject( obj, tableIsPrepared=True, recalculate=recalculate )

	def setShownFields(self,fields):
		"""
			Sets the list of _shownFields.
			This causes the whole table to be rebuild.
			Be careful if calling this function often on a large table!
			:param fields: List of model-keys which will be displayed.
			:type fields: list
		"""
		self._shownFields = fields
		self.rebuildTable(recalculate=True) #we only add or remove new rows, dont recalculate existing values
		self.table.tableChangedEvent.fire( self, self.getRowCount() )

	def onSelectionChanged( self, table, rows, *args,**kwargs ):
		"""
			Re-emit the event. Maps row-numbers to actual models.
		"""
		vals = [ self._model[x] for x in (rows or []) ]
		self.selectionChangedEvent.fire( self, vals )

	def onSelectionActivated( self, table, rows ):
		"""
			Re-emit the event. Maps row-numbers to actual models.
		"""
		vals = [ self._model[x] for x in rows]
		self.selectionActivatedEvent.fire( self, vals )

	def onTableChanged( self, table, rowCount, *args,**kwargs ):
		"""
			Re-emit the event.
		"""
		self.tableChangedEvent.fire(self, rowCount)

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
			assert "viewWidget" in dir(render), "The render must provide a 'render' method"
			self._cellRender[ field ] = render

		#self.rebuildTable()

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
				assert "viewWidget" in dir(render), "The render must provide a 'render' method"
				self._cellRender[ field ] = render

		#self.rebuildTable()

	def activateCurrentSelection(self):
		"""
			Emits the selectionActivated event if there's currently a selection

		"""
		selection = self.getCurrentSelection()
		if len( selection )>0:
			self.selectionActivatedEvent.fire( self, selection )

class ViewportDataTable(DataTable):

	def __init__(self, _loadOnDisplay=False, rows=99, *args, **kwargs):
		super(ViewportDataTable, self).__init__(_loadOnDisplay,*args,**kwargs)
		self._rows = rows

	def clear(self, keepModel=False):
		"""
			Flushes the whole table.
			Override explanation
			- replaced clear with dropTableContent
		"""
		self.table.dropTableContent()
		if not keepModel:
			self._model = []

	def rebuildTable(self , recalculate=True):
		"""
			Rebuilds the entire table.
			Useful if something fundamental changed (ie. the cell renderer or the list of visible fields)#

			Override explanation
			- uses the predefined _rows to prepare the grid
			- only load first rows from model
		"""
		self.clear( keepModel=True )

		if not self.table.getRowCount() == self._rows or not self.table.currentCols == len(self._shownFields):
			self.table.clear()
			self.table.fastGrid( self._rows, len(self._shownFields), createHidden = True) #at the beginning all rows are hidden

		for idx, obj in enumerate(self._model):
			if idx < self._rows:
				self._renderObject( obj, tableIsPrepared=True, recalculate=recalculate )


	def add(self, obj):
		"""
			Adds an row to the model
			:param obj: Dictionary of values for this row
			:type obj: dict

			Override explanation
			- _renderObject call is always prepared
		"""
		obj["_uniqeIndex"] = self._modelIdx
		self._modelIdx += 1
		self._model.append( obj )
		self._renderObject( obj, tableIsPrepared=True )
		self._isAjaxLoading = False
		if "is-loading" in self.table["class"]:
			self.table.removeClass("is-loading")
		self.table.tableChangedEvent.fire(self, self.getRowCount())

	def extend(self, objList, writeToModel=True):
		self.update(objList,writeToModel=writeToModel)

	def update(self, objList, writeToModel=True):
		"""
			Adds multiple rows at once.
			Much faster than calling add() multiple times.

			Override explanation
			- removed grid preparation

		"""
		self.table.dropTableContent()

		for obj in objList:
			self._renderedModel.append( { } )
			if writeToModel:
				obj["_uniqeIndex"] = self._modelIdx
				self._modelIdx += 1
				self._model.append(obj)
			self._renderObject(obj, tableIsPrepared=True)
			self._isAjaxLoading = False
			if "is-loading" in self.table["class"]:
				self.table.removeClass("is-loading")



		self.table.tableChangedEvent.fire( self, self.getRowCount())

	def _renderObject(self, obj, tableIsPrepared=True, recalculate=True):
		"""
			Renders the object to into the table.
			Does nothing if the list of _shownFields is empty.
			:param obj: Dictionary of values for this row
			:type obj: dict

			Override explanation
			- removed Table preperation
			- rowIndex modulo shownrows
		"""
		if not self._shownFields:
			return

		rowIdx = self._model.index(obj) % self._rows
		cellIdx = 0

		for field in self._shownFields:
			if not recalculate and rowIdx<len(self._renderedModel) and field in self._renderedModel[rowIdx] and self._renderedModel[rowIdx][field]:
				lbl = self._renderedModel[rowIdx][field]
			else:

				if field in self._cellRender.keys():
					lbl = self._cellRender[field].viewWidget(obj[field])
				elif field in obj.keys():
					lbl = html5.Div(obj[field])
				else:
					lbl = html5.Div("...")
				lbl.addClass("ignt-table-content")
				self._renderedModel[ rowIdx ][ field ] = lbl

			self.table.getTrByIndex(rowIdx).removeClass("is-hidden") #unhide used rows
			self.table.setCell( rowIdx, cellIdx, lbl )
			cellIdx += 1
