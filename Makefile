#
# Makefile for ViUR/vi
#

# Programs
PYJSBUILD	=	python `which pyjsbuild`
LESSC		=	lessc

# Variables
OUTPUT		=	../appengine/vi
DEBUGOPTS	=	-S --enable-signatures -d
DEPLOYOPTS	=	--disable-debug --dynamic-link -O --enable-speed -S

# Targets

LESSFILES	= 	public/vi.less \
				public/vi_custom.less

CSSFILES	=	$(LESSFILES:.less=.css)

# Rules

all: debug

%.css: %.less
	$(LESSC) $< >$@

css: $(CSSFILES)

version:
	./version.sh

$(OUTPUT): 
	mkdir -p $@

debug: $(OUTPUT) css version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEBUGOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"

deploy: clean css version
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEPLOYOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"
	
clean: $(OUTPUT)
	rm -rf $(OUTPUT)/*

