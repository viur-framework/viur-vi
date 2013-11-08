from html5.widget import Widget

class Source( Widget ):
    _baseClass = "source"

    def __init__(self, *args, **kwargs):
        super(Source,self).__init__( *args, **kwargs )

	def _getMedia(self):
		return self.element.media
	def _setMedia(self,val):
		self.element.media=val

	def _getSrc(self):
		return self.element.src
	def _setSrc(self,val):
		self.element.src=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val




