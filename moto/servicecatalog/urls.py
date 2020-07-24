from __future__ import unicode_literals
from .responses import SimpleServiceCatalogResponse

url_bases = ["https?://servicecatalog.(.+).amazonaws.com", "https?://servicecatalog.(.+).amazonaws.com.cn"]

url_paths = {"{0}/$": SimpleServiceCatalogResponse.dispatch}
