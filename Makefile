.PHONY: clean-pyc test clean-build
TEST_PATH=tests

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info


clean: clean-pyc clean-build

isort:
	sh -c "isort --skip-glob=.tox --recursive . "

lint:
	flake8 --exclude=.tox

test: clean-pyc
	tox

black:
	black deck/
	black test/

create-volumes:
	docker volume create nextcloud-data
	docker volume create nextcloud-config

build-test-image:
	docker build -t nextcloud-test .
