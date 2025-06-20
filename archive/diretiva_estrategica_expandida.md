# 🧠 Diretiva Estratégica Expandida para o Projeto "AstroManus"
## Plano Diretor de Desenvolvimento Pós-Reorganização Arquitetural e Migração para Plataforma Orquestrada

---

### 📋 **Sumário Executivo**

O projeto AstroManus representa uma evolução paradigmática no desenvolvimento de sistemas astrológicos, transitando de uma arquitetura monolítica tradicional para uma plataforma de dados moderna, escalável e orientada por eventos. Esta diretiva estratégica estabelece o roteiro completo para a transformação do sistema em uma solução empresarial robusta, capaz de processar dados astrológicos em escala, gerar insights automatizados e orquestrar pipelines complexos de dados.

**Objetivo Estratégico Principal:** Transformar o AstroManus em uma plataforma de dados astrológicos que opera de forma proativa, gerando valor contínuo através de automação inteligente, análises preditivas e entrega personalizada de conteúdo.

---

## 1. 🌟 **Contexto Estratégico do Projeto**

### 1.1 **Evolução Arquitetural**

O projeto AstroManus iniciou como uma API REST simples para cálculos astrológicos, mas evoluiu para uma arquitetura de plataforma de dados sofisticada. A recente reorganização estrutural (commit 7c1262f) representa um marco fundamental na maturidade do projeto, estabelecendo as bases para:

- **Desacoplamento de Componentes**: Separação clara entre lógica de negócio, apresentação e orquestração
- **Escalabilidade Horizontal**: Capacidade de processar múltiplas requisições simultaneamente
- **Observabilidade Completa**: Monitoramento, logging e métricas em tempo real
- **Automação Inteligente**: Pipelines de dados que operam sem intervenção manual

### 1.2 **Visão de Futuro**

O objetivo final transcende a simples resposta a requisições (modelo reativo) para estabelecer um sistema que:

1. **Gera Produtos de Dados Proativamente**
   - Relatórios diários personalizados para cada usuário
   - Alertas de eventos astrológicos significativos
   - Análises de tendências e padrões astrológicos
   - Previsões baseadas em dados históricos

2. **Orquestra Pipelines Complexos**
   - JSON → SVG → PDF → E-mail (pipeline de relatórios)
   - Dados brutos → Análise → Insights → Notificações
   - Integração com sistemas externos (CRM, marketing, etc.)

3. **Oferece Inteligência Astrológica**
   - Machine learning para identificação de padrões
   - Recomendações personalizadas baseadas em perfis
   - Análises comparativas e estatísticas avançadas

---

## 2. 🏗️ **Estado Atual da Plataforma - Análise Detalhada**

### 2.1 **Motor de Cálculo (astrotask.py e app/utils/)**

**Características Atuais:**
- Lógica de negócio centralizada e modular
- Interface de linha de comando agnóstica
- Suporte a múltiplos formatos de saída (JSON, SVG, PDF)
- Cálculos astrológicos precisos usando bibliotecas especializadas

**Capacidades Implementadas:**
```bash
# Exemplos de uso do motor de cálculo
python astrotask.py --task natal_chart --name "João" --date "1990-03-21" --time "14:30" --location "São Paulo"
python astrotask.py --task daily_transits --date "2025-06-13" --location "Rio de Janeiro"
python astrotask.py --task combined_svg --natal-data "natal.json" --transit-data "transit.json"
```

**Pontos de Melhoria Identificados:**
- Implementar cache inteligente para cálculos repetitivos
- Adicionar validação robusta de dados de entrada
- Expandir suporte a diferentes sistemas de casas astrológicas
- Implementar cálculos de aspectos harmônicos avançados

### 2.2 **Infraestrutura como Código**

**Docker Compose - Arquitetura de Serviços:**
```yaml
# Estrutura atual dos serviços
services:
  astromanus-api:      # API principal FastAPI
  kestra:              # Orquestrador de workflows
  postgresql:          # Banco de dados principal
  redis:               # Cache e sessões
  nginx:               # Proxy reverso e load balancer
  prometheus:          # Coleta de métricas
  grafana:             # Visualização de métricas
```

**Benefícios da Abordagem Atual:**
- Ambiente reproduzível em qualquer máquina
- Isolamento de dependências
- Facilidade de deploy e rollback
- Monitoramento integrado desde o início

### 2.3 **Base de Dados - Schema Robusto**

**Estrutura Atual (database/init.sql):**
```sql
-- Tabelas principais identificadas
users                 -- Usuários da plataforma
user_profiles         -- Dados astrológicos dos usuários
natal_charts          -- Cache de mapas natais calculados
transit_calculations  -- Histórico de cálculos de trânsitos
execution_logs        -- Logs detalhados de execução
api_usage_stats       -- Estatísticas de uso da API
```

**Recursos Avançados Implementados:**
- Índices otimizados para consultas frequentes
- Triggers para auditoria automática
- Views materializadas para relatórios
- Particionamento por data para performance

### 2.4 **Blueprints de Orquestração (kestra/)**

**Workflows Atuais:**
- `natal_chart_on_demand.yml` - Geração sob demanda de mapas natais
- `daily_transits_report.yml` - Relatórios diários de trânsitos
- `weekly_transits_report.yml` - Relatórios semanais (em desenvolvimento)

**Padrões de Orquestração Estabelecidos:**
- Uso de runners Docker para isolamento
- Implementação de cache com tarefas Exists/Switch
- Notificações via Slack para eventos importantes
- Tratamento de erros e retry automático

---

## 3. 🗺️ **Plano de Ação Estratégico Detalhado**

### **FASE 1: Solidificação e Configuração da Base** ⭐ *Prioridade Máxima*

#### **Ação 1.1: Implementação de Segurança e Otimização**

**Objetivo:** Estabelecer práticas de segurança e otimização desde a base.

**Tarefas Específicas:**

1. **Configuração do .gitignore:**
```gitignore
# Dependências Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Ambientes virtuais
venv/
ENV/
env/
.venv/

# Configurações sensíveis
.env
.env.local
.env.production
*.key
*.pem
*.crt

# Dados e cache
output/
cache/
logs/
temp/
backups/
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Sistema operacional
.DS_Store
Thumbs.db
```

2. **Configuração do .dockerignore:**
```dockerignore
# Controle de versão
.git
.gitignore

# Documentação
README.md
*.md
docs/

# Desenvolvimento
.vscode/
.idea/
*.swp
*.swo

# Dados locais
output/
cache/
logs/
temp/
backups/

# Testes
tests/
test_*.py
*_test.py

# Configurações locais
.env.local
.env.development

# Dependências desnecessárias
node_modules/
npm-debug.log
```

#### **Ação 1.2: Implementação Completa dos Workflows Kestra**

**1.2.1 - Workflow: natal_chart_on_demand.yml**
```yaml
id: natal_chart_on_demand
namespace: astromanus.charts

description: "Geração sob demanda de mapas natais com cache inteligente"

inputs:
  - name: user_name
    type: STRING
    required: true
  - name: birth_date
    type: DATETIME
    required: true
  - name: birth_time
    type: STRING
    required: true
  - name: birth_location
    type: STRING
    required: true
  - name: output_format
    type: STRING
    defaults: "svg"
    enum: ["json", "svg", "pdf"]

tasks:
  - id: validate_input
    type: io.kestra.plugin.core.log.Log
    message: "Validando dados de entrada para {{ inputs.user_name }}"

  - id: check_cache
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      SELECT chart_id, file_path, created_at 
      FROM natal_charts 
      WHERE user_name = '{{ inputs.user_name }}'
        AND birth_date = '{{ inputs.birth_date }}'
        AND created_at > NOW() - INTERVAL '30 days'
      LIMIT 1

  - id: cache_decision
    type: io.kestra.plugin.core.flow.Switch
    value: "{{ outputs.check_cache.size > 0 }}"
    cases:
      true:
        - id: return_cached
          type: io.kestra.plugin.core.log.Log
          message: "Retornando mapa natal do cache"
      false:
        - id: generate_new_chart
          type: io.kestra.plugin.docker.DockerRun
          image: astromanus:latest
          commands:
            - python astrotask.py 
              --task natal_chart 
              --name "{{ inputs.user_name }}"
              --date "{{ inputs.birth_date }}"
              --time "{{ inputs.birth_time }}"
              --location "{{ inputs.birth_location }}"
              --format "{{ inputs.output_format }}"
              --output "/tmp/output/"

        - id: save_to_cache
          type: io.kestra.plugin.jdbc.postgresql.Query
          url: "{{ secret('DATABASE_URL') }}"
          sql: |
            INSERT INTO natal_charts (user_name, birth_date, birth_time, birth_location, file_path, format)
            VALUES ('{{ inputs.user_name }}', '{{ inputs.birth_date }}', '{{ inputs.birth_time }}', 
                    '{{ inputs.birth_location }}', '{{ outputs.generate_new_chart.outputFiles[0] }}', '{{ inputs.output_format }}')

  - id: notify_completion
    type: io.kestra.plugin.notifications.slack.SlackIncomingWebhook
    url: "{{ secret('SLACK_WEBHOOK_URL') }}"
    payload: |
      {
        "text": "✅ Mapa natal gerado para {{ inputs.user_name }}",
        "attachments": [
          {
            "color": "good",
            "fields": [
              {"title": "Usuário", "value": "{{ inputs.user_name }}", "short": true},
              {"title": "Data", "value": "{{ inputs.birth_date }}", "short": true},
              {"title": "Formato", "value": "{{ inputs.output_format }}", "short": true}
            ]
          }
        ]
      }
```

**1.2.2 - Workflow: daily_transits_report.yml**
```yaml
id: daily_transits_report
namespace: astromanus.reports

description: "Relatório diário de trânsitos planetários"

triggers:
  - id: daily_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 6 * * *"  # Todo dia às 6h da manhã

inputs:
  - name: target_date
    type: DATE
    defaults: "{{ now() | date('yyyy-MM-dd') }}"
  - name: location
    type: STRING
    defaults: "São Paulo, Brasil"

tasks:
  - id: get_active_users
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      SELECT u.user_id, u.name, u.email, up.birth_date, up.birth_time, up.birth_location
      FROM users u
      JOIN user_profiles up ON u.user_id = up.user_id
      WHERE u.active = true AND u.daily_reports = true

  - id: process_users_parallel
    type: io.kestra.plugin.core.flow.EachParallel
    value: "{{ outputs.get_active_users.rows }}"
    tasks:
      - id: generate_personal_transit
        type: io.kestra.plugin.docker.DockerRun
        image: astromanus:latest
        commands:
          - python astrotask.py
            --task daily_transits
            --natal-name "{{ taskrun.value.name }}"
            --natal-date "{{ taskrun.value.birth_date }}"
            --natal-time "{{ taskrun.value.birth_time }}"
            --natal-location "{{ taskrun.value.birth_location }}"
            --transit-date "{{ inputs.target_date }}"
            --format "pdf"
            --output "/tmp/reports/"

      - id: send_email_report
        type: io.kestra.plugin.notifications.mail.MailSend
        from: "{{ secret('SMTP_FROM') }}"
        to: ["{{ taskrun.value.email }}"]
        subject: "Seu Relatório Diário de Trânsitos - {{ inputs.target_date }}"
        htmlTextContent: |
          <h2>Olá {{ taskrun.value.name }}!</h2>
          <p>Seu relatório diário de trânsitos está pronto.</p>
          <p>Data: {{ inputs.target_date }}</p>
          <p>Este relatório foi gerado automaticamente pelo sistema AstroManus.</p>
        attachments:
          - "{{ outputs.generate_personal_transit.outputFiles[0] }}"

  - id: generate_summary_stats
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      INSERT INTO daily_report_stats (report_date, users_processed, reports_sent)
      VALUES ('{{ inputs.target_date }}', {{ outputs.get_active_users.size }}, {{ outputs.process_users_parallel.numberOfExecutions }})
```

### **FASE 2: Integração Contínua e Geração de Valor** ⭐ *Alta Prioridade*

#### **Ação 2.1: Workflow de Relatório Semanal Avançado**

**Objetivo:** Criar relatórios semanais com análises de tendências e insights personalizados.

**weekly_transits_report.yml - Implementação Completa:**
```yaml
id: weekly_transits_report
namespace: astromanus.reports

description: "Relatório semanal com análises de tendências e insights personalizados"

triggers:
  - id: weekly_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 8 * * 1"  # Toda segunda-feira às 8h

inputs:
  - name: week_start_date
    type: DATE
    defaults: "{{ now() | date('yyyy-MM-dd') | dateAdd(-7, 'DAYS') }}"

tasks:
  - id: calculate_week_range
    type: io.kestra.plugin.core.log.Log
    message: "Processando semana de {{ inputs.week_start_date }} a {{ inputs.week_start_date | dateAdd(6, 'DAYS') }}"

  - id: get_premium_users
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      SELECT u.user_id, u.name, u.email, up.birth_date, up.birth_time, up.birth_location,
             u.subscription_tier, u.preferences
      FROM users u
      JOIN user_profiles up ON u.user_id = up.user_id
      WHERE u.active = true 
        AND u.weekly_reports = true
        AND u.subscription_tier IN ('premium', 'enterprise')

  - id: generate_global_trends
    type: io.kestra.plugin.docker.DockerRun
    image: astromanus:latest
    commands:
      - python astrotask.py
        --task weekly_trends
        --start-date "{{ inputs.week_start_date }}"
        --end-date "{{ inputs.week_start_date | dateAdd(6, 'DAYS') }}"
        --analysis-type "global"
        --output "/tmp/trends/"

  - id: process_premium_users
    type: io.kestra.plugin.core.flow.EachParallel
    value: "{{ outputs.get_premium_users.rows }}"
    tasks:
      - id: generate_personalized_weekly
        type: io.kestra.plugin.docker.DockerRun
        image: astromanus:latest
        commands:
          - python astrotask.py
            --task weekly_personal_analysis
            --user-id "{{ taskrun.value.user_id }}"
            --natal-data "{{ taskrun.value }}"
            --week-start "{{ inputs.week_start_date }}"
            --include-trends "{{ outputs.generate_global_trends.outputFiles[0] }}"
            --format "enhanced_pdf"
            --output "/tmp/weekly_reports/"

      - id: create_interactive_chart
        type: io.kestra.plugin.docker.DockerRun
        image: astromanus:latest
        commands:
          - python astrotask.py
            --task interactive_weekly_chart
            --user-id "{{ taskrun.value.user_id }}"
            --week-data "{{ outputs.generate_personalized_weekly.outputFiles[0] }}"
            --format "html"
            --output "/tmp/interactive/"

      - id: send_premium_report
        type: io.kestra.plugin.notifications.mail.MailSend
        from: "{{ secret('SMTP_FROM') }}"
        to: ["{{ taskrun.value.email }}"]
        subject: "📊 Seu Relatório Semanal Premium - Semana de {{ inputs.week_start_date }}"
        htmlTextContent: |
          <h1>Relatório Semanal Premium</h1>
          <h2>Olá {{ taskrun.value.name }}!</h2>
          
          <p>Seu relatório semanal personalizado está pronto, incluindo:</p>
          <ul>
            <li>✨ Análise detalhada dos trânsitos da semana</li>
            <li>📈 Tendências astrológicas globais</li>
            <li>🎯 Insights personalizados para seu mapa natal</li>
            <li>📊 Gráfico interativo (anexo HTML)</li>
          </ul>
          
          <p>Período analisado: {{ inputs.week_start_date }} a {{ inputs.week_start_date | dateAdd(6, 'DAYS') }}</p>
          
          <hr>
          <p><small>Este é um serviço premium do AstroManus. Para dúvidas, responda este email.</small></p>
        attachments:
          - "{{ outputs.generate_personalized_weekly.outputFiles[0] }}"
          - "{{ outputs.create_interactive_chart.outputFiles[0] }}"

  - id: update_analytics
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      INSERT INTO weekly_report_analytics (
        week_start_date, 
        premium_users_processed, 
        reports_generated, 
        interactive_charts_created,
        processing_time_seconds
      ) VALUES (
        '{{ inputs.week_start_date }}',
        {{ outputs.get_premium_users.size }},
        {{ outputs.process_premium_users.numberOfExecutions }},
        {{ outputs.process_premium_users.numberOfExecutions }},
        {{ taskrun.duration.seconds }}
      )
```

#### **Ação 2.2: Pipeline Orientado ao Banco de Dados**

**generate_personalized_daily_reports.yml - Sistema Inteligente:**
```yaml
id: generate_personalized_daily_reports
namespace: astromanus.intelligence

description: "Sistema inteligente de geração de relatórios personalizados baseado em dados históricos"

triggers:
  - id: intelligent_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 7 * * *"  # Todo dia às 7h

tasks:
  - id: analyze_user_engagement
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      WITH user_engagement AS (
        SELECT 
          u.user_id,
          u.name,
          u.email,
          up.birth_date,
          up.birth_time,
          up.birth_location,
          u.subscription_tier,
          COUNT(rl.report_id) as reports_opened_last_30_days,
          AVG(rl.engagement_score) as avg_engagement,
          MAX(rl.opened_at) as last_opened
        FROM users u
        JOIN user_profiles up ON u.user_id = up.user_id
        LEFT JOIN report_logs rl ON u.user_id = rl.user_id 
          AND rl.opened_at > NOW() - INTERVAL '30 days'
        WHERE u.active = true AND u.auto_reports = true
        GROUP BY u.user_id, u.name, u.email, up.birth_date, up.birth_time, up.birth_location, u.subscription_tier
      )
      SELECT *,
        CASE 
          WHEN avg_engagement > 8 THEN 'high'
          WHEN avg_engagement > 5 THEN 'medium'
          ELSE 'low'
        END as engagement_level
      FROM user_engagement
      ORDER BY avg_engagement DESC

  - id: segment_users_by_engagement
    type: io.kestra.plugin.core.flow.Switch
    value: "{{ outputs.analyze_user_engagement.rows | length }}"
    cases:
      "0":
        - id: no_users_log
          type: io.kestra.plugin.core.log.Log
          message: "Nenhum usuário ativo encontrado para relatórios automáticos"
      default:
        - id: process_high_engagement_users
          type: io.kestra.plugin.core.flow.EachParallel
          value: "{{ outputs.analyze_user_engagement.rows | filter(row => row.engagement_level == 'high') }}"
          tasks:
            - id: generate_premium_daily_report
              type: io.kestra.plugin.core.flow.Subflow
              namespace: astromanus.reports
              flowId: daily_transits_report
              inputs:
                user_data: "{{ taskrun.value }}"
                report_type: "premium"
                include_predictions: true
                include_recommendations: true

        - id: process_medium_engagement_users
          type: io.kestra.plugin.core.flow.EachParallel
          value: "{{ outputs.analyze_user_engagement.rows | filter(row => row.engagement_level == 'medium') }}"
          tasks:
            - id: generate_standard_daily_report
              type: io.kestra.plugin.core.flow.Subflow
              namespace: astromanus.reports
              flowId: daily_transits_report
              inputs:
                user_data: "{{ taskrun.value }}"
                report_type: "standard"
                include_predictions: false
                include_recommendations: true

        - id: process_low_engagement_users
          type: io.kestra.plugin.core.flow.EachParallel
          value: "{{ outputs.analyze_user_engagement.rows | filter(row => row.engagement_level == 'low') }}"
          tasks:
            - id: generate_summary_report
              type: io.kestra.plugin.docker.DockerRun
              image: astromanus:latest
              commands:
                - python astrotask.py
                  --task engagement_recovery_report
                  --user-id "{{ taskrun.value.user_id }}"
                  --engagement-data "{{ taskrun.value }}"
                  --format "engaging_email"
                  --output "/tmp/recovery_reports/"

  - id: machine_learning_insights
    type: io.kestra.plugin.docker.DockerRun
    image: astromanus-ml:latest
    commands:
      - python ml_pipeline.py
        --task daily_pattern_analysis
        --user-data "{{ outputs.analyze_user_engagement.rows }}"
        --historical-data-days 90
        --output-insights "/tmp/ml_insights/"

  - id: update_user_preferences
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      UPDATE users 
      SET 
        last_report_generated = NOW(),
        engagement_score = CASE 
          WHEN user_id IN ({{ outputs.process_high_engagement_users.taskRunList | map(t => t.inputs.user_data.user_id) | join(',') }}) THEN engagement_score + 0.1
          WHEN user_id IN ({{ outputs.process_low_engagement_users.taskRunList | map(t => t.inputs.user_data.user_id) | join(',') }}) THEN GREATEST(engagement_score - 0.1, 0)
          ELSE engagement_score
        END
      WHERE user_id IN ({{ outputs.analyze_user_engagement.rows | map(row => row.user_id) | join(',') }})
```

### **FASE 3: Evolução da Plataforma** ⭐ *Médio Prazo*

#### **Ação 3.1: Pipeline Avançado SVG → PDF → E-mail**

**svg_to_pdf_email_pipeline.yml - Sistema Completo:**
```yaml
id: svg_to_pdf_email_pipeline
namespace: astromanus.pipelines

description: "Pipeline completo de conversão SVG para PDF com envio por email"

inputs:
  - name: svg_file_path
    type: STRING
    required: true
  - name: user_email
    type: STRING
    required: true
  - name: user_name
    type: STRING
    required: true
  - name: report_title
    type: STRING
    required: true
  - name: custom_message
    type: STRING
    defaults: ""

tasks:
  - id: validate_svg_file
    type: io.kestra.plugin.core.flow.If
    condition: "{{ inputs.svg_file_path | fileExists }}"
    then:
      - id: log_file_found
        type: io.kestra.plugin.core.log.Log
        message: "Arquivo SVG encontrado: {{ inputs.svg_file_path }}"
    else:
      - id: error_file_not_found
        type: io.kestra.plugin.core.flow.Fail
        message: "Arquivo SVG não encontrado: {{ inputs.svg_file_path }}"

  - id: optimize_svg
    type: io.kestra.plugin.docker.DockerRun
    image: astromanus-graphics:latest
    commands:
      - python svg_optimizer.py
        --input "{{ inputs.svg_file_path }}"
        --optimize-size true
        --enhance-quality true
        --output "/tmp/optimized/"

  - id: convert_to_pdf
    type: io.kestra.plugin.docker.DockerRun
    image: astromanus-graphics:latest
    commands:
      - python svg_to_pdf_converter.py
        --svg-input "{{ outputs.optimize_svg.outputFiles[0] }}"
        --pdf-output "/tmp/pdf/"
        --quality "high"
        --paper-size "A4"
        --orientation "portrait"
        --margins "20mm"
        --include-metadata true
        --title "{{ inputs.report_title }}"
        --author "AstroManus"
        --subject "Relatório Astrológico para {{ inputs.user_name }}"

  - id: add_watermark_and_branding
    type: io.kestra.plugin.docker.DockerRun
    image: astromanus-graphics:latest
    commands:
      - python pdf_enhancer.py
        --input "{{ outputs.convert_to_pdf.outputFiles[0] }}"
        --add-header true
        --add-footer true
        --add-page-numbers true
        --add-logo "/assets/astromanus_logo.png"
        --watermark-text "AstroManus - {{ now() | date('yyyy-MM-dd') }}"
        --output "/tmp/enhanced_pdf/"

  - id: generate_email_template
    type: io.kestra.plugin.core.http.Request
    uri: "{{ secret('TEMPLATE_SERVICE_URL') }}/generate"
    method: "POST"
    contentType: "application/json"
    body: |
      {
        "template_type": "astrological_report",
        "user_name": "{{ inputs.user_name }}",
        "report_title": "{{ inputs.report_title }}",
        "custom_message": "{{ inputs.custom_message }}",
        "generation_date": "{{ now() | date('yyyy-MM-dd HH:mm:ss') }}",
        "include_tips": true,
        "include_social_links": true
      }

  - id: send_enhanced_email
    type: io.kestra.plugin.notifications.mail.MailSend
    from: "{{ secret('SMTP_FROM') }}"
    to: ["{{ inputs.user_email }}"]
    subject: "🌟 {{ inputs.report_title }} - AstroManus"
    htmlTextContent: "{{ outputs.generate_email_template.body.html_content }}"
    attachments:
      - name: "{{ inputs.report_title | slugify }}.pdf"
        content: "{{ outputs.add_watermark_and_branding.outputFiles[0] }}"

  - id: track_delivery
    type: io.kestra.plugin.jdbc.postgresql.Query
    url: "{{ secret('DATABASE_URL') }}"
    sql: |
      INSERT INTO email_delivery_log (
        user_email, 
        report_title, 
        pdf_file_path, 
        sent_at, 
        email_size_kb,
        delivery_status
      ) VALUES (
        '{{ inputs.user_email }}',
        '{{ inputs.report_title }}',
        '{{ outputs.add_watermark_and_branding.outputFiles[0] }}',
        NOW(),
        {{ outputs.add_watermark_and_branding.outputFiles[0] | fileSize / 1024 }},
        'sent'
      )

  - id: cleanup_temp_files
    type: io.kestra.plugin.docker.DockerRun
    image: alpine:latest
    commands:
      - rm -rf /tmp/optimized/ /tmp/pdf/ /tmp/enhanced_pdf/
```

#### **Ação 3.2: Implementação de CI/CD Avançado**

**GitHub Actions Workflow (.github/workflows/ci-cd.yml):**
```yaml
name: AstroManus CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: astromanus

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check app/
        isort --check-only app/
    
    - name: Run type checking
      run: mypy app/
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
        pytest tests/integration/ -v
        docker-compose -f docker-compose.test.yml down
    
    - name: Run API tests
      run: |
        chmod +x ./tools/test_api.sh
        ./tools/test_api.sh
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check -r requirements.txt
        bandit -r app/ -f json -o bandit-report.json
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: bandit-report.json

  build-and-push:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.DOCKER_REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Aqui seria a lógica de deploy para staging

  deploy-production:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment..."
        # Aqui seria a lógica de deploy para produção
```

#### **Ação 3.3: Documentação Técnica Completa**

**README.md Atualizado - Estrutura Completa:**
```markdown
# 🌟 AstroManus - Plataforma de Dados Astrológicos

[![CI/CD](https://github.com/username/astromanus/workflows/CI-CD/badge.svg)](https://github.com/username/astromanus/actions)
[![Coverage](https://codecov.io/gh/username/astromanus/branch/main/graph/badge.svg)](https://codecov.io/gh/username/astromanus)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)

## 📋 Visão Geral

AstroManus é uma plataforma moderna de dados astrológicos que combina cálculos precisos, orquestração inteligente de workflows e análises avançadas para fornecer insights astrológicos personalizados em escala.

### 🎯 Características Principais

- **🔮 Cálculos Astrológicos Precisos**: Motor de cálculo baseado em bibliotecas especializadas
- **🤖 Orquestração Inteligente**: Workflows automatizados com Kestra
- **📊 Análises Avançadas**: Machine learning para identificação de padrões
- **📧 Entrega Personalizada**: Relatórios automáticos por email
- **📈 Monitoramento Completo**: Métricas e observabilidade em tempo real
- **🔒 Segurança Empresarial**: Autenticação, autorização e auditoria

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Kestra        │
│   (React/Vue)   │◄──►│   (Nginx)       │◄──►│   (Workflows)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   PostgreSQL    │    │   Redis         │
│   (Core API)    │◄──►│   (Database)    │    │   (Cache)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   Monitoring    │
                    │ (Prometheus +   │
                    │   Grafana)      │
                    └─────────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+ (para desenvolvimento)
- Git

### Instalação Automática

#### Linux/macOS:
```bash
git clone https://github.com/username/astromanus.git
cd astromanus
chmod +x setup.sh
./setup.sh
```

#### Windows (PowerShell):
```powershell
git clone https://github.com/username/astromanus.git
cd astromanus
.\setup.ps1
```

#### Windows (Command Prompt):
```cmd
git clone https://github.com/username/astromanus.git
cd astromanus
setup.bat
```

### Acesso aos Serviços

Após a instalação, os seguintes serviços estarão disponíveis:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| 🌟 API Principal | http://localhost:8000 | API Key: `testapikey` |
| 📚 Documentação | http://localhost:8000/docs | - |
| 🔧 Kestra UI | http://localhost:8080 | - |
| 📊 Grafana | http://localhost:3000 | admin / astro123 |
| 📈 Prometheus | http://localhost:9090 | - |

## 📖 Documentação

### API Reference

#### Endpoints Principais

```http
GET /api/v1/natal-chart
POST /api/v1/natal-chart
GET /api/v1/transits
POST /api/v1/svg-combined-chart
GET /api/v1/health
```

#### Exemplo de Uso

```python
import requests

# Gerar mapa natal
response = requests.post('http://localhost:8000/api/v1/natal-chart', 
    headers={'X-API-Key': 'testapikey'},
    json={
        'name': 'João Silva',
        'birth_date': '1990-03-21',
        'birth_time': '14:30',
        'birth_location': 'São Paulo, Brasil'
    }
)

natal_chart = response.json()
```

### Workflows Kestra

#### Importar Workflows

1. Acesse http://localhost:8080
2. Vá para "Flows" → "Import"
3. Importe os arquivos da pasta `kestra/`

#### Workflows Disponíveis

- **natal_chart_on_demand**: Geração sob demanda de mapas natais
- **daily_transits_report**: Relatórios diários automáticos
- **weekly_transits_report**: Análises semanais avançadas
- **svg_to_pdf_email_pipeline**: Pipeline de conversão e envio

## 🛠️ Desenvolvimento

### Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install
```

### Executar Testes

```bash
# Testes unitários
pytest tests/unit/ -v

# Testes de integração
pytest tests/integration/ -v

# Testes da API
./tools/test_api.sh

# Coverage
pytest --cov=app --cov-report=html
```

### Estrutura do Projeto

```
astromanus/
├── app/                    # Código principal da aplicação
│   ├── api/               # Endpoints da API
│   ├── routers/           # Roteadores FastAPI
│   ├── utils/             # Utilitários e helpers
│   ├── models.py          # Modelos de dados
│   └── main.py            # Aplicação principal
├── kestra/                # Workflows de orquestração
├── database/              # Scripts de banco de dados
├── monitoring/            # Configurações de monitoramento
├── nginx/                 # Configurações do proxy
├── tools/                 # Scripts de ferramentas
├── tests/                 # Testes automatizados
├── docker-compose.yml     # Orquestração de containers
├── Dockerfile            # Imagem da aplicação
└── setup.sh              # Script de instalação
```

## 🔧 Configuração

### Variáveis de Ambiente

Edite o arquivo `.env` para configurar:

```env
# API
API_KEY_KERYKEION=your_api_key_here

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Configuração Avançada

Para configurações avançadas, consulte:
- [Configuração de Database](docs/database.md)
- [Configuração de Email](docs/email.md)
- [Configuração de Monitoramento](docs/monitoring.md)
- [Configuração de Segurança](docs/security.md)

## 📊 Monitoramento

### Métricas Disponíveis

- **Performance da API**: Latência, throughput, taxa de erro
- **Workflows**: Execuções, sucessos, falhas, duração
- **Sistema**: CPU, memória, disco, rede
- **Negócio**: Usuários ativos, relatórios gerados, engajamento

### Dashboards Grafana

Dashboards pré-configurados disponíveis:
- **API Overview**: Visão geral da performance da API
- **Workflow Monitoring**: Monitoramento de workflows Kestra
- **System Health**: Saúde do sistema e recursos
- **Business Metrics**: Métricas de negócio e usuários

## 🤝 Contribuição

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- **Python**: PEP 8, Black, isort
- **Commits**: Conventional Commits
- **Documentação**: Docstrings, README atualizado
- **Testes**: Cobertura mínima de 80%

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/username/astromanus/issues)
- **Discussões**: [GitHub Discussions](https://github.com/username/astromanus/discussions)
- **Email**: support@astromanus.com

## 🙏 Agradecimentos

- [Kerykeion](https://github.com/g-battaglia/kerykeion) - Biblioteca de cálculos astrológicos
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Kestra](https://kestra.io/) - Plataforma de orquestração
- Comunidade open source que torna este projeto possível

---

**Feito com ❤️ pela equipe AstroManus**
```

---

## 4. 🎯 **Cronograma de Implementação**

### **Sprint 1 (Semanas 1-2): Fundação Sólida**
- [ ] Implementar .gitignore e .dockerignore completos
- [ ] Finalizar workflows Kestra básicos
- [ ] Configurar monitoramento inicial
- [ ] Testes de integração básicos

### **Sprint 2 (Semanas 3-4): Inteligência de Dados**
- [ ] Implementar workflow de relatório semanal
- [ ] Criar pipeline orientado ao banco de dados
- [ ] Desenvolver sistema de segmentação de usuários
- [ ] Implementar analytics básicos

### **Sprint 3 (Semanas 5-6): Automação Avançada**
- [ ] Pipeline SVG → PDF → Email completo
- [ ] Sistema de templates de email
- [ ] Machine learning básico para insights
- [ ] Otimização de performance

### **Sprint 4 (Semanas 7-8): Produção e CI/CD**
- [ ] Implementar CI/CD completo
- [ ] Documentação técnica completa
- [ ] Testes de carga e performance
- [ ] Deploy em ambiente de produção

---

## 5. 📈 **Métricas de Sucesso**

### **Métricas Técnicas**
- **Uptime**: > 99.9%
- **Latência da API**: < 200ms (p95)
- **Taxa de Sucesso de Workflows**: > 98%
- **Cobertura de Testes**: > 90%

### **Métricas de Negócio**
- **Engajamento de Usuários**: > 70% de abertura de emails
- **Retenção**: > 80% de usuários ativos mensalmente
- **Satisfação**: NPS > 50
- **Crescimento**: 20% de novos usuários por mês

### **Métricas de Performance**
- **Tempo de Geração de Relatórios**: < 30 segundos
- **Processamento Paralelo**: 100+ usuários simultâneos
- **Armazenamento**: Crescimento controlado < 10GB/mês
- **Custos de Infraestrutura**: < $500/mês para 10k usuários

---

## 6. 🔮 **Visão de Longo Prazo**

### **Roadmap 2025-2026**

#### **Q1 2025: Consolidação**
- Plataforma estável em produção
- Base de usuários estabelecida
- Workflows principais funcionando

#### **Q2 2025: Expansão**
- API pública para desenvolvedores
- Integrações com terceiros
- Mobile app básico

#### **Q3 2025: Inteligência**
- Machine learning avançado
- Previsões personalizadas
- Análises preditivas

#### **Q4 2025: Escala**
- Arquitetura multi-tenant
- Internacionalização
- Marketplace de plugins

#### **2026: Inovação**
- IA generativa para relatórios
- Realidade aumentada para mapas
- Blockchain para certificação

---

**Esta diretiva estratégica expandida serve como o blueprint completo para a evolução do AstroManus em uma plataforma de dados astrológicos de classe mundial, combinando precisão técnica, automação inteligente e experiência do usuário excepcional.**

