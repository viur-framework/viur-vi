from html5.widget import Widget

class Tr( Widget ):
	_baseClass = "tr"

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		if not span:
			return( 1 )
		else:
			return( span )

class Td( Widget ):
	_baseClass = "td"

	def _getColspan(self):
		span = self.element.getAttribute("colspan")
		if not span:
			return( 1 )
		else:
			return( span )

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		if not span:
			return( 1 )
		else:
			return( span )


class Thead( Widget ):
	_baseClass = "thead"


class Tbody( Widget ):
	_baseClass = "tbody"


class ColWrapper( object ):
	def __init__( self, parentElem, *args, **kwargs ):
		super( ColWrapper, self ).__init__( *args, **kwargs )
		self.parentElem = parentElem

	def __getitem__(self, item):
		assert isinstance(item,int), "Invalid col-number. Expected int, got %s" % str(type(item))
		if item < 0 or item> len(self.parentElem._children):
			return( None )
		for col in self.parentElem._children:
			item -= col["rowspan"]
			if item < 0:
				return( col )
		return( None )

	def __setitem__(self, key, value):
		col = self[ key ]
		assert col is not None, "Cannot assign widget to invalid column"
		for c in col._children[:]:
			col.removeChild( c )
		col.appendChild( value )


class RowWrapper( object ):
	def __init__( self, parentElem, *args, **kwargs ):
		super( RowWrapper, self ).__init__( *args, **kwargs )
		self.parentElem = parentElem

	def __getitem__(self, item):
		assert isinstance(item,int), "Invalid row-number. Expected int, got %s" % str(type(item))
		if item < 0 or item> len(self.parentElem._children):
			return( None )
		for row in self.parentElem._children:
			item -= row["rowspan"]
			if item < 0:
				return( ColWrapper(row) )
		return( None )




class Table( Widget ):
	_baseClass = "table"

	def __init__(self, *args, **kwargs):
		super(Table,self).__init__( *args, **kwargs )
		self.head = Thead()
		self.body = Tbody()
		self.appendChild( self.head )
		self.appendChild( self.body )

	def prepareRow(self, row):
		assert row>=0, "Cannot create rows with negative index"
		for child in self.body._children:
			print("REM COLSPAN", child["rowspan"])
			row -= child["rowspan"]
			if row<0:
				return
		while row >= 0:
			self.body.appendChild( Tr() )
			row -= 1

	def prepareCol(self, row, col ):
		assert col>=0, "Cannot create cols with negative index"
		print("PREPARING", row, col)
		self.prepareRow( row )
		for rowChild in self.body._children:
			row -= rowChild["rowspan"]
			if row<0:
				for colChild in rowChild._children:
					col -= colChild["colspan"]
					if col < 0:
						return
				while col>=0:
					rowChild.appendChild( Td() )
					col -= 1
				return

	def clear(self):
		for row in self.body._children[ : ]:
			for col in row._children[ : ]:
				row.removeChild( col )
			self.body.removeChild( row )

	def _getCell(self):
		return( RowWrapper( self.body ) ) #FIXME: Return wrapper

	def getRowCount(self):
		cnt = 0
		for tr in self.body._children:
			cnt += tr["rowspan"]
		return( cnt )

