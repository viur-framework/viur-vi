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
	if not member.name.startswith("pyodide."):
		continue

	print(">>> %s" % member.name)
	tar.extract(member, "pyodide")
	extracted.append(member.name)

tar.close()

if not extracted:
	print("This doesn't look like a Pyodide build package!")
	sys.exit(1)

# Write an empty packages.json
f = open("pyodide/packages.json", "w")
f.write("""{"dependencies": {}, "import_name_to_package_name": {}}""")
f.close()

os.remove(download)
print("Done")
