deploy:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi

watch:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -n vi -w

.PHONY: deploy
