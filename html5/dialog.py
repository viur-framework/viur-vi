from html5.details import Details

class Dialog( Details):
	_baseClass = "dialog"

	def __init__(self, *args, **kwargs):
		super(Dialog,self).__init__( *args, **kwargs )
