.PHONY: virtualenv ipython lint fmt

virtualenv:
	@python -m venv .env

ipython:
	@.env/bin/ipython

lint:
	@.env/bin/pflake8 __main__.py app.py config.py dados.py utils.py

fmt:
	@.env/bin/black -l 79 __main__.py app.py config.py dados.py utils.py