import translations

_currentLanguage = eval("navigator.language")
_runtimeTranslations = {}
_lngMap = {}

#Populate the lng table
for key in dir( translations ):
	if key.startswith("lng"):
		_lngMap[ key[3:].lower() ] = { k.lower(): v for k,v in getattr( translations, key ).items() }


def translate( key, **kwargs ):
	"""
		Tries to translate the given string in the currently selected language.
		Supports replacing markers (using {markerName} syntax).

		@param key: The string to translate
		@type key: String
		@returns: The translated string
	"""
	def processTr( inStr, **kwargs ):
		for k,v in kwargs.items():
			inStr = inStr.replace("{%s}" % k, str(v))
		return( inStr )
	#assert _currentLanguage is not None and len(_currentLanguage)==2 #FIXME: Fails for en-US
	if _currentLanguage in _runtimeTranslations.keys():
		if key.lower() in _runtimeTranslations[ _currentLanguage ].keys():
			return( processTr( _runtimeTranslations[ _currentLanguage ][key.lower()], **kwargs ) )
	if _currentLanguage in _lngMap.keys():
		if key.lower() in _lngMap[ _currentLanguage ].keys():
			return( processTr( _lngMap[ _currentLanguage ][key.lower()], **kwargs) )
	return( processTr( key, **kwargs ).upper() ) #FIXME!


def addTranslation( lang, a, b=None ):
	"""
		Adds or updates new translations.
	"""
	if not lang in _runtimeTranslations.keys():
		_runtimeTranslations[ lang ] = {}
	if isinstance(a,str) and b is not None:
		updateDict = { a.lower() : b }
	elif isinstance( a, dict ):
		updateDict = { k.lower(): v for k,v in a.items() }
	else:
		raise ValueError("Invalid call to addTranslation")
	_runtimeTranslations[ lang ].update( updateDict )

def setLanguage( lang ):
	"""
		Sets the current language to lang
	"""
	_currentLanguage = lang
