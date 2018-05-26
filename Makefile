clean:
	@echo CLEAN
	@rm -r html latex

docs:
	@doxygen Doxyfile

test:
	@python3 -m unittest discover .
