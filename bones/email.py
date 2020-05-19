from vi.priorityqueue import boneSelector
from vi.config import conf
from vi.bones.base import BaseBone, BaseEditWidget, BaseViewWidget


class EmailEditWidget(BaseEditWidget):
	def _updateWidget(self):
		self.widget["type"] = "email"


class EmailViewWidget(BaseViewWidget):
	def unserialize(self, value=None):
		self.value = value

		if value:
			self.appendChild(
				"""<a href="mailto:{{value}}">{{value}}</a>""",
				vars={"value": value},
				replace=True
			)
		else:
			self.appendChild(conf["emptyValue"], replace=True)


class EmailBone(BaseBone):
	editWidgetFactory = EmailEditWidget
	viewWidgetFactory = EmailViewWidget

	@staticmethod
	def checkFor(moduleName, boneName, skelStructure):
		return skelStructure[boneName]["type"] == "str.email" or skelStructure[boneName]["type"].startswith("str.email.")


boneSelector.insert(2, EmailBone.checkFor, EmailBone)
