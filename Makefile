.PHONY: clean-pyc test clean-build
TEST_PATH=test

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

test: clean-pyc build-test start-nextcloud-test-instance
	tox

black:
	black deck/
	black tests/

create-volumes:
	docker volume create nextcloud-data
	docker volume create nextcloud-config

build-test-image:
	docker build -t nextcloud-test .

build-test: create-volumes build-test-image

build:
	poetry build

deploy: build
	poetry publish

publish: deploy

start-nextcloud-test-instance:
	./bin/start-nextcloud.sh
