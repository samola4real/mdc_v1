from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from apps.api.views.post_views import service_discovery_search


_legacy_views_path = Path(__file__).resolve().parent.parent / "views.py"
_legacy_spec = spec_from_file_location("apps.api._legacy_views", _legacy_views_path)
_legacy_views = module_from_spec(_legacy_spec)
_legacy_spec.loader.exec_module(_legacy_views)

health = _legacy_views.health
catalog_filters = _legacy_views.catalog_filters
catalog_search = _legacy_views.catalog_search
provider_publication = _legacy_views.provider_publication
provider_detail = _legacy_views.provider_detail
offering_detail = _legacy_views.offering_detail

