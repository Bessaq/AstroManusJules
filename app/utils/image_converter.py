import cairosvg
import io
from typing import Optional
from fastapi import HTTPException
from app.config.image_settings import image_settings # Added import
# Pillow (PIL) is imported conditionally within the optimize_png method

class ImageConverter:
    @staticmethod
    def svg_to_png(
        svg_content: str,
        quality: int = image_settings.DEFAULT_PNG_QUALITY, # DPI for cairosvg
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> bytes:
        """
        Converts SVG to PNG using cairosvg.

        Args:
            svg_content: SVG content as a string.
            quality: DPI for the output PNG (default 300).
            width: Optional output width in pixels.
            height: Optional output height in pixels.

        Returns:
            PNG content as bytes.
        """
        try:
            # cairosvg uses 'dpi' parameter
            png_bytes = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=None, # Returns bytes directly
                output_width=width,
                output_height=height,
                dpi=quality
            )
            if not png_bytes:
                raise ValueError("CairoSVG returned empty content.")
            return png_bytes
        except Exception as e:
            # Consider logging the error server-side as well
            # print(f"CairoSVG conversion error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro na conversão SVG->PNG com CairoSVG: {str(e)}"
            )

    @staticmethod
    def optimize_png(png_content: bytes, compression_level: int = image_settings.PNG_COMPRESSION_LEVEL) -> bytes:
        """Otimiza PNG para reduzir tamanho usando Pillow (PIL)."""
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(png_content))
            output_buffer = io.BytesIO()
            img.save(
                output_buffer,
                format='PNG',
                optimize=True,
                compress_level=compression_level # Pillow uses 0 (no compression) to 9 (max compression)
            )
            return output_buffer.getvalue()
        except ImportError:
            # Pillow not installed, return original PNG content
            # print("Pillow (PIL) not installed. PNG optimization skipped.")
            return png_content
        except Exception as e:
            # Error during optimization, return original PNG content
            # print(f"Error optimizing PNG with Pillow: {e}")
            return png_content

# Função de conveniência
def convert_svg_to_png(
    svg_content: str,
    quality: int = image_settings.DEFAULT_PNG_QUALITY, # DPI
    width: Optional[int] = None,
    height: Optional[int] = None,
    optimize: bool = image_settings.ENABLE_PNG_OPTIMIZATION,
    compression_level: int = image_settings.PNG_COMPRESSION_LEVEL
) -> bytes:
    """Função wrapper para conversão SVG -> PNG com otimização opcional."""
    # Instantiating to call static methods, could also call them directly: ImageConverter.svg_to_png(...)
    # No real need for an instance if methods are static. Let's call them statically.

    png_bytes = ImageConverter.svg_to_png(svg_content, quality=quality, width=width, height=height)

    if optimize:
        png_bytes = ImageConverter.optimize_png(png_bytes, compression_level=compression_level)

    return png_bytes
