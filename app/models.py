"""
Modelos Pydantic para a API de Astrologia AstroManus.

Este arquivo contém os modelos de dados necessários para os endpoints SVG.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

# Enums
class HouseSystem(str, Enum):
    PLACIDUS = "placidus"
    KOCH = "koch"
    REGIOMONTANUS = "regiomontanus"
    CAMPANUS = "campanus"
    EQUAL = "equal"
    WHOLE_SIGN = "whole_sign"
    
# Mapeamento de sistemas de casas para identificadores do Kerykeion
HOUSE_SYSTEM_MAP = {
    "placidus": "P",
    "koch": "K",
    "regiomontanus": "R",
    "campanus": "C",
    "equal": "E",
    "whole_sign": "W"
}

# Modelos Básicos
class PlanetPosition(BaseModel):
    name: str
    sign: str
    sign_num: int
    position: float # In-sign longitude
    abs_pos: float  # Absolute ecliptical longitude
    house_name: str # Textual name, e.g., "First_House"
    house_number: int # Integer number of the house, e.g., 1
    speed: float = 0.0
    retrograde: bool = False
    quality: Optional[str] = None # Quality of the sign the planet is in
    element: Optional[str] = None # Element of the sign the planet is in
    emoji: Optional[str] = None   # Emoji of the sign the planet is in

class NatalChartRequest(BaseModel):
    name: Optional[str] = Field(None, description="Nome da pessoa ou evento")
    year: int = Field(..., description="Ano de nascimento")
    month: int = Field(..., description="Mês de nascimento (1-12)")
    day: int = Field(..., description="Dia de nascimento (1-31)")
    hour: int = Field(..., description="Hora de nascimento (0-23)")
    minute: int = Field(..., description="Minuto de nascimento (0-59)")
    latitude: float = Field(..., description="Latitude do local de nascimento")
    longitude: float = Field(..., description="Longitude do local de nascimento")
    tz_str: str = Field(..., description="String de fuso horário (ex: 'America/Sao_Paulo')")
    house_system: HouseSystem = Field(HouseSystem.PLACIDUS, description="Sistema de casas a ser usado")
    zodiac_type: Optional[str] = Field("Tropic", description="Tipo de Zodíaco: 'Tropic' (padrão) ou 'Sidereal'")
    sidereal_mode: Optional[str] = Field(None, description="Modo Sidereal (Ayanamsha), ex: 'Lahiri'. Relevante apenas se zodiac_type='Sidereal'")
    perspective_type: Optional[str] = Field("Apparent Geocentric", description="Perspectiva de cálculo: 'Apparent Geocentric' (padrão), 'True Geocentric', ou 'Heliocentric'")

class TransitRequest(BaseModel):
    year: int = Field(..., description="Ano do trânsito")
    month: int = Field(..., description="Mês do trânsito (1-12)")
    day: int = Field(..., description="Dia do trânsito (1-31)")
    hour: int = Field(..., description="Hora do trânsito (0-23)")
    minute: int = Field(..., description="Minuto do trânsito (0-59)")
    latitude: float = Field(..., description="Latitude do local para cálculo do trânsito")
    longitude: float = Field(..., description="Longitude do local para cálculo do trânsito")
    tz_str: str = Field(..., description="String de fuso horário (ex: 'America/Sao_Paulo')")
    house_system: HouseSystem = Field(HouseSystem.PLACIDUS, description="Sistema de casas a ser usado")
    name: Optional[str] = Field(None, description="Nome opcional para o trânsito (ex: 'Trânsitos 2025')")
    zodiac_type: Optional[str] = Field("Tropic", description="Tipo de Zodíaco: 'Tropic' (padrão) ou 'Sidereal'")
    sidereal_mode: Optional[str] = Field(None, description="Modo Sidereal (Ayanamsha), ex: 'Lahiri'. Relevante apenas se zodiac_type='Sidereal'")
    perspective_type: Optional[str] = Field("Apparent Geocentric", description="Perspectiva de cálculo: 'Apparent Geocentric' (padrão), 'True Geocentric', ou 'Heliocentric'")

# Modelo para Gráficos SVG
class SVGChartRequest(BaseModel):
    natal_chart: NatalChartRequest
    transit_chart: Optional[TransitRequest] = Field(None, description="Dados do mapa de trânsito (para chart_type 'transit' ou 'combined') ou dados do segundo mapa natal (para chart_type 'composite').")
    chart_type: Literal["natal", "transit", "combined", "composite"] = Field(..., description="Tipo de gráfico: natal, trânsito, combinado (sinastria) ou composto")
    theme: str = Field("Kerykeion", description="Tema visual para o gráfico SVG")

    class Config:
        schema_extra = {
            "example": {
                "natal_chart": {
                    "name": "João Silva",
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "minute": 30,
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "tz_str": "America/Sao_Paulo",
                    "house_system": "placidus"
                },
                "transit_chart": {
                    "name": "Trânsitos Atuais",
                    "year": 2024,
                    "month": 12,
                    "day": 1,
                    "hour": 12,
                    "minute": 0,
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "tz_str": "America/Sao_Paulo",
                    "house_system": "placidus"
                },
                "chart_type": "combined",
                "theme": "Kerykeion"
            }
        }

# Modelo para SVG combinado (para compatibilidade com código existente)
class SVGCombinedChartRequest(BaseModel):
    """
    Modelo para requisição de gráfico SVG combinado de mapa natal e trânsitos.
    """
    natal_chart: NatalChartRequest = Field(..., description="Dados do mapa natal")
    transit_chart: TransitRequest = Field(..., description="Dados do trânsito")
    
    class Config:
        schema_extra = {
            "example": {
                "natal_chart": {
                    "name": "João",
                    "year": 1997,
                    "month": 10,
                    "day": 13,
                    "hour": 22,
                    "minute": 0,
                    "latitude": -3.7172,
                    "longitude": -38.5247,
                    "tz_str": "America/Fortaleza",
                    "house_system": "placidus"
                },
                "transit_chart": {
                    "name": "Trânsitos 2025",
                    "year": 2025,
                    "month": 6,
                    "day": 2,
                    "hour": 12,
                    "minute": 0,
                    "latitude": -3.7172,
                    "longitude": -38.5247,
                    "tz_str": "America/Fortaleza",
                    "house_system": "placidus"
                }
            }
        }


# Modelos de Resposta
class PlanetData(BaseModel):
    name: str
    sign: str
    sign_num: int
    position: float
    abs_pos: float
    house_name: str
    house_number: Optional[int] = Field(None, description="Número da casa (1-12)")
    speed: float = 0.0
    retrograde: bool = False
    quality: Optional[str] = Field(None, description="Qualidade do signo (Cardinal, Fixo, Mutável)")
    element: Optional[str] = Field(None, description="Elemento do signo (Fogo, Terra, Ar, Água)")
    emoji: Optional[str] = Field(None, description="Emoji Unicode para o signo do planeta")

class HouseCuspData(BaseModel):
    house: int
    sign: str
    position: float
    quality: Optional[str] = Field(None, description="Qualidade do signo (Cardinal, Fixo, Mutável)")
    element: Optional[str] = Field(None, description="Elemento do signo (Fogo, Terra, Ar, Água)")
    emoji: Optional[str] = Field(None, description="Emoji Unicode para o signo da cúspide")

class AspectData(BaseModel):
    planet1: str
    planet2: str
    aspect: str
    orb: float
    applying: bool = False

class NatalChartResponse(BaseModel):
    name: Optional[str] = None
    birth_date: str
    birth_time: str
    location: str
    planets: List[PlanetData]
    houses: List[HouseCuspData]
    aspects: List[AspectData]
    chart_info: Dict[str, Any]

class TransitResponse(BaseModel):
    name: Optional[str] = None
    transit_date: str
    transit_time: str
    location: str
    transiting_planets: List[PlanetData]
    aspects_to_natal: List[AspectData]
    chart_info: Dict[str, Any]


# Modelos para Sinastria
class SynastryRequest(BaseModel):
    person1: NatalChartRequest = Field(..., description="Dados da primeira pessoa")
    person2: NatalChartRequest = Field(..., description="Dados da segunda pessoa")

class SynastryAspect(BaseModel):
    planet1: str
    person1: str
    planet2: str
    person2: str
    aspect: str
    orb: float
    applying: bool = False

class SynastryResponse(BaseModel):
    person1_name: Optional[str] = None
    person2_name: Optional[str] = None
    aspects: List[SynastryAspect]
    compatibility_score: float
    chart_info: Dict[str, Any]


# Modelos para Trânsitos em Período
class TransitEventData(BaseModel):
    date: str = Field(..., description="Data do evento de trânsito (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Hora aproximada do evento (HH:MM), se aplicável")
    transiting_planet: str = Field(..., description="Planeta em trânsito")
    aspect_type: str = Field(..., description="Tipo de aspecto (ex: 'conjunction', 'square')")
    natal_planet_or_point: str = Field(..., description="Planeta ou ponto natal aspectado")
    orb: float = Field(..., description="Orbe do aspecto no momento do evento (graus)")
    is_applying: Optional[bool] = Field(None, description="Indica se o aspecto está se formando (aplicando)")
    # Considerar adicionar:
    # exactness_score: Optional[float] = Field(None, description="Pontuação de quão exato é o aspecto (ex: 1 - orb/max_orb)")
    # description: Optional[str] = Field(None, description="Breve descrição do evento")

class TransitRangeRequest(BaseModel):
    natal_data: NatalChartRequest = Field(..., description="Dados do mapa natal de base")
    start_date: str = Field(..., description="Data de início (YYYY-MM-DD)") # Validar formato YYYY-MM-DD
    end_date: str = Field(..., description="Data de fim (YYYY-MM-DD)")   # Validar formato YYYY-MM-DD
    transiting_planets: Optional[List[str]] = Field(None, description="Lista de planetas em trânsito a considerar (ex: ['Mars', 'Jupiter']). Padrão considera os principais.")
    natal_points: Optional[List[str]] = Field(None, description="Lista de planetas/pontos natais a considerar (ex: ['Sun', 'Ascendant']). Padrão considera os principais.")
    aspect_types: Optional[List[str]] = Field(None, description="Lista de tipos de aspecto a considerar (ex: ['conjunction', 'trine']). Padrão considera os principais.")
    step: Literal["exact", "day", "week", "month"] = Field("exact", description="Granularidade do cálculo: 'exact' para todos os eventos precisos, ou 'day', 'week', 'month' para snapshots periódicos.")
    # orb_tolerance_multiplier: Optional[float] = Field(1.0, description="Multiplicador para orbes de aspecto. >1 para mais largo, <1 para mais apertado.")

class TransitRangeResponse(BaseModel):
    request_data: TransitRangeRequest = Field(..., description="Dados da requisição original")
    events: List[TransitEventData] = Field(..., description="Lista de eventos de trânsito encontrados no período")
    summary: Optional[Dict[str, Any]] = Field(None, description="Sumário dos trânsitos (ex: contagem por planeta/aspecto)")


# Modelos para Retorno Solar (movidos de moon_solar_router.py)
class SolarReturnRequestModel(BaseModel): # Renaming to avoid potential conflicts if imported directly where old one was
    year: int = Field(..., description="Ano de nascimento")
    month: int = Field(..., description="Mês de nascimento")
    day: int = Field(..., description="Dia de nascimento")
    hour: int = Field(..., description="Hora de nascimento")
    minute: int = Field(..., description="Minuto de nascimento")
    latitude: float = Field(..., description="Latitude do local de nascimento")
    longitude: float = Field(..., description="Longitude do local de nascimento")
    tz_str: str = Field(..., description="Timezone do local de nascimento")
    return_year: int = Field(..., description="Ano para o qual o Retorno Solar será calculado")
    # Incluir os campos de NatalChartRequest para consistência e para que create_subject funcione diretamente
    name: Optional[str] = Field(None, description="Nome da pessoa ou evento (para o mapa natal base)")
    house_system: Optional[HouseSystem] = Field(HouseSystem.PLACIDUS, description="Sistema de casas para o mapa natal base")
    zodiac_type: Optional[str] = Field("Tropic", description="Tipo de Zodíaco para o mapa natal base")
    sidereal_mode: Optional[str] = Field(None, description="Modo Sidereal para o mapa natal base")
    perspective_type: Optional[str] = Field("Apparent Geocentric", description="Perspectiva para o mapa natal base")

# Detalhes do mapa de Retorno Solar
class SolarReturnChartDetails(BaseModel):
    name: str = Field(description="Nome do mapa de Retorno Solar (ex: Solar Return 2024)")
    planets: Dict[str, PlanetData] = Field(..., description="Planetas no mapa de Retorno Solar")
    houses: Dict[str, HouseCuspData] = Field(..., description="Cúspides das casas no mapa de Retorno Solar")
    ascendant: HouseCuspData = Field(..., description="Ascendente do Retorno Solar")
    midheaven: HouseCuspData = Field(..., description="Meio do Céu do Retorno Solar")
    aspects: List[AspectData] = Field(..., description="Aspectos no mapa de Retorno Solar")
    house_system: Optional[str] = Field(None, description="Sistema de casas usado")
    zodiac_type: Optional[str] = Field(None, description="Tipo de Zodíaco do Retorno Solar")
    # perspective_type: Optional[str] = Field(None, description="Perspectiva de cálculo do Retorno Solar") # Could be added if needed


class SolarReturnResponseModel(BaseModel):
    precise_solar_return_datetime_utc: Optional[str] = Field(None, description="Data e hora exatas do Retorno Solar em UTC (se calculado com precisão)")
    highlights: List[str] = Field(..., description="Destaques do retorno solar")
    solar_return_chart_details: Optional[SolarReturnChartDetails] = Field(None, description="Detalhes completos do mapa de Retorno Solar (se calculado)")


# Modelos para Retorno Lunar
class LunarReturnRequest(BaseModel):
    natal_data: NatalChartRequest = Field(..., description="Dados do mapa natal de base")
    search_start_date: str = Field(..., description="Data de início para buscar o próximo Retorno Lunar (YYYY-MM-DD)")
    # Consider adding optional parameters from NatalChartRequest for the LR chart context if needed,
    # e.g., house_system, zodiac_type, etc., if they can differ from natal_data for the LR calculation.
    # For now, assuming these will be derived from natal_data or a default for the LR chart.

class LunarReturnChartDetails(BaseModel):
    name: str = Field(description="Nome do mapa de Retorno Lunar (ex: Lunar Return YYYY-MM)")
    planets: Dict[str, PlanetData] = Field(..., description="Planetas no mapa de Retorno Lunar")
    houses: Dict[str, HouseCuspData] = Field(..., description="Cúspides das casas no mapa de Retorno Lunar")
    ascendant: HouseCuspData = Field(..., description="Ascendente do Retorno Lunar")
    midheaven: HouseCuspData = Field(..., description="Meio do Céu do Retorno Lunar")
    aspects: List[AspectData] = Field(..., description="Aspectos no mapa de Retorno Lunar")
    house_system: Optional[str] = Field(None, description="Sistema de casas usado no Retorno Lunar")
    zodiac_type: Optional[str] = Field(None, description="Tipo de Zodíaco do Retorno Lunar")
    # perspective_type: Optional[str] = Field(None, description="Perspectiva de cálculo do Retorno Lunar")

class LunarReturnResponse(BaseModel):
    request_data: LunarReturnRequest = Field(..., description="Dados da requisição original")
    precise_lunar_return_datetime_utc: Optional[str] = Field(None, description="Data e hora exatas do Retorno Lunar em UTC")
    lunar_return_chart_details: Optional[LunarReturnChartDetails] = Field(None, description="Detalhes completos do mapa de Retorno Lunar")
    highlights: Optional[List[str]] = Field(None, description="Destaques astrológicos do Retorno Lunar")


# Modelos para Mapa Composto
class CompositeChartRequest(BaseModel):
    person1_natal_data: NatalChartRequest = Field(..., description="Dados do mapa natal da Pessoa 1")
    person2_natal_data: NatalChartRequest = Field(..., description="Dados do mapa natal da Pessoa 2")
    # Adicionar opções de cálculo de composto se Kerykeion suportar (ex: método de ponto médio, Davison)
    # Por enquanto, assume-se ponto médio, que é comum.

class CompositeChartDetails(BaseModel):
    name: str = Field(description="Nome do mapa composto (ex: Composto Pessoa1 & Pessoa2)")
    planets: Dict[str, PlanetData] = Field(..., description="Planetas no mapa composto")
    # Casas em mapas compostos de ponto médio são um tópico debatido e calculadas de formas variadas.
    # O CompositeSubjectFactory do Kerykeion pode ou não fornecê-las.
    # Incluindo como opcionais por agora.
    houses: Optional[Dict[str, HouseCuspData]] = Field(None, description="Cúspides das casas no mapa composto (se aplicável)")
    ascendant: Optional[HouseCuspData] = Field(None, description="Ascendente do mapa composto (se aplicável)")
    midheaven: Optional[HouseCuspData] = Field(None, description="Meio do Céu do mapa composto (se aplicável)")
    aspects: List[AspectData] = Field(..., description="Aspectos no mapa composto")
    # Mapas compostos geralmente usam o mesmo tipo de zodíaco das entradas.
    zodiac_type: Optional[str] = Field(None, description="Tipo de Zodíaco do mapa composto")
    # house_system não é necessário se as casas não são padrão ou derivadas de forma diferente.

class CompositeChartResponse(BaseModel):
    request_data: CompositeChartRequest = Field(..., description="Dados da requisição original")
    composite_chart_details: Optional[CompositeChartDetails] = Field(None, description="Detalhes completos do mapa composto")
    # Destaques ou interpretações podem ser adicionados aqui no futuro.
    # highlights: Optional[List[str]] = Field(None, description="Destaques astrológicos do Mapa Composto")
