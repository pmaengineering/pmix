SRC=./pmix/
TEST=./test/


.PHONY: style style_all lint lint_src lint_test codestyle codestyle_src \
codestyle_test docstyle docstyle_src docstyle_test test clean build pypi \
pypi_test pip_no_cache help


help:
	@echo " make style          # Check style of source with linters"
	@echo " make style_all      # Check style of source and test with linters"
	@echo ""
	@echo " make lint           # Run pylint on source and test code"
	@echo " make lint_src       # Run pylint on source code"
	@echo " make lint_test      # Run pylint on test code"
	@echo ""
	@echo " make codestyle      # Run pycodestyle on source and test code"
	@echo " make codestyle_src  # Run pycodestyle on source code"
	@echo " make codestyle_test # Run pycodestyle on test code"
	@echo ""
	@echo " make docstyle       # Run pycdocstyle on source and test code"
	@echo " make docstyle_src   # Run pycdocstyle on source code"
	@echo " make docstyle_test  # Run pycdocstyle on test code"
	@echo ""
	@echo " make test           # Run tests"
	@echo ""
	@echo " make build          # Create Python sdist and wheel"
	@echo " make clean          # Remove generated files from a build"
	@echo " make pypi_test      # Build and push to test PyPI"
	@echo " make pypi           # Build and push to PyPI"


# Batched Commands
style: lint_src codestyle_src docstyle_src
style_all: lint codestyle docstyle


# Pylint Only
PYLINT_BASE =python3 -m pylint --output-format=colorized --reports=n
lint: lint_src lint_test
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


# TESTING
test:
	python3 -m unittest discover -v


# PACKAGE MANAGEMENT
clean:
	rm -rf ./dist;
	rm -rf ./build;
	rm -rf ./*.egg-info
build: clean
	python3 setup.py sdist bdist_wheel
pypi: build
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*;
pypi_test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
