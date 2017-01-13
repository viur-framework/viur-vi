#-*- coding: utf-8 -*-
from event import EventDispatcher
from i18n import translate

conf = {
	"vi.version": (2, 0, 1),
	"vi.version.appendix": "",
	"mainConfig": None,
	"mainWindow": None,
	"server": {},
	"server.version": None,
	"modules": {"_tasks": {"handler": "singleton", "name": "Tasks"}},
	"tasks": {"server": [], "client": []},
	"currentlanguage":"de",
	"currentUser": None,
	"empty_value": translate("-"),
	"initialHashEvent": EventDispatcher("initialHash"),
    "toplevelactions": ["tasks", "userstate", "logout"],
	"batchSize": 20,
	"showBoneNames": False,
	"internalPreview": True,
	"maxMultiBoneEntries": 5
}
