from flare.event import EventDispatcher
from flare.i18n import translate

vi_conf = {
	# Vi version number
	"vi.version": (3, 0, 0),
	# ViUR server version number
	"core.version": None,
	"core.version.min": (3, 0, 0),  # minimal core Version
	"core.version.max": (3, 1, 0),  # max recomended version core Version, musst be less than!
	# Appendix to version
	"vi.version.appendix": "dev",

	# ViUR core name
	"vi.viur": "ViUR-core",

	# ViUR vi name
	"vi.name": "ViUR-vi",

	# Title delimiter
	"vi.title.delimiter": " - ",

	# Which access rights are required to open the Vi?
	"vi.access.rights": ["admin", "root"],

	# Context access variable prefix
	"vi.context.prefix": "",

	# Context action title fields
	"vi.context.title.bones": ["name"],

	# Global holder to main configuration taken from the server
	"mainConfig": None,

	# Global holder to main admin window
	"mainWindow": None,

	# Exposed server configuration
	"server": {},

	# Modules list
	"modules": {"_tasks": {"handler": "singleton", "name": "Tasks"}},

	# Callable tasks
	"tasks": {"server": [], "client": []},

	# Language settings
	"currentLanguage": "de",
	"defaultLanguage": "de",

	# Global holder to the currently logged-in user
	"currentUser": None,

	# A value displayed as "empty value"
	"emptyValue": translate("-"),

	# Event dispatcher for initial startup Hash
	"initialHashEvent": EventDispatcher("initialHash"),

	# Actions in the top level bar
	"toplevelactions": ["scripter", "log", "tasks", "userstate", "logout"],

	# Number of rows to fetch in list widgets
	"batchSize": 30,

	# Show bone names instead of description
	"showBoneNames": False,

	# Globally enable/disable dataset preview in lists
	"internalPreview": True,

	# Fallback default preview path template (if set None, adminInfo.preview only takes place)
	"defaultPreview": None,  # "/{{module}}/view/{{key}}"

	# Max number of entries to show in multiple Bones
	"maxMultiBoneEntries": 5,

	# Cached selector widgets on relationalBones for re-use
	"selectors": {},

	"updateParams": None,

	"cacheObj": {},
	"indexeddb": None,
	"logAmount": 50,
	"flare.icon.svg.embedding.path": "public/svgs",
	"modulepipe": False
}


def updateConf(_conf):
	vi_conf.update(_conf)
	return vi_conf


def getConf():
	from flare.config import conf
	return conf


conf = getConf()
