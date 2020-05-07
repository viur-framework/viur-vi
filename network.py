# -*- coding: utf-8 -*-
import os, sys, json, string, random, time

from vi import html5
from vi import framework
from vi.config import conf


class DeferredCall(framework.utils.DeferredCall):
	'''
		Deprecated. Moved to framework.utils
	'''
	pass


class HTTPRequest(object):
	"""
		Wrapper around XMLHttpRequest
	"""

	def __init__(self, *args, **kwargs):
		super(HTTPRequest, self).__init__(*args, **kwargs)
		self.req = html5.jseval("new XMLHttpRequest()")
		self.req.onreadystatechange = self.onReadyStateChange
		self.cb = None
		self.hasBeenSent = False

	def asyncGet(self, url, cb):
		"""
			Performs a GET operation on a remote server
			:param url: The url to fetch. Either absolute or relative to the server
			:type url: str
			:param cb: Target object to call "onCompletion" on success
			:type cb: object
		"""
		self.cb = cb
		self.type = "GET"
		self.payload = None
		self.content_type = None
		self.req.open("GET", url, True)

	def asyncPost(self, url, payload, cb, content_type=None):
		"""
			Performs a POST operation on a remote server
			:param url: The url to fetch. Either absolute or relative to the server
			:type url: str
			:param cb: Target object to call "onCompletion" on success
			:type cb: object
		"""
		self.cb = cb
		self.type = "POST"
		self.payload = payload
		self.content_type = content_type
		self.req.open("POST", url, True)

	def onReadyStateChange(self, *args, **kwargs):
		"""
			Internal callback.
		"""
		if self.req.readyState == 1 and not self.hasBeenSent:
			self.hasBeenSent = True  # Internet Explorer calls this function twice!

			if self.type == "POST" and self.content_type is not None:
				self.req.setRequestHeader('Content-Type', self.content_type)

			self.req.send(self.payload)

		if self.req.readyState == 4:
			if self.req.status >= 200 and self.req.status < 300:
				self.cb.onCompletion(self.req.responseText)
			else:
				self.cb.onError(self.req.responseText, self.req.status)


class NetworkService(object):
	"""
		Generic wrapper around ajax requests.
		Handles caching and multiplexing multiple concurrent requests to
		the same resource. It also acts as the central proxy to notify
		currently active widgets of changes made to data on the server.
	"""
	changeListeners = []  # All currently active widgets which will be informed of changes made
	_cache = {}  # module->Cache index map (for requests that can be cached)
	host = ""
	prefix = "/json"
	defaultFailureHandler = None

	retryCodes = [0, -1]
	retryMax = 3
	retryDelay = 5000

	@staticmethod
	def notifyChange(module, **kwargs):
		"""
			Broadcasts a change made to data of module 'module' to all currently
			registered changeListeners.
			Also invalidates our _cache
			:param module: Name of the module where the change occured
			:type module: str
		"""
		if module in NetworkService._cache.keys():
			NetworkService._cache[module] += 1

		for c in NetworkService.changeListeners:
			c.onDataChanged(module, **kwargs)

	@staticmethod
	def registerChangeListener(listener):
		"""
			Registers object 'listener' for change notifications.
			'listener' must provide an 'onDataChanged' function accepting
			one parameter: the name of the module. Does nothing if that object
			has already registered.
			:param listener: The object to register
			:type listener: object
		"""
		if listener in NetworkService.changeListeners:
			return

		NetworkService.changeListeners.append(listener)

	@staticmethod
	def removeChangeListener(listener):
		"""
			Unregisters the object 'listener' from change notifications.
			:param listener: The object to unregister. It must be currently registered.
			:type listener: object
		"""
		assert listener in NetworkService.changeListeners, "Attempt to remove unregistered listener %s" % str(listener)
		NetworkService.changeListeners.remove(listener)

	@staticmethod
	def genReqStr(params: dict):
		"""
			Creates a MIME (multipart/mixed) payload for post requests transmitting
			the values given in params.

			:param params: Dictionary of key->values to encode
			:type params: dict

			:returns: (string payload, string boundary)
		"""
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
					f"\r\nMIME - Version: 1.0" \
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
				ret += str(value)
				ret += '\r\n--' + boundary

			return ret

		for key, value in params.items():
			res += expand(key, value)

		res += "--\r\n"

		print(res)
		return res, boundary

	@staticmethod
	def decode(req):
		"""
			Decodes a response received from the server (ie parsing the json)
			:type req: Instance of NetworkService response
			:returns: object
		"""
		return json.loads(req.result)

	@staticmethod
	def isOkay(req):
		answ = NetworkService.decode(req)
		return isinstance(answ, str) and answ == "OKAY"

	@staticmethod
	def urlForArgs(module, path, cacheable):
		"""
			Constructs the final url for that request.
			If module is given, it prepends "/json" and injects a timestamp
			to fool the builtin cache of modern browsers.
			If module is None, path is returned unchanged.
			:param module: Name of the target module or None
			:type module: str or None
			:param path: Path (either relative to 'module' or absolute if 'module' is None
			:type path: str
			:param cacheable: If true, allow the browser to cache that request
			:type cacheable: bool
			:returns: str
		"""
		cacheKey = time.time()

		if cacheable and module:
			if not module in NetworkService._cache.keys():
				NetworkService._cache[module] = 1

			cacheKey = "c%s" % NetworkService._cache[module]

		if module:
			href = "%s/%s/%s?_unused_time_stamp=%s" % (NetworkService.prefix,
			                                           module, path, cacheKey)
		else:
			href = "%s%s_unused_time_stamp=%s" % (path, "&" if "?" in path else "?", cacheKey)

		if not href.startswith("/"):
			href = "/" + href

		return NetworkService.host + href

	def __init__(self, module, url, params, successHandler, failureHandler, finishedHandler,
	             modifies, cacheable, secure, kickoff):
		"""
			Constructs a new NetworkService request.
			Should not be called directly (use NetworkService.request instead).
		"""
		super(NetworkService, self).__init__()

		self.result = None
		self.status = None
		self.waitingForSkey = False
		self.module = module
		self.url = url
		self.params = params

		self.successHandler = [successHandler] if successHandler else []
		self.failureHandler = [failureHandler] if failureHandler else []
		self.finishedHandler = [finishedHandler] if finishedHandler else []

		self.modifies = modifies
		self.cacheable = cacheable
		self.secure = secure

		self.kickoffs = 0
		if kickoff:
			self.kickoff()

	def kickoff(self):
		self.status = "running"
		self.kickoffs += 1

		if self.secure:
			self.waitingForSkey = True
			self.doFetch("%s%s/skey" % (NetworkService.host, NetworkService.prefix), None, None)
		else:
			self.doFetch(NetworkService.urlForArgs(self.module, self.url, self.cacheable), self.params, None)

	@staticmethod
	def request(module, url, params=None, successHandler=None, failureHandler=None,
	            finishedHandler=None, modifies=False, cacheable=False, secure=False, kickoff=True):
		"""
			Performs an AJAX request. Handles caching and security-keys.

			Calls made to this function are guaranteed to be asynchron, even
			if the result is already known (cached).

			:param module: Target module on the server. Set to None if you want to call anything else
			:type module: str or None
			:param url: The path (relative to module) or a full url if module is None
			:type url: None
			:param successHandler: function beeing called if the request succeeds. Must take one argument (the request).
			:type successHandler: callable
			:param failureHandler: function beeing called if the request failes. Must take two arguments (the request and an error-code).
			:type failureHandler: callable
			:param finishedHandler: function beeing called if the request finished (regardless wherever it succeeded or not). Must take one argument (the request).
			:type finishedHandler: callable
			:param modifies: If set to True, it will automatically broadcast an onDataChanged event for that module.
			:type modifies: bool
			:param cacheable: Indicates if this request could be cached. Defaults to False.
			:type cacheable: bool
			:param secure: If true, include a fresh securitykey in this request. Defaults to False.
			:type secure: bool

		"""
		print("NS REQUEST", module, url, params)
		assert not (cacheable and modifies), "Cannot cache a request modifying data!"

		# Seems not cacheable or not cached
		return NetworkService(module, url, params,
		                      successHandler, failureHandler, finishedHandler,
		                      modifies, cacheable, secure, kickoff)

	def doFetch(self, url, params, skey):
		"""
			Internal function performing the actual AJAX request.
		"""

		if "updateParams" in conf and conf["updateParams"] and callable(conf["updateParams"]):
			params = conf["updateParams"](url, params)

		if params:
			if skey:
				params["skey"] = skey

			contentType = None

			if isinstance(params, dict):
				multipart, boundary = NetworkService.genReqStr(params)
				contentType = "multipart/form-data; boundary=" + boundary + "; charset=utf-8"
			elif isinstance(params, bytes):
				contentType = "application/x-www-form-urlencoded"
				multipart = params
			else:
				print(params)
				print(type(params))
				multipart = params

			HTTPRequest().asyncPost(url, multipart, self, content_type=contentType)

		else:
			if skey:
				if "?" in url:
					url += "&skey=%s" % skey
				else:
					url += "?skey=%s" % skey

			HTTPRequest().asyncGet(url, self)

	def onCompletion(self, text):
		"""
			Internal hook for the AJAX call.
		"""
		if self.waitingForSkey:
			self.waitingForSkey = False
			self.doFetch(NetworkService.urlForArgs(self.module, self.url, self.cacheable),
			             self.params, json.loads(text))
		else:
			self.result = text
			self.status = "succeeded"
			try:
				for s in self.successHandler:
					s(self)
				for s in self.finishedHandler:
					s(self)
			except:
				if self.modifies:
					DeferredCall(
						NetworkService.notifyChange, self.module,
						key=self.params.get("key") if self.params else None,
						action=self.url,
						_delay=2500
					)
				raise

			if self.modifies:
				DeferredCall(
					NetworkService.notifyChange, self.module,
					key=self.params.get("key") if self.params else None,
					action=self.url, _delay=2500
				)

			# Remove references to our handlers
			self.clear()

	def onError(self, text, code):
		"""
			Internal hook for the AJAX call.
		"""
		self.status = "failed"
		self.result = text

		print("onError", self.kickoffs, self.retryMax, int(code), self.retryCodes)

		if self.kickoffs < self.retryMax and int(code) in self.retryCodes:
			try:
				logError = html5.window.top.logError
			except:
				logError = None
			if logError and self.kickoffs == self.retryMax - 1:
				logError("NetworkService.onError code:%s module:%s url:%s params:%s" % (
				code, self.module, self.url, self.params))

			print("error %d, kickoff %d, will retry now" % (int(code), self.kickoffs))
			DeferredCall(self.kickoff, _delay=self.retryDelay)
			return

		for s in self.failureHandler:
			s(self, code)

		if not self.failureHandler and self.defaultFailureHandler:
			self.defaultFailureHandler(self, code)

		if not self.defaultFailureHandler:
			self.clear()

		for s in self.finishedHandler:
			s(self)

	def onTimeout(self, text):
		"""
			Internal hook for the AJAX call.
		"""
		self.onError(text, -1)

	def clear(self):
		self.successHandler = []
		self.finishedHandler = []
		self.failureHandler = []
		self.params = None
