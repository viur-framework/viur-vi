import html5
from config import conf

def formatString( format, skelStructure, data, prefix=None, unescape=False ):
	"""
	Parses a string given by format and substitutes placeholders using values specified by data.

	The syntax for the placeholders is $(%s).
	Its possible to traverse to sub-dictionarys by using a dot as seperator.
	If data is a list, the result each element from this list applied to the given string; joined by ", ".

	Example:

		data = {"name": "Test","subdict": {"a":"1","b":"2"}}
		formatString = "Name: $(name), subdict.a: $(subdict.a)"

	Result: "Name: Test, subdict.a: 1"

	:param format: String containing the format.
	:type format: str

	:param skelStructure: Parses along the structure of the given skeleton.
	:type skelStructure: dict

	:param data: Data applied to the format String
	:type data: list | dict

	:return: The traversed string with the replaced values.
	:rtype: str
	"""

	def chooseLang( value, prefs, key ): #FIXME: Copy&Paste from bones/string
		"""
			Tries to select the best language for the current user.
			Value is the dictionary of lang -> text recived from the server,
			prefs the list of languages (in order of preference) for that bone.
		"""
		if not isinstance( value, dict ):
			return( str(value) )
		# Datastore format. (ie the langdict has been serialized to name.lang pairs
		try:
			lang = "%s.%s" % (key,conf["currentlanguage"])
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
				lang = conf["currentlanguage"]
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
		return(", ".join( [ formatString( format, skelStructure, x, prefix, unescape ) for x in data ] ) )

	res = format

	if isinstance( data, str ):
		return data

	if not data:
		return res

	for key in data.keys():
		if isinstance( data[ key ], dict ):
			res = formatString( res, skelStructure, data[key], prefix + [key] )
		elif isinstance( data[ key ], list ) and len( data[ key ] )>0 and isinstance( data[ key ][0], dict) :
			res = formatString( res, skelStructure, data[key][0], prefix + [key] )
		else:
			tok = key.split(".")
			if "." in key and "$(%s)" % tok[0] in res and tok[1] == conf["currentlanguage"]:
				res = res.replace("$(%s)" % (".".join( prefix + [tok[0]])), str(data[key]))
			else:
				res = res.replace( "$(%s)" % (".".join( prefix + [key] ) ), str(data[key]) )

	#Check for translated top-level bones
	if not prefix:
		for key, bone in skelStructure.items():
			if "languages" in bone.keys() and bone[ "languages" ]:
				res = res.replace( "$(%s)" % key, str(chooseLang( data, bone[ "languages" ], key) ) )

	# Unesacpe?
	if unescape:
		return html5.utils.unescape(res)

	return res

def boneListToDict( l ):
	res = {}
	for key, bone in l:
		res[ key ] = bone
	return( res )

def getImagePreview(data):
	if "mimetype" in data.keys() and isinstance(data["mimetype"], str) and data["mimetype"].startswith("image/svg"):
		return "/file/download/%s" % data["dlkey"]
	elif "servingurl" in data.keys():
		if data["servingurl"]:
			return data["servingurl"] + "=s150-c"

		return ""

	return None
