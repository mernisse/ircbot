PYSRC := $(shell find . -path ./deadModules -prune -o -name \*.py -print )

coverage:
	@coverage run -m unittest discover .
	@coverage html

clean:
	@echo CLEAN
	@rm -r html || true
	@rm -r latex || true

docs:
	@doxygen Doxyfile

lint: $(PYSRC)

$(PYSRC):
	@printf "FLAKE8 $@\n"
	@printf "===============\n"
	@flake8 --ignore=W191,E101,F401 $@ || true
	@printf "\n"

test:
	@python3 -m unittest discover .

.PHONY: lint $(PYSRC)
