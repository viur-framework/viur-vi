deploy:
	python3 vi/flare/scripts/flare.py -s `pwd`/vi -t ../../deploy/vi

watch:
	python3 vi/flare/scripts/watch.py `pwd`/vi ../../deploy/vi -n vi

.PHONY: deploy
