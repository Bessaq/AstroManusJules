# AstroManus v2.1.0 - Sistema de Geolocalização Integrado

## 🌟 Novidades da Versão 2.1.0

Esta versão do AstroManus integra um sistema completo de geolocalização e timezone, eliminando a necessidade de APIs externas e permitindo o uso de nomes de cidades em vez de coordenadas manuais.

### ✨ Principais Funcionalidades Adicionadas

1. **Geolocalização Automática**
   - Resolução de coordenadas a partir de nomes de cidades
   - Suporte a cidades brasileiras e internacionais
   - Cache inteligente para melhor performance

2. **Sistema de Timezone Avançado**
   - Detecção automática de fuso horário baseado em coordenadas
   - Cálculo automático de horário de verão (DST)
   - Histórico preciso de DST para qualquer data

3. **API Melhorada**
   - Campos opcionais: `city` como alternativa a `latitude` + `longitude` + `tz_str`
   - Compatibilidade total com versões anteriores
   - Informações detalhadas sobre resolução de localização

## 🔧 Como Usar

### Opção 1: Com Nome da Cidade (NOVO!)

```json
{
  "name": "João Silva",
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "city": "São Paulo, SP, Brasil",
  "house_system": "placidus"
}
```

### Opção 2: Com Coordenadas (Método Tradicional)

```json
{
  "name": "João Silva", 
  "year": 1990,
  "month": 6,
  "day": 15,
  "hour": 14,
  "minute": 30,
  "latitude": -23.5505,
  "longitude": -46.6333,
  "tz_str": "America/Sao_Paulo",
  "house_system": "placidus"
}
```

## 📁 Arquivos Modificados

### Novos Módulos
- `app/utils/astro_geolocation.py` - Sistema de geolocalização
- `app/utils/daylight_saving.py` - Cálculos de horário de verão

### Arquivos Atualizados
- `app/models.py` - Adicionado campo `city` opcional
- `app/utils/astro_helpers.py` - Função `resolve_location()` e `create_subject()` modificada
- `app/routers/natal_chart_router.py` - Suporte a geolocalização
- `app/routers/synastry_router.py` - Suporte a geolocalização
- `app/routers/svg_combined_chart_router.py` - Suporte a geolocalização
- `requirements.txt` - Dependências adicionadas

### Dependências Adicionadas
- `geopy` - Geocodificação via OpenStreetMap
- `timezonefinder` - Detecção de timezone por coordenadas
- `pytz` - Manipulação de timezones
- `requests` - Requisições HTTP (para elevação)

## 🚀 Instalação e Execução

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar o servidor:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Testar funcionalidades:**
```bash
python demonstracao_geolocation.py
```

## 📊 Exemplos de Uso

### Mapa Natal com Cidade

```python
import requests

data = {
    "name": "Teste",
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "city": "Rio de Janeiro, RJ, Brasil"
}

response = requests.post(
    "http://localhost:8000/api/v1/natal_chart",
    json=data,
    headers={"X-API-Key": "testapikey"}
)

result = response.json()
print(f"Localização resolvida: {result['resolved_location']}")
```

### Sinastria com Cidades

```python
synastry_data = {
    "person1": {
        "name": "João",
        "year": 1990, "month": 6, "day": 15,
        "hour": 14, "minute": 30,
        "city": "São Paulo, SP, Brasil"
    },
    "person2": {
        "name": "Maria", 
        "year": 1992, "month": 3, "day": 20,
        "hour": 9, "minute": 45,
        "city": "Fortaleza, CE, Brasil"
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/synastry",
    json=synastry_data,
    headers={"X-API-Key": "testapikey"}
)
```

## 🔍 Informações Técnicas

### Sistema de Cache
- Cache automático para geocodificação (evita consultas repetidas)
- Cache para timezones e dados de elevação
- Limpeza automática quando cache atinge limite

### Rate Limiting
- Respeitamos limites do Nominatim (1 requisição/segundo)
- Retry automático em caso de timeout
- Fallback gracioso para coordenadas manuais

### Tratamento de Erros
- Validação robusta de entrada
- Mensagens de erro claras
- Logging detalhado para depuração

### Exemplos de Cidades Suportadas

**Brasil:**
- São Paulo, SP, Brasil
- Rio de Janeiro, RJ, Brasil
- Brasília, DF, Brasil
- Fortaleza, CE, Brasil
- Salvador, BA, Brasil

**Internacional:**
- Paris, França
- New York, USA
- London, UK
- Tokyo, Japan
- Sydney, Australia

## 🎯 Benefícios

1. **Facilidade de Uso**
   - Não precisa procurar coordenadas manualmente
   - Interface mais amigável para usuários finais

2. **Precisão**
   - Coordenadas precisas via OpenStreetMap
   - Cálculo correto de horário de verão

3. **Performance**
   - Sistema de cache reduz latência
   - Menos dependência de APIs externas

4. **Confiabilidade**
   - Funciona offline para cidades já consultadas
   - Fallback para coordenadas manuais

## 🔄 Compatibilidade

- ✅ **Totalmente compatível** com versões anteriores
- ✅ Todos os endpoints existentes continuam funcionando
- ✅ Coordenadas manuais ainda são aceitas
- ✅ Estrutura de resposta mantida (com adições opcionais)

## 🛠️ Para Desenvolvedores

### Estrutura da Resposta com Localização Resolvida

```json
{
  "input_data": {...},
  "planets": {...},
  "houses": {...},
  "ascendant": {...},
  "midheaven": {...},
  "aspects": [...],
  "house_system": "placidus",
  "resolved_location": {
    "method": "geolocation",
    "input_city": "São Paulo, SP, Brasil",
    "resolved_latitude": -23.5505199,
    "resolved_longitude": -46.6333094,
    "resolved_timezone": "America/Sao_Paulo",
    "timezone_info": {
      "timezone_name": "America/Sao_Paulo",
      "utc_offset": -3.0,
      "dst_offset": 0.0,
      "is_dst_active": false,
      "standard_offset": -3.0,
      "date_checked": "1990-06-15"
    }
  }
}
```

### Adicionando Suporte a Novos Endpoints

Para adicionar suporte de geolocalização a novos endpoints:

1. Importe as funções necessárias:
```python
from app.utils.astro_helpers import create_subject
```

2. Use `create_subject()` em vez de criar `AstrologicalSubject` diretamente:
```python
subject, location_info = create_subject(request_data, "DefaultName")
```

3. Inclua `location_info` na resposta se desejado.

## 📞 Suporte

Para dúvidas ou problemas com o sistema de geolocalização:

1. Verifique se a cidade está sendo escrita corretamente
2. Teste com coordenadas manuais se a cidade não for encontrada
3. Consulte os logs para detalhes de erros
4. Use o script `demonstracao_geolocation.py` para testes

---

**AstroManus v2.1.0** - Sistema de Astrologia com Geolocalização Integrada  
*Desenvolvido por Manus AI - 2025*