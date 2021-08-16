deploy:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi

min:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -m -n vi

zip:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -m -c -z -n vi

watch:
	python3 vi/flare/tools/flare.py -s `pwd`/vi -t ../../deploy/vi -n vi -w

.PHONY: deploy
