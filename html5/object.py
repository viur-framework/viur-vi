from html5.widget import Widget

class Object( Widget ):
    _baseClass = "object"

    def __init__(self, *args, **kwargs):
        super(Object,self).__init__( *args, **kwargs )


	def _getData(self):
		return self.element.data
	def _setData(self,val):
		self.element.data=val

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.height=val

	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.width=val

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getUsemap(self):
		return self.element.usemap
	def _setUsemap(self,val):
		self.element.usemap=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val


