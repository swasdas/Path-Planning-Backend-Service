from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://robot:robot123@localhost:5432/robotdb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"

    # Algorithm Settings
    ga_population_size: int = 50
    ga_generations: int = 30
    ga_mutation_rate: float = 0.1
    ga_crossover_rate: float = 0.8
    grid_resolution: float = 0.3  # 10cm grid cells for fine-grained path planning

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
