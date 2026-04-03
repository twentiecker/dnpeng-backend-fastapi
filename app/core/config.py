from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    BASE_PATH: str = "public/files"
    BASE_PATH_CPANEL: str = "/home/devdnpen/api-suplemen/public/files"
    ALLOWED_CATEGORIES: List[str] = [
        "intl",
        "bri",
        "bca",
        "mandiri",
        "pefindo",
        "kemenkeu",
        "bi",
        "samuel",
        "data",
        "pengeluaran",
        "produksi",
        "suplemen",
        "vicon",
        "rapat",
        "paparan",
        "brs",
        "lapres",
    ]
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".doc",
        ".docx",
    ]

    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
