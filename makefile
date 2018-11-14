SRC=./pmix/
TEST=./test/

.PHONY: lint tags ltags test all lint_all codestyle docstyle lint_src \
lint_test doctest linters_all  remove-previous-build build  pypi-push-test \
pypi-push install upgrade uninstall reinstall backup-trunk-develop \
push-latest-to-trunk pypi-push-only

# Batched Commands
all: linters_all test_all
lint: lint_src codestyle_src docstyle_src
linters_all: docstyle codestyle lint_all

# Pylint Only
PYLINT_BASE =python3 -m pylint --output-format=colorized --reports=n
lint_all: lint_src lint_test
lint_src:
	${PYLINT_BASE} ${SRC}
lint_test:
	${PYLINT_BASE} ${TEST}

# PyCodeStyle Only
PYCODESTYLE_BASE=python3 -m pycodestyle
codestyle: codestyle_src codestyle_test
codestyle_src:
	${PYCODESTYLE_BASE} ${SRC}
codestyle_test:
	 ${PYCODESTYLE_BASE} ${TEST}

# PyDocStyle Only
PYDOCSTYLE_BASE=python3 -m pydocstyle
docstyle: docstyle_src docstyle_test
docstyle_src:
	${PYDOCSTYLE_BASE} ${SRC}
docstyle_test:
	${PYDOCSTYLE_BASE} ${TEST}

# Text Editor Commands
TAGS_BASE=ctags -R --python-kinds=-i
tags:
	${TAGS_BASE} .
ltags:
	${TAGS_BASE} ${SRC}
codetest:
	${CODE_TEST}

# PYDOCSTYLE
doc:
	${DOC_SRC

# TESTING
test:
	python3 -m unittest discover -v
testdoc:
	python3 -m test.test --doctests-only
test_all: test testdoc

# Package Management
install:
	pip install -r requirements-unlocked.txt --no-cache-dir; \
	pip freeze > requirements.txt
remove-previous-build:
	rm -rf ./dist;
	rm -rf ./build;
	rm -rf ./*.egg-info
build: remove-previous-build
	python3 setup.py sdist bdist_wheel
pypi-push-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pypi-push-only:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*; \
	make remove-previous-build
pypi-push:
	make pypi-push-only; \
	make push-latest-to-trunk
