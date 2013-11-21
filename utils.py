def formatString( format, skelStructure, data, prefix=None ):
	""" Parses a String given by format and substitutes Placeholders using values specified by data.
	Syntax for Placeholders is $(%s). Its possible to traverse to subdictionarys by using a dot as seperator.
	If data is a list, the result each element from this list applied to the given string; joined by ", ".
	Example:
	data = {"name": "Test","subdict": {"a":"1","b":"2"}}
	formatString = "Name: $(name), subdict.a: $(subdict.a)"
	Result: "Name: Test, subdict.a: 1"

	@type format: String
	@param format: String contining the format
	@type skelStructure: Dict
	@param skelStructure: Parses along the structure of the given skeleton
	@type data: List or Dict
	@param data: Data applied to the format String
	@return: String
	"""
	def chooseLang( value, prefs, key ): #FIXME: Copy&Paste from bones/string
		"""
			Tries to select the best language for the current user.
			Value is the dictionary of lang -> text recived from the server,
			prefs the list of languages (in order of preference) for that bone.
		"""
		##FIXME!!!
		return( str(value))
		if not isinstance( value, dict ):
			return( str(value) )
		# Datastore format. (ie the langdict has been serialized to name.lang pairs
		try:
			lang = "%s.%s" % (key,conf.adminConfig["language"])
		except:
			lang = ""
		if lang in value.keys() and value[ lang ]:
			return( value[ lang ] )
		for lang in prefs:
			if "%s.%s" % (key,lang) in value.keys():
				if value[ "%s.%s" % (key,lang) ]:
					return( value[ "%s.%s" % (key,lang) ] )
		# Normal edit format ( name : { lang: xx } ) format
		if key in value.keys() and isinstance( value[ key ], dict ):
			langDict = value[ key ]
			try:
				lang = conf.adminConfig["language"]
			except:
				lang = ""
			if lang in langDict.keys():
				return( langDict[ lang ] )
			for lang in prefs:
				if lang in langDict.keys():
					if langDict[ lang ]:
						return( langDict[ lang ] )
		return( "" )
	if isinstance( skelStructure, list):
		# The server sends the information as list; but the first thing
		# editWidget etc does, is building up an dictionary again.
		# It this hasn't happen yet, we do it here
		tmpDict = {}
		for key, bone in skelStructure:
			tmpDict[ key ] = bone
		skelStructure = tmpDict
	prefix = prefix or []
	if isinstance( data,  list ):
		return(", ".join( [ formatString( format, skelStructure, x, prefix ) for x in data ] ) )
	res = format
	if isinstance( data, str ):
		return( data )
	if not data:
		return( res )
	for key in data.keys():
		if isinstance( data[ key ], dict ):
			res = formatString( res, skelStructure, data[key], prefix + [key] )
		elif isinstance( data[ key ], list ) and len( data[ key ] )>0 and isinstance( data[ key ][0], dict) :
			res = formatString( res, skelStructure, data[key][0], prefix + [key] )
		else:
			res = res.replace( "$(%s)" % (".".join( prefix + [key] ) ), str(data[key]) )
	#Check for translated top-level bones
	if not prefix:
		for key, bone in skelStructure.items():
			if "languages" in bone.keys() and bone[ "languages" ]:
				res = res.replace( "$(%s)" % key, str(chooseLang( data, bone[ "languages" ], key) ) )
	return( res )

def boneListToDict( l ):
	res = {}
	for key, bone in l:
		res[ key ] = bone
	return( res )

def doesEventHitWidget( event, widget ):
	"""
		Test if event 'event' hits widget 'widget' (or *any* of its children)
	"""
	while widget:
		if event.target == widget.element:
			return( True )
		widget = widget.parent()
	return( False )