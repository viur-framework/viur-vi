
def isSingleSelectionKey( keyCode ):
	"""
		Tests wherever keyCode means the modifier key for single selection
	"""
	if keyCode==17: # "ctrl" on all major platforms
		return( True )
	elif eval("navigator.appVersion.indexOf(\"Mac\")!=-1"): # "cmd" on the broken one
		if keyCode in [ 224, 17, 91, 93 ]:
			return( True )
	return( False )


def isArrowUp( keyCode ):
	return( keyCode==38 )

def isArrowDown( keyCode ):
	return( keyCode==40 )

def isReturn( keyCode ):
	return( keyCode==13 )
