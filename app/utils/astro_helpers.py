"""
Módulo de utilidades para funções compartilhadas entre os routers da API de Astrologia.
Centraliza funções auxiliares para evitar duplicação de código e facilitar manutenção.

Este módulo contém:
- Funções para criação de subjects astrológicos
- Extração de dados planetários
- Cálculo centralizado de aspectos
- Constantes e mapeamentos
- Utilitários de conversão
- Resolução de localização integrada
"""

import math
from datetime import date
from typing import Optional, Dict, Any, List, Union, Tuple
from kerykeion import AstrologicalSubject
from fastapi import HTTPException # Added for error handling
from app.models import (
    NatalChartRequest, TransitRequest, PlanetPosition,
    HOUSE_SYSTEM_MAP
)
from app.utils.astro_geolocation import get_coordinates_from_city
from app.utils.daylight_saving import get_timezone_info
import os # Added for os.getenv

def resolve_location(data: Union[NatalChartRequest, TransitRequest, Dict]) -> Tuple[float, float, str, Dict]:
    """
    Resolve os dados de localização a partir dos campos fornecidos.
    Prioriza city se fornecida, senão usa latitude/longitude.
    
    Args:
        data: Dados da requisição contendo informações de localização
        
    Returns:
        Tuple: (latitude, longitude, timezone_str, location_info)
        
    Raises:
        ValueError: Se não for possível resolver a localização
    """
    # Suporte tanto para objetos Pydantic quanto dicionários
    if isinstance(data, dict):
        city = data.get('city')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        tz_str = data.get('tz_str')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
    else:
        city = getattr(data, 'city', None)
        latitude = getattr(data, 'latitude', None)
        longitude = getattr(data, 'longitude', None)
        tz_str = getattr(data, 'tz_str', None)
        year = data.year
        month = data.month
        day = data.day
    
    location_info = {}
    
    # Se city foi fornecida, usar geolocalização
    if city:
        print(f"Resolvendo localização para cidade: {city}")
        coords = get_coordinates_from_city(city)
        if coords:
            resolved_lat, resolved_lng, resolved_tz = coords
            location_info = {
                "method": "geolocation",
                "input_city": city,
                "resolved_latitude": resolved_lat,
                "resolved_longitude": resolved_lng,
                "resolved_timezone": resolved_tz
            }
            
            # Verificar horário de verão para a data específica
            check_date = date(year, month, day)
            tz_info = get_timezone_info(check_date, resolved_tz)
            location_info["timezone_info"] = tz_info
            
            return resolved_lat, resolved_lng, resolved_tz, location_info
        else:
            raise ValueError(f"Não foi possível resolver a localização para a cidade: {city}")
    
    # Se latitude/longitude foram fornecidas
    elif latitude is not None and longitude is not None:
        if tz_str:
            location_info = {
                "method": "coordinates",
                "input_latitude": latitude,
                "input_longitude": longitude,
                "input_timezone": tz_str
            }
            
            # Verificar horário de verão para a data específica
            check_date = date(year, month, day)
            tz_info = get_timezone_info(check_date, tz_str)
            location_info["timezone_info"] = tz_info
            
            return latitude, longitude, tz_str, location_info
        else:
            raise ValueError("Timezone (tz_str) é obrigatório quando usando coordenadas latitude/longitude")
    
    else:
        raise ValueError("É necessário fornecer 'city' ou ('latitude' + 'longitude' + 'tz_str')")


def create_subject(data: Union[NatalChartRequest, TransitRequest, Dict], default_name: str) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Cria um objeto AstrologicalSubject (ou similar, Kerykeion v5) a partir dos dados da requisição.
    Agora inclui resolução automática de localização e tenta usar Kerykeion v5 factory methods.
    
    Args:
        data: Dados do mapa natal ou trânsito (objeto Pydantic ou dict)
        default_name: Nome padrão a ser usado se não especificado
        
    Returns:
        Tuple: (Kerykeion Subject Object, location_info_dict)
        
    Raises:
        AttributeError: Se dados obrigatórios estiverem ausentes
        ValueError: Se não for possível resolver localização
    """
    # Suporte tanto para objetos Pydantic quanto dicionários
    if isinstance(data, dict):
        house_system = data.get('house_system', 'placidus')
        name = data.get('name', default_name)
        year = data['year']
        month = data['month']
        day = data['day']
        hour = data['hour']
        minute = data['minute']
    else:
        house_system = getattr(data, 'house_system', 'placidus')
        name = getattr(data, 'name', default_name)
        year = data.year
        month = data.month
        day = data.day
        hour = data.hour
        minute = data.minute
    
    # Resolver localização
    latitude, longitude, tz_str, location_info = resolve_location(data)
    
    # Converter enum para string se necessário
    if hasattr(house_system, 'value'):
        house_system = house_system.value # Now house_system is a string like "placidus"

    house_system_code = HOUSE_SYSTEM_MAP.get(house_system, "P") # Get code like "P"

    # Extract zodiac_type and sidereal_mode from data
    if isinstance(data, dict):
        zodiac_type = data.get("zodiac_type", "Tropic")
        sidereal_mode = data.get("sidereal_mode")
        perspective_type = data.get("perspective_type", "Apparent Geocentric")
    else:
        zodiac_type = getattr(data, "zodiac_type", "Tropic")
        sidereal_mode = getattr(data, "sidereal_mode", None)
        perspective_type = getattr(data, "perspective_type", "Apparent Geocentric")

    # The all_location_details_explicitly_provided logic and subject_params dictionary are less critical
    # if we pass parameters directly, and geonames_username/online are not used.

    try:
        print(f"Attempting K4 AstrologicalSubject constructor for: {name or default_name}")

        k_subject = AstrologicalSubject(
            name or default_name,
            year, month, day, hour, minute,
            lng=longitude,
            lat=latitude,
            tz_str=tz_str,
            houses_system_identifier=house_system_code,
            zodiac_type=zodiac_type,
            sidereal_mode=sidereal_mode if zodiac_type.lower() == "sidereal" else None,
            perspective_type=perspective_type,
        )

        if not k_subject:
            raise ValueError("Failed to create AstrologicalSubject instance (K4 style).")

        return k_subject, location_info

    except Exception as e:
        # Include more details in the error for debugging
        error_params = {
            "name": name or default_name, "year": year, "month": month, "day": day, "hour": hour, "minute": minute,
            "lat": latitude, "lng": longitude, "tz_str": tz_str, "house_system_code": house_system_code,
            "zodiac_type": zodiac_type, "sidereal_mode": sidereal_mode
        }
        print(f"Error creating AstrologicalSubject (K4 style): {type(e).__name__} - {e}. Params: {error_params}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor ao criar objeto astrológico (Kerykeion v4): {type(e).__name__} - {e}")


def get_house_from_kerykeion_attribute(planet_obj) -> int:
    """
    Extrai o número da casa do atributo 'house' do Kerykeion.
    
    Args:
        planet_obj: Objeto planeta do Kerykeion
        
    Returns:
        Número da casa (1-12), retorna 1 se não puder determinar
    """
    try:
        if hasattr(planet_obj, 'house'):
            house_str = str(planet_obj.house)
            house_mapping = {
                'First_House': 1, 'Second_House': 2, 'Third_House': 3, 'Fourth_House': 4,
                'Fifth_House': 5, 'Sixth_House': 6, 'Seventh_House': 7, 'Eighth_House': 8,
                'Ninth_House': 9, 'Tenth_House': 10, 'Eleventh_House': 11, 'Twelfth_House': 12
            }
            return house_mapping.get(house_str, 1)
        return 1
    except Exception:
        return 1


def get_planet_data(subject: Any, planet_name_kerykeion: str, api_planet_name: str) -> Optional[PlanetPosition]: # Changed subject type hint to Any
    """
    Extrai dados de um planeta do objeto AstrologicalSubject.
    
    Args:
        subject: Objeto AstrologicalSubject contendo os dados do mapa
        planet_name_kerykeion: Nome do planeta no Kerykeion (ex: 'sun', 'moon')
        api_planet_name: Nome do planeta na API (ex: 'Sun', 'Moon')
        
    Returns:
        Objeto PlanetPosition com os dados do planeta ou None se não encontrado
    """
    try:
        p = getattr(subject, planet_name_kerykeion.lower())
        if p and hasattr(p, 'name') and p.name:
            return PlanetPosition(
                name=api_planet_name,
                sign=p.sign,
                sign_num=p.sign_num,
                position=round(p.position, 4),
                abs_pos=round(p.abs_pos, 4),
                house_name=str(p.house),
                house_number=get_house_from_kerykeion_attribute(p),
                speed=round(p.speed, 4) if hasattr(p, 'speed') else 0.0,
                retrograde=p.retrograde if hasattr(p, 'retrograde') else False,
                quality=p.quality if hasattr(p, 'quality') else None,
                element=p.element if hasattr(p, 'element') else None,
                emoji=p.sign_emoji if hasattr(p, 'sign_emoji') else None
            )
    except AttributeError:
        pass
    return None


def calculate_aspects(
    planets1: Dict[str, Any], 
    planets2: Dict[str, Any], 
    aspect_type: str = "natal",
    orb_multiplier: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Calcula aspectos entre dois conjuntos de planetas (função centralizada).
    """
    aspects = []
    aspect_definitions = {
        0: ("conjunction", 8), 60: ("sextile", 6), 90: ("square", 7),
        120: ("trine", 8), 180: ("opposition", 8), 150: ("quincunx", 3),
        30: ("semisextile", 2), 45: ("semisquare", 2), 135: ("sesquiquadrate", 2),
        72: ("quintile", 2), 144: ("biquintile", 2)
    }
    adjusted_aspects = {
        angle: (name, orb * orb_multiplier) 
        for angle, (name, orb) in aspect_definitions.items()
    }
    planet_keys1 = list(planets1.keys())
    planet_keys2 = list(planets2.keys()) if planets1 != planets2 else planet_keys1
    
    for i, planet1_key in enumerate(planet_keys1):
        planet1 = planets1[planet1_key]
        start_idx = i + 1 if planets1 == planets2 else 0
        for j, planet2_key in enumerate(planet_keys2[start_idx:], start=start_idx):
            planet2 = planets2[planet2_key]
            if planets1 == planets2 and planet1_key == planet2_key:
                continue
            pos1 = _get_planet_position(planet1)
            pos2 = _get_planet_position(planet2)
            if pos1 is None or pos2 is None:
                continue
            angular_diff = _calculate_angular_difference(pos1, pos2)
            for aspect_angle, (aspect_name, orb_tolerance) in adjusted_aspects.items():
                orb = abs(angular_diff - aspect_angle)
                if orb <= orb_tolerance:
                    strength = _calculate_aspect_strength(orb, orb_tolerance)
                    planet1_name = _get_planet_name(planet1, planet1_key)
                    planet2_name = _get_planet_name(planet2, planet2_key)
                    aspect_data = {
                        "p1": planet1_name, "p2": planet2_name, "type": aspect_name,
                        "orb": round(orb, 2), "exact_angle": round(angular_diff, 2),
                        "strength": strength, "aspect_type": aspect_type,
                        "interpretation": _get_aspect_interpretation(aspect_name, planet1_name, planet2_name)
                    }
                    if aspect_type == "natal":
                        aspect_data["category"] = _get_natal_aspect_category(aspect_name)
                    elif aspect_type == "transit":
                        aspect_data["duration"] = _estimate_transit_duration(aspect_name, planet1_name, planet2_name)
                    aspects.append(aspect_data)
    
    aspects.sort(key=lambda x: x['strength'], reverse=True)
    major_aspects = [a for a in aspects if a['type'] in ['conjunction', 'opposition', 'trine', 'square', 'sextile']]
    minor_aspects = [a for a in aspects if a['type'] not in ['conjunction', 'opposition', 'trine', 'square', 'sextile']]
    return major_aspects + minor_aspects[:10]


def _get_planet_position(planet_data: Union[Dict, Any]) -> Optional[float]:
    if isinstance(planet_data, dict):
        return planet_data.get('position')
    elif hasattr(planet_data, 'position'):
        return planet_data.position
    return None


def _get_planet_name(planet_data: Union[Dict, Any], fallback_key: str) -> str:
    if isinstance(planet_data, dict):
        return planet_data.get('name', fallback_key)
    elif hasattr(planet_data, 'name'):
        return planet_data.name
    return fallback_key


def _calculate_angular_difference(pos1: float, pos2: float) -> float:
    diff = abs(pos1 - pos2)
    return min(diff, 360 - diff)


def _calculate_aspect_strength(orb: float, max_orb: float) -> float:
    if max_orb == 0:
        return 100.0
    return round((max_orb - orb) / max_orb * 100, 1)


def _get_aspect_interpretation(aspect_type: str, planet1: str, planet2: str) -> str:
    interpretations = {
        "conjunction": f"União e fusão das energias de {planet1} e {planet2}",
        "opposition": f"Tensão e polaridade entre {planet1} e {planet2}",
        "trine": f"Fluxo harmonioso entre {planet1} e {planet2}",
        "square": f"Desafio e tensão dinâmica entre {planet1} e {planet2}",
        "sextile": f"Oportunidade de cooperação entre {planet1} e {planet2}",
        "quincunx": f"Necessidade de ajuste entre {planet1} e {planet2}",
        "semisextile": f"Conexão sutil entre {planet1} e {planet2}",
        "semisquare": f"Irritação menor entre {planet1} e {planet2}",
        "sesquiquadrate": f"Tensão crescente entre {planet1} e {planet2}",
        "quintile": f"Potencial criativo entre {planet1} e {planet2}",
        "biquintile": f"Talento especial na combinação {planet1}-{planet2}"
    }
    return interpretations.get(aspect_type, f"Aspecto {aspect_type} entre {planet1} e {planet2}")


def _get_natal_aspect_category(aspect_type: str) -> str:
    categories = {
        "conjunction": "fusão", "opposition": "polaridade", "trine": "harmonia",
        "square": "tensão", "sextile": "oportunidade", "quincunx": "ajuste",
        "semisextile": "conexão", "semisquare": "irritação", "sesquiquadrate": "pressão",
        "quintile": "criatividade", "biquintile": "talento"
    }
    return categories.get(aspect_type, "neutro")


def _estimate_transit_duration(aspect_type: str, planet1: str, planet2: str) -> str:
    planet_speeds = {
        "Sun": 1.0, "Moon": 13.0, "Mercury": 1.4, "Venus": 1.2, "Mars": 0.5,
        "Jupiter": 0.08, "Saturn": 0.03, "Uranus": 0.01, "Neptune": 0.006, "Pluto": 0.004
    }
    aspect_orbs = {"conjunction": 8, "opposition": 8, "trine": 8, "square": 7, "sextile": 6}
    speed1 = planet_speeds.get(planet1, 0.5)
    speed2 = planet_speeds.get(planet2, 0.5)
    faster_speed = max(speed1, speed2)
    orb = aspect_orbs.get(aspect_type, 5)
    duration_days = (orb * 2) / faster_speed
    if duration_days < 1: return "algumas horas"
    elif duration_days < 7: return f"cerca de {int(duration_days)} dias"
    elif duration_days < 30: return f"cerca de {int(duration_days/7)} semanas"
    elif duration_days < 365: return f"cerca de {int(duration_days/30)} meses"
    else: return f"cerca de {int(duration_days/365)} anos"


def degrees_to_dms(degrees: float) -> str:
    deg = int(degrees)
    minutes = (degrees - deg) * 60
    min_int = int(minutes)
    seconds = (minutes - min_int) * 60
    sec_int = int(seconds)
    return f"{deg}°{min_int:02d}'{sec_int:02d}\""


def normalize_angle(angle: float) -> float:
    while angle < 0: angle += 360
    while angle >= 360: angle -= 360
    return angle


def get_sign_from_position(position: float) -> Tuple[str, int]:
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_num = int(position // 30)
    sign_name = signs[sign_num]
    return sign_name, sign_num + 1


def calculate_midpoint(pos1: float, pos2: float) -> float:
    diff = abs(pos1 - pos2)
    midpoint = (pos1 + pos2) / 2
    if diff > 180:
        midpoint = (pos1 + pos2 + 360) / 2
        if midpoint >= 360: midpoint -= 360
    return normalize_angle(midpoint)


# === CONSTANTES COMPARTILHADAS ===
HOUSE_NUMBER_TO_NAME_BASE = {
    1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
    7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh", 12: "twelfth"
}
HOUSE_NAMES_FULL = {
    1: "Primeira Casa - Personalidade", 2: "Segunda Casa - Recursos",
    3: "Terceira Casa - Comunicação", 4: "Quarta Casa - Lar e Família",
    5: "Quinta Casa - Criatividade", 6: "Sexta Casa - Trabalho e Saúde",
    7: "Sétima Casa - Relacionamentos", 8: "Oitava Casa - Transformação",
    9: "Nona Casa - Filosofia", 10: "Décima Casa - Carreira",
    11: "Décima Primeira Casa - Amizades", 12: "Décima Segunda Casa - Subconsciente"
}
PLANETS_MAP = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars",
    "jupiter": "Jupiter", "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune",
    "pluto": "Pluto", "mean_node": "Mean_Node", "true_node": "True_Node",
}
ADDITIONAL_PLANETS_MAP = {
    "chiron": "Chiron", "lilith": "Lilith", "ceres": "Ceres",
    "pallas": "Pallas", "juno": "Juno", "vesta": "Vesta"
}
SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth", 
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}
SIGN_MODALITIES = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
}
PLANETARY_DIGNITIES = {
    "Sun": {"domicile": ["Leo"], "exaltation": ["Aries"], "detriment": ["Aquarius"], "fall": ["Libra"]},
    "Moon": {"domicile": ["Cancer"], "exaltation": ["Taurus"], "detriment": ["Capricorn"], "fall": ["Scorpio"]},
    "Mercury": {"domicile": ["Gemini", "Virgo"], "exaltation": ["Virgo"], "detriment": ["Sagittarius", "Pisces"], "fall": ["Pisces"]},
    "Venus": {"domicile": ["Taurus", "Libra"], "exaltation": ["Pisces"], "detriment": ["Scorpio", "Aries"], "fall": ["Virgo"]},
    "Mars": {"domicile": ["Aries", "Scorpio"], "exaltation": ["Capricorn"], "detriment": ["Libra", "Taurus"], "fall": ["Cancer"]},
    "Jupiter": {"domicile": ["Sagittarius", "Pisces"], "exaltation": ["Cancer"], "detriment": ["Gemini", "Virgo"], "fall": ["Capricorn"]},
    "Saturn": {"domicile": ["Capricorn", "Aquarius"], "exaltation": ["Libra"], "detriment": ["Cancer", "Leo"], "fall": ["Aries"]}
}