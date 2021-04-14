deploy:
	python3 vi/flare/scripts/flare.py -s ../../sources/viur-vi/vi -t ../../deploy/vi

watch:
	python3 vi/flare/scripts/watch.py ../../sources/viur-vi/vi ../../deploy/vi -n vi

.PHONY: deploy
