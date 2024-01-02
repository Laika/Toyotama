.PHONY: build
build:
	poetry build

.PHONY: set-credentials-testpypi
set-credentials-testpypi:
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	@read -p "Username [testpypi]: " TESTPYPI_USERNAME; \
	read -p "Password [testpypi]: " TESTPYPI_PASSWORD; \
	poetry config http-basic.testpypi $$TESTPYPI_USERNAME $$TESTPYPI_PASSWORD

.PHONY: publish-testpypi
publish-testpypi:
	poetry publish \
		-r testpypi

.PHONY: set-credentials-pypi
set-credentials-pypi:
	poetry config repositories.pypi https://upload.pypi.org/legacy/
	@read -p "Username [pypi]: " PYPI_USERNAME; \
	read -p "Password [pypi]: " PYPI_PASSWORD; \
	poetry config http-basic.pypi $$PYPI_USERNAME $$PYPI_PASSWORD


.PHONY: publish
publish:
	poetry publish

