#
# Makefile for ViUR/vi
#

# Programs
PYJSBUILD	=	pyjsbuild
LESSC		=	lessc

# Variables
VI_CUSTOM	= 	../vi_customizing
OUTPUT		=	$(wildcard ../appengine/)$(wildcard ../deploy/)vi
DEFAULTOPTS	=	-P Mozilla
DEBUGOPTS	=	$(DEFAULTOPTS) -d
DEPLOYOPTS	=	$(DEFAULTOPTS) -S --dynamic-link --disable-debug
LESSCOPTS	=	--include-path="$(VI_CUSTOM)/static:public/default"

# Targets

DEFAULT_CSS	=	public/default/vi.css

MAIN_CSS	=	public/css/style.css
MAIN_LESS	= 	sources/less/vi.less

CUSTOM_LESS	=	$(wildcard $(VI_CUSTOM)/static/vi_custom.less)

# Rules

all: debug

setup:
	if [ ! -f $(MAIN_CSS) ]; then cp $(DEFAULT_CSS) $(MAIN_CSS); fi

defaultcss: $(MAIN_CSS)
	cp $(MAIN_CSS) $(DEFAULT_CSS)

$(MAIN_CSS): $(MAIN_LESS) $(MORE_LESS) $(CUSTOM_LESS)
	$(LESSC) $(LESSCOPTS) $(MAIN_LESS) >$@

copyfiles:
	if [ -x $(VI_CUSTOM)/static ]; then \
		cp -rv $(VI_CUSTOM)/static/* $(OUTPUT); \
	fi

version:
	./version.sh

$(OUTPUT):
	mkdir -p $@

watch: $(OUTPUT) $(MAIN_CSS) version copyfiles
	$(PYJSBUILD) -o $(OUTPUT) \
        $(DEBUGOPTS) \
        --bootloader=bootstrap_progress.js \
        -I ./$(VI_CUSTOM) \
		--enable-rebuilds \
	        main.py

debug: $(OUTPUT) $(MAIN_CSS) version copyfiles
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEBUGOPTS) \
		--bootloader=bootstrap_progress.js \
		-I ./$(VI_CUSTOM) \
				main.py
	@echo "--- FINISHED DEBUG BUILD ---"

deploy: $(MAIN_CSS) version copyfiles
	@echo "--- STARTING DEPLOY BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEPLOYOPTS) \
		--bootloader=bootstrap_progress.js \
		-I ./$(VI_CUSTOM) \
				main.py
	@echo "--- FINISHED DEPLOY BUILD ---"

tarfile: deploy
	tar cvf "vi_`date +'%Y-%m-%d'`.tar" vi

clean: $(OUTPUT)
	rm -rf $(MAIN_CSS) $(OUTPUT)/*
