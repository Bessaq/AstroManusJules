

# **Kerykeion — Um Guia Técnico Completo para Cálculos Astrológicos em Python**

## **1.0 Introdução à Kerykeion**

### **1.1 Visão Geral: O que é a Kerykeion e sua Finalidade**

Kerykeion é uma biblioteca Python de alto nível projetada para a realização de cálculos astrológicos precisos, com um foco fundamental em uma abordagem orientada a dados (*data-driven*).1 Sua principal finalidade é fornecer a desenvolvedores e cientistas de dados uma ferramenta programática robusta para computar posições de planetas e casas, calcular aspectos astrológicos e gerar representações visuais de mapas astrais em formato SVG (Scalable Vector Graphics).3

A biblioteca suporta uma gama completa de cálculos e tipos de mapas essenciais para a prática astrológica, incluindo:

* **Mapas Natais:** O mapa de nascimento de um indivíduo.  
* **Sinastria:** A análise de relacionamento através da sobreposição de dois mapas natais.  
* **Trânsitos:** A análise da posição atual dos planetas em relação a um mapa natal.  
* **Mapas Compostos:** A criação de um mapa único a partir dos pontos médios dos planetas de dois indivíduos, representando a dinâmica da relação.1

O que distingue a Kerykeion é sua arquitetura focada na entrega de dados estruturados. Em vez de apenas gerar uma imagem final, a biblioteca expõe todos os dados calculados — como a posição de um planeta, seu signo, elemento e casa — em estruturas de dados Python nativas, como dicionários e listas.6 Esta abordagem deliberada torna a Kerykeion uma ferramenta excepcionalmente poderosa para o desenvolvimento de aplicações modernas. A estrutura de dados limpa e previsível facilita enormemente a integração com outros sistemas, como APIs web (FastAPI, Flask), bancos de dados (SQL, NoSQL), ferramentas de análise de dados (pandas) e, crucialmente, aplicações de Inteligência Artificial e Modelos de Linguagem Grandes (LLMs), que dependem de dados estruturados para funcionar eficazmente.8 Assim, a Kerykeion posiciona-se não apenas como um gerador de mapas, mas como um motor de cálculo astrológico para uma nova geração de aplicações programáticas e analíticas.

### **1.2 Arquitetura e Dependências Chave**

A precisão e a confiabilidade da Kerykeion são construídas sobre uma base sólida de dependências de alta qualidade. A biblioteca funciona como um *wrapper* de alto nível, ou seja, uma camada de abstração que simplifica o uso de ferramentas mais complexas que operam nos bastidores.

A dependência mais crítica é a pyswisseph, o *binding* oficial em Python para a **Swiss Ephemeris**.10 A Swiss Ephemeris, desenvolvida pela Astrodienst, é considerada o padrão de ouro na indústria de software astrológico para cálculos astronômicos. Sua precisão deriva do uso das efemérides do Jet Propulsion Laboratory (JPL) da NASA, especificamente o conjunto de dados DE431, que cobre um vasto período de tempo com exatidão notável.12 Ao utilizar a

pyswisseph, a Kerykeion herda diretamente essa precisão de nível profissional para todas as suas computações de posições celestes.

Essa dependência fundamental, no entanto, traz consigo uma implicação importante: o modelo de licenciamento. A Swiss Ephemeris é distribuída sob uma licença dupla: a GNU AGPL (Affero General Public License) ou uma licença profissional paga.12 A Kerykeion, por sua vez, adota a licença AGPL-3.0.7 Isso significa que qualquer software de código aberto que utilize a Kerykeion deve, em geral, ser distribuído sob uma licença compatível. Para contornar essa restrição em projetos comerciais de código fechado, o desenvolvedor da Kerykeion criou a

**AstrologerAPI**, uma API web comercial que fornece os mesmos cálculos precisos sem exigir que o código do cliente seja aberto.6 Esta API também serve como uma fonte de financiamento para sustentar o desenvolvimento contínuo da biblioteca de código aberto.6

Outras dependências notáveis incluem:

* **GeoNames:** Para geocodificação automática, a Kerykeion pode se conectar ao serviço web GeoNames para converter nomes de cidades e países em coordenadas geográficas (latitude e longitude) e fuso horário. Para otimizar o uso e evitar exceder os limites da API, a biblioteca implementa um sistema de cache, cujo tempo de expiração foi recentemente estendido para 30 dias.17  
* **Pydantic:** A biblioteca utiliza o Pydantic para validação e modelagem de dados.18 Isso reforça a abordagem  
  *data-driven*, garantindo que os objetos e dados manipulados sejam consistentes e sigam um esquema predefinido, o que aumenta a robustez do código e facilita a depuração.

### **1.3 Evolução da Biblioteca: De KrInstance a AstrologicalSubject**

Ao explorar exemplos de código de diferentes épocas, é possível notar uma evolução na nomenclatura da classe principal da biblioteca. Versões e tutoriais mais antigos frequentemente se referem a KrInstance (abreviação de Kerykeion Instance) como a classe central para criar um mapa.3 No entanto, a documentação mais recente e as versões atuais padronizaram o uso de

AstrologicalSubject.1

Essa mudança de KrInstance para AstrologicalSubject não é meramente cosmética; ela reflete uma refatoração significativa e a maturação da biblioteca. O nome AstrologicalSubject é muito mais descritivo e alinhado com os princípios do design orientado a objetos e do *Domain-Driven Design* (DDD). Ele comunica claramente que a classe representa a entidade central do domínio do problema: um "sujeito astrológico". Essa transição provavelmente coincidiu com a adoção do Pydantic, que permitiu que o AstrologicalSubject fosse modelado não apenas como um objeto computacional, mas como um modelo de dados robusto, validado e facilmente serializável para formatos como JSON. Essa evolução foi um passo crucial para solidificar a Kerykeion como uma ferramenta ideal para integrações com APIs e outras aplicações que consomem dados estruturados.

## **2.0 Instalação e Configuração**

### **2.1 Requisitos do Sistema**

Para utilizar a Kerykeion, é necessário ter o **Python 3.9 ou uma versão superior** instalada no sistema.3 A biblioteca depende de vários pacotes Python que são gerenciados e instalados automaticamente durante o processo de instalação. As dependências principais incluem:

* pyswisseph: Para os cálculos astronômicos.  
* pydantic: Para a modelagem e validação de dados.  
* pytz: Para o gerenciamento de fusos horários.  
* requests: Para realizar chamadas de API (por exemplo, para o serviço GeoNames).18

### **2.2 Processo de Instalação via pip**

A instalação da Kerykeion é um processo padrão do ecossistema Python, realizado através do gerenciador de pacotes pip. É altamente recomendável realizar a instalação dentro de um ambiente virtual (venv, virtualenv, conda, etc.) para isolar as dependências do projeto e evitar conflitos com outros pacotes instalados no sistema.19

Para instalar a biblioteca, execute o seguinte comando no seu terminal:

Bash

pip3 install kerykeion

Este comando fará o download da versão mais recente da Kerykeion do Python Package Index (PyPI) e instalará automaticamente todas as suas dependências necessárias.3

### **2.3 Gerenciamento de Dependências (Swiss Ephemeris)**

A dependência pyswisseph requer arquivos de efemérides (com extensão .se1) para realizar cálculos de alta precisão, especialmente para corpos celestes como asteroides e para períodos de tempo muito longos.11 A Kerykeion foi projetada para gerenciar essa necessidade de forma transparente para o usuário. Os arquivos de efemérides essenciais, que cobrem o período de 1800 a 2399 AD, são empacotados com a biblioteca, então, na maioria dos casos de uso, nenhuma configuração manual é necessária.20

Para casos de uso avançados que exijam cálculos fora desse intervalo de tempo ou para asteroides não incluídos por padrão, pode ser necessário baixar arquivos de efemérides adicionais do site da Astrodienst e configurar a pyswisseph para encontrá-los, geralmente através de uma variável de ambiente (SE\_EPHE\_PATH).12

### **2.4 Configuração do geonames\_username**

A Kerykeion oferece um mecanismo de conveniência para determinar automaticamente a latitude, a longitude e o fuso horário a partir de um nome de cidade e país. Esse recurso depende do serviço web gratuito GeoNames. Para utilizar este serviço, é necessário registrar-se no site do GeoNames e obter um nome de usuário.

No contexto da biblioteca Kerykeion usada localmente, a necessidade de configurar este nome de usuário pode variar. No entanto, para a **AstrologerAPI** (a contraparte web da Kerykeion), o uso da geocodificação automática exige explicitamente que o geonames\_username seja passado em cada requisição de API.15

Esta funcionalidade apresenta um importante trade-off entre conveniência e controle. Utilizar a geocodificação automática (city e nation) é simples, mas introduz uma dependência de rede, está sujeito a limites de uso da API do GeoNames e pode ser mais lento.6 A alternativa, que é a prática recomendada para aplicações de produção, é fornecer os dados de localização manualmente, passando os parâmetros

lng (longitude), lat (latitude) e tz\_str (string do fuso horário, ex: "America/New\_York") diretamente ao instanciar o objeto. Este método offline é mais rápido, mais confiável e não requer conexão com a internet, dando ao desenvolvedor controle total sobre a aplicação.3

## **3.0 A Classe Principal: AstrologicalSubject**

O coração da biblioteca Kerykeion é a classe AstrologicalSubject. Esta classe encapsula todos os dados de entrada de um indivíduo ou evento (data, hora e local) e serve como o ponto de acesso central para todos os dados astrológicos calculados, desde as posições planetárias até as cúspides das casas.

### **3.1 Instanciação de um Sujeito Astrológico**

Existem duas maneiras principais de criar uma instância de AstrologicalSubject, refletindo o trade-off entre conveniência online e controle offline.

#### **3.1.1 Modo Padrão (Online)**

No modo padrão, você fornece informações de data, hora e localização textual. A Kerykeion usará o serviço GeoNames para resolver a localização em coordenadas geográficas e fuso horário.

**Parâmetros do Construtor:**

* name (str): O nome do sujeito para rotulagem.  
* year (int): Ano de nascimento.  
* month (int): Mês de nascimento.  
* day (int): Dia de nascimento.  
* hour (int): Hora de nascimento (formato 24h).  
* minute (int): Minuto de nascimento.  
* city (str): Cidade de nascimento.  
* nation (str, opcional): País de nascimento (código de duas letras, ex: "US").6

**Exemplo:**

Python

from kerykeion import AstrologicalSubject

\# Instanciação usando cidade e país  
kanye \= AstrologicalSubject("Kanye", 1977, 6, 8, 8, 45, "Atlanta", "US")

#### **3.1.2 Modo Offline (Recomendado para Produção)**

Para evitar a dependência da API GeoNames, você pode fornecer os dados geográficos e de fuso horário diretamente.

**Parâmetros Adicionais:**

* lng (float): Longitude.  
* lat (float): Latitude.  
* tz\_str (str): String de fuso horário do banco de dados IANA (ex: "Europe/Rome", "America/Los\_Angeles").

**Exemplo:**

Python

from kerykeion import AstrologicalSubject

\# Instanciação offline com coordenadas e fuso horário explícitos  
kanye\_offline \= AstrologicalSubject(  
    "Kanye", 1977, 6, 8, 8, 45,  
    lng=-84.38798,  
    lat=33.749,  
    tz\_str="America/New\_York",  
    city="Atlanta"  \# Opcional, usado apenas para rotulagem  
)

#### **3.1.3 Instanciação a partir de um Timestamp ISO 8601 UTC**

Para casos de uso onde o tempo já está em um formato padronizado, a Kerykeion oferece um método de classe conveniente para instanciar um objeto a partir de uma string de data e hora no formato ISO 8601 UTC.

**Exemplo:**

Python

from kerykeion import AstrologicalSubject

\# O 'Z' no final indica o fuso horário Zulu (UTC)  
subject\_iso \= AstrologicalSubject.get\_from\_iso\_utc\_time(  
    "Johnny Depp", "1963-06-09T05:00:00Z", "Owensboro", "US"  
)

### **3.2 Atributos de Dados: Acessando Informações Planetárias e das Casas**

Uma vez que um objeto AstrologicalSubject é criado, todas as informações calculadas estão disponíveis como atributos diretos. Por exemplo, para acessar os dados do Sol ou da Lua, você simplesmente usa subject.sun ou subject.moon. O mesmo se aplica às cúspides das casas, como subject.first\_house para o Ascendente.6

Cada um desses atributos retorna um dicionário Python com uma estrutura rica e consistente, detalhada na tabela abaixo.

**Tabela 1: Estrutura de Dados dos Objetos Planetários**

| Chave (Key) | Descrição | Tipo de Dado | Exemplo de Saída (para o Sol) |
| :---- | :---- | :---- | :---- |
| name | O nome do corpo celeste. | str | "Sun" |
| quality | A qualidade ou modalidade do signo (Cardinal, Fixo, Mutável). | str | "Mutable" |
| element | O elemento do signo (Fogo, Terra, Ar, Água). | str | "Air" |
| sign | O nome abreviado do signo do zodíaco. | str | "Gem" |
| sign\_num | O número do signo do zodíaco (0 para Áries, 1 para Touro, etc.). | int | 2 |
| pos | A posição em graus dentro do signo, de 0.0 a 29.99. | float | 17.598 |
| abs\_pos | A posição absoluta na eclíptica, de 0.0 a 359.99. | float | 77.598 |
| emoji | O emoji Unicode para o signo. | str | "♊️" |
| house | A casa astrológica em que o corpo se encontra. | str | "12th House" |
| retrograde | Um booleano indicando se o planeta está em movimento retrógrado. | bool | False |

Fonte: Baseado em exemplos de saída em.6

Essa estrutura de dados detalhada é a base da filosofia *data-driven* da Kerykeion, permitindo que os desenvolvedores manipulem, analisem e integrem facilmente os resultados dos cálculos astrológicos.

### **3.3 Parâmetros de Cálculo Avançado**

A classe AstrologicalSubject oferece vários parâmetros opcionais em seu construtor para customizar a maneira como os cálculos são realizados, atendendo a diferentes escolas e tradições astrológicas.

* **Sistemas de Zodíaco:** O parâmetro zodiac\_type permite escolher entre o zodíaco "Tropic" (padrão, usado na astrologia ocidental) e o "Sidereal" (usado na astrologia Védica/Jyotish). Ao usar o zodíaco sideral, o parâmetro sidereal\_mode deve ser especificado para definir o Ayanamsa (a diferença entre os dois zodíacos). Exemplos de modos incluem "LAHIRI", "RAMAN", e "FAGAN\_BRADLEY".7 A existência dessas opções demonstra que a biblioteca foi projetada para ser flexível e servir a uma comunidade astrológica diversificada.  
* **Sistemas de Casas:** Por padrão, a Kerykeion utiliza o sistema de casas Placidus ("P"). No entanto, o parâmetro houses\_system permite selecionar qualquer um dos sistemas suportados pela Swiss Ephemeris, como Koch ("K"), Morinus ("M"), Campanus ("C"), ou Casas Iguais ("A").7 Isso dá aos astrólogos a liberdade de trabalhar com o sistema de sua preferência.  
* **Perspectivas de Cálculo:** O parâmetro perspective\_type define o ponto de vista para os cálculos. O padrão é "Apparent Geocentric", que representa a visão da Terra. Outras opções incluem "Heliocentric" (visão do Sol), "Topocentric" (visão de um local específico na superfície da Terra), e "True Geocentric".7

### **3.4 Corpos Celestes e Pontos Calculados**

A Kerykeion é capaz de calcular uma lista abrangente de corpos e pontos astrológicos.

**Tabela 2: Lista de Corpos Celestes e Pontos Suportados**

| Categoria | Nome | Identificador (string) |
| :---- | :---- | :---- |
| Planeta | Sol | "Sun" |
| Planeta | Lua | "Moon" |
| Planeta | Mercúrio | "Mercury" |
| Planeta | Vênus | "Venus" |
| Planeta | Marte | "Mars" |
| Planeta | Júpiter | "Jupiter" |
| Planeta | Saturno | "Saturn" |
| Planeta | Urano | "Uranus" |
| Planeta | Netuno | "Neptune" |
| Planeta | Plutão | "Pluto" |
| Asteroide | Quíron | "Chiron" |
| Ponto Fictício | Lilith Média | "Mean\_Lilith" |
| Nodo Lunar | Nodo Norte Médio (Rahu) | "Mean\_Node" |
| Nodo Lunar | Nodo Sul Médio (Ketu) | "Mean\_South\_Node" |
| Nodo Lunar | Nodo Norte Verdadeiro (Rahu) | "True\_Node" |
| Nodo Lunar | Nodo Sul Verdadeiro (Ketu) | "True\_South\_Node" |
| Ângulo | Ascendente | "Ascendant" |
| Ângulo | Meio do Céu | "Medium\_Coeli" |
| Ângulo | Descendente | "Descendant" |
| Ângulo | Fundo do Céu | "Imum\_Coeli" |

Fonte: Compilado de.1

A biblioteca adota uma abordagem de design inteligente para o gerenciamento desses pontos. Por padrão, a classe AstrologicalSubject calcula todos os pontos disponíveis para garantir que os dados estejam prontos para qualquer tipo de análise.17 No entanto, as classes de apresentação e análise, como

KerykeionChartSVG e SynastryAspects, ativam apenas um subconjunto mais comum por padrão (por exemplo, apenas os Nodos Lunares Médios) para evitar poluição visual e computacional. O desenvolvedor pode então usar o parâmetro active\_points para customizar exatamente quais pontos devem ser incluídos na visualização ou na análise de aspectos, fornecendo um controle granular sobre a saída final.7 Para desativar o cálculo de Quíron e Lilith desde o início, pode-se usar o parâmetro

disable\_chiron\_and\_lilith=True no construtor de AstrologicalSubject.17

## **4.0 Geração de Mapas Astrais em SVG com KerykeionChartSVG**

Enquanto a classe AstrologicalSubject é o motor de cálculo, a KerykeionChartSVG é a ferramenta de visualização. Ela consome os dados calculados para gerar mapas astrais limpos e esteticamente agradáveis no formato vetorial SVG. Esta separação de responsabilidades é uma prática de design de software robusta, permitindo que os desenvolvedores usem o motor de cálculo da Kerykeion de forma independente, seja para alimentar uma API ou para criar visualizações customizadas com outras ferramentas como Matplotlib ou D3.js.

### **4.1 Tipos de Mapas: Natal, Trânsito, Sinastria e Composto**

A classe KerykeionChartSVG é instanciada de maneiras ligeiramente diferentes dependendo do tipo de mapa desejado.

* **Mapa Natal:** Requer apenas um objeto AstrologicalSubject.  
  Python  
  from kerykeion import AstrologicalSubject, KerykeionChartSVG  
  john \= AstrologicalSubject("John Lennon", 1940, 10, 9, 18, 30, "Liverpool", "GB")  
  natal\_chart\_svg \= KerykeionChartSVG(john)

* **Mapa de Sinastria:** Requer dois objetos AstrologicalSubject, com o tipo de mapa "Synastry" especificado.  
  Python  
  paul \= AstrologicalSubject("Paul McCartney", 1942, 6, 18, 15, 30, "Liverpool", "GB")  
  synastry\_chart\_svg \= KerykeionChartSVG(john, "Synastry", paul)

* **Mapa de Trânsito:** Requer o sujeito natal e um sujeito de "trânsito" (geralmente para a data atual ou uma data futura).  
  Python  
  from datetime import datetime  
  now \= datetime.now()  
  transit\_subject \= AstrologicalSubject("Transit", now.year, now.month, now.day, now.hour, now.minute, "Liverpool", "GB")  
  transit\_chart\_svg \= KerykeionChartSVG(john, "Transit", transit\_subject)

* **Mapa Composto:** Requer um modelo de sujeito composto, gerado pela CompositeSubjectFactory.  
  Python  
  from kerykeion import CompositeSubjectFactory  
  factory \= CompositeSubjectFactory(john, paul)  
  composite\_model \= factory.get\_midpoint\_composite\_subject\_model()  
  composite\_chart\_svg \= KerykeionChartSVG(composite\_model, "Composite")

  Fonte para todos os exemplos:.1

### **4.2 Geração de Mapas Completos (makeSVG)**

Após instanciar a classe, o método makeSVG() é chamado para gerar o arquivo SVG. Por padrão, o arquivo é salvo no diretório home do usuário.1

Python

\# Gera o arquivo SVG para o mapa natal de John Lennon  
natal\_chart\_svg.makeSVG()

Este método aceita parâmetros para otimizar a saída:

* minify=True: Gera uma versão minificada do SVG, reduzindo o tamanho do arquivo.1  
* remove\_css\_variables=True: Embuti todos os estilos CSS diretamente nos elementos SVG, em vez de usar variáveis CSS. Isso aumenta a compatibilidade com visualizadores de SVG mais antigos ou menos capazes que não suportam variáveis CSS.1

### **4.3 Geração de Componentes de Mapa**

Para desenvolvedores que desejam criar layouts de interface gráfica mais complexos, a Kerykeion oferece métodos para gerar partes do mapa de forma independente.

* makeWheelOnlySVG(): Gera apenas a roda do zodíaco com os planetas e as casas, sem a grade de aspectos no centro. É útil para criar uma visualização mais limpa ou para quando a grade de aspectos será exibida separadamente.5  
* makeGridOnlySVG(): Gera apenas a grade triangular de aspectos. Isso permite que os desenvolvedores posicionem a grade em qualquer lugar em sua própria interface de usuário, desacoplando-a da roda do zodíaco.5

### **4.4 Opções de Customização Visual**

A classe KerykeionChartSVG oferece várias opções de customização, passadas durante a sua instanciação.

* new\_output\_directory: Permite especificar um diretório de saída customizado para o arquivo SVG, em vez do diretório home padrão. Por exemplo, new\_output\_directory="." salvaria o arquivo no diretório atual.5  
* chart\_language: Altera o idioma dos nomes dos planetas, signos e outros textos no mapa. Suporta vários idiomas, incluindo 'EN', 'IT', 'ES', 'PT', 'FR', 'DE', entre outros.7  
* theme: Aplica um dos quatro temas visuais pré-definidos: "Classic" (padrão), "Dark", "Dark High Contrast", ou "Light". Esses temas alteram as cores de fundo, texto e símbolos para diferentes estéticas.1  
* active\_points: Como mencionado anteriormente, esta lista de strings permite controlar exatamente quais corpos e pontos são desenhados no mapa.7

## **5.0 Análise de Aspectos e Relacionamentos**

A Kerykeion fornece classes dedicadas para análises astrológicas mais profundas, especialmente aquelas que envolvem a interação entre diferentes mapas ou ao longo do tempo.

### **5.1 Aspectos Natais**

Os aspectos dentro de um único mapa natal são calculados automaticamente quando um objeto AstrologicalSubject é criado. Eles podem ser acessados através de propriedades do objeto, embora a maneira mais comum de visualizá-los seja através da grade de aspectos gerada pela KerykeionChartSVG.

### **5.2 Aspectos de Sinastria com SynastryAspects**

Para analisar a interação entre os mapas de duas pessoas (sinastria), a classe SynastryAspects é a ferramenta indicada. Ela é instanciada com dois objetos AstrologicalSubject e calcula todos os aspectos formados entre os planetas de uma pessoa e os planetas da outra.3

O método get\_relevant\_aspects() retorna uma lista de dicionários, onde cada dicionário representa um aspecto significativo encontrado. A estrutura do dicionário inclui chaves como p1\_name (planeta da pessoa 1), p2\_name (planeta da pessoa 2), aspect (nome do aspecto, ex: "trine"), e orbit (o quão exato é o aspecto).3

Python

from kerykeion import AstrologicalSubject, SynastryAspects

first \= AstrologicalSubject("Jack", 1990, 6, 15, 15, 15, "Roma", "IT")  
second \= AstrologicalSubject("Jane", 1991, 10, 25, 21, 0, "Roma", "IT")

synastry \= SynastryAspects(first, second)  
aspect\_list \= synastry.get\_relevant\_aspects()

\# Imprime o primeiro aspecto relevante encontrado  
print(aspect\_list)  
\# Saída de exemplo:  
\# {'p1\_name': 'Sun', 'p1\_abs\_pos': 84.17, 'p2\_name': 'Sun', 'p2\_abs\_pos': 211.90, 'aspect': 'trine',...}

### **5.3 Geração de Mapas Compostos com CompositeSubjectFactory**

O mapa composto é uma técnica que cria um único mapa para um relacionamento, calculando os pontos médios entre os planetas de duas pessoas. A Kerykeion abstrai essa complexidade com a CompositeSubjectFactory. Esta classe recebe dois objetos AstrologicalSubject e possui um método, get\_midpoint\_composite\_subject\_model(), que retorna um novo objeto AstrologicalSubject "virtual" representando o mapa composto. Este objeto pode então ser usado para gerar um mapa SVG ou para análise de dados, como qualquer outro sujeito astrológico.1

### **5.4 Análise de Trânsitos Avançada com TransitsTimeRangeFactory**

Uma das adições mais recentes e poderosas à biblioteca é a TransitsTimeRangeFactory. Esta classe foi projetada para a astrologia preditiva e de pesquisa, permitindo a análise de eventos de trânsito ao longo de um período de tempo definido.17 Em vez de calcular um único momento de trânsito, esta fábrica pode gerar dados para cada dia (ou outro intervalo) dentro de um período, identificando todos os aspectos exatos que os planetas em trânsito formam com o mapa natal. O resultado é um

TransitsTimeRangeModel, uma estrutura de dados que consolida todos os eventos de trânsito, tornando mais fácil identificar períodos astrologicamente significativos.17

## **6.0 Manipulação e Exportação de Dados**

Um dos principais pontos fortes da Kerykeion é a facilidade com que os dados calculados podem ser extraídos e manipulados. A biblioteca oferece formatos de saída tanto para consumo humano (texto) quanto para consumo de máquina (JSON).

### **6.1 Geração de Relatórios Textuais com a Classe Report**

Para uma visualização rápida e legível dos dados de um mapa, a classe Report é ideal. Ela recebe um objeto AstrologicalSubject e, através do método print\_report(), gera uma tabela formatada em texto simples no console.3 Este relatório inclui as posições dos planetas (signo, grau, casa, status retrógrado) e as cúspides das casas.

Python

from kerykeion import AstrologicalSubject, Report

kanye \= AstrologicalSubject("Kanye", 1977, 6, 8, 8, 45, "Atlanta", "US")  
report \= Report(kanye)  
report.print\_report()

A saída pode ser facilmente redirecionada para um arquivo de texto para armazenamento ou compartilhamento:

Bash

python your\_script.py \> kanye\_report.txt

### **6.2 Exportação de Dados para JSON**

Para integração com outras aplicações, a exportação para JSON é o método preferido. Todo objeto AstrologicalSubject possui um método .json() que serializa o objeto inteiro, incluindo todos os planetas, casas e outros dados calculados, em uma string JSON.7

Python

from kerykeion import AstrologicalSubject

johnny \= AstrologicalSubject("Johnny Depp", 1963, 6, 9, 0, 0, "Owensboro", "US")

\# Gera a string JSON com indentação para melhor legibilidade  
json\_output \= johnny.json(dump=True, indent=2)  
print(json\_output)

Este método é a espinha dorsal para a construção de APIs, pois o formato JSON é universalmente compreendido por aplicações web e clientes.

### **6.3 Padrões de Manipulação: Formatando e Exibindo Dados**

Com os dados disponíveis como estruturas Python nativas, é simples iterar sobre eles para criar saídas customizadas. Por exemplo, para exibir apenas o nome, o grau e o signo de cada planeta:

Python

from kerykeion import AstrologicalSubject

subject \= AstrologicalSubject("Example", 2000, 1, 1, 12, 0, "London", "GB")

print(f"Planets for {subject.name}:")  
for planet in subject.planets:  
    \# Formata a posição para duas casas decimais  
    position \= f"{planet\['pos'\]:.2f}"  
    sign\_name \= planet\['sign'\]  
    planet\_name \= planet\['name'\]  
    print(f"- {planet\_name}: {position}° {sign\_name}")

## **7.0 Integração com o Ecossistema Python**

A Kerykeion foi projetada para se integrar perfeitamente com outras bibliotecas populares do ecossistema de ciência de dados e desenvolvimento web em Python.

### **7.1 Análise de Dados com pandas**

Embora a Kerykeion não tenha um método nativo .to\_pandas(), a integração com a biblioteca pandas é extremamente direta. A razão para isso reside na estrutura de dados da Kerykeion: métodos que retornam múltiplos itens, como a lista de planetas (subject.planets) ou a lista de aspectos (synastry.get\_relevant\_aspects()), o fazem como uma lista de dicionários. O construtor do pandas.DataFrame é otimizado para aceitar exatamente este formato de dados, tornando a conversão trivial.

**Exemplo Prático: Análise de Planetas com pandas**

Python

import pandas as pd  
from kerykeion import AstrologicalSubject

\# 1\. Criar o objeto AstrologicalSubject  
subject \= AstrologicalSubject("Test Subject", 1995, 5, 10, 10, 30, "New York", "US")

\# 2\. Acessar a lista de planetas e criar o DataFrame  
planets\_list \= subject.planets  
df \= pd.DataFrame(planets\_list)

\# 3\. Realizar análises com o DataFrame  
print("DataFrame de Planetas:")  
print(df\[\['name', 'sign', 'pos', 'house', 'retrograde'\]\])

\# Exemplo de análise: Contar planetas por elemento  
print("\\nDistribuição de Planetas por Elemento:")  
print(df\['element'\].value\_counts())

\# Exemplo de análise: Filtrar planetas retrógrados  
print("\\nPlanetas Retrógrados:")  
print(df\[df\['retrograde'\] \== True\]\['name'\].tolist())

Este padrão permite que os usuários aproveitem todo o poder do pandas para filtrar, agregar, analisar e visualizar dados astrológicos em larga escala, abrindo portas para pesquisas estatísticas e projetos de *machine learning*.22

### **7.2 Criação de APIs Web: Padrões com FastAPI e Flask**

A Kerykeion serve como um motor de cálculo ideal para o backend de uma API de astrologia. Frameworks como FastAPI ou Flask podem ser usados para criar endpoints que recebem dados de nascimento, utilizam a Kerykeion para processá-los e retornam os resultados em JSON ou como um mapa SVG.

**Exemplo Prático com FastAPI:**

Este exemplo cria uma API simples com dois endpoints: um que retorna os dados do mapa natal em JSON e outro que retorna o mapa em SVG.

Python

\# main.py  
from fastapi import FastAPI  
from fastapi.responses import Response  
from pydantic import BaseModel  
from kerykeion import AstrologicalSubject, KerykeionChartSVG

\# Modelo Pydantic para validar os dados de entrada  
class BirthData(BaseModel):  
    name: str  
    year: int  
    month: int  
    day: int  
    hour: int  
    minute: int  
    city: str  
    nation: str

app \= FastAPI()

@app.post("/chart/json")  
def get\_chart\_json(data: BirthData):  
    """  
    Recebe dados de nascimento e retorna o mapa astral completo em formato JSON.  
    """  
    subject \= AstrologicalSubject(  
        data.name, data.year, data.month, data.day,  
        data.hour, data.minute, data.city, data.nation  
    )  
    \# O método.json() da Kerykeion retorna um dicionário, que o FastAPI converte para JSON  
    return subject.json(dump=False)

@app.post("/chart/svg")  
def get\_chart\_svg(data: BirthData):  
    """  
    Recebe dados de nascimento e retorna o mapa astral como uma imagem SVG.  
    """  
    subject \= AstrologicalSubject(  
        data.name, data.year, data.month, data.day,  
        data.hour, data.minute, data.city, data.nation  
    )  
    \# Gera o SVG em memória  
    chart\_svg \= KerykeionChartSVG(subject)  
    svg\_string \= chart\_svg.makeSVG(get\_svg=True)

    return Response(content=svg\_string, media\_type="image/svg+xml")

Para executar esta API, salve o código como main.py e execute no terminal: uvicorn main:app \--reload. Você pode então enviar requisições POST para http://127.0.0.1:8000/chart/json ou http://127.0.0.1:8000/chart/svg.23

### **7.3 Armazenamento de Dados**

Os dados estruturados gerados pela Kerykeion, especialmente a saída JSON, são facilmente armazenáveis em diferentes tipos de bancos de dados.

* **Bancos de Dados NoSQL (ex: MongoDB):** Esta é a abordagem mais natural. O documento JSON completo retornado por subject.json() pode ser inserido diretamente em uma coleção do MongoDB. Isso preserva a estrutura aninhada dos dados e oferece grande flexibilidade para consultas futuras.  
* **Bancos de Dados SQL (ex: PostgreSQL, SQLite):** A integração com bancos de dados relacionais requer a normalização dos dados. Seria necessário criar tabelas, como Charts, Planets, Houses, e mapear os campos do JSON para as colunas correspondentes, estabelecendo relações entre elas (por exemplo, uma chave estrangeira chart\_id na tabela Planets).

## **8.0 Funcionamento Interno da Biblioteca**

### **8.1 O Motor de Cálculo: pyswisseph**

O núcleo computacional da Kerykeion é inteiramente dependente da pyswisseph. Quando um AstrologicalSubject é instanciado, a Kerykeion realiza uma série de etapas internas:

1. **Conversão de Tempo:** A data e hora de nascimento, juntamente com o fuso horário, são convertidas para o formato de Dia Juliano (Julian Day) em Tempo Universal (UT), que é o padrão de entrada para a maioria das funções da Swiss Ephemeris.  
2. **Cálculo Planetário:** A biblioteca itera sobre a lista de corpos celestes a serem calculados e chama a função swe.calc\_ut (ou swe.calc em versões mais antigas) para cada um.10 Esta função recebe o Dia Juliano e o identificador do planeta, e retorna um array com sua longitude, latitude, distância, e velocidades. A Kerykeion então processa essa saída para extrair a longitude eclíptica (  
   abs\_pos) e convertê-la para o formato de signo e grau (sign, pos).  
3. **Cálculo das Casas:** A Kerykeion chama a função swe.houses passando o Dia Juliano, a latitude, a longitude e o caractere do sistema de casas desejado (ex: 'P' para Placidus).11 Esta função retorna as cúspides das 12 casas e os quatro ângulos principais (Ascendente, Meio do Céu, etc.).

Toda a precisão astronômica da Kerykeion é, portanto, uma herança direta da implementação rigorosa da Swiss Ephemeris.11

### **8.2 Lógica de Cálculo das Casas e Aspectos**

O posicionamento de um planeta em uma casa é determinado comparando a posição absoluta do planeta (abs\_pos) com as posições das cúspides das casas. A Kerykeion verifica entre quais duas cúspides a posição do planeta se encontra para atribuir a casa correta. Recentemente, a lógica foi aprimorada com a função is\_point\_between para lidar corretamente com sistemas de casas onde o Ascendente não coincide necessariamente com a cúspide da primeira casa (como no sistema de Signos Inteiros).17

O cálculo de aspectos é um processo puramente matemático. A biblioteca compara as posições angulares absolutas (abs\_pos) de todos os pares de planetas ativos. Para cada par, ela calcula a diferença angular e verifica se essa diferença se encaixa em um dos aspectos definidos (ex: Conjunção, Sextil, Quadratura, Trígono, Oposição) dentro de uma margem de erro permitida, conhecida como "órbita".

### **8.3 Geocodificação e Gerenciamento de Cache**

Quando o modo online é usado, a Kerykeion envia uma requisição HTTP para a API do GeoNames com o nome da cidade e do país. O serviço retorna dados geográficos, incluindo latitude, longitude e o tz\_str correspondente. Para minimizar a dependência e o número de chamadas a esta API externa, a Kerykeion implementa um mecanismo de cache local. Os resultados bem-sucedidos da geocodificação são armazenados localmente. Em versões recentes, o tempo de vida padrão desse cache foi aumentado de 24 horas para 30 dias, otimizando significativamente o desempenho para requisições repetidas para a mesma localização.17

## **9.0 Boas Práticas, Limitações e Erros Comuns**

### **9.1 Melhores Práticas de Uso**

* **Prefira o Modo Offline para Produção:** Para aplicações web, APIs ou qualquer sistema que precise de alta disponibilidade e desempenho, é fundamental usar o modo offline, fornecendo lng, lat e tz\_str explicitamente. Isso elimina a latência da rede, a dependência de um serviço externo e o risco de falhas por limites de API.6  
* **Seja Explícito sobre Pontos Ativos:** Ao gerar SVGs ou calcular aspectos, use o parâmetro active\_points para especificar apenas os corpos que você precisa. Isso torna o código mais legível, a saída mais limpa e o processamento mais rápido.  
* **Separe a Lógica de Cálculo e Apresentação:** Crie o objeto AstrologicalSubject uma vez para obter todos os dados. Em seguida, passe esse objeto para diferentes funções ou classes responsáveis pela apresentação (geração de SVG, formatação de JSON para uma API, etc.). Isso segue o princípio da responsabilidade única e torna o código mais modular e testável.  
* **Gerencie Versões:** Verifique o CHANGELOG.md para entender as mudanças entre as versões. Funcionalidades mais recentes, como TransitsTimeRangeFactory, exigirão uma versão mais nova da biblioteca.

### **9.2 Limitações Conhecidas**

* **Documentação Oficial:** A documentação oficial hospedada em kerykeion.net e seus subdomínios (pydocs.kerykeion.net) está frequentemente inacessível ou desatualizada.26 Atualmente, o arquivo  
  README.md no repositório GitHub é a fonte de informação mais confiável e atualizada.7  
* **Funcionalidades Astrológicas Avançadas:** Técnicas como progressões secundárias e direções de arco solar não são implementadas nativamente nas versões estáveis. A funcionalidade de Retornos Solares é mencionada como um objetivo futuro, mas ainda não está disponível.27  
* **Escalabilidade de SVG:** Existe um *issue* aberto no GitHub relacionado ao desafio de escalar e redimensionar os SVGs gerados para se ajustarem a diferentes proporções de tela (como 16:9) de forma responsiva. Isso pode exigir manipulação manual do SVG após a geração.28  
* **Licenciamento AGPL:** A licença AGPL-3.0 pode ser uma limitação para desenvolvedores que desejam integrar a Kerykeion em projetos comerciais de código fechado, direcionando-os para o uso da AstrologerAPI.7

### **9.3 Erros Comuns e Suas Soluções**

* **Erro de Geocodificação:** A falha na obtenção de coordenadas do GeoNames é um erro comum. Pode ser causado por falta de conexão com a internet, limites de API excedidos ou nomes de cidades ambíguos.  
  * **Solução:** A solução mais robusta é migrar para o modo offline, fornecendo as coordenadas e o fuso horário manualmente.  
* **Incompatibilidade de Versão:** Usar código de exemplos antigos com versões novas da biblioteca (ou vice-versa) pode levar a erros como AttributeError ou TypeError, devido a mudanças em nomes de classes (KrInstance vs. AstrologicalSubject) ou parâmetros (disable\_chiron vs. disable\_chiron\_and\_lilith).  
  * **Solução:** Certifique-se de que a versão mais recente da Kerykeion está instalada (pip install \--upgrade kerykeion) e siga os exemplos da documentação atual no GitHub.  
* **Problemas de Dependência em Ambientes Serverless (AWS Lambda, etc.):** Um erro comum ao implantar uma aplicação que usa Kerykeion em um ambiente como AWS Lambda é Unable to import module 'lambda\_function': No module named 'swisseph'. Isso ocorre porque a pyswisseph possui componentes binários que precisam ser empacotados corretamente.  
  * **Solução:** É crucial criar uma camada (Lambda Layer) que contenha não apenas os pacotes Python, mas também todos os binários e arquivos de efemérides necessários pela pyswisseph. O pacote de implantação deve ser construído em um ambiente compatível com o ambiente de execução do Lambda (por exemplo, Amazon Linux).29

## **10.0 Desenvolvimento e Futuro da Biblioteca**

### **10.1 Histórico de Versões e CHANGELOG Relevante**

A Kerykeion tem um ciclo de desenvolvimento ativo, com novas versões sendo lançadas para adicionar funcionalidades, corrigir bugs e refatorar o código. A análise do arquivo CHANGELOG.md revela marcos importantes na evolução recente da biblioteca.30

**Tabela 3: Resumo das Principais Mudanças por Versão (v4.x)**

| Versão | Data de Lançamento (Aproximada) | Principais Mudanças e Novidades |
| :---- | :---- | :---- |
| **4.25.0** | Fevereiro 2025 | Introdução da classe TransitsTimeRangeFactory para análise detalhada de trânsitos ao longo do tempo.17 |
| **4.24.0** | Fevereiro 2025 | Adição da CompositeSubjectFactory para a criação de mapas compostos baseados em pontos médios.17 |
| **4.22.0** | Janeiro 2025 | Introdução do parâmetro active\_points na KerykeionChartSVG para controle granular dos pontos exibidos no mapa.17 |
| **4.19.0** | Novembro 2024 | Cálculo explícito dos quatro ângulos (AC, MC, DC, IC), melhorando a precisão para sistemas de casas como Signos Inteiros.17 |
| **4.16.0** | Agosto 2024 | Adicionado suporte para Lilith. O parâmetro disable\_chiron foi depreciado e substituído por disable\_chiron\_and\_lilith.17 |
| **4.13.0** | Julho 2024 | O tempo de cache padrão do GeoNames foi estendido de 24 horas para 30 dias para reduzir chamadas de API.17 |
| **4.5.0** | (Data anterior) | Adicionada a opção disable\_chiron=True para compatibilidade com datas mais antigas.30 |

Fonte: Compilado de.17

### **10.2 O Roadmap para a Versão 5**

O desenvolvimento da **Versão 5** da Kerykeion está em andamento ativo e representa uma evolução significativa para a biblioteca. O trabalho está sendo realizado publicamente na branch next do repositório GitHub, e várias versões alfa (como 5.0.0a4) já foram disponibilizadas no PyPI para testes pela comunidade.7

Embora um roadmap formal não seja publicado, as discussões no GitHub, os commits na branch next e os comentários do desenvolvedor em plataformas como Ko-fi 27 indicam as principais direções do projeto:

* **Refatoração Profunda:** A V5 parece ser uma grande refatoração ou reescrita da base de código. O objetivo é modernizar a arquitetura, torná-la mais manutenível, mais flexível e mais fácil de estender no futuro.  
* **Novas Funcionalidades:** A implementação de cálculos de **Retornos Solares e Planetários** é uma das funcionalidades mais aguardadas e mencionadas como um objetivo para o futuro.27  
* **Flexibilidade Gráfica:** Melhorar a flexibilidade da geração de SVGs é outro foco, visando facilitar a customização e a integração em diferentes layouts.

A existência de uma branch de desenvolvimento de longa duração e múltiplas versões alfa sugere que as mudanças na V5 são estruturais, com o objetivo de preparar a biblioteca para a próxima década de desenvolvimento de aplicações astrológicas.

### **10.3 Como Contribuir para o Projeto**

A Kerykeion é um projeto de código aberto que acolhe contribuições da comunidade. As formas de contribuir incluem:

* **Relatar Bugs e Sugerir Funcionalidades:** Abrindo *Issues* no repositório GitHub do projeto.7  
* **Enviar Código:** Contribuindo com correções de bugs ou novas funcionalidades através de *Pull Requests*.7  
* **Apoio Financeiro:** O desenvolvedor mantém uma página no Ko-fi para doações, que ajudam a financiar o tempo dedicado ao projeto e os custos associados.6

É importante notar que, devido à licença **AGPL-3.0**, qualquer projeto que incorpore a biblioteca Kerykeion e seja distribuído publicamente deve, em geral, ter seu código-fonte aberto sob uma licença compatível. Para projetos de código fechado, a alternativa recomendada é o uso da **AstrologerAPI**.7

Para fins acadêmicos, a biblioteca pode ser citada formalmente, e o formato de citação sugerido pelo autor está disponível no README.md do projeto.7

#### **Referências citadas**

1. g-battaglia/kerykeion: Data-Driven Astrology Kerykeion is a Python library for astrology, ideal for AI and data science applications. It generates SVG charts and extracts detailed structured data for birth charts, synastry, transits, composite charts, and more. \- GitHub, acessado em junho 19, 2025, [https://github.com/g-battaglia/kerykeion](https://github.com/g-battaglia/kerykeion)  
2. astrology-calculator · GitHub Topics, acessado em junho 19, 2025, [https://github.com/topics/astrology-calculator?l=python](https://github.com/topics/astrology-calculator?l=python)  
3. kerykeion \- Codesandbox, acessado em junho 19, 2025, [http://codesandbox.io/p/github/mettaversesociety/kerykeion](http://codesandbox.io/p/github/mettaversesociety/kerykeion)  
4. kerykeion \- PyPI, acessado em junho 19, 2025, [https://pypi.org/project/kerykeion/2.3.3/](https://pypi.org/project/kerykeion/2.3.3/)  
5. kerykeion \- PyPI, acessado em junho 19, 2025, [https://pypi.org/project/kerykeion/](https://pypi.org/project/kerykeion/)  
6. kerykeion \- Giacomo Battaglia \- GitLab, acessado em junho 19, 2025, [https://gitlab.com/g-battaglia/kerykeion](https://gitlab.com/g-battaglia/kerykeion)  
7. kerykeion/README.md at master \- GitHub, acessado em junho 19, 2025, [https://github.com/g-battaglia/kerykeion/blob/master/README.md](https://github.com/g-battaglia/kerykeion/blob/master/README.md)  
8. Exploring OpenAI Agent SDK \- Rangarajan Krishnamoorthy on Programming and Other Topics, acessado em junho 19, 2025, [https://www.rangakrish.com/index.php/2025/03/26/exploring-openai-agent-sdk/](https://www.rangakrish.com/index.php/2025/03/26/exploring-openai-agent-sdk/)  
9. yash676ganga/AI-Astrologer \- GitHub, acessado em junho 19, 2025, [https://github.com/yash676ganga/AI-Astrologer](https://github.com/yash676ganga/AI-Astrologer)  
10. How to get Heliocentric positions from pyswisseph or kerykeion library \- Stack Overflow, acessado em junho 19, 2025, [https://stackoverflow.com/questions/77286337/how-to-get-heliocentric-positions-from-pyswisseph-or-kerykeion-library](https://stackoverflow.com/questions/77286337/how-to-get-heliocentric-positions-from-pyswisseph-or-kerykeion-library)  
11. Decoding the SWISS Ephemeris \- Av8rAero, acessado em junho 19, 2025, [https://www.av8raero.com/blog/decoding-the-swiss-ephemeris](https://www.av8raero.com/blog/decoding-the-swiss-ephemeris)  
12. astrorigin/pyswisseph: Python extension to the Swiss Ephemeris \- GitHub, acessado em junho 19, 2025, [https://github.com/astrorigin/pyswisseph](https://github.com/astrorigin/pyswisseph)  
13. pyswisseph \- PyPI, acessado em junho 19, 2025, [https://pypi.org/project/pyswisseph/](https://pypi.org/project/pyswisseph/)  
14. Swiss Ephemeris \- Astrodienst, acessado em junho 19, 2025, [https://www.astro.com/ftp/swisseph/doc/swephprg.2.10.pdf](https://www.astro.com/ftp/swisseph/doc/swephprg.2.10.pdf)  
15. Astrologer \- Rapid API, acessado em junho 19, 2025, [https://rapidapi.com/gbattaglia/api/astrologer](https://rapidapi.com/gbattaglia/api/astrologer)  
16. kerykeion \- PyPI, acessado em junho 19, 2025, [https://pypi.org/project/kerykeion/4.13.1/](https://pypi.org/project/kerykeion/4.13.1/)  
17. Releases · g-battaglia/kerykeion \- GitHub, acessado em junho 19, 2025, [https://github.com/g-battaglia/kerykeion/releases](https://github.com/g-battaglia/kerykeion/releases)  
18. notebook77517cac57 \- Kaggle, acessado em junho 19, 2025, [https://www.kaggle.com/code/dangaichharsh/notebook77517cac57/notebook?scriptVersionId=197865950](https://www.kaggle.com/code/dangaichharsh/notebook77517cac57/notebook?scriptVersionId=197865950)  
19. kerykeion \- piwheels, acessado em junho 19, 2025, [https://www.piwheels.org/project/kerykeion/](https://www.piwheels.org/project/kerykeion/)  
20. Haskell bindings for the Swiss Ephemeris C library \- Hackage, acessado em junho 19, 2025, [https://hackage.haskell.org/package/swiss-ephemeris](https://hackage.haskell.org/package/swiss-ephemeris)  
21. kerykeion \- PyPI, acessado em junho 19, 2025, [https://pypi.org/project/kerykeion/0.9.5/](https://pypi.org/project/kerykeion/0.9.5/)  
22. Astrology Elements Distribution over a Few Years. Visualization. Pandas. Seaborn, acessado em junho 19, 2025, [https://www.kvdm.dev/articles/astrology-elements-distribution-over-a-few-years-visualization-pandas-seaborn/](https://www.kvdm.dev/articles/astrology-elements-distribution-over-a-few-years-visualization-pandas-seaborn/)  
23. CrewAI \+ MCP \+ Neo4j \+ FastAPI \- YouTube, acessado em junho 19, 2025, [https://www.youtube.com/watch?v=q3NIH6wE3M4](https://www.youtube.com/watch?v=q3NIH6wE3M4)  
24. keryc/chatgpt-plugins-fastapi-quickstart \- GitHub, acessado em junho 19, 2025, [https://github.com/keryc/chatgpt-plugins-fastapi-quickstart](https://github.com/keryc/chatgpt-plugins-fastapi-quickstart)  
25. charts · GitHub Topics, acessado em junho 19, 2025, [https://github.com/topics/charts?l=python\&o=desc\&s=updated](https://github.com/topics/charts?l=python&o=desc&s=updated)  
26. acessado em dezembro 31, 1969, httpss://kerykeion.net/pydocs/kerykeion.html  
27. Buy kerykeion a Coffee \- Ko-fi, acessado em junho 19, 2025, [https://ko-fi.com/kerykeion](https://ko-fi.com/kerykeion)  
28. Issues · g-battaglia/kerykeion \- GitHub, acessado em junho 19, 2025, [https://github.com/g-battaglia/kerykeion/issues](https://github.com/g-battaglia/kerykeion/issues)  
29. Error when importing library dependencies added to a layer \- AWS re:Post, acessado em junho 19, 2025, [https://repost.aws/questions/QUrTcYYcFvTS67wzk2aDJtdg/error-when-importing-library-dependencies-added-to-a-layer](https://repost.aws/questions/QUrTcYYcFvTS67wzk2aDJtdg/error-when-importing-library-dependencies-added-to-a-layer)  
30. kerykeion/CHANGELOG.md at master · g-battaglia/kerykeion · GitHub, acessado em junho 19, 2025, [https://github.com/g-battaglia/kerykeion/blob/master/CHANGELOG.md](https://github.com/g-battaglia/kerykeion/blob/master/CHANGELOG.md)