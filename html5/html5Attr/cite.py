class Cite(object):
	def _getCite(self):
		return self.element.cite
	def _setCite(self,val):
		self.element.cite=val

class Datetime(object):
	def _getDatetime(self):
		return self.element.datetime
	def _setDatetime(self,val):
		self.element.datetime=val
