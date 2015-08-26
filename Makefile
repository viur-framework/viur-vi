#
# Makefile for ViUR/vi
#

# Programs
PYJSBUILD	=	pyjsbuild
LESSC		=	lessc

# Variables
VI_CUSTOM	= 	../vi_customizing
OUTPUT		=	$(wildcard ../appengine/)vi
DEBUGOPTS	=	-S --enable-signatures -d
DEPLOYOPTS	=	--disable-debug --dynamic-link -O --enable-speed -S
LESSCOPTS	=	--include-path="$(VI_CUSTOM)/static:public/default"

# Targets

DEFAULT_CSS	=	public/default/vi.css

MAIN_CSS	=	public/vi.css
MAIN_LESS	= 	public/vi.less
CUSTOM_LESS	=	public/default/vi_custom.less \
				$(wildcard $(VI_CUSTOM)/static/vi_custom.less)

# Rules

all: debug

setup:
	if [ ! -f $(MAIN_CSS) ]; then cp $(DEFAULT_CSS) $(MAIN_CSS); fi
	if [ ! -x vi_plugins -a -x $(VI_CUSTOM)/vi_plugins ]; then \
		ln -s $(VI_CUSTOM)/vi_plugins; fi

defaultcss: $(MAIN_CSS)
	cp $(MAIN_CSS) $(DEFAULT_CSS)

$(MAIN_CSS): $(MAIN_LESS) $(CUSTOM_LESS)
	$(LESSC) $(LESSCOPTS) $(MAIN_LESS) >$@

copyfiles:
	if [ -x $(VI_CUSTOM)/static ]; then \
		cp -rv $(VI_CUSTOM)/static/* $(OUTPUT); \
	fi

version:
	./version.sh

$(OUTPUT): 
	mkdir -p $@

debug: $(OUTPUT) $(MAIN_CSS) version copyfiles
	@echo "--- STARTING DEBUG BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEBUGOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEBUG BUILD ---"

deploy: $(MAIN_CSS) version copyfiles
	@echo "--- STARTING DEPLOY BUILD ---"
	$(PYJSBUILD) -o $(OUTPUT) \
		$(DEPLOYOPTS) \
		--bootloader=bootstrap_progress.js \
				admin.py
	@echo "--- FINISHED DEPLOY BUILD ---"

tarfile: deploy
	tar cvf "vi_`date +'%Y-%m-%d'`.tar" vi
	
clean: $(OUTPUT)
	rm -rf $(OUTPUT)/*

