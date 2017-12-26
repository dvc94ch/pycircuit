PYCIRCUIT = ../..

build:
	python3 build.py

view:
	node $(PYCIRCUIT)/viewer/app.js net.dot.svg pcb.svg

clean:
	rm -f *.net *.hash *.dot *.svg *.place *.route *.pro *.kicad_pcb

.PHONY: build view clean
