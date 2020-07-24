from __future__ import unicode_literals

import re
from boto3 import Session
from collections import defaultdict

from moto.core import ACCOUNT_ID, BaseBackend, BaseModel
from moto.core.exceptions import RESTError
from moto.cloudformation import cloudformation_backends

import datetime
import time
import uuid
import itertools
import json
import yaml
import hashlib

from .utils import portfolio_arn
from .exceptions import (
    ValidationException,
    InvalidFilterValue,
    InvalidFilterOption,
    InvalidFilterKey,
    ParameterVersionLabelLimitExceeded,
    ParameterVersionNotFound,
    ParameterNotFound,
    DocumentAlreadyExists,
    InvalidDocumentOperation,
    InvalidDocument,
    InvalidDocumentContent,
    InvalidDocumentVersion,
    DuplicateDocumentVersionName,
    DuplicateDocumentContent,
)


class Portfolio(BaseModel):
    def __init__(
            self,
            accept_language,
            display_name,
            description,
            provider_name,
            tags,
            idempotency_token,
    ):
        self.accept_language = accept_language
        self.display_name = display_name
        self.description = description
        self.provider_name = provider_name
        self.tags = tags
        self.idempotency_token = idempotency_token
        self._id = None
        self._created_time = None

    def details_response_object(self):
        response = {
            "Id": self._id,
            "DisplayName": self.display_name,
            "Description": self.description,
            "CreatedTime": self._created_time,
            "ProviderName": self.provider_name,
        }

        if region:
            response["ARN"] = portfolio_arn(region, self._id)

        return response

    def response_object(self):
        return {
            "PortfolioDetail": self.details_response_object(),
            "Tags": self.tags,
        }

    def set_product_id(self, product_id):
        self._id = product_id
        self._created_time = '1234567890'


MAX_TIMEOUT_SECONDS = 3600


class SimpleServiceCatalogBackend(BaseBackend):
    def __init__(self, region_name=None):
        super(SimpleServiceCatalogBackend, self).__init__()
        self._portfolios = dict()
        self._portfolio_idempotency_tokens = dict()

        self._errors = []
        self._region = region_name

    def reset(self):
        region_name = self._region
        self.__dict__ = {}
        self.__init__(region_name)

    def _format_error(self, key, value, constraint):
        return 'Value "{value}" at "{key}" failed to satisfy constraint: {constraint}'.format(
            constraint=constraint, key=key, value=value
        )

    def _raise_errors(self):
        if self._errors:
            count = len(self._errors)
            plural = "s" if len(self._errors) > 1 else ""
            errors = "; ".join(self._errors)
            self._errors = []  # reset collected errors

            raise ValidationException(
                "{count} validation error{plural} detected: {errors}".format(
                    count=count, plural=plural, errors=errors
                )
            )

    def create_portfolio(
            self, AcceptLanguage, DisplayName, Description, ProviderName, Tags, IdempotencyToken
    ):
        portfolio = Portfolio(
            accept_language=AcceptLanguage,
            display_name=DisplayName,
            description=Description,
            provider_name=ProviderName,
            tags=Tags,
            idempotency_token=IdempotencyToken,
        )

        if IdempotencyToken is not None:
            if self._portfolio_idempotency_tokens.get(IdempotencyToken) is not None:
                self._portfolio_idempotency_tokens[IdempotencyToken] = portfolio
            else:
                self._add_portfolio(portfolio)
                self._portfolio_idempotency_tokens[IdempotencyToken] = portfolio
        else:
            self._add_portfolio(portfolio)

        return portfolio.response_object()

    def list_portfolios(
            self, AcceptLanguage, PageToken, PageSize
    ):
        portfolios = [p.details_response_object() for p in list(self._portfolios.values())]
        return {
            'PortfolioDetails': portfolios
        }

    def delete_portfolio(self, AcceptLanguage, Id):
        del self._portfolios[Id]
        return {}

    def _add_portfolio(self, portfolio):
        n_portfolios = len(self._portfolios.keys())
        uid = "{n_portfolios}".format(n_portfolios=n_portfolios).zfill(4)
        portfolio.set_product_id("port-nvca3bl63{uid}".format(uid=uid))

        self._portfolios[portfolio._id] = portfolio


servicecatalog_backends = {}
for region in Session().get_available_regions("ssm"):
    servicecatalog_backends[region] = SimpleServiceCatalogBackend(region)
for region in Session().get_available_regions("ssm", partition_name="aws-us-gov"):
    servicecatalog_backends[region] = SimpleServiceCatalogBackend(region)
for region in Session().get_available_regions("ssm", partition_name="aws-cn"):
    servicecatalog_backends[region] = SimpleServiceCatalogBackend(region)
