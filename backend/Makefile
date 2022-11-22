ifeq (upgrade,$(firstword $(MAKECMDGOALS)))
  UPGRADE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(UPGRADE_ARGS):;@:)
endif

dev:
	python -B -u manage.py runserver

# cov:
# 	coverage run --rcfile=coverage.toml -m pytest
# 	coverage report --rcfile=coverage.toml

# hcov:
# 	coverage run --rcfile=coverage.toml -m pytest
# 	coverage html --rcfile=coverage.toml

# rep:
# 	coverage report --rcfile=coverage.toml

# -- Dependencies Management --

pip:
	python -m pip install --no-cache-dir --upgrade pip

upgrade:
	pip install --no-cache-dir --upgrade --upgrade-strategy eager $(UPGRADE_ARGS)

install-dev:
	pip install --no-cache-dir -r requirements/dev.txt

install-prod:
	pip install --no-cache-dir -r requirements/prod.txt

# --
