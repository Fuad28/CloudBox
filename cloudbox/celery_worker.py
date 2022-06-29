from cloudbox import celery, create_app
from cloudbox.config import Config

app = create_app(Config)
app.app_context().push()