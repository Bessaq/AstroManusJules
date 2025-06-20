"""
Gerador Aprimorado de SVG Astrológico para AstroManus.

Este módulo implementa um gerador de SVG de alta qualidade que produz
mapas astrológicos profissionais similares aos exemplos fornecidos.
"""
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from kerykeion.settings.kerykeion_settings import get_settings
from typing import Optional, Dict, Any, Tuple, Union, List
import os
import tempfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET


class EnhancedSVGGenerator:
    """
    Gerador aprimorado de SVG com configurações avançadas para máxima qualidade.
    """

    DEFAULT_ASPECTS_SETTINGS = { # Added default aspects
        "conjunction": {"active": True, "orb": 8, "color": "#ff0000"},
        "opposition": {"active": True, "orb": 8, "color": "#0000ff"},
        "trine": {"active": True, "orb": 8, "color": "#00ff00"},
        "square": {"active": True, "orb": 7, "color": "#ff00ff"},
        "sextile": {"active": True, "orb": 6, "color": "#ffff00"},
        "quincunx": {"active": True, "orb": 5, "color": "#00ffff"},
        "semi_sextile": {"active": True, "orb": 3, "color": "#ffa500"},
        "semi_square": {"active": True, "orb": 3, "color": "#800080"},
        "sesqui_square": {"active": True, "orb": 3, "color": "#008080"},
        "quintile": {"active": True, "orb": 2, "color": "#800000"},
        "bi_quintile": {"active": True, "orb": 2, "color": "#808000"}
    }

    # Configurações avançadas para diferentes tipos de mapas
    CHART_CONFIGURATIONS = {
        "natal": {
            "chart_type": "Natal", # Kerykeion internal type for KerykeionChartSVG
            "show_aspects": True,
            "show_degree_symbols": True,
            "show_planet_symbols": True,
            "show_zodiac_symbols": True,
            "show_houses": True,
            "aspects_settings": DEFAULT_ASPECTS_SETTINGS
        },
        "transit": {
            "chart_type": "Transit", # Kerykeion internal type
            "show_aspects": True,
            "show_degree_symbols": True,
            "show_planet_symbols": True,
            "show_zodiac_symbols": True,
            "show_houses": True,
            "aspects_settings": {
                "conjunction": {"active": True, "orb": 3, "color": "#ff0000"},
                "opposition": {"active": True, "orb": 3, "color": "#0000ff"},
                "trine": {"active": True, "orb": 3, "color": "#00ff00"},
                "square": {"active": True, "orb": 3, "color": "#ff00ff"},
                "sextile": {"active": True, "orb": 2, "color": "#ffff00"}
            }
        },
        "synastry": {
            "chart_type": "Synastry",
            "show_aspects": True,
            "show_degree_symbols": True,
            "show_planet_symbols": True,
            "show_zodiac_symbols": True,
            "show_houses": True,
            "aspects_settings": { # Slightly tighter orbs for synastry by default
                "conjunction": {"active": True, "orb": 7, "color": "#ff0000"}, # Example color
                "opposition": {"active": True, "orb": 7, "color": "#0000ff"},
                "trine": {"active": True, "orb": 6, "color": "#00ff00"},
                "square": {"active": True, "orb": 6, "color": "#ff00ff"},
                "sextile": {"active": True, "orb": 5, "color": "#ffff00"},
                "quincunx": {"active": True, "orb": 3, "color": "#00ffff"} # Example
            }
        },
        "composite": { # New configuration for composite charts
            "chart_type": "Composite", # Kerykeion internal type (assuming it supports "Composite")
            "show_aspects": True,
            "aspects_settings": DEFAULT_ASPECTS_SETTINGS, # Use default aspects, can be customized
            "show_degree_symbols": True,
            "show_planet_symbols": True,
            "show_zodiac_symbols": True, # Glyphs on the zodiac ring
            "show_houses": False,  # Houses are often handled differently or omitted in midpoint composites
            "show_house_numbers": False, # Consistent with show_houses = False
            "show_asc_mc_lines": True, # Composite Asc/MC are often key points if calculated
            # KerykeionChartSVG parameters that might be relevant:
            # "draw_zodiac_glyphs": True, # Already covered by show_zodiac_symbols effectively
            # "draw_planet_glyphs": True, # Already covered by show_planet_symbols
            # "draw_house_cusps_tropical_pos": False, # if show_houses is False
            # "draw_house_numbers": False, # if show_houses is False
        }
    }

    # Configurações de tema avançadas
    THEME_CONFIGURATIONS = {
        "strawberry": {
            "paper_0": "#330011",  # Dark text, deep berry
            "paper_1": "#FFDDEE",  # Light pink background
            "signs_font_color": "#AA0033", # Berry red
            "planets_font_color": "#330011",
            "cusps_font_color": "#550022",
            "points_font_color": "#770022",
            "stroke_color": "#BB0044",
            "zodiac_bg_base": ["#FFC0CB", "#FFB6C1", "#FF69B4", "#FF1493",  # Pinks
                               "#DB7093", "#C71585", "#E6E6FA", "#D8BFD8",  # PaleLavenders
                               "#FFDAB9", "#FFA07A", "#FA8072", "#F08080"], # Peachy/Corals
            "aspect_line_default": "#DDA0DD", # Plum
            "aspect_colors": { # Ensuring all aspects from other themes are considered
                "conjunction": "#FF0055", # Strong pink-red
                "opposition": "#AA0033",  # Dark berry
                "trine": "#FF69B4",       # Hot pink
                "square": "#DB7093",      # Pale violet red
                "sextile": "#FFB6C1",     # Light pink
                "quincunx": "#C71585",    # Medium Violet Red (example)
                "semi_sextile": "#FFDAB9", # Light Peach (example)
                "semi_square": "#FA8072",  # Salmon (example)
                "sesqui_square": "#F08080",# Light Coral (example)
                "quintile": "#E6E6FA",    # Lavender (example)
                "bi_quintile": "#D8BFD8", # Thistle (example)
                "major": "#FF0055", # Fallback for "major" if used by kerykeion
                "minor": "#AA0033"  # Fallback for "minor" if used by kerykeion
            },
            "house_cusp_color": "#8B0000", # Dark red
            "asc_mc_stroke_color": "#C71585", # Medium violet red
            "planet_colors": {
                 "Sun": "#FF4500", "Moon": "#FFDA7E", "Mercury": "#FFC3A0",
                 "Venus": "#FF8C94", "Mars": "#FF0000", "Jupiter": "#E45E9D",
                 "Saturn": "#C71585", "Uranus": "#A569BD", "Neptune": "#5B2C6F",
                 "Pluto": "#8B0000", "Default": "#D2B4DE"
             },
             "sign_colors": {
                 "Fire": "#FF4500", "Earth": "#FF69B4",
                 "Air": "#FFA07A", "Water": "#DB7093", "Default": "#FFC0CB"
             },
             # Include zodiac_icon_base similar to other themes if needed by _apply_theme_to_chart
             "zodiac_icon_base": ["#AA0033", "#AA0033", "#AA0033", "#AA0033"] # Simplified, adjust if complex logic like light/dark
        },
        "light": {
            "paper_0": "#000000",
            "paper_1": "#ffffff",
            "zodiac_bg_base": ["#ff7200", "#6b3d00", "#69acf1", "#2b4972"],
            "zodiac_icon_base": ["#ff7200", "#6b3d00", "#69acf1", "#2b4972"],
            "aspect_colors": {
                "major": "#ff0000",
                "minor": "#666666"
            }
        },
        "dark": {
            "paper_0": "#ffffff",
            "paper_1": "#1a1a1a",
            "zodiac_bg_base": ["#ff8533", "#8b5a2b", "#87c4ff", "#4a5f8a"],
            "zodiac_icon_base": ["#ff8533", "#8b5a2b", "#87c4ff", "#4a5f8a"],
            "aspect_colors": {
                "major": "#ff4444",
                "minor": "#999999"
            }
        },
        "colorful": {
            "paper_0": "#000000",
            "paper_1": "#fafafa",
            "zodiac_bg_base": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"],
            "zodiac_icon_base": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"],
            "aspect_colors": {
                "major": "#e74c3c",
                "minor": "#95a5a6"
            }
        }
    }

    def __init__(self, natal_subject: AstrologicalSubject, 
                 transit_subject: Optional[AstrologicalSubject] = None) -> None:
        """
        Inicializa o gerador com configurações otimizadas.
        """
        self.natal_subject = natal_subject
        self.transit_subject = transit_subject
        self.settings = get_settings()
        
    def _configure_advanced_settings(self, chart_type: str, theme: str = "light") -> Dict[str, Any]:
        """
        Configura configurações avançadas para o Kerykeion baseadas no tipo e tema.
        """
        config = self.CHART_CONFIGURATIONS.get(chart_type, self.CHART_CONFIGURATIONS["natal"])
        theme_config = self.THEME_CONFIGURATIONS.get(theme, self.THEME_CONFIGURATIONS["light"])
        
        # Configurações avançadas do Kerykeion
        advanced_config = {
            # Configurações gerais
            "chart_type": config["chart_type"],
            "new_output_directory": True,
            "output_file_format": "svg",
            
            # Configurações visuais
            "chart_size": 550,  # Tamanho otimizado como nos exemplos
            "chart_width": 820,  # Largura otimizada como nos exemplos
            "chart_height": 550,  # Altura otimizada como nos exemplos
            
            # Configurações dos elementos
            "show_aspects": config["show_aspects"],
            "show_degree_symbols": config["show_degree_symbols"],
            "show_planet_symbols": config["show_planet_symbols"],
            "show_zodiac_symbols": config["show_zodiac_symbols"],
            "show_houses": config["show_houses"],
            
            # Configurações de aspectos
            "aspects_settings": config["aspects_settings"],
            
            # Configurações de tema
            "theme_colors": theme_config,
            
            # Configurações de qualidade
            "high_resolution": True,
            "antialiasing": True,
            "vector_optimization": True
        }
        
        return advanced_config

    def _apply_theme_to_chart(self, chart_instance, theme: str = "light") -> None:
        """
        Aplica tema avançado ao objeto de chart do Kerykeion.
        """
        theme_config = self.THEME_CONFIGURATIONS.get(theme, self.THEME_CONFIGURATIONS["light"])
        
        try:
            # Kerykeion v5's set_up_theme(theme_name) is not standard in v4.
            # Theme colors are typically passed via `custom_colors` to constructor or by updating `chart.colors` directly.
            # The `custom_colors` parameter in the constructor (added in previous step) should handle most of this.
            # This method's direct update of chart.colors can remain as a supplement if needed for more granular control
            # or if the constructor's `custom_colors` doesn't map all theme aspects perfectly.

            # Ensure chart.colors object exists and can be updated.
            if hasattr(chart_instance, 'colors') and hasattr(chart_instance.colors, 'update'):
                custom_colors = {}
                
                # Aplicar cores do papel
                custom_colors.update({
                    'paper_0': theme_config["paper_0"],
                    'paper_1': theme_config["paper_1"]
                })
                
                # Aplicar cores zodiacais
                zodiac_colors = theme_config["zodiac_bg_base"]
                for i in range(12):
                    color_index = i % len(zodiac_colors)
                    custom_colors[f'zodiac_bg_{i}'] = zodiac_colors[color_index]
                    custom_colors[f'zodiac_icon_{i}'] = theme_config["zodiac_icon_base"][color_index]
                
                chart_instance.colors.update(custom_colors)
                
        except Exception as e:
            print(f"Aviso: Não foi possível aplicar tema personalizado: {e}")

    def _optimize_svg_output(self, svg_content: str, chart_type: str) -> str:
        """
        Otimiza o conteúdo SVG para melhor qualidade e compatibilidade.
        """
        try:
            # Parse do XML para manipulação
            root = ET.fromstring(svg_content)
            
            # Adicionar namespace Kerykeion se não existir
            if 'kr' not in root.attrib:
                root.set('xmlns:kr', 'https://www.kerykeion.net/')
            
            # Otimizar viewBox para qualidade máxima
            root.set('viewBox', '0 0 820 550.0')
            root.set('width', '100%')
            root.set('height', '100%')
            root.set('preserveAspectRatio', 'xMidYMid')
            
            # Adicionar título profissional
            title_elem = root.find('.//title')
            if title_elem is not None:
                if chart_type == "transit":
                    title_elem.text = f"{self.natal_subject.name} - Trânsitos | AstroManus"
                elif chart_type == "synastry" and self.transit_subject:
                    title_elem.text = f"{self.natal_subject.name} & {self.transit_subject.name} - Sinastria | AstroManus"
                elif chart_type == "composite":
                    # self.natal_subject is the composite_subject in this case
                    title_elem.text = f"{self.natal_subject.name} - Mapa Composto | AstroManus"
                else: # Default for "natal"
                    title_elem.text = f"{self.natal_subject.name} - Mapa Natal | AstroManus"
            
            # Converter de volta para string
            return ET.tostring(root, encoding='unicode', method='xml')
            
        except Exception as e:
            print(f"Aviso: Não foi possível otimizar SVG: {e}")
            return svg_content

    def _validate_chart_data(self, chart_type: str) -> None:
        """
        Valida se os dados necessários estão disponíveis para o tipo de chart solicitado.
        """
        if not self.natal_subject:
            raise ValueError("Dados do mapa natal são obrigatórios")
        
        if chart_type in ["transit", "synastry"] and not self.transit_subject:
            raise ValueError(f"Dados de trânsito/segunda pessoa são necessários para charts do tipo '{chart_type}'")
        
        # Validar dados essenciais do subject
        required_attrs = ['name', 'year', 'month', 'day', 'hour', 'minute', 'lat', 'lng']
        for attr in required_attrs:
            if not hasattr(self.natal_subject, attr) or getattr(self.natal_subject, attr) is None:
                raise ValueError(f"Dados incompletos no mapa natal: faltando '{attr}'")
        
        if self.transit_subject:
            for attr in required_attrs:
                if not hasattr(self.transit_subject, attr) or getattr(self.transit_subject, attr) is None:
                    raise ValueError(f"Dados incompletos no trânsito/segunda pessoa: faltando '{attr}'")

    def generate_enhanced_svg(
        self,
        chart_type: str = "natal",
        theme: str = "light",
        show_aspects: bool = True,
        high_quality: bool = True,
        custom_settings: Optional[Dict[str, Any]] = None,
        active_points: Optional[List[str]] = None
    ) -> str:
        """
        Gera um SVG de alta qualidade com configurações avançadas.
        
        Args:
            chart_type: Tipo do chart ("natal", "transit", "synastry")
            theme: Tema do chart ("light", "dark", "colorful")
            show_aspects: Se deve mostrar aspectos
            high_quality: Se deve usar configurações de alta qualidade
            custom_settings: Configurações personalizadas opcionais
            
        Returns:
            Conteúdo SVG como string
        """
        # Validar dados de entrada
        self._validate_chart_data(chart_type)
        
        # Configurar parâmetros avançados
        config = self._configure_advanced_settings(chart_type, theme)
        
        # Aplicar configurações personalizadas se fornecidas
        if custom_settings:
            config.update(custom_settings)
        
        # Criar diretório temporário para output
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Prepare parameters for KerykeionChartSVG constructor
                # Kerykeion v4 usually takes chart_type_name, and other visual settings directly.
                # Custom colors from the theme are also often passed via a parameter like `custom_colors`.

                chart_params = {
                    "chart_type_name": config["chart_type"], # Use chart_type_name for K4
                    "output_directory": temp_path,
                    # Visual settings from config:
                    "chart_size_percentage": config.get("chart_size", 100), # Assuming chart_size is a percentage or needs mapping
                    # Kerykeion v4 might use chart_size_px for pixel dimensions directly
                    # For now, let's assume chart_size_percentage is what K4 expects or can handle.
                    # Or, if K4 uses width/height:
                    # "chart_width": config.get("chart_width"),
                    # "chart_height": config.get("chart_height"),
                    "show_aspects": config["show_aspects"],
                    "show_degree_symbols": config["show_degree_symbols"],
                    "show_planet_glyphs": config["show_planet_symbols"], # K4 often uses 'show_planet_glyphs'
                    "show_zodiac_glyphs": config["show_zodiac_symbols"], # K4 often uses 'show_zodiac_glyphs'
                    "show_houses": config["show_houses"],
                    "aspects_settings": config["aspects_settings"],
                    # Custom colors from theme:
                    # The _apply_theme_to_chart method currently updates chart.colors directly.
                    # Alternatively, if K4 KerykeionChartSVG takes custom_colors dict:
                    "custom_colors": self.THEME_CONFIGURATIONS.get(theme, self.THEME_CONFIGURATIONS["light"]),
                    # Add active_points to chart_params if provided, based on K4 guide
                    "active_points": active_points if active_points else None
                }

                # Filter out None values from chart_params for optional parameters like active_points
                chart_params = {k: v for k, v in chart_params.items() if v is not None or k not in ["active_points"]}
                # If active_points is None, it might still need to be passed as None if the constructor expects it.
                # Or, if KerykeionChartSVG uses its default if 'active_points' is missing, we can filter None.
                # For safety, let's ensure active_points is in chart_params if it was originally provided by the user, even if None.
                # A better filter might be:
                # chart_params = {k: v for k, v in chart_params.items() if not (k == "active_points" and v is None)}
                # This ensures active_points is only added if it's not None.
                # However, Kerykeion might expect active_points=None to mean "use defaults".
                # The previous chart_params update already includes active_points: active_points if active_points else None
                # So, if active_points is None from the function call, it will be None in chart_params.
                # The filtering chart_params = {k: v for k,v in chart_params.items() if v is not None} will remove it if it's None.
                # This is probably fine, as KerykeionChartSVG will use its default list of points if active_points param is missing.
                # Let's refine the filtering to keep active_points if it's explicitly None.
                # No, the original filter is better: if active_points is None from input, it will be None in dict.
                # Then {k: v for k, v in chart_params.items() if v is not None} will REMOVE active_points from chart_params
                # if its value is None. This is generally the desired behavior for optional params.
                # If active_points is an empty list, it will be passed as an empty list.

                # Revised filtering for clarity for active_points:
                # We want to pass active_points if it's a list (even empty).
                # If it's None (default from function signature), we don't want to pass the key at all to KSVG.
                if active_points is None:
                    if "active_points" in chart_params: # It would be None here
                        del chart_params["active_points"]
                # All other None values for other parameters will be filtered by the next line:
                chart_params = {k: v for k, v in chart_params.items() if v is not None}



                # Create KerykeionChartSVG instance
                if chart_type == "natal":
                    chart = KerykeionChartSVG(self.natal_subject, **chart_params)
                elif chart_type == "transit":
                    chart = KerykeionChartSVG(self.transit_subject, self.natal_subject, **chart_params)
                elif chart_type == "synastry":
                    chart = KerykeionChartSVG(self.natal_subject, self.transit_subject, **chart_params)
                elif chart_type == "composite":
                    chart = KerykeionChartSVG(self.natal_subject, **chart_params) # self.natal_subject is the composite_subject
                else:
                    chart = KerykeionChartSVG(self.natal_subject, **chart_params) # Default to natal

                # The `show_aspects` parameter is now passed to KerykeionChartSVG constructor.
                # The old logic to manually clear aspects_settings if show_aspects is False is no longer needed here.
                # if not config["show_aspects"] and hasattr(chart, 'aspects_settings'):
                #    chart.aspects_settings = {} # Or an empty list, depending on Kerykeion's expectation

                # Kerykeion v4 typically generates SVG by calling makeSVG() which writes to a file.
                # It usually does not have get_svg_string() or makeSVG(get_svg=True).
                print(f"Calling KerykeionChartSVG.makeSVG() for chart_type: {chart_type} in dir: {temp_path}")
                chart.makeSVG()

                svg_content = None
                # Attempt to read from file first (most reliable for K4)
                # Kerykeion typically names the file based on the subject's name or type.
                # Example: Natal_Chart_John_Doe.svg or Transit_Chart_Event.svg
                # We need a robust way to find the generated file.
                # Assuming Kerykeion uses subject name and chart type in filename.
                # A simpler way is to list all SVGs in temp_dir and pick the newest one if only one chart is made.
                
                svg_files = list(temp_path.glob("*.svg"))
                if not svg_files:
                    # Check for .xml as Kerykeion sometimes used that extension for SVG data.
                    svg_files = list(temp_path.glob("*.xml"))

                if svg_files:
                    svg_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    svg_file_path = svg_files[0]
                    with open(svg_file_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    print(f"Retrieved SVG from file: {svg_file_path}")
                else: # Fallback to checking attributes, though less likely for K4
                    if hasattr(chart, 'svg_string') and chart.svg_string:
                        svg_content = chart.svg_string
                        print("Retrieved SVG from chart.svg_string attribute.")
                    elif hasattr(chart, 'svg') and chart.svg:
                        svg_content = chart.svg
                        print("Retrieved SVG from chart.svg attribute.")
                
                if not svg_content:
                    raise FileNotFoundError(f"Nenhum arquivo SVG foi gerado por KerykeionChartSVG.makeSVG() no diretório {temp_path} ou encontrado nos atributos.")

                # Otimizar SVG para melhor qualidade
                if high_quality: # high_quality is a parameter of generate_enhanced_svg
                    svg_content = self._optimize_svg_output(svg_content, chart_type)
                
                return svg_content
                
            except Exception as e:
                raise Exception(f"Erro ao gerar SVG aprimorado: {str(e)}")

    def generate_multiple_formats(
        self,
        chart_type: str = "natal",
        theme: str = "light",
        formats: List[str] = ["svg"]
    ) -> Dict[str, str]:
        """
        Gera o chart em múltiplos formatos.
        
        Args:
            chart_type: Tipo do chart
            theme: Tema do chart
            formats: Lista de formatos desejados ["svg", "png", "pdf"]
            
        Returns:
            Dicionário com formato -> conteúdo
        """
        results = {}
        
        # Gerar SVG base
        svg_content = self.generate_enhanced_svg(chart_type, theme)
        results["svg"] = svg_content
        
        # TODO: Implementar conversão para outros formatos se necessário
        # Para PNG e PDF, seria necessário usar bibliotecas como cairosvg ou wkhtmltopdf
        
        return results

    def get_chart_info(self, chart_type: str = "natal") -> Dict[str, Any]:
        """
        Retorna informações detalhadas sobre o chart que será gerado.
        
        Args:
            chart_type: Tipo do chart
            
        Returns:
            Dicionário com informações do chart
        """
        self._validate_chart_data(chart_type)
        
        info = {
            "chart_type": chart_type,
            "primary_subject": {
                "name": self.natal_subject.name,
                "birth_date": f"{self.natal_subject.day}/{self.natal_subject.month}/{self.natal_subject.year}",
                "birth_time": f"{self.natal_subject.hour:02d}:{self.natal_subject.minute:02d}",
                "location": f"Lat: {self.natal_subject.lat}, Lon: {self.natal_subject.lng}"
            }
        }
        
        if self.transit_subject and chart_type in ["transit", "synastry"]:
            info["secondary_subject"] = {
                "name": self.transit_subject.name,
                "birth_date": f"{self.transit_subject.day}/{self.transit_subject.month}/{self.transit_subject.year}",
                "birth_time": f"{self.transit_subject.hour:02d}:{self.transit_subject.minute:02d}",
                "location": f"Lat: {self.transit_subject.lat}, Lon: {self.transit_subject.lng}"
            }
        
        return info