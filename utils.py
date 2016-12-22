#-*- coding: utf-8 -*-

def formatString(format, data, structure = None, prefix = None, language = None, _rec = 0):
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

	:param data: Data applied to the format String
	:type data: list | dict

	:param structure: Parses along the structure of the given skeleton.
	:type structure: dict

	:return: The traversed string with the replaced values.
	:rtype: str
	"""

	if structure and isinstance(structure, list):
		structure = {k:v for k, v in structure}

	prefix = prefix or []
	res = format

	if isinstance(data,  list):
		return ", ".join([formatString(format, x, structure, prefix, language, _rec = _rec + 1) for x in data])

	elif isinstance(data, str):
		return data

	elif not data:
		return res

	for key in data.keys():
		val = data[key]
		struct = structure.get(key) if structure else None

		#print("%s%s: %s" % (_rec * " ", key, val))
		#print("%s%s: %s" % (_rec * " ", key, struct))

		if isinstance(val, dict):
			if struct and ("$(%s)" % ".".join(prefix + [key])) in res:
				langs = struct.get("languages")
				if langs:
					if language and language in langs and language in val.keys():
						val = val[language]
					else:
						val = ", ".join(val.values())

				else:
					continue

			else:
				res = formatString(res, val, structure, prefix + [key], language, _rec = _rec + 1)

		elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
			res = formatString(res, val[0], structure, prefix + [key], language, _rec = _rec + 1)
		elif isinstance(val, list):
			val = ", ".join(val)

		res = res.replace("$(%s)" % (".".join(prefix + [key])), str(val))

	return res

def getImagePreview(data):
	if "mimetype" in data.keys() and isinstance(data["mimetype"], str) and data["mimetype"].startswith("image/svg"):
		return "/file/download/%s" % data["dlkey"]
	elif "servingurl" in data.keys():
		if data["servingurl"]:
			return data["servingurl"] + "=s150-c"

		return ""

	return None

def setPreventUnloading(mode = True):
	count = eval("window.top.preventViUnloading")

	print("setPreventUnloading", count, mode)

	if not mode:
		if count == 0:
			return

	count += (1 if mode else -1)

	eval("window.top.preventViUnloading = %d;" % count)
	return count
