import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from newrelic.agent import initialize
from .settings import settings

def setup_monitoring():
    """Configure monitoring tools"""
    # Initialize Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[
                FastApiIntegration(),
                sentry_sdk.integrations.sqlalchemy.SqlalchemyIntegration(),
                sentry_sdk.integrations.redis.RedisIntegration(),
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    # Initialize New Relic
    if settings.NEW_RELIC_LICENSE_KEY:
        initialize('newrelic.ini')

def get_monitoring_status():
    """Get status of monitoring tools"""
    return {
        "sentry": {
            "enabled": bool(settings.SENTRY_DSN),
            "environment": settings.ENVIRONMENT
        },
        "new_relic": {
            "enabled": bool(settings.NEW_RELIC_LICENSE_KEY)
        }
    } 