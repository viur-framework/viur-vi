import html5
from network import DeferredCall
from datetime import datetime

class Log( html5.Div ):
	"""
		Provides the "messaging" center displayed at the bottom of VI
	"""
	def __init__(self):
		super( Log, self ).__init__()
		self["class"].append("vi_messenger")
		self.logUL = html5.Ul()
		self.logUL["id"] = "statuslist"
		self.logUL["class"].append( "statuslist" )
		self.appendChild( self.logUL )
		#self.backlog = []

	def log(self, type, msg ):
		"""
			Adds a message to the log
			@param type: The type of the message.
			@type type: "success", "error", "warning", "info", "progress"
			@param msg: The message to append
			@type msg: String
		"""
		assert type in ["success", "error", "warning", "info", "progress"]
		liwrap = html5.Li()
		liwrap["class"].append("log_"+type)
		liwrap["class"].append("is_new")
		spanDate = html5.Span()
		spanDate.appendChild( html5.TextNode( datetime.now().strftime("%H:%M:%S") ))
		spanDate["class"].append("date")
		liwrap.appendChild(spanDate)
		spanMsg = html5.Span()
		spanMsg.appendChild( html5.TextNode( msg ))
		spanMsg["class"].append("msg")
		liwrap.appendChild(spanMsg)
		DeferredCall(self.removeNewCls, liwrap,_delay=2500)
		self.logUL.appendChild( liwrap )
		if len(self.logUL._children)>1:
			self.logUL.element.removeChild( liwrap.element )
			self.logUL.element.insertBefore( liwrap.element, self.logUL.element.children.item(0) )

	def removeNewCls(self,span):
		span["class"].remove("is_new")