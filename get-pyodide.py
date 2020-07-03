#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, requests

VERSION = "0.15.0"
CDN = "https://pyodide-cdn2.iodide.io"
URL = "{CDN}/v{VERSION}/full/{file}"
DIR = "pyodide"

if not os.path.isdir(DIR):
	sys.stdout.write(f"Creating {DIR}/...")
	sys.stdout.flush()

	os.mkdir(DIR)
	print("Done")

print(f"Installing Pyodide v{VERSION}:")

for file in [
	"console.html",
	"distlib.data",
	"distlib.js",
	"micropip.data",
	"micropip.js",
	"pyodide.asm.data",
	"pyodide.asm.data.js",
	"pyodide.asm.js",
	"pyodide.asm.wasm",
	"pyodide.js",
	"renderedhtml.css",
	"setuptools.data",
	"setuptools.js"
]:
	url = URL.format(file=file, CDN=CDN, VERSION=VERSION)
	file = os.path.join(DIR, file)

	sys.stdout.write(f">>> {url}...")
	sys.stdout.flush()

	r = requests.get(url, stream=True)
	with open(file, 'wb') as f:
		for chunk in r.iter_content(2 * 1024):
			f.write(chunk)

	print("Done")

print(f"Done installing Pyodide v{VERSION}!")

# Patch console.html to use pyodide.js
file = os.path.join(DIR, "console.html")
sys.stdout.write(f"Patching {file}...")
sys.stdout.flush()

with open(file, "r") as f:
	console_html = f.read()

with open(file, "w") as f:
	f.write(console_html.replace(
		"""<script src="./pyodide_dev.js"></script>""",
		"""<script>window.languagePluginUrl = "./";</script>"""
		"""<script src="./pyodide.js"></script>"""
	))

print("Done")

# Write a minimal packages.json with micropip, setuptools and distlibs pre-installed.
file = os.path.join(DIR, "packages.json")
sys.stdout.write(f"Patching {file}...")
sys.stdout.flush()

with open(file, "w") as f:
	f.write(json.dumps({
		"dependencies": {
			"micropip": ["distlib"],
			"distlib": [],
			"setuptools": []
		},
		"import_name_to_package_name": {
			"distlib": "distlib",
			"setuptools":"setuptools",
			"micropip": "micropip"
		}
	}))

print("Done")
