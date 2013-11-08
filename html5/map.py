from html5.widget import Widget

class Map( Widget ):
    _baseClass = "map"

    def __init__(self, *args, **kwargs):
        super(Map,self).__init__( *args, **kwargs )

	def _getLabel(self):
		return self.element.label
	def _setLabel(self,val):
		self.element.label=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val
