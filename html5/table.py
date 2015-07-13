from html5.widget import Widget

class Tr( Widget ):
	_baseClass = "tr"

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		return span if span else 1


class Th( Widget ):
	_baseClass = "th"

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		return span if span else 1


class Td( Widget ):
	_baseClass = "td"

	def _getColspan(self):
		span = self.element.getAttribute("colspan")
		return span if span else 1

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		return span if span else 1


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
		return( self.parentElem._children[item] )

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
		if item < 0 or item > len(self.parentElem._children):
			return( None )
		return ColWrapper(self.parentElem._children[item])


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
			row -= child["rowspan"]
			if row<0:
				return
		while row >= 0:
			self.body.appendChild( Tr() )
			row -= 1

	def prepareCol(self, row, col ):
		assert col>=0, "Cannot create cols with negative index"
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

	def prepareGrid(self, rows, cols ):
		for row in range( self.getRowCount(), self.getRowCount() + rows ):
			self.prepareCol( row, cols )

	def clear(self):
		for row in self.body._children[ : ]:
			for col in row._children[ : ]:
				row.removeChild( col )
			self.body.removeChild( row )

	def _getCell(self):
		return RowWrapper( self.body )

	def getRowCount(self):
		cnt = 0

		for tr in self.body._children:
			cnt += tr["rowspan"]

		return cnt

