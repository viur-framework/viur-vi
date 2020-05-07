# -*- coding: utf-8 -*-
from vi import html5

from vi.framework.components.button import Button
from vi.priorityqueue import boneSelector
from vi.config import conf


class BaseEditWidget(html5.ignite.Input):
	"""
	Base class for a bone-compliant edit widget implementation using an input field.
	"""
	style = ["vi-bone"]

	def unserialize(self, value=None):
		self["value"] = value or ""

	def serialize(self):
		return self["value"]


class BaseViewWidget(html5.Div):
	"""
	Base class for a bone-compliant view widget implementation using a div.
	"""
	style = ["vi-bone"]

	def unserialize(self, value=None):
		self.appendChild(html5.TextNode(value or conf["emptyValue"]), replace=True)


class BaseMultiEditWidgetEntry(html5.Div):
	"""
	Base class for an entry in a MultiBone container.
	"""

	def __init__(self, widget: html5.Widget):
		super().__init__()
		self.widget = widget

		# Proxy some functions of the original widget
		for fct in ["unserialize", "serialize", "focus"]:
			setattr(self, fct, getattr(self.widget, fct))

		self.appendChild(
			self.widget,
			"""<button [name]="removeBtn" class="btn--delete" text="Delete" icon="icons-delete" />"""
		)

	def onRemoveBtnClick(self):
		self.parent().removeChild(self)


class BaseMultiEditWidget(html5.Div):
	"""
	Class for encapsulating multiple bones inside a container
	"""
	entryFactory = BaseMultiEditWidgetEntry

	def __init__(self, widgetFactory: callable):
		super().__init__("""
			<div [name]="widgets" class="vi-bone-widgets"></div>
			<div [name]="actions" class="vi-bone-actions">
				<button [name]="addBtn" class="btn--add" text="Add" icon="icons-add"></button>
			</div>
		""")

		self.widgetFactory = widgetFactory

	def onAddBtnClick(self):
		last = self.widgets.children(-1)
		if last and not last.serialize():
			last.focus()
			return

		entry = self.addEntry()
		entry.focus()

	def addEntry(self, value=None):
		entry = self.widgetFactory()
		if self.entryFactory:
			entry = self.entryFactory(entry)

		if value:
			entry.unserialize(value)

		self.widgets.appendChild(entry)
		return entry

	def unserialize(self, value):
		self.widgets.removeAllChildren()

		if not isinstance(value, list):
			return

		for entry in value:
			self.addEntry(entry)

	def serialize(self):
		return [widget.serialize() for widget in self.widgets]


class BaseMultiViewWidget(html5.Ul):
	def __init__(self, widgetFactory: callable):
		super().__init__()
		self.widgetFactory = widgetFactory

	def unserialize(self, value):
		self.removeAllChildren()

		if not isinstance(value, list):
			return

		for entry in value:
			widget = self.widgetFactory()
			print(widget, entry)
			widget.unserialize(entry)
			self.appendChild(widget)


class BaseLanguageEditWidget(html5.Div):
	"""
	Class for encapsulating a bone for each language inside a container
	"""

	def __init__(self, widgetFactory: callable, languages: list):
		super().__init__("""
			<div [name]="widgets" class="vi-bone-widgets"></div>
			<div [name]="actions" class="vi-bone-actions"></div>
		""")

		assert languages, "This parameter must not be empty!"

		self.languages = languages
		self._languageWidgets = {}

		for lang in self.languages:
			assert not any([ch in lang for ch in "<>\"'/"]), "This is not a valid language identifier!"

			langBtn = Button(lang, callback=self.onLangBtnClick)
			langBtn.addClass("btn--lang", "btn--lang-" + lang)

			if lang == conf["defaultLanguage"]:
				langBtn.addClass("is-active")

			self.actions.appendChild(langBtn)

			langWidget = widgetFactory()

			if lang != conf["defaultLanguage"]:
				langWidget.hide()

			self.widgets.appendChild(langWidget)

			self._languageWidgets[lang] = (langBtn, langWidget)

	def onLangBtnClick(self, sender):
		for btn, widget in self._languageWidgets.values():
			if sender is btn:
				widget.show()
				btn.addClass("is-active")
			else:
				widget.hide()
				btn.removeClass("is-active")

	def unserialize(self, value):
		if not isinstance(value, dict):
			value = {}

		for lang, (_, widget) in self._languageWidgets.items():
			widget.unserialize(value.get(lang))

	def serialize(self):
		ret = {}
		for lang, (_, widget) in self._languageWidgets.items():
			ret[lang] = widget.serialize()

		return ret


class BaseBone(object):
	editWidgetFactory = BaseEditWidget
	viewWidgetFactory = BaseViewWidget

	"""
	Base "Catch-All" delegate for everything not handled separately.
	"""
	def __init__(self, moduleName, boneName, skelStructure):
		super().__init__()

		self.moduleName = moduleName
		self.boneName = boneName
		self.skelStructure = skelStructure

	def toEditWidget(self, value=None) -> html5.Widget:
		boneStructure = self.skelStructure[self.boneName]
		widgetFactory = self.editWidgetFactory

		if boneStructure.get("multiple"):
			multiWidgetFactory = widgetFactory  # have to make a separate "free" variable
			widgetFactory = lambda: BaseMultiEditWidget(multiWidgetFactory)

		if boneStructure.get("languages"):
			languageWidgetFactory = widgetFactory  # have to make a separate "free" variable
			widgetFactory = lambda: BaseLanguageEditWidget(languageWidgetFactory, boneStructure["languages"])

		widget = widgetFactory()
		widget.unserialize(value)
		return widget

	def toViewWidget(self, value=None):
		boneStructure = self.skelStructure[self.boneName]
		widgetFactory = self.viewWidgetFactory

		if boneStructure.get("multiple"):
			multiWidgetFactory = widgetFactory  # have to make a separate "free" variable
			widgetFactory = lambda: BaseMultiViewWidget(multiWidgetFactory)

		if boneStructure.get("languages"):
			languageWidgetFactory = widgetFactory   # have to make a separate "free" variable
			widgetFactory = lambda: BaseLanguageEditWidget(languageWidgetFactory, boneStructure["languages"])

		widget = widgetFactory()
		widget.unserialize(value)
		return widget

	'''
	def toString(self, value):
		return value or conf["emptyValue"]

	def toJSON(self, value):
		if isinstance(value, list):
			return [str(i) for i in value]

		return value
	'''


boneSelector.insert(0, lambda *args, **kwargs: True, BaseBone)
