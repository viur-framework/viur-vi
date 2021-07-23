"""WARNING! THIS SCRIPTS ARE USED IN A SANDBOX SO ALL DEPENDENCIES SHOULD BE HANDELED HERE!

	 THIS USES PYODIDE V0.17!
"""
from js import eval as jseval, self as web_self, Blob, URL
import os, sys, json, string, random, csv
from io import StringIO

def request(url,params=None,jsonResult=True, whitelist=("/list/","/view/")):
	"""A very simple version of the NetworkService to request synchronous data"""

	if not url.startswith("/"):
		return None

	valid = False
	for i in whitelist:
		if i in url:
			valid=True
			break

	if not valid:
		return None

	url = "/json"+url

	request = SimpleNetwork().request(url, params)

	if request.status=="failed":
		return request.status

	if not jsonResult:
		return request.result

	return json.loads(request.result)


class requestList():

	def __init__(self, url, params=None, maxRequests=999):
		self.url = url
		self.params = params or {}
		self.maxRequests = maxRequests

		self.currentList = []

		self.requests = 0
		self.cursor = None
		self.started=False

	def requestData(self):
		self.requests += 1
		if self.cursor:
			self.params["cursor"] = self.cursor

		res = request(self.url, self.params)
		if not res:
			return
		self.cursor = None if res["cursor"] == self.cursor else res["cursor"]
		self.currentList = res["skellist"]

	def next(self):
		if self.requests > self.maxRequests:
			return False

		if self.currentList:
			return self.currentList.pop(0)

		if not self.cursor:
			return False

	def running(self):
		if not self.currentList:
			self.requestData()

		if self.requests > self.maxRequests:
			return False

		if not self.started and self.requests == 0: #min 1 request
			self.started = True
			return True

		if self.currentList:
			return True

		if self.cursor: #list is empty but we have a valid cursor
			return True

		return False


class csvWriter():
	delimiter = ";"

	def __init__(self, delimiter=";"):
		self.delimiter = delimiter
		self.file = StringIO()
		self.writer = csv.writer(self.file, delimiter=self.delimiter, dialect='excel', quoting=csv.QUOTE_ALL)
		self.file.write('\ufeff')  # excel needs this for right utf-8 decoding

	def writeRow(self, row):
		for i, s in enumerate(row):
			if isinstance(s, str):
				row[i] = s.replace('"', "").replace("'","")  # .replace("&nbsp;"," ").replace( ";", "" ).replace( "<br />", "\n" ).replace( "<div>", "\n" ).replace( "</div>", "" )
		self.writer.writerow(row)

	def writeRows(self, rows):
		for r in rows:
			self.writeRow(r)

	# self.writer.writerows(rows) #nativ version doesnot support unicode and we do some cleaning to avoid broken csv files

	def download(self,name="export.csv"):
		blob = Blob.new([self.file.getvalue()], **{
			"type":"application/csv;charset=utf-8;"
		})
		#send blob to app
		# in a webworker we cant manipulate the dom
		web_self.postMessage(type="download", blob=blob, filename=name)


class weblog():
	@staticmethod
	def info(text):
		if not isinstance(text,str):
			text = str(text)
		web_self.postMessage(type="info",text=text)

	@staticmethod
	def warn(text):
		if not isinstance(text,str):
			text = str(text)
		web_self.postMessage(type="warn", text=text)

	@staticmethod
	def error(text):
		if not isinstance(text,str):
			text = str(text)
		web_self.postMessage(type="error",text=text)
log = weblog() #shortcut to use log.info ...


# HELPERS

class HTTPRequest(object):
	"""
		Wrapper around XMLHttpRequest
	"""

	def __init__(self, method, url, callbackSuccess=None, callbackFailure=None, payload=None, content_type=None,
				 asynchronous=True):
		super(HTTPRequest, self).__init__()

		method = method.upper()
		assert method in ["GET", "POST"]

		self.method = method
		self.callbackSuccess = callbackSuccess
		self.callbackFailure = callbackFailure
		self.hasBeenSent = False
		self.payload = payload
		self.content_type = content_type

		self.req = jseval("new XMLHttpRequest()")
		self.req.onreadystatechange = self.onReadyStateChange
		self.req.open(method, url, asynchronous)

	def onReadyStateChange(self, *args, **kwargs):
		"""
			Internal callback.
		"""
		if self.req.readyState == 1 and not self.hasBeenSent:
			self.hasBeenSent = True  # Internet Explorer calls this function twice!

			if self.method == "POST" and self.content_type is not None:
				self.req.setRequestHeader("Content-Type", self.content_type)

			self.req.send(self.payload)

		if self.req.readyState == 4:
			if 200 <= self.req.status < 300:
				if self.callbackSuccess:
					self.callbackSuccess(self.req.responseText)
			else:
				if self.callbackFailure:
					self.callbackFailure(self.req.responseText, self.req.status)


class SimpleNetwork(object):

	def genReqStr(self, params):
		boundary_str = "---" + ''.join(
			[random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(13)])
		boundary = boundary_str

		res = f"Content-Type: multipart/mixed; boundary=\"{boundary}\"\r\nMIME-Version: 1.0\r\n"
		res += "\r\n--" + boundary

		def expand(key, value):
			ret = ""

			if all([x in dir(value) for x in ["name", "read"]]):  # File
				type = "application/octet-stream"
				filename = os.path.basename(value.name).decode(sys.getfilesystemencoding())

				ret += \
					f"\r\nContent-Type: {type}" \
					f"\r\nMIME-Version: 1.0" \
					f"\r\nContent-Disposition: form-data; name=\"{key}\"; filename=\"{filename}\"\r\n\r\n"
				ret += str(value.read())
				ret += '\r\n--' + boundary

			elif isinstance(value, list):
				if any([isinstance(entry, dict) for entry in value]):
					for idx, entry in enumerate(value):
						ret += expand(key + "." + str(idx), entry)
				else:
					for entry in value:
						ret += expand(key, entry)

			elif isinstance(value, dict):
				for key_, entry in value.items():
					ret += expand(((key + ".") if key else "") + key_, entry)

			else:
				ret += \
					"\r\nContent-Type: application/octet-stream" \
					"\r\nMIME-Version: 1.0" \
					f"\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n"
				ret += str(value) if value is not None else ""
				ret += '\r\n--' + boundary

			return ret

		for key, value in params.items():
			res += expand(key, value)

		res += "--\r\n"
		return res, boundary

	def __init__(self):
		self.result = None
		self.status = None

	def request(self, url, params):
		if params:
			method = "POST"

			contentType = None

			if isinstance(params, dict):
				multipart, boundary = self.genReqStr(params)
				contentType = "multipart/form-data; boundary=" + boundary + "; charset=utf-8"
			elif isinstance(params, bytes):
				contentType = "application/x-www-form-urlencoded"
				multipart = params
			else:
				multipart = params

			HTTPRequest(method, url, self.onCompletion, self.onError, payload=multipart, content_type=contentType,
						asynchronous=False)
		else:
			method = "GET"
			HTTPRequest(method, url, self.onCompletion, self.onError, asynchronous=False)
		return self

	def onCompletion(self, text):
		self.result = text
		self.status = "succeeded"

	def onError(self, text, code):
		self.status = "failed"
		self.result = text
		self.code = code
