#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import json
import string, random, time

class DeferredCall( object ):
	"""
		Calls the given function with a fixed delay.
		This allows assuming that calls to NetworkService are always
		asynchronous, so its guaranteed that any initialization code can run
		before the Network-Call yields results.
	"""
	def __init__( self, func, *args, **kwargs ):
		"""
			@param func: Callback function
			@type func: Callable
		"""
		super( DeferredCall, self ).__init__()
		delay = 25
		if "_delay" in kwargs.keys():
			delay = kwargs["_delay"]
			del kwargs["_delay"]
		self._tFunc = func
		self._tArgs = args
		self._tKwArgs = kwargs
		w = eval("window")
		w.setTimeout( self.run, delay )

	def run(self):
		"""
			Internal callback that executes the callback function
		"""
		self._tFunc( *self._tArgs, **self._tKwArgs )

class HTTPRequest(object):
	"""
		Wrapper around XMLHttpRequest
	"""
	def __init__(self, *args, **kwargs ):
		super( HTTPRequest, self ).__init__( *args, **kwargs )
		self.req = eval("new XMLHttpRequest()")
		self.req.onreadystatechange = self.onReadyStateChange
		self.cb = None
		self.hasBeenSent = False

	def asyncGet(self, url, cb):
		"""
			Performs a GET operation on a remote server
			@param url: The url to fetch. Either absolute or relative to the server
			@type url: String
			@param cb: Target object to call "onCompletion" on success
			@type cb: object
		"""
		self.cb = cb
		self.type = "GET"
		self.payload = None
		self.content_type = None
		self.req.open("GET",url,True)

	def asyncPost(self, url, payload, cb, content_type=None ):
		"""
			Performs a POST operation on a remote server
			@param url: The url to fetch. Either absolute or relative to the server
			@type url: String
			@param cb: Target object to call "onCompletion" on success
			@type cb: object
		"""
		self.cb = cb
		self.type = "POST"
		self.payload = payload
		self.content_type = content_type
		self.req.open("POST",url,True)

	def onReadyStateChange(self, *args, **kwargs):
		"""
			Internal callback.
		"""
		if self.req.readyState == 1 and not self.hasBeenSent:
			self.hasBeenSent = True # Internet Explorer calls this function twice!

			if self.type=="POST" and self.content_type is not None:
				self.req.setRequestHeader('Content-Type', self.content_type)

			self.req.send( self.payload )

		if self.req.readyState == 4:
			if self.req.status >= 200 and self.req.status < 300:
				self.cb.onCompletion( self.req.responseText )
			else:
				self.cb.onError( self.req.responseText, self.req.status )

class NetworkService( object ):
	"""
		Generic wrapper around ajax requests.
		Handles caching and multiplexing multiple concurrent requests to
		the same resource. It also acts as the central proxy to notify
		currently active widgets of changes made to data on the server.
	"""
	changeListeners = [] # All currently active widgets which will be informed of changes made
	_cache = {} # Modul->Cache index map (for requests that can be cached)

	@staticmethod
	def notifyChange( modul ):
		"""
			Broadcasts a change made to data of modul 'modul' to all currently
			registered changeListeners.
			Also invalidates our _cache
			@param modul: Name of the modul where the change occured
			@type modul: string
		"""
		if modul in NetworkService._cache.keys():
			NetworkService._cache[ modul ] += 1
		for c in NetworkService.changeListeners:
			c.onDataChanged( modul )

	@staticmethod
	def registerChangeListener( listener ):
		"""
			Registers object 'listener' for change notifications.
			'listener' must provide an 'onDataChanged' function accepting
			one parameter: the name of the modul. Does nothing if that object
			has already registered.
			@param listener: The object to register
			@type listener: object
		"""
		if listener in NetworkService.changeListeners:
			return
		NetworkService.changeListeners.append( listener )

	@staticmethod
	def removeChangeListener( listener ):
		"""
			Unregisters the object 'listener' from change notifications.
			@param listener: The object to unregister. It must be currently registered.
			@type listener: object
		"""
		assert listener in NetworkService.changeListeners, "Attempt to remove unregistered listener %s" % str( listener )
		NetworkService.changeListeners.remove( listener )

	@staticmethod
	def genReqStr( params ):
		"""
			Creates a MIME (multipart/mixed) payload for post requests transmitting
			the values given in params.
			@param params: Dictionary of key->values to encode
			@type params: dict
			@returns: (string payload, string boundary )
		"""
		boundary_str = "---"+''.join( [ random.choice(string.ascii_lowercase+string.ascii_uppercase + string.digits) for x in range(13) ] )
		boundary = boundary_str
		res = b'Content-Type: multipart/mixed; boundary="'+boundary+b'"\r\nMIME-Version: 1.0\r\n'
		res += b'\r\n--'+boundary
		for(key, value) in list(params.items()):
			if all( [x in dir( value ) for x in ["name", "read"] ] ): #File
				try:
					(type, encoding) = mimetypes.guess_type( value.name.decode( sys.getfilesystemencoding() ), strict=False )
					type = type or "application/octet-stream"
				except:
					type = "application/octet-stream"
				res += b'\r\nContent-Type: '+type+b'\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b'"; filename="'+os.path.basename(value.name).decode(sys.getfilesystemencoding())+b'"\r\n\r\n'
				res += str(value.read())
				res += b'\r\n--'+boundary
			elif isinstance( value, list ):
				for val in value:
					res += b'\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b'"\r\n\r\n'
					res += str(val)
					res += b'\r\n--'+boundary
			elif isinstance( value, dict ):
				for k,v in value.items():
					res += b'\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b"."+k+b'"\r\n\r\n'
					res += str(v)
					res += b'\r\n--'+boundary
			else:
				res += b'\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b'"\r\n\r\n'
				res += str(value)
				res += b'\r\n--'+boundary
		res += b'--\r\n'
		return( res, boundary )


	@staticmethod
	def decode( req ):
		"""
			Decodes a response recived from the server (ie parsing the json)
			@type req: Instance of NetworkService response
			@returns: object
		"""
		return json.loads( req.result )

	@staticmethod
	def isOkay(req):
		answ = NetworkService.decode(req)
		return isinstance(answ, str) and answ == "OKAY"

	@staticmethod
	def urlForArgs( modul, path, cacheable ):
		"""
			Constructs the final url for that request.
			If modul is given, it prepends "/admin" and injects a timestamp
			to fool the builtin cache of modern browsers.
			If modul is None, path is returned unchanged.
			@param modul: Name of the target modul or None
			@type modul: string or None
			@param path: Path (either relative to 'modul' or absolute if 'modul' is None
			@type path: string
			@param cacheable: If true, allow the browser to cache that request
			@type cacheable: bool
			@returns: string
		"""
		cacheKey = time.time()
		if cacheable and modul:
			if not modul in NetworkService._cache.keys():
				NetworkService._cache[ modul ] = 1
			cacheKey = "c%s" % NetworkService._cache[ modul ]
		if modul:
			return( "/admin/%s/%s?_unused_time_stamp=%s" % (modul, path, cacheKey))
		else:
			if "?" in path:
				return( path+"&_unused_time_stamp=%s" % cacheKey)
			else:
				return( path+"?_unused_time_stamp=%s" % cacheKey)

	def __init__(self, modul, url, params, successHandler, failureHandler, finishedHandler, modifies, cacheable, secure ):
		"""
			Constructs a new NetworkService request.
			Should not be called directly (use NetworkService.request instead).
		"""
		super( NetworkService, self ).__init__()
		self.result = None
		self.status = "running"
		self.waitingForSkey = False
		self.modul = modul
		self.url = url
		self.params = params
		self.successHandler = [successHandler] if successHandler else []
		self.failureHandler = [failureHandler] if failureHandler else []
		self.finishedHandler = [finishedHandler] if finishedHandler else []
		self.modifies = modifies
		self.cacheable = cacheable
		self.secure = secure
		if secure:
			self.waitingForSkey = True
			self.doFetch("/admin/skey",None,None)
		else:
			self.doFetch(NetworkService.urlForArgs(modul,url,cacheable),params, None)


	@staticmethod
	def request( modul, url, params=None, successHandler=None, failureHandler=None,
		   finishedHandler=None, modifies=False, cacheable=False, secure=False ):
		"""
			Performs an AJAX request. Handles caching and security-keys.
			Calls made to this function are guaranteed to be asynchron, even
			if the result is already known (cached).
			@param modul: Target modul on the server. Set to None if you want to call anything else
			@type modul: string or None
			@param url: The path (relative to modul) or a full url if modul is None
			@type url: None
			@param successHandler: function beeing called if the request succeeds. Must take one argument (the request).
			@type successHandler: callable
			@param failureHandler: function beeing called if the request failes. Must take two arguments (the request and an error-code).
			@type failureHandler: callable
			@param finishedHandler: function beeing called if the request finished (regardless wherever it succeeded or not). Must take one argument (the request).
			@type finishedHandler: callable
			@param modifies: If set to True, it will automatically broadcast an onDataChanged event for that modul.
			@type modifies: bool
			@param cacheable: Indicates if this request could be cached. Defaults to False.
			@type cacheable: bool
			@param secure: If true, include a fresh securitykey in this request. Defaults to False.
			@type secure: bool

		"""
		print("NS REQUEST", modul, url, params )
		assert not( cacheable and modifies ), "Cannot cache a request modifying data!"
		#Seems not cacheable or not cached
		return( NetworkService(modul, url, params, successHandler, failureHandler, finishedHandler,
				       modifies, cacheable, secure) )


	def doFetch(self, url, params, skey ):
		"""
			Internal function performing the actual AJAX request.
		"""
		if params:
			if skey:
				params["skey"] = skey
			contentType = None
			if isinstance( params, dict):
				multipart, boundary = NetworkService.genReqStr( params )
				contentType = b'multipart/form-data; boundary='+boundary+b'; charset=utf-8'
			elif isinstance( params, bytes ):
				contentType =  b'application/x-www-form-urlencoded'
				multipart = params
			else:
				print( params )
				print( type( params ) )
			HTTPRequest().asyncPost(url, multipart, self, content_type=contentType )
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
			self.doFetch( NetworkService.urlForArgs(self.modul,self.url,self.cacheable), self.params, json.loads(text) )
		else:
			#print("IM COMPLETE", self)
			self.result = text
			self.status = "succeeded"
			try:
				for s in self.successHandler:
					s( self )
				for s in self.finishedHandler:
					s( self )
			except:
				if self.modifies:
					DeferredCall(NetworkService.notifyChange, self.modul, _delay=2500)
					#NetworkService.notifyChange( self.modul )
				raise
			# Remove references to our handlers
			self.successHandler = []
			self.finishedHandler = []
			self.failureHandler = []
			self.params = None
			if self.modifies:
				DeferredCall(NetworkService.notifyChange, self.modul, _delay=2500)

	def onError(self, text, code):
		"""
			Internal hook for the AJAX call.
		"""
		self.status = "failed"
		self.result = text
		for s in self.failureHandler:
			s( self, code )
		for s in self.finishedHandler:
			s( self )
		self.successHandler = []
		self.finishedHandler = []
		self.failureHandler = []
		self.params = None

	def onTimeout(self, text):
		"""
			Internal hook for the AJAX call.
		"""
		self.onError( text, -1 )
