import os
from varys_message_retrieval import VarysMessageRetrieval
from empty_message_retrieval import EmptyMessageRetrieval

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create a SECRET_KEY.
SECRET_KEY = os.environ["SECRET_KEY"]

# Set to True if in development, or False is in production
DEBUG = os.getenv("DEBUG", "False") == "True"

# Set to ['*'] if in development, or specific IP addresses and domains if in production
ALLOWED_HOSTS = [os.environ["ALLOWED_HOST"]]

# Provide the email address for the site admin (e.g. the researcher/research team)
ADMIN_EMAIL = [os.environ["ADMIN_EMAIL"]]

# Set the database name below
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DATABASE_NAME"],
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": os.environ["DATABASE_HOST"],
    }
}

CORS_ALLOWED_ORIGINS = [
    allowed_origin
    for allowed_origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if allowed_origin
]
CSRF_TRUSTED_ORIGINS = [
    trusted_origin
    for trusted_origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if trusted_origin
]


ONYX_DOMAIN = os.environ["ONYX_DOMAIN"]

if "VARYS_CONFiG_PATH" in os.environ:

    MESSAGE_RETRIEVAL = VarysMessageRetrieval(
                              queue_suffix="agate",
                              timeout=1,
                              config_path=os.environ["VARYS_CONFiG_PATH"],
                              profile="test",
                              logfile="varys.log",
                              log_level="DEBUG",
                              auto_acknowledge=False)
else:
    MESSAGE_RETRIEVAL = EmptyMessageRetrieval()
