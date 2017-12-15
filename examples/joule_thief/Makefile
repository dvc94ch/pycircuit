PYCIRCUIT=../..

build:
	python3 joule_thief.py

place:
	- rm -f joule_thief.out.pcpl
	python3 $(PYCIRCUIT)/placer/place.py joule_thief.pcpl

route:
	- rm -f joule_thief.out.pcrt
	python3 $(PYCIRCUIT)/router/router.py joule_thief.pcrt

view:
	node $(PYCIRCUIT)/viewer/app.js net.dot.svg pcb.svg

all:
	- make build
	make place
	- make build
	make route
	make build

clean:
	rm -f *.dot *.svg *.pcpl *.pcrt *.pro *.kicad_pcb

.PHONY: build route view all clean
