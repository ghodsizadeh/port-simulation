# Check if Poetry is installed
POETRY := $(shell command -v poetry 2> /dev/null)

# Set the virtual environment name
VENV_NAME := .venv

# Install dependencies
install:
ifdef POETRY
	@poetry install
else
	@python3 -m venv $(VENV_NAME)
	@source $(VENV_NAME)/bin/activate && pip install -r requirements.txt
endif

# Run the script
simulate:
ifdef POETRY
	@poetry run python maersk_task
else
	@source $(VENV_NAME)/bin/activate && python -m maersk_task
endif