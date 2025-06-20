#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de Geolocalização para Aplicações de Astrologia

Este módulo fornece funcionalidades para obter dados de geolocalização
precisos necessários para cálculos astrológicos, incluindo:
- Coordenadas geográficas (latitude/longitude)
- Fuso horário local
- Elevação (altitude)
- Dados astronômicos relevantes

Autor: Manus AI
Versão: 1.0.0
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import requests
import time
import functools
import json
import math

class GeocodingCache:
    """Cache para evitar consultas repetidas de geocodificação e dados astronômicos"""
    def __init__(self, max_size=1000):
        self._cache = {}
        self._max_size = max_size
    
    def get(self, key):
        """Obtém um valor do cache se existir"""
        return self._cache.get(key)
    
    def set(self, key, value):
        """Armazena um valor no cache com controle de tamanho"""
        # Implementação simples de LRU: se o cache estiver cheio, limpa 20% dos itens
        if len(self._cache) >= self._max_size:
            # Remove 20% dos itens mais antigos
            remove_count = int(self._max_size * 0.2)
            keys_to_remove = list(self._cache.keys())[:remove_count]
            for k in keys_to_remove:
                del self._cache[k]
        
        self._cache[key] = value
    
    def clear(self):
        """Limpa todo o cache"""
        self._cache.clear()
    
    def size(self):
        """Retorna o número de itens no cache"""
        return len(self._cache)

# Caches globais
_geocoding_cache = GeocodingCache()
_timezone_cache = GeocodingCache()
_elevation_cache = GeocodingCache()
_astro_data_cache = GeocodingCache()

def rate_limit(min_interval=1.0):
    """
    Decorator para implementar rate limiting em chamadas de API
    
    Args:
        min_interval (float): Intervalo mínimo entre chamadas em segundos
    """
    def decorator(func):
        last_called = [0.0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(1.1)  # Nominatim permite 1 req/segundo, usando 1.1 para segurança
def geocode_location(location_name, use_cache=True, max_retries=3):
    """
    Converte um nome de local em coordenadas de latitude e longitude.
    Utiliza o serviço Nominatim do OpenStreetMap com melhorias.
    
    Args:
        location_name (str): Nome do local para geocodificar
        use_cache (bool): Se deve usar cache para consultas repetidas
        max_retries (int): Número máximo de tentativas em caso de timeout
    
    Returns:
        dict ou None: Dados da localização ou None se não encontrada
    """
    # Validação de entrada
    if not location_name or not isinstance(location_name, str):
        print("Erro: Nome da localização deve ser uma string não vazia.")
        return None
    
    location_name = location_name.strip()
    if not location_name:
        print("Erro: Nome da localização não pode estar vazio.")
        return None
    
    # Verificar cache
    if use_cache:
        cached_result = _geocoding_cache.get(location_name)
        if cached_result is not None:
            print(f"  (Resultado obtido do cache)")
            return cached_result
    
    # Configurar geolocalizador com user-agent mais específico
    geolocator = Nominatim(
        user_agent="astrology_app_geocoder_v1.0",
        timeout=10
    )
    
    # Tentar geocodificar com retry
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(location_name, timeout=10)
            
            if location:
                result = {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "raw_data": location.raw  # Dados completos da resposta
                }
                
                # Salvar no cache
                if use_cache:
                    _geocoding_cache.set(location_name, result)
                
                return result
            else:
                # Não encontrado, salvar no cache para evitar consultas repetidas
                if use_cache:
                    _geocoding_cache.set(location_name, None)
                return None
                
        except GeocoderTimedOut:
            if attempt < max_retries - 1:
                print(f"  Timeout na tentativa {attempt + 1}, tentando novamente...")
                time.sleep(2)  # Aguardar antes de tentar novamente
            else:
                print("Erro: O serviço de geocodificação excedeu o tempo limite após múltiplas tentativas.")
                return None
                
        except GeocoderServiceError as e:
            print(f"Erro no serviço de geocodificação: {e}")
            return None
    
    return None

@rate_limit(1.0)
def get_timezone_data(latitude, longitude, use_cache=True):
    """
    Obtém informações de fuso horário para coordenadas geográficas.
    
    Args:
        latitude (float): Latitude da localização
        longitude (float): Longitude da localização
        use_cache (bool): Se deve usar cache para consultas repetidas
    
    Returns:
        dict: Informações de fuso horário ou None se não encontrado
    """
    # Validação de entrada
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        print("Erro: Latitude e longitude devem ser números.")
        return None
    
    # Chave de cache
    cache_key = f"{latitude:.6f},{longitude:.6f}"
    
    # Verificar cache
    if use_cache:
        cached_result = _timezone_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
    
    try:
        # Usar TimezoneFinder para determinar o fuso horário
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        
        if not timezone_str:
            print(f"Aviso: Não foi possível determinar o fuso horário para ({latitude}, {longitude})")
            return None
        
        # Obter informações do fuso horário
        timezone = pytz.timezone(timezone_str)
        now = datetime.now(timezone)
        utc_offset = now.utcoffset().total_seconds() / 3600  # Converter para horas
        
        result = {
            "timezone_name": timezone_str,
            "utc_offset": utc_offset,
            "dst_active": now.dst().total_seconds() > 0,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
        }
        
        # Salvar no cache
        if use_cache:
            _timezone_cache.set(cache_key, result)
        
        return result
        
    except Exception as e:
        print(f"Erro ao obter informações de fuso horário: {e}")
        return None

@rate_limit(1.0)
def get_elevation_data(latitude, longitude, use_cache=True):
    """
    Obtém dados de elevação (altitude) para coordenadas geográficas.
    Utiliza a API Open-Elevation.
    
    Args:
        latitude (float): Latitude da localização
        longitude (float): Longitude da localização
        use_cache (bool): Se deve usar cache para consultas repetidas
    
    Returns:
        float: Elevação em metros ou None se não encontrada
    """
    # Validação de entrada
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        print("Erro: Latitude e longitude devem ser números.")
        return None
    
    # Chave de cache
    cache_key = f"{latitude:.6f},{longitude:.6f}"
    
    # Verificar cache
    if use_cache:
        cached_result = _elevation_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
    
    try:
        # Usar API Open-Elevation
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                elevation = data["results"][0].get("elevation")
                
                # Salvar no cache
                if use_cache and elevation is not None:
                    _elevation_cache.set(cache_key, elevation)
                
                return elevation
        
        print(f"Aviso: Não foi possível obter dados de elevação para ({latitude}, {longitude})")
        return None
        
    except Exception as e:
        print(f"Erro ao obter dados de elevação: {e}")
        return None

def get_astro_location_data(location_name, use_cache=True):
    """
    Obtém dados completos de localização para uso em cálculos astrológicos.
    
    Args:
        location_name (str): Nome do local para buscar
        use_cache (bool): Se deve usar cache para consultas repetidas
    
    Returns:
        dict: Dados completos da localização ou None se não encontrada
    """
    # Verificar cache
    if use_cache:
        cached_result = _astro_data_cache.get(location_name)
        if cached_result is not None:
            print(f"  (Dados astrológicos obtidos do cache)")
            return cached_result
    
    # Obter coordenadas geográficas
    geo_data = geocode_location(location_name, use_cache)
    if not geo_data:
        return None
    
    # Obter dados de fuso horário
    timezone_data = get_timezone_data(
        geo_data["latitude"], 
        geo_data["longitude"],
        use_cache
    )
    
    # Obter dados de elevação
    elevation = get_elevation_data(
        geo_data["latitude"], 
        geo_data["longitude"],
        use_cache
    )
    
    # Combinar todos os dados
    result = {
        "location": {
            "name": location_name,
            "address": geo_data["address"],
            "latitude": geo_data["latitude"],
            "longitude": geo_data["longitude"],
            "elevation": elevation
        },
        "timezone": timezone_data
    }
    
    # Salvar no cache
    if use_cache:
        _astro_data_cache.set(location_name, result)
    
    return result

def clear_all_caches():
    """Limpa todos os caches utilizados pelo módulo"""
    _geocoding_cache.clear()
    _timezone_cache.clear()
    _elevation_cache.clear()
    _astro_data_cache.clear()
    print("Todos os caches foram limpos.")

def get_coordinates_from_city(city_name):
    """
    Função simplificada para obter coordenadas de uma cidade.
    
    Args:
        city_name (str): Nome da cidade
        
    Returns:
        tuple: (latitude, longitude, timezone_str) ou None se não encontrado
    """
    try:
        location_data = get_astro_location_data(city_name)
        if location_data:
            latitude = location_data["location"]["latitude"]
            longitude = location_data["location"]["longitude"]
            timezone_str = location_data["timezone"]["timezone_name"] if location_data["timezone"] else "UTC"
            return (latitude, longitude, timezone_str)
        return None
    except Exception as e:
        print(f"Erro ao obter coordenadas da cidade {city_name}: {e}")
        return None