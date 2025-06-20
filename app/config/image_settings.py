from pydantic_settings import BaseSettings, SettingsConfigDict # Pydantic v2 uses pydantic-settings
from typing import Optional

class ImageSettings(BaseSettings):
    # Default PNG quality (DPI)
    DEFAULT_PNG_QUALITY: int = 300
    MAX_PNG_QUALITY: int = 600 # Max value for quality parameter
    MIN_PNG_QUALITY: int = 72  # Min value for quality parameter

    # Default dimensions for conversion if specific output_width/height not given
    # These are not max dimensions, but defaults if no specific dimensions are requested by user.
    # Kerykeion's SVG has a viewBox of '0 0 820 550.0'.
    # Using these as default dimensions for PNG if not specified by user might be an option.
    DEFAULT_PNG_WIDTH: Optional[int] = None # Let cairosvg decide based on SVG if not set
    DEFAULT_PNG_HEIGHT: Optional[int] = None

    # Maximum dimensions to prevent abuse / oversized images
    MAX_PNG_WIDTH: int = 4000
    MAX_PNG_HEIGHT: int = 4000

    # PNG Optimization
    ENABLE_PNG_OPTIMIZATION: bool = True
    PNG_COMPRESSION_LEVEL: int = 6 # Pillow: 0 (no compression) to 9 (max)

    # Cache (Placeholder for future, not implemented in current scope)
    # ENABLE_IMAGE_CACHE: bool = False
    # IMAGE_CACHE_TTL: int = 3600  # 1 hour

    model_config = SettingsConfigDict(env_prefix='IMG_') # Pydantic v2 style for env_prefix

image_settings = ImageSettings()
