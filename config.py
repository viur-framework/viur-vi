from event import EventDispatcher

conf = { "mainWindow": None,
	 "modules": { "_tasks" : { "handler" : "singleton", "name": "Tasks" } },
	 "tasks" : { "server" : [], "client" : [] },
	 "currentlanguage":"de",
	 "currentUser": None,
	 "initialHashEvent": EventDispatcher("initialHash")
	 }
