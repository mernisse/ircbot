docs:
	@doxygen Doxyfile

test:
	@python3 -m unittest discover .
