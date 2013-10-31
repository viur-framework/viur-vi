#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, time
#from config import conf
import json
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas import Timer
import string, random, time


class DeferredCall( Timer ):
	"""
		Calls the given function with a fixed delay.
		This allows assuming that calls to NetworkService are always
		asynchronous, so its guaranteed that any initialization code can run
		before the Network-Call yields results.
	"""
	def __init__( self, func, *args, **kwargs ):
		Timer.__init__( self, 25 )
		#super( DeferredCall, self ).__init__(25)
		self._tFunc = func
		self._tArgs = args
		self._tKwArgs = kwargs

	def run(self):
		self._tFunc( *self._tArgs, **self._tKwArgs )

class NetworkService( object ):
	"""
		Generic wrapper around ajax requests.
		Handles caching and multiplexing multiple concurrent requests to
		the same resource. It also acts as the central proxy to notify
		currently active widgets of changes made to data on the server.
	"""
	changeListeners = [] # All currently active widgets which will be informed of changes made
	_cache = {} # Result cache of recently made network requests

	@staticmethod
	def notifyChange( modul ):
		"""
			Broadcasts a change made to data of modul 'modul' to all currently
			registered changeListeners.
			@param modul: Name of the modul where the change occured
			@type modul: string
		"""
		print("NOTIFIYING CHANGES NOW")
		print( NetworkService.changeListeners )
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
				res += value.read()
				res += b'\r\n--'+boundary
			elif isinstance( value, list ):
				for val in value:
					res += b'\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b'"\r\n\r\n'
					res += val
					res += b'\r\n--'+boundary
			else:
				res += b'\r\nContent-Type: application/octet-stream\r\nMIME-Version: 1.0\r\nContent-Disposition: form-data; name="'+key+b'"\r\n\r\n'
				res += value
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
		return( json.loads( req.result ) )


	@staticmethod
	def keyFromQuery( modul, url, params ):
		"""
			Calculates the cache key for the given parameters.
		"""
		res = NetworkService.urlForArgs(modul,url)
		if params:
			tmp = []
			for k,v in params.items():
				tmp.append( (k,v) )
			tmp.sort( key=lambda x: x[0])
			for k,v in tmp:
				res += k+v
		return( res )

	@staticmethod
	def urlForArgs( modul, path ):
		"""
			Constructs the final url for that request.
			If modul is given, it prepends "/admin" and injects a timestamp
			to fool the builtin cache of modern browsers.
			If modul is None, path is returned unchanged.
			@param modul: Name of the target modul or None
			@type modul: string or None
			@param path: Path (either relative to 'modul' or absolute if 'modul' is None
			@type path: string
			@returns: string
		"""
		if modul:
			return( "/admin/%s/%s?_unused_time_stamp=%s" % (modul, path, time.time()))
		else:
			return( path )

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
		if cacheable:
			self.cacheKey = NetworkService.keyFromQuery( modul, url, params )
			NetworkService._cache[ self.cacheKey ] = self
		else:
			self.cacheKey = None
		self.secure = secure
		if secure:
			self.waitingForSkey = True
			self.doFetch("/admin/skey",None,None)
		else:
			self.doFetch(NetworkService.urlForArgs(modul,url),params, None)


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
		assert not( cacheable and modifies ), "Cannot cache a request modifying data!"
		print( params )
		if cacheable:
			key = NetworkService.keyFromQuery( modul, url, params )
			if key in NetworkService._cache.keys():
				req = NetworkService._cache[ key ]
				if req.status=="running":
					# Stack these handlers on that request
					if successHandler:
						req.successHandler.append( successHandler )
					if failureHandler:
						req.successHandler.append( failureHandler )
					if finishedHandler:
						req.successHandler.append( finishedHandler )
					return( req )
				elif req.status == "succeeded":
					if successHandler:
						DeferredCall( successHandler, req )
					if finishedHandler:
						DeferredCall( finishedHandler, req )
					return( req )
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
			HTTPRequest().asyncGet(url, self)

	def onCompletion(self, text):
		"""
			Internal hook for the AJAX call.
		"""
		if self.waitingForSkey:
			self.waitingForSkey = False
			self.doFetch( NetworkService.urlForArgs(self.modul,self.url), self.params, json.loads(text) )
		else:
			print("IM COMPLETE", self)
			self.result = text
			self.status = "succeeded"
			try:
				for s in self.successHandler:
					s( self )
				for s in self.finishedHandler:
					s( self )
			except:
				if self.modifies:
					NetworkService.notifyChange( self.modul )
				raise
			# Remove references to our handlers
			self.successHandler = []
			self.finishedHandler = []
			self.failureHandler = []
			self.params = None
			if self.modifies:
				NetworkService.notifyChange( self.modul )

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
		# As we failed anyway, there's no need to cache this
		if self.cacheKey and self.cacheKey in NetworkService._cache.keys():
			del NetworkService._cache[ self.cacheKey ]

	def onTimeout(self, text):
		"""
			Internal hook for the AJAX call.
		"""

		self.onError( text, -1 )
