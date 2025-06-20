"""
Router aprimorado para geração de SVG de alta qualidade.

Este módulo substitui o router SVG original com funcionalidades
avançadas para produzir mapas astrológicos profissionais.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body # Added Body
from fastapi.responses import Response
from app.models import SVGChartRequest, NatalChartRequest, TransitRequest
# For locally defined Pydantic model SVGToPNGConversionRequest
from pydantic import BaseModel, Field as PydanticField # Aliased Field to avoid conflict with fastapi.Query if any confusion
from app.security import verify_api_key
from app.utils.astro_helpers import create_subject
from app.utils.image_converter import convert_svg_to_png # Added for PNG conversion
from app.svg.enhanced_svg_generator import EnhancedSVGGenerator
from app.config.image_settings import image_settings # Added image_settings import
from kerykeion import CompositeSubjectFactory # Added for composite charts
import base64
import os
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Literal

router = APIRouter(prefix="/api/v2", tags=["enhanced_svg_charts"], dependencies=[Depends(verify_api_key)])

@router.post("/svg_chart", 
             response_class=Response,
             summary="Gera SVG de alta qualidade",
             description="Gera mapas astrológicos em SVG com qualidade profissional similar aos exemplos fornecidos.",
             responses={
                 200: {
                     "content": {"image/svg+xml": {}},
                     "description": "Retorna o gráfico SVG de alta qualidade diretamente."
                 },
                 422: {"description": "Erro de validação nos dados de entrada."},
                 500: {"description": "Erro interno ao gerar o gráfico."}
             })
async def generate_enhanced_svg_chart(
    data: SVGChartRequest,
    theme: Literal["light", "dark", "colorful", "strawberry"] = Query("light", description="Tema do chart"),
    high_quality: bool = Query(True, description="Usar configurações de alta qualidade para SVG"),
    show_aspects: bool = Query(True, description="Mostrar aspectos no chart"),
    active_points: Optional[List[str]] = Query(None, description="Lista de pontos ativos para desenhar no gráfico (ex: ['Sun', 'Moon', 'Ascendant']). Padrão desenha todos os configurados."),
    format: Literal["svg", "png"] = Query("svg", description="Formato de saída: 'svg' ou 'png'"),
    png_quality: int = Query(image_settings.DEFAULT_PNG_QUALITY, ge=image_settings.MIN_PNG_QUALITY, le=image_settings.MAX_PNG_QUALITY, description=f"DPI para saída PNG ({image_settings.MIN_PNG_QUALITY}-{image_settings.MAX_PNG_QUALITY})"),
    png_width: Optional[int] = Query(image_settings.DEFAULT_PNG_WIDTH, le=image_settings.MAX_PNG_WIDTH, description="Largura em pixels para saída PNG"),
    png_height: Optional[int] = Query(image_settings.DEFAULT_PNG_HEIGHT, le=image_settings.MAX_PNG_HEIGHT, description="Altura em pixels para saída PNG")
):
    """
    Gera um gráfico SVG de alta qualidade para mapas natais, trânsitos ou sinastrias, com opção de saída em PNG.
    
    Esta versão aprimorada produz SVGs com qualidade profissional, incluindo:
    - Sistema de cores CSS avançado
    - Geometria otimizada e elementos visuais complexos
    - Configurações personalizáveis por tipo de chart
    - Temas profissionais (light, dark, colorful)
    """
    try:
        natal_subject_for_generator = None
        transit_subject_for_generator = None
        
        # Mapear chart_type da requisição para tipo interno do EnhancedSVGGenerator
        # Kerykeion usa 'synastry' para charts combinados de duas pessoas (não midpoint composite)
        # 'combined' em SVGChartRequest.chart_type é usado para synastry.
        # 'composite' é o novo tipo para midpoint composite.
        chart_type_map = {
            "natal": "natal",
            "transit": "transit", 
            "combined": "synastry", # Synastry (two separate charts shown together)
            "composite": "composite"  # Midpoint Composite chart
        }
        enhanced_chart_type = chart_type_map.get(data.chart_type, "natal")

        # Criar subjects astrológicos baseados no chart_type
        if data.chart_type == "composite":
            if not data.transit_chart: # For composite, transit_chart holds person2's natal data
                raise HTTPException(status_code=422, detail="Para mapa composto (composite), 'transit_chart' deve conter os dados natais da segunda pessoa.")

            # transit_chart in SVGChartRequest is Optional[TransitRequest].
            # For composite, we expect it to be populated with data compatible with NatalChartRequest.
            # The create_subject helper can take Union[NatalChartRequest, TransitRequest, Dict].
            # We assume data.transit_chart's structure is compatible enough for create_subject.
            # If data.transit_chart was strictly TransitRequest, it might lack 'name', 'house_system' etc.
            # However, our TransitRequest includes these, making it more flexible here.
            person1_natal_data = data.natal_chart
            person2_natal_data = data.transit_chart # Re-interpreting transit_chart as Person2 Natal for composite

            person1_subject, _ = create_subject(person1_natal_data, person1_natal_data.name or "Pessoa1")
            # Ensure person2_natal_data has a name, default if necessary
            person2_name = getattr(person2_natal_data, 'name', "Pessoa2") or "Pessoa2"
            person2_subject, _ = create_subject(person2_natal_data, person2_name)

            if not CompositeSubjectFactory:
                 raise ImportError("CompositeSubjectFactory não pôde ser importado da Kerykeion.")
            factory = CompositeSubjectFactory(person1_subject, person2_subject)
            natal_subject_for_generator = factory.get_midpoint_composite_subject_model()
            transit_subject_for_generator = None # Composite chart is a single entity

        elif data.chart_type == "transit" or data.chart_type == "combined": # combined is synastry
            natal_subject_for_generator, _ = create_subject(data.natal_chart, data.natal_chart.name or "NatalChart")
            if not data.transit_chart:
                raise HTTPException(status_code=422, detail=f"Para chart_type '{data.chart_type}', 'transit_chart' é obrigatório.")
            transit_subject_for_generator, _ = create_subject(data.transit_chart, data.transit_chart.name or "TransitChart")

        else: # Default to "natal"
            natal_subject_for_generator, _ = create_subject(data.natal_chart, data.natal_chart.name or "NatalChart")
            transit_subject_for_generator = None

        if not natal_subject_for_generator:
            raise HTTPException(status_code=500, detail="Falha ao criar o subject astrológico principal.")

        generator = EnhancedSVGGenerator(
            natal_subject=natal_subject_for_generator,
            transit_subject=transit_subject_for_generator
        )
        
        custom_settings = {}
        if data.chart_type == "transit":
            custom_settings.update({"orb_reduction": 0.5, "highlight_transits": True})
        elif data.chart_type == "combined": # Synastry
            custom_settings.update({"show_both_subjects": True, "composite_aspects": True})
        elif data.chart_type == "composite":
            # Potentially add specific settings for composite, e.g., how aspects are shown,
            # or if houses are handled differently. For now, no specific overrides.
            pass

        svg_content = generator.generate_enhanced_svg(
        svg_content = generator.generate_enhanced_svg(
            chart_type=enhanced_chart_type,
            theme=theme,
            show_aspects=show_aspects,
            high_quality=high_quality,
            custom_settings=custom_settings,
            active_points=active_points
        )
        
        # Obter informações do chart para nome do arquivo
        chart_info = generator.get_chart_info(enhanced_chart_type)
        chart_name = chart_info["primary_subject"]["name"]
        
        # Adicionar informação do tipo no nome do arquivo
        type_suffix_map = {
            "natal": "Natal-Chart",
            "transit": "Transitos-Chart", 
            "combined": "Sinastria-Chart", # Synastry
            "composite": "Composto-Chart"   # Midpoint Composite
        }
        type_suffix = type_suffix_map.get(data.chart_type, "Chart")

        # For composite charts, the name might come from the composite_subject itself if it has one,
        # or construct from P1 & P2 names.
        final_chart_name = chart_name
        if data.chart_type == "composite" and natal_subject_for_generator:
            final_chart_name = natal_subject_for_generator.name # Kerykeion's composite subject has a name like "Composite P1 & P2"

        filename_svg = f"{final_chart_name}---{type_suffix}.svg"

        if format == "png":
            try:
                png_content = convert_svg_to_png(
                    svg_content,
                    quality=png_quality,
                    width=png_width,
                    height=png_height,
                    optimize=True # Assuming optimization is desired by default
                )
                png_filename_base = Path(filename_svg).stem
                png_filename = f"{png_filename_base}.png"
                return Response(
                    content=png_content,
                    media_type="image/png",
                    headers={
                        "Content-Disposition": f"inline; filename={png_filename}"
                    }
                )
            except HTTPException as he: # Re-raise HTTPExceptions from converter
                raise he
            except Exception as e_conv:
                # print(f"Error converting SVG to PNG: {e_conv}") # Server-side log
                raise HTTPException(status_code=500, detail=f"Erro ao converter SVG para PNG: {str(e_conv)}")

        # Default to SVG return
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={
                "Content-Disposition": f"inline; filename={filename_svg}",
                "X-Chart-Quality": "enhanced",
                "X-Chart-Type": enhanced_chart_type,
                "X-Chart-Theme": theme
            }
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Log detalhado para debugging
        print(f"Erro detalhado ao gerar SVG aprimorado: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao gerar gráfico SVG aprimorado: {type(e).__name__}"
        )

# --- Model for direct SVG to PNG conversion request ---
class SVGToPNGConversionRequest(BaseModel):
    svg_content: str = PydanticField(..., description="Conteúdo SVG como string a ser convertido.")
    quality: int = PydanticField(image_settings.DEFAULT_PNG_QUALITY, ge=image_settings.MIN_PNG_QUALITY, le=image_settings.MAX_PNG_QUALITY, description=f"DPI para a saída PNG ({image_settings.MIN_PNG_QUALITY}-{image_settings.MAX_PNG_QUALITY}). Padrão {image_settings.DEFAULT_PNG_QUALITY}.")
    width: Optional[int] = PydanticField(image_settings.DEFAULT_PNG_WIDTH, le=image_settings.MAX_PNG_WIDTH, description="Largura desejada em pixels para a saída PNG.")
    height: Optional[int] = PydanticField(image_settings.DEFAULT_PNG_HEIGHT, le=image_settings.MAX_PNG_HEIGHT, description="Altura desejada em pixels para a saída PNG.")
    optimize: bool = PydanticField(image_settings.ENABLE_PNG_OPTIMIZATION, description="Otimizar o PNG resultante para reduzir o tamanho.")
    compression_level: int = PydanticField(image_settings.PNG_COMPRESSION_LEVEL, ge=0, le=9, description="Nível de compressão para otimização do PNG (0-9).")


@router.post(
    "/convert/svg-to-png",
    response_class=Response, # Direct binary response
    summary="Converte conteúdo SVG para formato PNG",
    description="Recebe uma string SVG e a converte para uma imagem PNG com opções de qualidade e dimensões.",
    tags=["enhanced_svg_charts_conversion"]
)
async def convert_svg_to_png_endpoint(
    request_data: SVGToPNGConversionRequest = Body(...)
):
    try:
        png_content = convert_svg_to_png(
            svg_content=request_data.svg_content,
            quality=request_data.quality,
            width=request_data.width,
            height=request_data.height,
            optimize=request_data.optimize,
            compression_level=request_data.compression_level
        )

        return Response(
            content=png_content,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=converted_image.png"}
        )
    except HTTPException as he: # Re-raise HTTPExceptions from converter
        raise he
    except Exception as e:
        # print(f"Error in SVG to PNG conversion endpoint: {str(e)}") # Server-side log
        raise HTTPException(status_code=500, detail=f"Erro na conversão SVG para PNG: {str(e)}")


@router.post("/svg_chart_base64", 
             response_model=Dict[str, str],
             summary="Gera SVG de alta qualidade em Base64",
             description="Gera um gráfico SVG de alta qualidade e retorna como string base64.")
async def generate_enhanced_svg_chart_base64(
    data: SVGChartRequest,
    theme: Literal["light", "dark", "colorful", "strawberry"] = Query("light", description="Tema do chart"),
    high_quality: bool = Query(True, description="Usar configurações de alta qualidade"),
    show_aspects: bool = Query(True, description="Mostrar aspectos no chart"),
    active_points: Optional[List[str]] = Query(None, description="Lista de pontos ativos para desenhar no gráfico (ex: ['Sun', 'Moon', 'Ascendant']). Padrão desenha todos os configurados.")
):
    """
    Gera um gráfico SVG de alta qualidade e retorna como string base64.
    Útil para incorporação direta em aplicações web.
    """
    try:
        # Reutilizar a lógica do endpoint principal
        svg_response = await generate_enhanced_svg_chart(data, theme, high_quality, show_aspects, active_points)
        
        if svg_response.status_code != 200:
            raise HTTPException(status_code=svg_response.status_code, detail="Falha ao gerar SVG base.")
        
        svg_content_bytes = svg_response.body
        
        # Converter para base64
        base64_svg = base64.b64encode(svg_content_bytes).decode("utf-8")
        
        # Extrair informações dos headers
        chart_quality = svg_response.headers.get("X-Chart-Quality", "standard")
        chart_type = svg_response.headers.get("X-Chart-Type", "natal")
        chart_theme = svg_response.headers.get("X-Chart-Theme", "light")
        
        return {
            "svg_base64": base64_svg,
            "data_uri": f"data:image/svg+xml;base64,{base64_svg}",
            "chart_info": {
                "quality": chart_quality,
                "type": chart_type,
                "theme": chart_theme,
                "size_bytes": len(svg_content_bytes)
            }
        }
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Erro detalhado ao gerar SVG base64 aprimorado: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno ao gerar gráfico SVG em base64 aprimorado: {type(e).__name__}"
        )

@router.post("/svg_chart_info",
             response_model=Dict[str, any],
             summary="Informações do chart que será gerado",
             description="Retorna informações detalhadas sobre o chart que será gerado com os dados fornecidos.")
async def get_svg_chart_info(data: SVGChartRequest):
    """
    Retorna informações detalhadas sobre o chart que será gerado.
    Útil para preview e validação antes da geração do SVG.
    """
    try:
        # Criar subjects astrológicos
        natal_subject = create_subject(data.natal_chart, "Natal Chart")
        
        transit_subject = None
        if data.transit_chart and (data.chart_type == "transit" or data.chart_type == "synastry"):
            transit_subject = create_subject(data.transit_chart, "Transit/Second Person")
        
        # Mapear tipos de chart
        chart_type_map = {
            "natal": "natal",
            "transit": "transit",
            "combined": "synastry"
        }
        
        enhanced_chart_type = chart_type_map.get(data.chart_type, "natal")
        
        # Criar gerador para obter informações
        generator = EnhancedSVGGenerator(
            natal_subject=natal_subject,
            transit_subject=transit_subject
        )
        
        # Obter informações detalhadas
        chart_info = generator.get_chart_info(enhanced_chart_type)
        
        # Adicionar informações de configuração
        chart_info.update({
            "original_chart_type": data.chart_type,
            "enhanced_chart_type": enhanced_chart_type,
            "available_themes": list(generator.THEME_CONFIGURATIONS.keys()),
            "available_configurations": list(generator.CHART_CONFIGURATIONS.keys()),
            "supports_aspects": enhanced_chart_type in generator.CHART_CONFIGURATIONS,
            "estimated_svg_size": "150-200KB (alta qualidade)"
        })
        
        return chart_info
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        print(f"Erro ao obter informações do chart: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao obter informações do chart: {type(e).__name__}"
        )

@router.get("/themes",
           response_model=Dict[str, any],
           summary="Temas disponíveis",
           description="Lista todos os temas disponíveis para os charts SVG.")
async def get_available_themes():
    """
    Retorna informações sobre todos os temas disponíveis.
    """
    try:
        # Acessar THEME_CONFIGURATIONS diretamente da classe EnhancedSVGGenerator
        themes_info = {}
        for theme_name, theme_config in EnhancedSVGGenerator.THEME_CONFIGURATIONS.items():
            themes_info[theme_name] = {
                "name": theme_name,
                "description": {
                    "light": "Tema claro profissional com fundo branco",
                    "dark": "Tema escuro moderno com fundo preto",
                    "colorful": "Tema colorido vibrante com cores destacadas"
                }.get(theme_name, f"Tema {theme_name}"),
                "paper_background": theme_config["paper_1"],
                "text_color": theme_config["paper_0"],
                "zodiac_colors": theme_config["zodiac_bg_base"]
            }
        
        return {
            "available_themes": themes_info,
            "default_theme": "light",
            "recommended_theme": "light"
        }
        
    except Exception as e:
        print(f"Erro ao obter temas: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao obter temas: {type(e).__name__}"
        )

@router.get("/chart_types",
           response_model=Dict[str, any], 
           summary="Tipos de chart disponíveis",
           description="Lista todos os tipos de chart disponíveis e suas configurações.")
async def get_available_chart_types():
    """
    Retorna informações sobre todos os tipos de chart disponíveis.
    """
    try:
        # Criar instância temporária para acessar configurações
        temp_generator = EnhancedSVGGenerator(natal_subject=None)
        
        chart_types_info = {}
        for chart_type, config in temp_generator.CHART_CONFIGURATIONS.items():
            chart_types_info[chart_type] = {
                "name": chart_type,
                "kerykeion_type": config["chart_type"],
                "description": {
                    "natal": "Mapa natal individual - posições planetárias no momento do nascimento",
                    "transit": "Trânsitos atuais - posições planetárias atuais sobre o mapa natal",
                    "synastry": "Sinastria/Comparação - aspectos entre dois mapas natais"
                }.get(chart_type, f"Chart tipo {chart_type}"),
                "requires_second_subject": chart_type in ["transit", "synastry"],
                "default_aspects": list(config["aspects_settings"].keys()),
                "shows_houses": config["show_houses"],
                "shows_symbols": config["show_planet_symbols"]
            }
        
        return {
            "available_chart_types": chart_types_info,
            "default_type": "natal",
            "most_popular": ["natal", "transit", "synastry"]
        }
        
    except Exception as e:
        print(f"Erro ao obter tipos de chart: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao obter tipos de chart: {type(e).__name__}"
        )