EXAMPLES=joule_thief small sallen_key

define foreach-example
	$(foreach example, $(EXAMPLES), cd $(CURDIR)/$(example) && $(1);)
endef

build:
	cd $(CURDIR)/$(EXAMPLE) && python3 build.py

build-all:
	$(call foreach-example, python3 build.py)

view-all:
	$(call foreach-example, sh -c 'node ../../viewer/app.js &')

kicad-all:
	$(call foreach-example, pcbnew *.kicad_pcb &)

clean-all:
	$(call foreach-example, rm -rf build)

.PHONY: build-all view-all kicad-all clean-all
