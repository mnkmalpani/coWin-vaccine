# setup variables, which are used in this makefile
#VENV_DIR = .ve
#VENV_RUN = . $(VENV_DIR)/bin/activate

setup_standard_version:
	# setting up the standard-version package, which is used to version releases and the CHANGELOG.md
	./bin/setup-standard-version.sh