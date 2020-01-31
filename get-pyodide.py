#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, zipfile, urllib.request

# Install latest built of Pyodide...
zipname = "pyodide_2019-09-24-bin.zip"

sys.stdout.write("Downloading Pyodide...")
sys.stdout.flush()
urllib.request.urlretrieve("https://github.com/mausbrand/pyodide/releases/download/2019-09-24/pyodide_2019-09-24-bin.zip", zipname)
print("Done")

sys.stdout.write("Extracting Pyodide...")
sys.stdout.flush()

zip = zipfile.ZipFile(zipname, "r")
zip.extractall()
zip.close()

os.remove(zipname)
print("Done")

