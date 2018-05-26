clean:
	@echo CLEAN
	@rm -r html || true
	@rm -r latex || true

docs:
	@doxygen Doxyfile

test:
	@python3 -m unittest discover .
