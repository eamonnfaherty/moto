from __future__ import unicode_literals
import json

from moto.core.responses import BaseResponse
from .models import servicecatalog_backends


class SimpleServiceCatalogResponse(BaseResponse):
    @property
    def servicecatalog_backend(self):
        return servicecatalog_backends[self.region]

    @property
    def request_params(self):
        try:
            return json.loads(self.body)
        except ValueError:
            return {}

    def create_portfolio(self):
        accept_language = self._get_param('AcceptLanguage')
        display_name = self._get_param('DisplayName')
        description = self._get_param('Description')
        provide_name = self._get_param('ProviderName')
        tags = self._get_param('Tags')
        idempotency_token = self._get_param('IdempotencyToken')

        result = self.servicecatalog_backend.create_portfolio(
            accept_language, display_name, description, provide_name, tags, idempotency_token
        )

        response = result
        return json.dumps(response)

    def list_portfolios(self):
        accept_language = self._get_param('AcceptLanguage')
        page_token = self._get_param('PageToken')
        page_size = self._get_param('PageSize')

        result = self.servicecatalog_backend.list_portfolios(
            accept_language, page_token, page_size
        )

        response = result
        r = json.dumps(response)
        return r

    def delete_portfolio(self):
        accept_language = self._get_param('AcceptLanguage')
        id = self._get_param('Id')

        result = self.servicecatalog_backend.delete_portfolio(
            accept_language, id
        )

        response = result
        return json.dumps(response)
