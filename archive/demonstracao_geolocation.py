#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demonstração do AstroManus com Sistema de Geolocalização Integrado

Este script demonstra como usar a nova funcionalidade de geolocalização
e timezone integrada ao AstroManus, que permite usar nomes de cidades
em vez de coordenadas manuais.

Autor: Manus AI
Versão: 2.1.0
"""

import requests
import json
from datetime import datetime

# URL base da API (ajuste conforme necessário)
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "testapikey"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_natal_chart_with_city():
    """Testa criação de mapa natal usando nome da cidade"""
    print("=== TESTE: Mapa Natal com Cidade ===")
    
    natal_data = {
        "name": "João Silva",
        "year": 1990,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "São Paulo, SP, Brasil",  # Novo campo!
        "house_system": "placidus"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/natal_chart",
            json=natal_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso!")
            print(f"Nome: {result['input_data']['name']}")
            
            if 'resolved_location' in result:
                loc_info = result['resolved_location']
                print(f"Método de resolução: {loc_info.get('method', 'N/A')}")
                print(f"Cidade entrada: {loc_info.get('input_city', 'N/A')}")
                print(f"Latitude resolvida: {loc_info.get('resolved_latitude', 'N/A')}")
                print(f"Longitude resolvida: {loc_info.get('resolved_longitude', 'N/A')}")
                print(f"Timezone: {loc_info.get('resolved_timezone', 'N/A')}")
                
                if 'timezone_info' in loc_info:
                    tz_info = loc_info['timezone_info']
                    print(f"Horário de verão ativo: {tz_info.get('is_dst_active', 'N/A')}")
                    print(f"Offset UTC: {tz_info.get('utc_offset', 'N/A')} horas")
            
            print(f"Planetas encontrados: {len(result['planets'])}")
            print(f"Aspectos encontrados: {len(result['aspects'])}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()

def test_natal_chart_with_coordinates():
    """Testa criação de mapa natal usando coordenadas tradicionais"""
    print("=== TESTE: Mapa Natal com Coordenadas ===")
    
    natal_data = {
        "name": "Maria Santos",
        "year": 1985,
        "month": 12,
        "day": 25,
        "hour": 10,
        "minute": 0,
        "latitude": -23.5505,  # São Paulo
        "longitude": -46.6333,
        "tz_str": "America/Sao_Paulo",
        "house_system": "placidus"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/natal_chart",
            json=natal_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso!")
            print(f"Nome: {result['input_data']['name']}")
            
            if 'resolved_location' in result:
                loc_info = result['resolved_location']
                print(f"Método de resolução: {loc_info.get('method', 'N/A')}")
                
                if 'timezone_info' in loc_info:
                    tz_info = loc_info['timezone_info']
                    print(f"Horário de verão ativo: {tz_info.get('is_dst_active', 'N/A')}")
                    print(f"Offset UTC: {tz_info.get('utc_offset', 'N/A')} horas")
            
            print(f"Planetas encontrados: {len(result['planets'])}")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()

def test_synastry_with_cities():
    """Testa sinastria usando cidades para ambas as pessoas"""
    print("=== TESTE: Sinastria com Cidades ===")
    
    synastry_data = {
        "person1": {
            "name": "João",
            "year": 1990,
            "month": 6,
            "day": 15,
            "hour": 14,
            "minute": 30,
            "city": "Rio de Janeiro, RJ, Brasil"
        },
        "person2": {
            "name": "Maria",
            "year": 1992,
            "month": 3,
            "day": 20,
            "hour": 9,
            "minute": 45,
            "city": "Fortaleza, CE, Brasil"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/synastry",
            json=synastry_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso!")
            print(f"Pessoas: {result['person1_data']['name']} & {result['person2_data']['name']}")
            print(f"Score de compatibilidade: {result['compatibility_score']}")
            print(f"Aspectos encontrados: {len(result['aspects'])}")
            print(f"Resumo: {result['summary'][:100]}...")
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print()

def test_international_cities():
    """Testa com cidades internacionais"""
    print("=== TESTE: Cidades Internacionais ===")
    
    cities_to_test = [
        "Paris, França",
        "New York, USA",
        "Tokyo, Japan",
        "London, UK",
        "Sydney, Australia"
    ]
    
    for city in cities_to_test:
        print(f"Testando: {city}")
        
        natal_data = {
            "name": f"Teste {city}",
            "year": 1995,
            "month": 7,
            "day": 10,
            "hour": 12,
            "minute": 0,
            "city": city,
            "house_system": "placidus"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/natal_chart",
                json=natal_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'resolved_location' in result:
                    loc_info = result['resolved_location']
                    print(f"  ✅ Resolvido: {loc_info.get('resolved_timezone', 'N/A')}")
                else:
                    print("  ✅ Sucesso (sem info de localização)")
            else:
                print(f"  ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    print()

def test_error_cases():
    """Testa casos de erro"""
    print("=== TESTE: Casos de Erro ===")
    
    # Teste 1: Sem cidade nem coordenadas
    print("1. Sem localização:")
    natal_data = {
        "name": "Teste Erro",
        "year": 1990,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "house_system": "placidus"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/natal_chart",
            json=natal_data,
            headers=headers
        )
        
        if response.status_code == 400:
            print("  ✅ Erro esperado capturado corretamente")
        else:
            print(f"  ❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro na requisição: {e}")
    
    # Teste 2: Cidade inválida
    print("2. Cidade inexistente:")
    natal_data = {
        "name": "Teste Erro",
        "year": 1990,
        "month": 6,
        "day": 15,
        "hour": 14,
        "minute": 30,
        "city": "CidadeQueNaoExiste123456789",
        "house_system": "placidus"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/natal_chart",
            json=natal_data,
            headers=headers
        )
        
        if response.status_code == 400:
            print("  ✅ Erro esperado capturado corretamente")
        else:
            print(f"  ❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erro na requisição: {e}")
    
    print()

def main():
    """Executa todos os testes"""
    print("🌟 DEMONSTRAÇÃO DO ASTROMANUS V2.1.0 🌟")
    print("Sistema de Geolocalização e Timezone Integrado")
    print("=" * 50)
    print()
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/")
        if response.status_code != 200:
            print("❌ API não está respondendo. Certifique-se de que o servidor está rodando.")
            return
    except:
        print("❌ Não foi possível conectar à API. Certifique-se de que o servidor está rodando em http://localhost:8000")
        return
    
    print("✅ API está respondendo!")
    print()
    
    # Executar testes
    test_natal_chart_with_city()
    test_natal_chart_with_coordinates()
    test_synastry_with_cities()
    test_international_cities()
    test_error_cases()
    
    print("🎉 Demonstração concluída!")
    print()
    print("📝 RESUMO DAS NOVIDADES:")
    print("- ✅ Suporte a nomes de cidades em vez de coordenadas")
    print("- ✅ Resolução automática de latitude/longitude")
    print("- ✅ Detecção automática de timezone")
    print("- ✅ Cálculo automático de horário de verão")
    print("- ✅ Funciona com cidades brasileiras e internacionais")
    print("- ✅ Mantém compatibilidade com coordenadas manuais")
    print("- ✅ Cache inteligente para melhor performance")

if __name__ == "__main__":
    main()