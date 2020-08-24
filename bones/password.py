from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget
from vi.exception import InvalidBoneValueException
from vi.i18n import translate


class PasswordEditWidget(BaseEditWidget):
	style = ["vi-value", "vi-value--password", "vi-value-container", "input-group"]

	def _createWidget(self):
		self.appendChild("""<ignite-input [name]="widget" type="password" >""")

		if self.bone.readonly:
			self.verify = None
		else:
			# language=HTML
			self.appendChild("""
				<label class="label vi-label vi-label--password is-required">
					{{txt}}
				</label>
				<ignite-input [name]="verify" type="password">
			""",
			vars={"txt": translate("reenter password")})

			self.widget.element.autocomplete="new-password"

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
