#
# Makefile for ViUR/vi
#

# Programs
PYJSBUILD	=	python `which pyjsbuild`
LESSC		=	lessc

# Variables
VI_CUSTOM	= 	../vi_customizing
OUTPUT		=	../appengine/vi
DEBUGOPTS	=	-S --enable-signatures -d
DEPLOYOPTS	=	--disable-debug --dynamic-link -O --enable-speed -S
LESSCOPTS	=	--include-path="$(VI_CUSTOM)/static:public/default"

# Targets

MAIN_CSS	=	public/vi.css
MAIN_LESS	= 	public/vi.less
CUSTOM_LESS	=	public/default/vi_custom.less \
				$(wildcard $(VI_CUSTOM)/static/vi_custom.less)

# Rules

all: debug

$(MAIN_CSS): $(MAIN_LESS) $(CUSTOM_LESS)
	$(LESSC) $(LESSCOPTS) $(MAIN_LESS) >$@

version:
	./version.sh

$(OUTPUT): 
	mkdir -p $@

debug: $(OUTPUT) $(MAIN_CSS) version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEBUGOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"

deploy: clean $(MAIN_CSS) version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEPLOYOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"
	
clean: $(OUTPUT)
	rm -rf $(OUTPUT)/*
	rm -f $(CSSFILES)

