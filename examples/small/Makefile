PYCIRCUIT=../..

build:
	python3 small.py

place:
	- rm -f small.out.pcpl
	python3 $(PYCIRCUIT)/placer/place.py small.pcpl

route:
	- rm -f small.out.pcrt
	python3 $(PYCIRCUIT)/router/router.py small.pcrt

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
