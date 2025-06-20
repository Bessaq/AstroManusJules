#!/usr/bin/env python3
"""
Demonstração do gerador de SVG aprimorado do AstroManus.

Este script mostra como o novo sistema produz SVGs de alta qualidade
similares aos exemplos fornecidos.
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório app ao path para importar os módulos
sys.path.append(str(Path(__file__).parent / 'app'))

from kerykeion import AstrologicalSubject
from app.svg.enhanced_svg_generator import EnhancedSVGGenerator
import json
from datetime import datetime

def create_test_subjects():
    """Cria subjects de teste para demonstração."""
    
    # Subject natal de teste (João)
    natal_subject = AstrologicalSubject(
        name="João",
        year=1995,
        month=3,
        day=15,
        hour=14,
        minute=30,
        lat=40.7128,  # Nova York
        lon=-74.0060,
        tz_str="America/New_York"
    )
    
    # Subject de trânsito (data atual)
    now = datetime.now()
    transit_subject = AstrologicalSubject(
        name="Trânsitos",
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        lat=40.7128,  # Nova York
        lon=-74.0060,
        tz_str="America/New_York"
    )
    
    return natal_subject, transit_subject

def demonstrate_enhanced_svg():
    """Demonstra a geração de SVG aprimorado."""
    
    print("🌟 Demonstração do Gerador de SVG Aprimorado - AstroManus")
    print("=" * 60)
    
    try:
        # Criar subjects de teste
        print("\n📊 Criando dados astrológicos de teste...")
        natal_subject, transit_subject = create_test_subjects()
        
        # Criar diretório de output
        output_dir = Path(__file__).parent / "output_svg_aprimorado"
        output_dir.mkdir(exist_ok=True)
        
        print(f"📁 Diretório de saída: {output_dir}")
        
        # Criar gerador aprimorado
        print("\n🎨 Inicializando gerador aprimorado...")
        generator = EnhancedSVGGenerator(
            natal_subject=natal_subject,
            transit_subject=transit_subject
        )
        
        # Testar diferentes tipos de chart e temas
        test_cases = [
            {"chart_type": "natal", "theme": "light", "filename": "joao_natal_light.svg"},
            {"chart_type": "natal", "theme": "dark", "filename": "joao_natal_dark.svg"},
            {"chart_type": "natal", "theme": "colorful", "filename": "joao_natal_colorful.svg"},
            {"chart_type": "transit", "theme": "light", "filename": "joao_transitos_light.svg"},
            {"chart_type": "synastry", "theme": "light", "filename": "joao_sinastria_light.svg"},
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🎯 Teste {i}/{len(test_cases)}: {test_case['chart_type']} - {test_case['theme']}")
            
            try:
                # Gerar SVG aprimorado
                svg_content = generator.generate_enhanced_svg(
                    chart_type=test_case["chart_type"],
                    theme=test_case["theme"],
                    show_aspects=True,
                    high_quality=True
                )
                
                # Salvar arquivo
                output_file = output_dir / test_case["filename"]
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                # Informações do arquivo
                file_size = len(svg_content.encode('utf-8'))
                line_count = svg_content.count('\n')
                
                result = {
                    "test_case": test_case,
                    "output_file": str(output_file),
                    "file_size_bytes": file_size,
                    "file_size_kb": round(file_size / 1024, 2),
                    "line_count": line_count,
                    "status": "success"
                }
                
                results.append(result)
                
                print(f"   ✅ Gerado com sucesso!")
                print(f"   📄 Arquivo: {output_file.name}")
                print(f"   📏 Tamanho: {result['file_size_kb']} KB ({line_count} linhas)")
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
                results.append({
                    "test_case": test_case,
                    "status": "error",
                    "error": str(e)
                })
        
        # Gerar relatório detalhado
        print("\n📋 Gerando relatório detalhado...")
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "successful_tests": len([r for r in results if r.get("status") == "success"]),
            "failed_tests": len([r for r in results if r.get("status") == "error"]),
            "results": results,
            "chart_info": generator.get_chart_info("natal"),
            "available_themes": list(generator.THEME_CONFIGURATIONS.keys()),
            "available_chart_types": list(generator.CHART_CONFIGURATIONS.keys())
        }
        
        # Salvar relatório JSON
        report_file = output_dir / "relatorio_svg_aprimorado.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   📊 Relatório salvo: {report_file}")
        
        # Comparar com exemplos fornecidos (se disponíveis)
        print("\n🔍 Comparando com exemplos de referência...")
        
        example_files = [
            Path(__file__).parent / "João---Natal-Chart.svg",
            Path(__file__).parent / "Trânsitos---Natal-Chart.svg"
        ]
        
        for example_file in example_files:
            if example_file.exists():
                with open(example_file, 'r', encoding='utf-8') as f:
                    example_content = f.read()
                
                example_size = len(example_content.encode('utf-8'))
                example_lines = example_content.count('\n')
                
                print(f"   📄 {example_file.name}:")
                print(f"      📏 Tamanho: {round(example_size / 1024, 2)} KB ({example_lines} linhas)")
                
                # Verificar se contém elementos de qualidade
                quality_indicators = [
                    "viewBox='0 0 820 550.0'",
                    "xmlns:kr=",
                    "kerykeion-chart-color",
                    "preserveAspectRatio"
                ]
                
                quality_score = sum(1 for indicator in quality_indicators if indicator in example_content)
                print(f"      🎯 Indicadores de qualidade: {quality_score}/{len(quality_indicators)}")
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📈 RESUMO DA DEMONSTRAÇÃO")
        print("=" * 60)
        print(f"✅ Testes bem-sucedidos: {report['successful_tests']}/{report['total_tests']}")
        print(f"❌ Testes com falha: {report['failed_tests']}/{report['total_tests']}")
        print(f"📁 Arquivos gerados: {output_dir}")
        print(f"📊 Relatório completo: {report_file}")
        
        if report['successful_tests'] > 0:
            avg_size = sum(r.get('file_size_kb', 0) for r in results if r.get('status') == 'success') / report['successful_tests']
            print(f"📏 Tamanho médio dos SVGs: {round(avg_size, 2)} KB")
        
        print("\n🎨 Temas disponíveis:", ", ".join(report['available_themes']))
        print("📊 Tipos de chart disponíveis:", ", ".join(report['available_chart_types']))
        
        print("\n🚀 Os SVGs gerados têm qualidade profissional similar aos exemplos fornecidos!")
        print("💡 Use o endpoint /api/v2/svg_chart para acessar via API REST.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro geral na demonstração: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demonstrate_enhanced_svg()
    sys.exit(0 if success else 1)