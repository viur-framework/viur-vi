#
# Makefile for ViUR/vi
#

PYJSBUILD=python `which pyjsbuild`
OUTPUT=../appengine/vi
DEPLOYOPTS=-S --enable-signatures -d
DEBUGOPTS=--disable-debug --dynamic-link -O --enable-speed -S

all: debug

version:
	./version.sh

$(OUTPUT): 
	mkdir -p $@

debug: $(OUTPUT) version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEBUGOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"

deploy: clean version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEPLOYOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"
	
clean: $(OUTPUT)
	rm -rf $(OUTPUT)/*

