from sqlalchemy.engine import Connection

from foundation.logger import logger


def async_handler_generic_task(cls, *args, **kwargs):  # type: ignore
  """
  This function is meant to be used for running asynchronous event handlers.

  It bootstraps application context and wraps task with DB transaction.
  """
  from main import bootstrap_app
  from main.modules import RequestScope

  app = bootstrap_app()
  scope = app.injector.get(RequestScope)
  scope.enter()
  connection = app.injector.get(Connection)
  try:
    with connection.begin():
      instance = app.injector.create_object(cls)
      instance(*args, **kwargs)
  except Exception as exc:
    logger.exception(exc)
    raise exc
  finally:
    scope.exit()
