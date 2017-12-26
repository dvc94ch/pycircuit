PYCIRCUIT = ../..

build:
	python3 build.py

view:
	node $(PYCIRCUIT)/viewer/app.js 3001 net.dot.svg pcb.svg

kicad:
	pcbnew *.kicad_pcb &>/dev/null &

clean:
	rm -f *.net *.hash *.dot *.svg *.place *.route *.pro *.kicad_pcb

.PHONY: build view kicad clean
