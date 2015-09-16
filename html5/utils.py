# -*- coding: utf-8 -*-

def unescape(val, maxLength = 0):
	"""
		Unquotes several HTML-quoted characters in a string.

		:param val: The value to be unescaped.
		:type val: str

		:param maxLength: Cut-off after maxLength characters.
				A value of 0 means "unlimited". (default)
		:type maxLength: int

		:returns: The unquoted string.
		:rtype: str
	"""
	val = val \
			.replace("&lt;", "<") \
			.replace("&gt;", ">") \
			.replace("&quot;", "\"") \
			.replace("&#39;", "'")

	if maxLength > 0:
		return val[0:maxLength]

	return val
