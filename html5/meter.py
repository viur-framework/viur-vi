from html5.widget import Widget
from html5.html5Attr.form import _Form as Form,Value
class Meter( Widget,Form ,Value):
	_baseClass = "meter"

	def __init__(self, *args, **kwargs):
		super(Meter,self).__init__( *args, **kwargs )

	def _getHigh(self):
		return self.element.high
	def _setHigh(self,val):
		self.element.high=val

	def _getLow(self):
		return self.element.low
	def _setLow(self,val):
		self.element.low=val

	def _getMax(self):
		return self.element.max
	def _setMax(self,val):
		self.element.max=val

	def _getMin(self):
		return self.element.min
	def _setMin(self,val):
		self.element.min=val

	def _getOptimum(self):
		return self.element.optimum
	def _setOptimum(self,val):
		self.element.optimum=val



