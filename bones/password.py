# -*- coding: utf-8 -*-
import html5,re
from priorityqueue import editBoneSelector, viewDelegateSelector
from widgets.edit import InvalidBoneValueException
from i18n import translate

class PasswordEditBone( html5.Div ):
	def __init__(self, moduleName, boneName, readOnly, *args, **kwargs ):
		super( PasswordEditBone,  self ).__init__( *args, **kwargs )
		self.boneName = boneName
		self.readOnly = readOnly
		self.primeinput=html5.Input()
		self.secondinput=html5.Input()
		self.primeinput["type"]="password"
		self.secondinput["type"]="password"
		self.appendChild(self.primeinput)
		lbl=html5.Label(translate("reenter password"))
		lbl["for"]==moduleName+"_"+boneName+"_reenterpwd"
		self.appendChild(lbl)
		self.secondinput["name"]=moduleName+"_"+boneName+"_reenterpwd"
		self.appendChild(self.secondinput)
		if self.readOnly:
			self["disabled"] = True

	@staticmethod
	def fromSkelStructure( moduleName, boneName, skelStructure ):
		readOnly = "readonly" in skelStructure[ boneName ].keys() and skelStructure[ boneName ]["readonly"]
		return( PasswordEditBone( moduleName, boneName, readOnly ) )

	def unserialize(self, data):
		pass
		#if self.boneName in data.keys():
			#self.primeinput["value"] = data[ self.boneName ] if data[ self.boneName ] else ""
			#print data[ self.boneName ]
			#print self.primeinput["value"]
			#self.lineEdit.setText( str( data[ self.boneName ] ) if data[ self.boneName ] else "" )

	def serializeForPost(self):
		if self.primeinput["value"]==self.secondinput["value"]: #and re.match("[a-zA-Z0-9]{6,100}$",self.primeinput["value"]):
			return( { self.boneName: self.primeinput["value"] } )
		raise InvalidBoneValueException()

	def setExtendedErrorInformation(self, errorInfo ):
		pass


def CheckForPasswordBone(  moduleName, boneName, skelStucture, *args, **kwargs ):
	return( str(skelStucture[boneName]["type"]).startswith("password") )


#Register this Bone in the global queue
editBoneSelector.insert( 5, CheckForPasswordBone, PasswordEditBone)


