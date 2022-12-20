ifeq (upgrade,$(firstword $(MAKECMDGOALS)))
  UPGRADE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(UPGRADE_ARGS):;@:)
endif

# -- Creating Environment --
venv:
	python3.11 -m venv venv

# -- Running Code --

dev:
	python -B -u manage.py runserver

initmigrations:
	python -B -u manage.py initmigrations

# -- Coverage --

# cov:
# 	coverage run --rcfile=coverage.toml -m pytest
# 	coverage report --rcfile=coverage.toml

# hcov:
# 	coverage run --rcfile=coverage.toml -m pytest
# 	coverage html --rcfile=coverage.toml

# -- Dependencies Management --

pip:
	python -m pip install --no-cache-dir --upgrade pip

out:
	pip list --outdated

idev:
	pip install --no-cache-dir -r requirements/dev.txt

iprod:
	pip install --no-cache-dir -r requirements/prod.txt

upgrade:
	pip install --no-cache-dir --upgrade --upgrade-strategy eager $(UPGRADE_ARGS)

# --
