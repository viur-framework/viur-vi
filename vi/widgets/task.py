from flare import html5, utils, ignite
from flare.button import Button
from flare.popup import Popup
from vi.config import conf
from flare.i18n import translate
from vi.widgets.edit import EditWidget


class TaskWidget(Popup):
	def __init__(self, title):
		super(TaskWidget, self).__init__(title=title)
		self["class"].append("popup--task")
		self.title = title


class ServerTaskWidget(TaskWidget):
	def __init__(self, title, key):
		super(ServerTaskWidget, self).__init__(title=title)
		self.widget = EditWidget("_tasks", EditWidget.appList, key, action="execute", logAction="vi.tasks.started")
		self.popupBody.appendChild(self.widget)
		self.popupBody.removeClass("box--content")
		self.popupFoot.appendChild(Button(translate("Cancel"), self.close))


class TaskSelectWidget(TaskWidget):
	def __init__(self):
		super(TaskSelectWidget, self).__init__(title=translate("vi.tasks.headline"))
		self.sinkEvent("onChange")

		div = html5.Div()
		div["class"] = ["vi-tasks-selector"]
		self.popupBody.appendChild(div)

		self.select = ignite.Select()
		div.appendChild(self.select)

		for type in ["server", "client"]:
			for i, task in enumerate(conf["tasks"][type]):
				if type == "client":
					assert task["task"], "task-Attribute must be set for client-side tasks"

				if not "type" in task.keys():
					task["type"] = type

				opt = html5.Option()
				opt.task = task

				opt.appendChild(html5.TextNode(task["name"]))

				if not self.select._children:
					opt._setSelected(True)

				self.select.appendChild(opt)

		self.descr = html5.Div()
		self.descr["class"] = ["vi-tasks-description"]
		self.popupBody.appendChild(self.descr)

		self.popupFoot.appendChild(Button(translate("Cancel"), self.close))
		self.popupFoot.appendChild(Button(translate("Run"), self.invokeTask))

		# Init
		self.setActiveTask()

	def getSelectedTask(self):
		if self.select["selectedIndex"]:
			return self.select._children[self.select["selectedIndex"]].task
		return False

	def setActiveTask(self):
		task = self.getSelectedTask()
		if not task:
			return 0
		self.descr.removeAllChildren()
		self.descr.appendChild(
			html5.TextNode(
				task.get("descr") or translate("vi.tasks.no-description")))

	def onChange(self, event):
		if utils.doesEventHitWidgetOrChildren(event, self.select):
			self.setActiveTask()

	def invokeTask(self, *args, **kwargs):
		task = self.getSelectedTask()
		if not task:
			return 0
		self.close()

		if task["type"] == "server":
			ServerTaskWidget(task["name"], task["key"])
		elif task["type"] == "client":
			if not "task" in task.keys():
				return

			task["task"](task["name"])
		else:
			raise NotImplementedError()
