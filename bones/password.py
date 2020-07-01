from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget
from vi.exception import InvalidBoneValueException
from vi.i18n import translate


class PasswordEditWidget(BaseEditWidget):
	style = ["vi-bone", "vi-bone--password", "vi-bone-container", "input-group"]

	def createWidget(self):
		self.appendChild("""<ignite-input [name]="widget" type="password">""")

		user = conf["currentUser"]
		if self.bone.readonly or (user and "root" in user["access"]):
			self.verify = None
		else:
			self.appendChild("""
				<label>
					{{txt}}
					<ignite-input [name]="verify" type="password">
				</label>
			""",
			vars={"txt": translate("reenter password")})

	def serialize(self):
		if not self.verify or self.widget["value"] == self.verify["value"]:
			return self.widget["value"]

		raise InvalidBoneValueException()


class PasswordBone(BaseBone):
	editWidgetFactory = PasswordEditWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "password" or skelStructure[boneName]["type"].startswith("password.")


boneSelector.insert(1, PasswordBone.checkFor, PasswordBone)
