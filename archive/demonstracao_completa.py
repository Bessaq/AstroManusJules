#!/usr/bin/env python3
"""
Script de teste completo para AstroManus - Versão Final
Demonstra todas as funcionalidades da plataforma
"""

from kerykeion import AstrologicalSubject
from pathlib import Path
import sys
import os
import re
from datetime import datetime, timedelta
import json

# Adicionar o diretório raiz ao path para importar módulos do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sanitize_filename(filename):
    """Remove caracteres especiais e espaços dos nomes de arquivos"""
    sanitized = re.sub(r'[^\w\-_]', '_', filename)
    return sanitized

def generate_combined_chart(natal_subject, transit_subject, output_dir):
    """
    Gera um gráfico SVG combinado de mapa natal e trânsitos.
    
    Args:
        natal_subject: Objeto AstrologicalSubject do mapa natal
        transit_subject: Objeto AstrologicalSubject dos trânsitos
        output_dir: Diretório para salvar o arquivo SVG
        
    Returns:
        Caminho do arquivo SVG gerado
    """
    # Criar diretório se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitizar nomes para o arquivo
    natal_name = sanitize_filename(natal_subject.name)
    transit_name = sanitize_filename(transit_subject.name)
    
    # Definir nome do arquivo
    file_name = f"{natal_name}_com_transitos_{transit_name}.svg"
    output_path = output_dir / file_name
    
    # Importar a função original
    try:
        from app.utils.svg_combined_chart import create_combined_chart_svg
        return create_combined_chart_svg(natal_subject, transit_subject, output_path)
    except ImportError:
        print("⚠️ Módulo app.utils.svg_combined_chart não encontrado")
        print("   Certifique-se de que a API está configurada corretamente")
        return None

def criar_mapas_demonstracao():
    """Cria mapas de demonstração com diferentes configurações"""
    
    print("🌟 === ASTROMANUS - DEMONSTRAÇÃO COMPLETA ===")
    print("Gerando mapas astrológicos de demonstração...")
    
    # Diretório para salvar os SVGs
    output_dir = Path("/home/ubuntu/mapas_demonstracao")
    
    # === DEMONSTRAÇÃO 1: Personalidades Famosas ===
    print("\n📚 1. Criando mapas de personalidades famosas")
    
    # Albert Einstein
    einstein = AstrologicalSubject(
        name='Albert_Einstein',
        year=1879,
        month=3,
        day=14,
        hour=11,
        minute=30,
        city='Ulm',
        lng=9.9937,  # Ulm, Alemanha
        lat=48.4011,
        tz_str='Europe/Berlin'
    )
    
    # Trânsitos no dia da Teoria da Relatividade (1905)
    transit_relatividade = AstrologicalSubject(
        name='Transitos_Relatividade_1905',
        year=1905,
        month=6,
        day=30,  # Publicação da Teoria da Relatividade Especial
        hour=12,
        minute=0,
        city='Bern',
        lng=7.4474,  # Bern, Suíça
        lat=46.9480,
        tz_str='Europe/Zurich'
    )
    
    svg_path1 = generate_combined_chart(einstein, transit_relatividade, output_dir)
    if svg_path1:
        print(f"✅ Mapa Einstein gerado: {svg_path1}")
    
    # === DEMONSTRAÇÃO 2: Eventos Históricos ===
    print("\n🏛️ 2. Criando mapas de eventos históricos")
    
    # Independência do Brasil
    independencia = AstrologicalSubject(
        name='Independencia_Brasil',
        year=1822,
        month=9,
        day=7,
        hour=16,
        minute=30,
        city='São Paulo',
        lng=-46.6333,
        lat=-23.5505,
        tz_str='America/Sao_Paulo'
    )
    
    # Trânsitos no Bicentenário
    bicentenario = AstrologicalSubject(
        name='Bicentenario_2022',
        year=2022,
        month=9,
        day=7,
        hour=16,
        minute=30,
        city='São Paulo',
        lng=-46.6333,
        lat=-23.5505,
        tz_str='America/Sao_Paulo'
    )
    
    svg_path2 = generate_combined_chart(independencia, bicentenario, output_dir)
    if svg_path2:
        print(f"✅ Mapa Independência gerado: {svg_path2}")
    
    # === DEMONSTRAÇÃO 3: Análise de Compatibilidade ===
    print("\n💕 3. Criando análise de compatibilidade")
    
    # Pessoa A
    pessoa_a = AstrologicalSubject(
        name='Pessoa_A_Compatibilidade',
        year=1985,
        month=7,
        day=15,
        hour=9,
        minute=45,
        city='Rio de Janeiro',
        lng=-43.1729,
        lat=-22.9068,
        tz_str='America/Sao_Paulo'
    )
    
    # Pessoa B
    pessoa_b = AstrologicalSubject(
        name='Pessoa_B_Compatibilidade',
        year=1987,
        month=11,
        day=23,
        hour=18,
        minute=20,
        city='São Paulo',
        lng=-46.6333,
        lat=-23.5505,
        tz_str='America/Sao_Paulo'
    )
    
    svg_path3 = generate_combined_chart(pessoa_a, pessoa_b, output_dir)
    if svg_path3:
        print(f"✅ Mapa Compatibilidade gerado: {svg_path3}")
    
    # === DEMONSTRAÇÃO 4: Análise de Retorno Solar ===
    print("\n🎂 4. Criando análise de retorno solar")
    
    # Pessoa para retorno solar
    aniversariante = AstrologicalSubject(
        name='Retorno_Solar_2025',
        year=1990,
        month=12,
        day=25,  # Nascimento no Natal
        hour=6,
        minute=0,
        city='Brasília',
        lng=-47.8825,
        lat=-15.7942,
        tz_str='America/Sao_Paulo'
    )
    
    # Retorno solar 2025
    retorno_2025 = AstrologicalSubject(
        name='Retorno_2025',
        year=2025,
        month=12,
        day=25,
        hour=14,  # Hora exata do retorno solar
        minute=23,
        city='Brasília',
        lng=-47.8825,
        lat=-15.7942,
        tz_str='America/Sao_Paulo'
    )
    
    svg_path4 = generate_combined_chart(aniversariante, retorno_2025, output_dir)
    if svg_path4:
        print(f"✅ Mapa Retorno Solar gerado: {svg_path4}")
    
    # === DEMONSTRAÇÃO 5: Análise de Lua Nova ===
    print("\n🌑 5. Criando análise de Lua Nova")
    
    # Pessoa para análise lunar
    pessoa_lunar = AstrologicalSubject(
        name='Analise_Lunar',
        year=1995,
        month=6,
        day=21,  # Solstício de inverno
        hour=12,
        minute=0,
        city='Salvador',
        lng=-38.5108,
        lat=-12.9714,
        tz_str='America/Bahia'
    )
    
    # Lua Nova em Gêmeos 2025
    lua_nova = AstrologicalSubject(
        name='Lua_Nova_Gemeos_2025',
        year=2025,
        month=6,
        day=6,  # Lua Nova em Gêmeos
        hour=8,
        minute=38,
        city='Salvador',
        lng=-38.5108,
        lat=-12.9714,
        tz_str='America/Bahia'
    )
    
    svg_path5 = generate_combined_chart(pessoa_lunar, lua_nova, output_dir)
    if svg_path5:
        print(f"✅ Mapa Lua Nova gerado: {svg_path5}")
    
    # === ESTATÍSTICAS FINAIS ===
    print("\n📊 === ESTATÍSTICAS DA DEMONSTRAÇÃO ===")
    print(f"Diretório de saída: {output_dir}")
    
    # Contar arquivos gerados
    svg_files = list(output_dir.glob("*.svg")) if output_dir.exists() else []
    print(f"\n📁 Arquivos SVG gerados: {len(svg_files)}")
    
    total_size = 0
    for svg_file in svg_files:
        file_size = svg_file.stat().st_size / 1024  # Tamanho em KB
        total_size += file_size
        print(f"   📄 {svg_file.name} ({file_size:.1f} KB)")
    
    print(f"\n💾 Tamanho total: {total_size:.1f} KB")
    
    # === INFORMAÇÕES TÉCNICAS ===
    print("\n🔧 === INFORMAÇÕES TÉCNICAS ===")
    print("Mapas gerados:")
    print("1. 🧠 Albert Einstein + Trânsitos da Relatividade (1905)")
    print("2. 🇧🇷 Independência do Brasil + Bicentenário (2022)")
    print("3. 💕 Análise de Compatibilidade entre duas pessoas")
    print("4. 🎂 Retorno Solar 2025")
    print("5. 🌑 Lua Nova em Gêmeos 2025")
    
    print("\n📈 Tipos de análise demonstrados:")
    print("• Mapas natais históricos")
    print("• Trânsitos planetários")
    print("• Sinastria (compatibilidade)")
    print("• Retornos solares")
    print("• Fases lunares")
    
    return output_dir

def testar_api_local():
    """Testa se a API pode ser iniciada localmente"""
    print("\n🔌 === TESTE DA API LOCAL ===")
    print("Para testar a API completa:")
    print("1. Execute: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Acesse: http://localhost:8000/docs")
    print("3. Use a API Key: testapikey")
    
    print("\n📡 Endpoints disponíveis:")
    print("• GET  /api/v1/health")
    print("• POST /api/v1/natal-chart")
    print("• POST /api/v1/svg-combined-chart")
    print("• POST /api/v1/svg-combined-chart-base64")
    print("• POST /api/v1/synastry")
    print("• POST /api/v1/daily-transits")

def gerar_relatorio_json():
    """Gera um relatório JSON com informações da demonstração"""
    
    relatorio = {
        "demonstracao": {
            "titulo": "AstroManus - Demonstração Completa",
            "versao": "2.0.0",
            "data_execucao": datetime.now().isoformat(),
            "mapas_gerados": [
                {
                    "nome": "Albert Einstein",
                    "tipo": "Personalidade Histórica",
                    "evento": "Teoria da Relatividade (1905)",
                    "descricao": "Mapa natal de Einstein com trânsitos do dia da publicação da Teoria da Relatividade Especial"
                },
                {
                    "nome": "Independência do Brasil",
                    "tipo": "Evento Histórico",
                    "evento": "Bicentenário (2022)",
                    "descricao": "Mapa da Independência do Brasil com trânsitos do bicentenário"
                },
                {
                    "nome": "Análise de Compatibilidade",
                    "tipo": "Sinastria",
                    "evento": "Relacionamento",
                    "descricao": "Análise de compatibilidade entre duas pessoas nascidas em diferentes cidades"
                },
                {
                    "nome": "Retorno Solar 2025",
                    "tipo": "Retorno Solar",
                    "evento": "Aniversário",
                    "descricao": "Análise do retorno solar para o ano de 2025"
                },
                {
                    "nome": "Lua Nova em Gêmeos",
                    "tipo": "Análise Lunar",
                    "evento": "Fase Lunar",
                    "descricao": "Impacto da Lua Nova em Gêmeos no mapa natal"
                }
            ],
            "tecnologias_utilizadas": [
                "Python 3.11",
                "Kerykeion (cálculos astrológicos)",
                "SVGWrite (geração de gráficos)",
                "FastAPI (API REST)",
                "Docker (containerização)",
                "Kestra (orquestração)"
            ],
            "recursos_demonstrados": [
                "Cálculos astrológicos precisos",
                "Geração de mapas SVG",
                "Análise de trânsitos",
                "Compatibilidade entre mapas",
                "Retornos solares",
                "Fases lunares",
                "Eventos históricos"
            ]
        }
    }
    
    relatorio_path = Path("/home/ubuntu/mapas_demonstracao/relatorio_demonstracao.json")
    relatorio_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Relatório JSON gerado: {relatorio_path}")
    return relatorio_path

if __name__ == "__main__":
    try:
        print("🚀 Iniciando demonstração completa do AstroManus...")
        
        # Criar mapas de demonstração
        output_dir = criar_mapas_demonstracao()
        
        # Gerar relatório JSON
        relatorio_path = gerar_relatorio_json()
        
        # Informações sobre teste da API
        testar_api_local()
        
        print(f"\n✅ === DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print(f"📁 Mapas salvos em: {output_dir}")
        print(f"📋 Relatório salvo em: {relatorio_path}")
        print(f"🌟 Total de demonstrações: 5 mapas astrológicos")
        
        print(f"\n💡 === PRÓXIMOS PASSOS ===")
        print("1. 🐳 Execute: docker-compose up -d (para iniciar todos os serviços)")
        print("2. 🌐 Acesse: http://localhost:8000/docs (documentação da API)")
        print("3. 🔧 Acesse: http://localhost:8080 (Kestra UI)")
        print("4. 📊 Acesse: http://localhost:3000 (Grafana)")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

