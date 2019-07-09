#-*- coding: utf-8 -*-
from event import EventDispatcher
from i18n import translate
from logics import Interpreter

conf = {
	# Vi version number
	"vi.version": (2, 5, 0),

	# Appendix to version
	"vi.version.appendix": "",

	# Vi server name
	"vi.viur": "ViUR",

	# Vi name
	"vi.name": "ViUR Visual Interface",

	# Title delimiter
	"vi.title.delimiter": " - ",

	# Which access rights are required to open the Vi?
	"vi.access.rights": ["admin", "root"],

	# Global holder to main configuration taken from the server
	"mainConfig": None,

	# Global holder to main admin window
	"mainWindow": None,

	# Exposed server configuration
	"server": {},

	# ViUR server version number
	"server.version": None,

	# Startup parameters
	"startupHash": eval("window.top.location.hash"),

	# Modules list
	"modules": {"_tasks": {"handler": "singleton", "name": "Tasks"}},

	# Callable tasks
	"tasks": {"server": [], "client": []},

	# Language
	"currentlanguage": "de",

	# Global holder to the currently logged-in user
	"currentUser": None,

	# A value displayed as "empty value"
	"empty_value": translate("-"),

	# Event dispatcher for initial startup Hash
	"initialHashEvent": EventDispatcher("initialHash"),

	# Actions in the top level bar
    "toplevelactions": ["tasks", "userstate", "logout"],

	# Number of rows to fetch in list widgets
	"batchSize": 20,

	# Show bone names instead of description
	"showBoneNames": False,

	# Globally enable/disable dataset preview in lists
	"internalPreview": True,

	# Max number of entries to show in multiple Bones
	"maxMultiBoneEntries": 5,

	# Global ViUR Logics interpreter instance
	"logics": Interpreter(),

	"updateParams": None
}
