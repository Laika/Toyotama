.PHONY: build
build:
	poetry build


.PHONY: publish-testpypi
publish-testpypi:
	poetry publish \
		-r testpypi

.PHONY: publish
publish:
	poetry publish

