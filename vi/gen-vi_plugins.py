#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, shutil, importlib

projectfolder = os.path.join("..","..")

target = os.path.join(projectfolder,"vi_plugins")
if os.path.exists(target):
	print("folder exists, we do nothing")
else:
	os.mkdir(target)
	os.mkdir( os.path.join(target,"custom") )
	os.mkdir( os.path.join(target,"custom","static") )
	os.mkdir( os.path.join(target,"custom","static","embedsvg") )
	os.mkdir( os.path.join(target,"custom","static","images") )
	with open( os.path.join( target, "vi_custom.less" ), "w" ) as f:pass  # create init
	with open( os.path.join(target,"__init__.py"), "w" ) as f: pass #create init
	shutil.copyfile("gen-files-json.py",os.path.join(target,"gen-files-json.py")) #copy gen files script
	os.system("cd %s && python3 gen-files-json.py" % target)
	print("vi_plugins initialized")






