PY?=python
PIP?=pip

.PHONY: test install

install:
	$(PIP) install --no-cache-dir -r requirements.txt

test: install
	$(PY) -m pytest -q


