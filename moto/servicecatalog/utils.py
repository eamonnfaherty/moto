ACCOUNT_ID = "1234567890"


def portfolio_arn(region, portfolio_id):

    return "arn:aws:servicecatalog:{0}:{1}:portfolio/{2}".format(
        region, ACCOUNT_ID, portfolio_id
    )
