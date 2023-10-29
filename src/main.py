from fastapi import Depends, FastAPI

from src.apps.pokemon.views import router as pokemon_router
from src import config
from src.db.deps import set_db
from src.db.exceptions import DatabaseValidationError
from src import exceptions


def get_app() -> FastAPI:
    _app = FastAPI(
        title=config.SERVICE_NAME,
        debug=config.DEBUG,
        dependencies=[Depends(set_db)],
    )

    _app.include_router(pokemon_router)

    # _app.add_exception_handler(
    #     DatabaseValidationError,
    #     exceptions.database_validation_exception_handler,
    # )

    return _app


app = get_app()
