from fastapi import FastAPI, Response
from .routes import auth, users
from fastapi.openapi.utils import get_openapi
import yaml

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_json = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    openapi_yaml = yaml.dump(openapi_json, sort_keys=False)
    return Response(content=openapi_yaml, media_type="application/yaml")