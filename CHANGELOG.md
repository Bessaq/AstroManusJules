## [Unreleased] - YYYY-MM-DD

### Fixed
- Updated the project to target **Kerykeion v4.26.0**, removing references to the experimental v5 API and ensuring all endpoints operate with the stable release.
- Corrected `AstrologicalSubject` creation to use the 4.x constructor parameters, eliminating the previous speculative v5 factory logic.
- Fixed errors in location field handling for `/api/v1/natal_chart` by:
  - Integrating a configurable `GEONAMES_USERNAME` from environment variables.
  - Intelligently setting Kerykeion's `online` flag to `False` when full lat/lon/tz_str are provided, preventing unnecessary GeoNames calls.
- Addressed field configuration problems in `/api/v1/synastry` by refactoring to use Kerykeion's `SynastryAspects` class (with a fallback to improved manual calculation) for more robust aspect determination.
- Fixed `/api/v2/svg_chart` incompatibilities with Kerykeion 4.x by ensuring `EnhancedSVGGenerator` uses robust methods for retrieving SVG strings from `KerykeionChartSVG` and correctly handles different chart types.
- Resolved an internal server error for `/api/v2/themes` by accessing `THEME_CONFIGURATIONS` as a class attribute in `EnhancedSVGGenerator`, avoiding problematic instantiation.

### Changed
- `app/utils/astro_helpers.py`: Major updates to `create_subject` for Kerykeion 4.26 compatibility and GeoNames username.
- `app/routers/synastry_router.py`: Refactored to use `SynastryAspects`.
- `app/svg/enhanced_svg_generator.py`: Improved SVG string retrieval from `KerykeionChartSVG`.
- `app/routers/enhanced_svg_router.py`: Corrected `/themes` endpoint logic.

---

# Changelog - AstroManus

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-06-13 - Reorganização Arquitetural Completa

### 🎉 Adicionado
- **Scripts de Setup para Windows**
  - `setup_windows.ps1` - Script PowerShell completo
  - `setup_windows.bat` - Script Batch para compatibilidade
  - Verificação automática de privilégios de administrador
  - Tratamento de erros robusto para ambiente Windows

- **Documentação Estratégica Expandida**
  - `diretiva_estrategica_expandida.md` - Plano estratégico completo (~15.000 palavras)
  - Workflows Kestra detalhados com código YAML
  - Pipeline CI/CD com GitHub Actions
  - Cronograma de implementação por sprints
  - Métricas de sucesso e roadmap até 2026

- **Configurações de Segurança**
  - `.gitignore` completo para projetos Python/Docker
  - `.dockerignore` otimizado para builds eficientes
  - Exclusão de arquivos sensíveis e temporários

- **Relatórios de Mudanças**
  - `relatorio_mudancas.md` - Análise detalhada das mudanças estruturais
  - Comparação entre versões antigas e novas
  - Impacto nas funcionalidades existentes

### 🔄 Modificado
- **Estrutura de Diretórios Reorganizada**
  - `main.py` movido para `app/main.py`
  - Configurações organizadas em diretórios específicos:
    - `database/` - Scripts de banco de dados
    - `kestra/` - Workflows de orquestração
    - `monitoring/` - Configurações de monitoramento
    - `nginx/` - Configurações do proxy
    - `tools/` - Scripts de ferramentas

- **README.md Completamente Reescrito**
  - Documentação técnica detalhada
  - Exemplos de uso da API
  - Guias de instalação para múltiplas plataformas
  - Estrutura do projeto explicada
  - Comandos úteis e troubleshooting

- **Comando de Execução da API**
  - **Antes**: `uvicorn main:app --reload`
  - **Agora**: `uvicorn app.main:app --reload`

### 📁 Movido
- **Arquivos Legados para `temp_old_files/`**
  - `README.md` original
  - `README_SVG_COMBINADO.md`
  - `example_run_house.py`
  - `example_svg_combined.py`
  - `examples-natal_chart_request.json`
  - `Procfile`
  - Diretórios `Integrar/` e `MCP/`
  - Diretórios `backup/` e `backup_original/`

- **Arquivos Renomeados e Reorganizados**
  - `Astrotagiario.dockerfile` → `Dockerfile`
  - `monitoring-prometheus.yml` → `monitoring/prometheus.yml`
  - `tools-test_api.sh` → `tools/test_api.sh`
  - `database-init.sql` → `database/init.sql`
  - Workflows Kestra organizados em `kestra/`

### ✨ Melhorado
- **Compatibilidade Multi-Plataforma**
  - Suporte completo para Windows, Linux e macOS
  - Scripts de setup específicos para cada plataforma
  - Tratamento de diferenças entre sistemas operacionais

- **Documentação Técnica**
  - Guias detalhados de instalação e configuração
  - Exemplos práticos de uso da API
  - Arquitetura do sistema explicada
  - Workflows Kestra documentados

- **Organização do Código**
  - Separação clara de responsabilidades
  - Estrutura de diretórios padronizada
  - Configurações centralizadas

### 🔧 Corrigido
- **Arquivos de Configuração Vazios**
  - `.gitignore` agora contém regras apropriadas
  - `.dockerignore` otimizado para builds Docker
  - `.env` será criado automaticamente pelo setup

- **Problemas de Compatibilidade**
  - Scripts funcionam em diferentes versões do Windows
  - Fallbacks para sistemas sem PowerShell
  - Verificação automática de dependências

### 🗑️ Removido
- **Arquivos Desnecessários da Raiz**
  - `.gitattributes` (movido para temp_old_files)
  - Arquivos de exemplo da raiz do projeto
  - Configurações duplicadas

## [1.0.0] - 2025-06-13 - Versão Inicial

### Adicionado
- API FastAPI para cálculos astrológicos
- Geração de mapas natais e trânsitos
- Visualizações SVG combinadas
- Integração com Kestra para orquestração
- Docker Compose para ambiente completo
- Monitoramento com Prometheus e Grafana

---

## Notas de Migração

### De 1.0.0 para 2.0.0

1. **Comando de Execução Alterado**
   ```bash
   # Antes
   uvicorn main:app --reload
   
   # Agora
   uvicorn app.main:app --reload
   ```

2. **Estrutura de Arquivos**
   - Verifique se seus scripts referenciam os novos caminhos
   - Arquivos de exemplo estão em `temp_old_files/`
   - Configurações estão organizadas em subdiretórios

3. **Scripts de Setup**
   - Use o script apropriado para seu sistema operacional
   - Windows: `setup_windows.ps1` ou `setup_windows.bat`
   - Linux/macOS: `setup.sh`

4. **Configurações**
   - Arquivo `.env` será criado automaticamente
   - Configure suas credenciais específicas após o setup
   - Verifique as novas variáveis de ambiente

## Compatibilidade

- **Python**: 3.9+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Sistemas Operacionais**: Windows 10+, Linux, macOS

## Próximas Versões

Veja `diretiva_estrategica_expandida.md` para o roadmap completo até 2026.
