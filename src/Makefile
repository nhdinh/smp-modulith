# order of libs is meaningful. First, we install libs without internal dependencies that other libs depend on.
libs := foundation auctions shipping db_infrastructure web_app_models auctions_infrastructure shipping_infrastructure customer_relationship payments processes product_catalog_infrastructure product_catalog main web_app

define install_dev
	pip install -e $(1)

endef

.PHONY: dev
dev:
	pip install --force --upgrade pip pip-tools
	pip install --force --upgrade -r requirements.txt -r requirements-dev.txt
	$(foreach lib,$(libs),$(call install_dev,$(lib)))

.PHONY: freeze-deps
freeze-deps:
	#pip install pip-tools==5.3.1
	pip install --force --upgrade pip pip-tools
	pip-compile --upgrade --output-file=requirements.txt $(foreach lib,$(libs), ./$(lib)/requirements.txt ./$(lib)/requirements-dev.txt)
