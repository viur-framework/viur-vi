from html5.widget import Widget

class Param( Widget ):
    _baseClass = "param"

    def __init__(self, *args, **kwargs):
        super(Param,self).__init__( *args, **kwargs )

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getValue(self):
		return self.element.value
	def _setValue(self,val):
		self.element.value=val




