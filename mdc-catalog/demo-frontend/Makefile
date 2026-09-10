# =============================================================================
# MaaSAI · Frontend — Docker buildx helpers
# -----------------------------------------------------------------------------
# Common targets:
#   make build                # local image, current arch
#   make run                  # docker compose up
#   make push                 # multi-arch (amd64+arm64) push to $(REGISTRY)
#   make release VERSION=1.2.3
#   make scan                 # vulnerability scan (needs trivy)
#   make size                 # show image size
# =============================================================================

REGISTRY      ?= ghcr.io/maasai
IMAGE_NAME    ?= maasai-frontend
VERSION       ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
TAG           ?= $(VERSION)
PLATFORMS     ?= linux/amd64,linux/arm64
BUILDER       ?= maasai-builder
FULL_IMAGE    := $(REGISTRY)/$(IMAGE_NAME)

.PHONY: help
help:
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# -----------------------------------------------------------------------------
# Buildx setup — creates an isolated buildx builder if missing.
# -----------------------------------------------------------------------------
.PHONY: builder
builder: ## Create/select a multi-arch buildx builder
	@if ! docker buildx inspect $(BUILDER) >/dev/null 2>&1; then \
		echo "→ Creating buildx builder '$(BUILDER)'..."; \
		docker buildx create --name $(BUILDER) --driver docker-container --bootstrap; \
	fi
	@docker buildx use $(BUILDER)

# -----------------------------------------------------------------------------
# Local build (single arch, loaded into local docker daemon).
# -----------------------------------------------------------------------------
.PHONY: build
build: ## Build for current arch, load into local docker
	docker buildx build \
		--load \
		--tag $(FULL_IMAGE):$(TAG) \
		--tag $(FULL_IMAGE):latest \
		--cache-from type=local,src=/tmp/.buildx-cache-$(IMAGE_NAME) \
		--cache-to   type=local,dest=/tmp/.buildx-cache-$(IMAGE_NAME),mode=max \
		.

# -----------------------------------------------------------------------------
# Multi-arch build & push to the registry. Requires `docker login $(REGISTRY)`.
# -----------------------------------------------------------------------------
.PHONY: push
push: builder ## Build & push multi-arch (amd64+arm64) to $(REGISTRY)
	docker buildx build \
		--platform $(PLATFORMS) \
		--push \
		--provenance=true \
		--sbom=true \
		--tag $(FULL_IMAGE):$(TAG) \
		--tag $(FULL_IMAGE):latest \
		--cache-from type=registry,ref=$(FULL_IMAGE):buildcache \
		--cache-to   type=registry,ref=$(FULL_IMAGE):buildcache,mode=max \
		--label org.opencontainers.image.title="MaaSAI Frontend" \
		--label org.opencontainers.image.source="https://github.com/MaaSAI/template-frontend" \
		--label org.opencontainers.image.version="$(VERSION)" \
		--label org.opencontainers.image.revision="$(shell git rev-parse HEAD 2>/dev/null || echo unknown)" \
		--label org.opencontainers.image.created="$(shell date -u +%Y-%m-%dT%H:%M:%SZ)" \
		.

# -----------------------------------------------------------------------------
# Tagged release — push and also create the immutable major/minor tags.
# Usage: make release VERSION=1.2.3
# -----------------------------------------------------------------------------
.PHONY: release
release: builder ## Push immutable + major.minor + latest tags
	@if [ "$(VERSION)" = "dev" ]; then \
		echo "✗ Refusing to release tag 'dev'. Pass VERSION=x.y.z"; exit 1; \
	fi
	$(eval MAJOR := $(shell echo $(VERSION) | cut -d. -f1))
	$(eval MAJOR_MINOR := $(shell echo $(VERSION) | cut -d. -f1-2))
	docker buildx build \
		--platform $(PLATFORMS) \
		--push \
		--provenance=true \
		--sbom=true \
		--tag $(FULL_IMAGE):$(VERSION) \
		--tag $(FULL_IMAGE):$(MAJOR_MINOR) \
		--tag $(FULL_IMAGE):$(MAJOR) \
		--tag $(FULL_IMAGE):latest \
		--cache-from type=registry,ref=$(FULL_IMAGE):buildcache \
		--cache-to   type=registry,ref=$(FULL_IMAGE):buildcache,mode=max \
		.

# -----------------------------------------------------------------------------
# Local lifecycle via docker compose.
# -----------------------------------------------------------------------------
.PHONY: run
run: ## Start with docker compose
	docker compose up --build -d
	@echo "→ http://localhost:3000"

.PHONY: stop
stop: ## Stop docker compose
	docker compose down

.PHONY: logs
logs: ## Tail logs
	docker compose logs -f frontend

# -----------------------------------------------------------------------------
# Quality gates.
# -----------------------------------------------------------------------------
.PHONY: scan
scan: ## Trivy vulnerability scan (requires trivy installed)
	@command -v trivy >/dev/null 2>&1 || { echo "trivy not installed — https://aquasecurity.github.io/trivy"; exit 1; }
	trivy image --severity HIGH,CRITICAL $(FULL_IMAGE):$(TAG)

.PHONY: size
size: ## Report final image size
	@docker image inspect $(FULL_IMAGE):$(TAG) --format='Size: {{.Size}} bytes ({{.Size}}B)' 2>/dev/null \
		|| echo "Image $(FULL_IMAGE):$(TAG) not found locally."

.PHONY: clean
clean: ## Remove local images and buildx cache
	-docker image rm $(FULL_IMAGE):$(TAG) $(FULL_IMAGE):latest 2>/dev/null
	-rm -rf /tmp/.buildx-cache-$(IMAGE_NAME)

# -----------------------------------------------------------------------------
# Quick sanity checks.
# -----------------------------------------------------------------------------
.PHONY: version
version: ## Show the version that will be used
	@echo "REGISTRY   = $(REGISTRY)"
	@echo "IMAGE      = $(FULL_IMAGE)"
	@echo "TAG        = $(TAG)"
	@echo "VERSION    = $(VERSION)"
	@echo "PLATFORMS  = $(PLATFORMS)"
