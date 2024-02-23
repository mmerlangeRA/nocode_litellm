from pydantic import BaseModel, Field

from settings.settings_loader import load_active_settings


class CorsSettings(BaseModel):
    """CORS configuration.

    For more details on the CORS configuration, see:
    # * https://fastapi.tiangolo.com/tutorial/cors/
    # * https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
    """

    enabled: bool = Field(
        description="Flag indicating if CORS headers are set or not."
        "If set to True, the CORS headers will be set to allow all origins, methods and headers.",
        default=False,
    )
    allow_credentials: bool = Field(
        description="Indicate that cookies should be supported for cross-origin requests",
        default=False,
    )
    allow_origins: list[str] = Field(
        description="A list of origins that should be permitted to make cross-origin requests.",
        default=[],
    )
    allow_origin_regex: list[str] = Field(
        description="A regex string to match against origins that should be permitted to make cross-origin requests.",
        default=None,
    )
    allow_methods: list[str] = Field(
        description="A list of HTTP methods that should be allowed for cross-origin requests.",
        default=[
            "GET",
        ],
    )
    allow_headers: list[str] = Field(
        description="A list of HTTP request headers that should be supported for cross-origin requests.",
        default=[],
    )


class AuthSettings(BaseModel):
    """Authentication configuration.

    The implementation of the authentication strategy must
    """

    enabled: bool = Field(
        description="Flag indicating if authentication is enabled or not.",
        default=True,
    )
    secret: str = Field(
        description="The secret to be used for authentication. "
        "It can be any non-blank string. For HTTP basic authentication, "
        "this value should be the whole 'Authorization' header that is expected"
    )


class ServerSettings(BaseModel):
    env_name: str = Field(
        description="Name of the environment (prod, staging, local...)"
    )
    port: int = Field(description="Port of PrivateGPT FastAPI server, defaults to 8001")
    cors: CorsSettings = Field(
        description="CORS configuration", default=CorsSettings(enabled=False)
    )


class DataSettings(BaseModel):
    local_data_folder: str = Field(
        description="Path to local storage."
        "It will be treated as an absolute path if it starts with /"
    )

class ModelKeys(BaseModel):
    openai: str = Field(
        description="openai key."
    )
    mistralai: str = Field(
        description="mistralai key."
    )

class Token(BaseModel):
    secret_key: str
    admin_key: str

class SupaBaseSettrings(BaseModel):
  url: str
  anon_key: str
  service_role_key: str

class LangsmithSettings(BaseModel):
    enabled:bool = False
    api_key: str

class DeeplSettings(BaseModel):
    api_key: str

class Settings(BaseModel):
    server: ServerSettings
    data: DataSettings
    model_keys: ModelKeys
    deepl: DeeplSettings
    token: Token
    supabase: SupaBaseSettrings
    langsmith:LangsmithSettings



"""
This is visible just for DI or testing purposes.

Use dependency injection or `settings()` method instead.
"""
unsafe_settings = load_active_settings()
#print(unsafe_settings)

"""
This is visible just for DI or testing purposes.

Use dependency injection or `settings()` method instead.
"""
unsafe_typed_settings = Settings(**unsafe_settings)
#print(unsafe_typed_settings)


def settings() -> Settings:
    """Get the current loaded settings from the DI container.

    This method exists to keep compatibility with the existing code,
    that require global access to the settings.

    For regular components use dependency injection instead.
    """
    from server.di import global_injector

    return global_injector.get(Settings)
