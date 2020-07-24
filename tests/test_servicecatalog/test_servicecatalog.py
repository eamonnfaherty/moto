from __future__ import unicode_literals

import string

from nose.tools import assert_equals

import boto3
import botocore.exceptions
import sure  # noqa
import datetime
import uuid
import json

from botocore.exceptions import ClientError, ParamValidationError
from nose.tools import assert_raises

from moto import mock_servicecatalog


@mock_servicecatalog
def test_create_portfolio_with_idempotency_token():
    client = boto3.client("servicecatalog", region_name="us-east-1")

    accept_language = 'en'
    display_name = 'portfolioA'
    description = 'a working portfolio'
    provider_name = 'teamA'
    tags = [{
        'Key': 'CostCenter',
        'Value': 'A',
    }]
    idempotency_token = 'banana'
    idempotency_token_2 = 'banana2'

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(0)

    client.create_portfolio(
        AcceptLanguage=accept_language,
        DisplayName=display_name,
        Description=description,
        ProviderName=provider_name,
        Tags=tags,
        IdempotencyToken=idempotency_token,
    )

    client.create_portfolio(
        AcceptLanguage=accept_language,
        DisplayName=display_name,
        Description=description,
        ProviderName=provider_name,
        Tags=tags,
        IdempotencyToken=idempotency_token,
    )

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(1)

    client.create_portfolio(
        AcceptLanguage=accept_language,
        DisplayName=display_name,
        Description=description,
        ProviderName=provider_name,
        Tags=tags,
        IdempotencyToken=idempotency_token_2,
    )

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(2)


@mock_servicecatalog
def test_create_portfolio_without_idempotency_token():
    client = boto3.client("servicecatalog", region_name="us-east-1")

    accept_language = 'en'
    display_name = 'portfolioA'
    description = 'a working portfolio'
    provider_name = 'teamA'
    tags = [{
        'Key': 'CostCenter',
        'Value': 'A',
    }]

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(0)

    client.create_portfolio(
        AcceptLanguage=accept_language,
        DisplayName=display_name,
        Description=description,
        ProviderName=provider_name,
        Tags=tags,
    )

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(1)


@mock_servicecatalog
def test_delete_portfolio():
    client = boto3.client("servicecatalog", region_name="us-east-1")

    accept_language = 'en'
    display_name = 'portfolioA'
    description = 'a working portfolio'
    provider_name = 'teamA'
    tags = [{
        'Key': 'CostCenter',
        'Value': 'A',
    }]

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(0)

    client.create_portfolio(
        AcceptLanguage=accept_language,
        DisplayName=display_name,
        Description=description,
        ProviderName=provider_name,
        Tags=tags,
    )

    portfolios = client.list_portfolios().get('PortfolioDetails')

    len(portfolios).should.equal(1)

    client.delete_portfolio(Id=portfolios[0].get('Id'))

    len(client.list_portfolios().get('PortfolioDetails')).should.equal(0)