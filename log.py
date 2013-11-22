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
		spanWrap = html5.Span()
		spanWrap["class"].append("log_"+type)
		spanWrap["class"].append("is_new")
		spanDate = html5.Span()
		spanDate.appendChild( html5.TextNode( datetime.now().strftime("%H:%M:%S") ))
		spanDate["class"].append("date")
		spanWrap.appendChild(spanDate)
		spanMsg = html5.Span()
		spanMsg.appendChild( html5.TextNode( msg ))
		spanMsg["class"].append("msg")
		spanWrap.appendChild(spanMsg)
		DeferredCall(self.removeNewCls, spanWrap,_delay=2500)
		self.appendChild( spanWrap )

	def removeNewCls(self,span):
		span["class"].remove("is_new")