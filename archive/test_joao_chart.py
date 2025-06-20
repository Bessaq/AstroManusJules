#!/usr/bin/env python3
"""
Script de teste para o endpoint /api/v2/svg_chart
Testa diretamente as funcionalidades do gerador SVG aprimorado
"""

import sys
import os
sys.path.append('/home/ubuntu/upload/AstroManus')

from app.models import SVGChartRequest, NatalChartRequest
from app.utils.astro_helpers import create_subject
from app.svg.enhanced_svg_generator import EnhancedSVGGenerator
import json

def test_joao_chart():
    """Testa o mapa do João (13/10/1997 às 22h em Fortaleza - CE)"""
    
    print("=== Testando Mapa Astrológico do João ===")
    print("Data: 13/10/1997 às 22:00")
    print("Local: Fortaleza - CE")
    print()
    
    # Dados do João
    natal_data = NatalChartRequest(
        name="João",
        year=1997,
        month=10,
        day=13,
        hour=22,
        minute=0,
        latitude=-3.7172,  # Fortaleza - CE
        longitude=-38.5247,
        tz_str="America/Fortaleza",
        house_system="placidus"
    )
    
    # Criar subject astrológico
    print("1. Criando subject astrológico...")
    natal_subject, location_info = create_subject(natal_data, "João")
    print(f"   ✓ Subject criado: {natal_subject.name}")
    print(f"   ✓ Data: {natal_subject.day}/{natal_subject.month}/{natal_subject.year}")
    print(f"   ✓ Hora: {natal_subject.hour}:{natal_subject.minute:02d}")
    print(f"   ✓ Local: {natal_subject.city}")
    print(f"   ✓ Coordenadas: {natal_subject.lat}, {natal_subject.lng}")
    print()
    
    # Criar gerador SVG aprimorado
    print("2. Criando gerador SVG aprimorado...")
    generator = EnhancedSVGGenerator(natal_subject=natal_subject)
    print("   ✓ Gerador criado com sucesso")
    print()
    
    # Obter informações do chart
    print("3. Obtendo informações do chart...")
    chart_info = generator.get_chart_info("natal")
    print(f"   ✓ Nome: {chart_info['primary_subject']['name']}")
    print(f"   ✓ Data: {chart_info['primary_subject']['birth_date']}")
    print(f"   ✓ Hora: {chart_info['primary_subject']['birth_time']}")
    print(f"   ✓ Localização: {chart_info['primary_subject']['location']}")
    print()
    
    # Gerar SVG com tema light (fundo branco)
    print("4. Gerando SVG com tema light (fundo branco)...")
    svg_light = generator.generate_enhanced_svg(
        chart_type="natal",
        theme="light",
        show_aspects=True,
        high_quality=True
    )
    
    # Salvar SVG
    svg_filename = "/home/ubuntu/upload/AstroManus/joao_mapa_natal_light.svg"
    with open(svg_filename, 'w', encoding='utf-8') as f:
        f.write(svg_light)
    print(f"   ✓ SVG salvo: {svg_filename}")
    print(f"   ✓ Tamanho: {len(svg_light):,} caracteres")
    print()
    
    # Gerar SVG com tema colorful (fundo branco colorido)
    print("5. Gerando SVG com tema colorful (fundo branco colorido)...")
    svg_colorful = generator.generate_enhanced_svg(
        chart_type="natal",
        theme="colorful",
        show_aspects=True,
        high_quality=True
    )
    
    # Salvar SVG colorful
    svg_colorful_filename = "/home/ubuntu/upload/AstroManus/joao_mapa_natal_colorful.svg"
    with open(svg_colorful_filename, 'w', encoding='utf-8') as f:
        f.write(svg_colorful)
    print(f"   ✓ SVG colorful salvo: {svg_colorful_filename}")
    print(f"   ✓ Tamanho: {len(svg_colorful):,} caracteres")
    print()
    
    return svg_filename, svg_colorful_filename

def convert_svg_to_png(svg_file, png_file):
    """Converte SVG para PNG usando cairosvg"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_file, write_to=png_file, background_color='white')
        print(f"   ✓ PNG gerado: {png_file}")
        return True
    except ImportError:
        print("   ⚠ cairosvg não instalado, tentando com inkscape...")
        try:
            import subprocess
            result = subprocess.run([
                'inkscape', 
                '--export-type=png',
                '--export-background=white',
                '--export-filename=' + png_file,
                svg_file
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✓ PNG gerado com inkscape: {png_file}")
                return True
            else:
                print(f"   ✗ Erro com inkscape: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ✗ Erro ao converter para PNG: {e}")
            return False

if __name__ == "__main__":
    try:
        svg_light, svg_colorful = test_joao_chart()
        
        print("6. Convertendo SVGs para PNG...")
        
        # Instalar cairosvg se necessário
        try:
            import cairosvg
        except ImportError:
            print("   Instalando cairosvg...")
            os.system("pip3 install cairosvg")
        
        # Converter para PNG
        png_light = "/home/ubuntu/upload/AstroManus/joao_mapa_natal_light.png"
        png_colorful = "/home/ubuntu/upload/AstroManus/joao_mapa_natal_colorful.png"
        
        convert_svg_to_png(svg_light, png_light)
        convert_svg_to_png(svg_colorful, png_colorful)
        
        print()
        print("=== TESTE CONCLUÍDO COM SUCESSO ===")
        print("Arquivos gerados:")
        print(f"  • {svg_light}")
        print(f"  • {svg_colorful}")
        print(f"  • {png_light}")
        print(f"  • {png_colorful}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

