from html5.widget import Widget

class Time( Widget ):
    _baseClass = "time"

    def __init__(self, *args, **kwargs):
        super(Time,self).__init__( *args, **kwargs )

	def _getDatetime(self):
		return self.element.datetime
	def _setDatetime(self,val):
		self.element.datetime=val