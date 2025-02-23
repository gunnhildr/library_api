from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from api.v1.router import api_router
from utils.logger import log_config

app = FastAPI()
app.include_router(api_router, prefix="/api")
add_pagination(app)

disable_installed_extensions_check()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8081, log_config=log_config)
