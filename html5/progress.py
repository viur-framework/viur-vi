from html5.widget import Widget

class Progress( Widget ):
    _baseClass = "progress"

    def __init__(self, *args, **kwargs):
        super(Progress,self).__init__( *args, **kwargs )

	def _getMax(self):
		return self.element.max
	def _setMax(self,val):
		self.element.max=val

	def _getValue(self):
		return self.element.value
	def _setValue(self,val):
		self.element.value=val




