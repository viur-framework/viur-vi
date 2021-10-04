deploy:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -z -m -c -n vi

develop:
	@echo "--- Please use 'make debug' for this ---"

debug:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -n vi

min:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -m -n vi

pyc:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -c -z -n vi

zip:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -z -n vi

watch:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -n vi -w

.PHONY: deploy
