from html5.widget import Widget

class Q( Widget ):
    _baseClass = "q"

    def __init__(self, *args, **kwargs):
        super(Q,self).__init__( *args, **kwargs )

	def _getCite(self):
		return self.element.cite
	def _setCite(self,val):
		self.element.cite=val



