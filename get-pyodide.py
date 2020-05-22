#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, tarfile, urllib.request

VERSION = "0.14.3"
URL = "https://github.com/iodide-project/pyodide/releases/download/{VERSION}/pyodide-build-{VERSION}.tar.bz2"

download = VERSION + ".tar.bz2"

sys.stdout.write("Downloading Pyodide...")
sys.stdout.flush()
urllib.request.urlretrieve(URL.format(VERSION=VERSION), download)
print("Done")

print("Extracting Pyodide...")

tar = tarfile.open(download, "r")

extracted = []
for member in tar.getmembers():
	if not (member.name.startswith("pyodide.")
			or member.name.startswith("micropip.")
			or member.name.startswith("distlib.")
			or member.name in ["console.html", "renderedhtml.css"]
		):
		continue

	print(">>> %s" % member.name)
	tar.extract(member, "pyodide")
	extracted.append(member.name)

tar.close()

if not extracted:
	print("This doesn't look like a Pyodide build package!")
	sys.exit(1)

# Patch console.html to use pyodide.js
with open("pyodide/console.html", "r") as f:
	console_html = f.read()

with open("pyodide/console.html", "w") as f:
	f.write(console_html.replace(
		"""<script src="./pyodide_dev.js"></script>""",
		"""<script>window.languagePluginUrl = "./";</script>"""
		"""<script src="./pyodide.js"></script>"""
	))

# Write a minimal packages.json with micropip and distlibs pre-installed.
f = open("pyodide/packages.json", "w")
f.write("""{"dependencies": {"micropip": ["distlib"], "distlib": []}, "import_name_to_package_name": {"distlib": "distlib", "micropip": "micropip"}}""")
f.close()

os.remove(download)
print("Done")
