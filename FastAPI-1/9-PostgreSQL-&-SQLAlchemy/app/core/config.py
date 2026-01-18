# from pydantic_settings import BaseSettings
# from pydantic import Field

# class Settings(BaseSettings):
#     APP_NAME: str = Field(..., env="APP_NAME")
#     ENV: str = Field("development", env="ENV")
#     DEBUG: bool = Field(False, env="DEBUG")

#     API_PREFIX: str = Field("/api", env="API_PREFIX")
#     API_VERSION: str = Field("v1", env="API_VERSION")

#     class Config:
#         env_file = ".env"
#         env_file_encoding = "utf-8"

# settings = Settings()


from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = Field(..., env="APP_NAME")
    ENV: str = Field("development", env="ENV")
    DEBUG: bool = Field(False, env="DEBUG")
    API_PREFIX: str = Field("/api", env="API_PREFIX")
    API_VERSION: str = Field("v1", env="API_VERSION")
    
    # Database configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # এটা add করলে extra fields ignore করবে

settings = Settings()