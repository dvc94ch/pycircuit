EXAMPLES=joule_thief small sallen_key

build:
	$(foreach example, $(EXAMPLES), cd $(CURDIR)/$(example) && make build;)

view:
	$(foreach example, $(EXAMPLES), sh -c 'cd $(CURDIR)/$(example) && make view &';)

kicad:
	$(foreach example, $(EXAMPLES), cd $(CURDIR)/$(example) && make kicad;)

clean:
	$(foreach example, $(EXAMPLES), cd $(CURDIR)/$(example) && make clean;)

.PHONY: build view kicad clean
