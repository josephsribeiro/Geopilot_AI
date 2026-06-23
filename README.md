<div align="center">

# 🛰️ GeoPilot AI

**Plataforma de análise geoespacial com Google Earth Engine e inteligência artificial**

*Analise o planeta. Sem escrever uma linha de código.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-ff4b4b?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Earth Engine](https://img.shields.io/badge/Google_Earth_Engine-4285F4?style=flat-square&logo=google&logoColor=white)](https://earthengine.google.com)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Pro-8E75B2?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/Licença-MIT-39ff14?style=flat-square)](LICENSE)

</div>

---

## O que é o GeoPilot AI?

O **GeoPilot AI** é uma aplicação web que conecta o poder do **Google Earth Engine** à inteligência do **Gemini AI**, permitindo que qualquer pessoa — pesquisadores, gestores ambientais, professores, analistas — execute análises geoespaciais complexas diretamente no navegador, sem precisar programar.

Você delimita uma área no mapa, escolhe ou descreve uma análise, e o sistema gera e executa o código automaticamente.

---

## Funcionalidades

- **Mapa interativo** para desenhar, editar e importar áreas de interesse
- **20+ análises pré-configuradas** organizadas por categoria temática
- **Seleção dinâmica de satélites** — cada análise mostra apenas os satélites compatíveis
- **Análise personalizada em linguagem natural** — descreva o que quer e o Gemini gera o código
- **Execução direta no GEE** sem sair do aplicativo
- **Visualização dos resultados** com mapas, estatísticas e gráficos integrados
- **Exportação** do código gerado e da geometria da AOI

---

## Demonstração rápida

```
1. Insira sua chave Gemini API
2. Conecte ao Google Earth Engine
3. Desenhe um polígono no mapa
4. Selecione "NDVI" → "Sentinel-2"
5. Clique em "Gerar Código com Gemini"
6. Clique em "Executar no GEE"
7. Visualize o resultado
```

---

## Análises disponíveis

| Categoria | Índices / Métodos |
|-----------|------------------|
| 🌿 **Vegetação** | NDVI · SAVI · EVI |
| 💧 **Recursos Hídricos** | NDWI · MNDWI · Turbidez |
| 🌡️ **Temperatura** | LST (Land Surface Temperature) |
| 🏙️ **Áreas Urbanas** | NDBI · Ilhas de Calor Urbanas |
| 🟫 **Solo** | BSI (Bare Soil Index) |
| 🔥 **Queimadas** | NBR · dNBR |
| 📈 **Mudanças Temporais** | Detecção de mudanças · Desmatamento · Expansão urbana |
| 🗺️ **Classificação** | Uso e cobertura · Supervisionada · Não supervisionada |
| 🤖 **Personalizada** | Qualquer análise descrita em linguagem natural |

---

## Satélites suportados

| Satélite | Coleção GEE | Resolução | Período disponível |
|----------|-------------|-----------|-------------------|
| **Sentinel-2** | `COPERNICUS/S2_SR_HARMONIZED` | 10 m | 2015 – presente |
| **Landsat 9** | `LANDSAT/LC09/C02/T1_L2` | 30 m | 2021 – presente |
| **Landsat 8** | `LANDSAT/LC08/C02/T1_L2` | 30 m | 2013 – presente |
| **Landsat 7** | `LANDSAT/LE07/C02/T1_L2` | 30 m | 1999 – 2022 |
| **Landsat 5** | `LANDSAT/LT05/C02/T1_L2` | 30 m | 1984 – 2013 |
| **MODIS Terra** | `MODIS/061/MOD13A2` | 500 m | 2000 – presente |

A seleção de satélites é **dinâmica** — ao escolher uma análise, apenas os satélites que possuem as bandas necessárias aparecem como opção.

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| **Interface** | [Streamlit](https://streamlit.io) |
| **Mapas** | [Leafmap](https://leafmap.org) · [Folium](https://python-visualization.github.io/folium) |
| **Inteligência Artificial** | [Google Gemini 1.5 Pro](https://deepmind.google/technologies/gemini) |
| **Geoprocessamento** | [Google Earth Engine](https://earthengine.google.com) · [geemap](https://geemap.org) |
| **Dados geoespaciais** | [GeoPandas](https://geopandas.org) · [Shapely](https://shapely.readthedocs.io) · [Fiona](https://fiona.readthedocs.io) |
| **Computação** | [NumPy](https://numpy.org) · [Pandas](https://pandas.pydata.org) |
| **Visualização** | [Plotly](https://plotly.com) · [Matplotlib](https://matplotlib.org) |

---

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Conta no [Google Earth Engine](https://earthengine.google.com/) (gratuita para pesquisa)
- Chave de API do [Google Gemini](https://aistudio.google.com/app/apikey) (gratuita)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/geopilot-ai.git
cd geopilot-ai

# 2. Crie e ative um ambiente virtual
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Autentique no Google Earth Engine (necessário apenas na primeira vez)
earthengine authenticate

# 5. Inicie o aplicativo
streamlit run app.py
```

O aplicativo abrirá automaticamente em `http://localhost:8501`.

---

## Configuração das credenciais

As credenciais são inseridas diretamente no aplicativo — não é necessário criar arquivos `.env` para uso básico.

| Credencial | Onde obter | Como usar no app |
|-----------|-----------|-----------------|
| **Gemini API Key** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | Campo "Chave Gemini API" na sidebar |
| **Google Earth Engine** | [earthengine.google.com](https://earthengine.google.com/) | Botão "Conectar ao GEE" na sidebar |

Para autenticação via **Service Account** (ambientes de produção ou servidores), faça upload do arquivo `.json` da conta de serviço diretamente na interface.

---

## Estrutura do projeto

```
geopilot/
│
├── app.py                         # Ponto de entrada — UI principal e hero header
├── requirements.txt               # Dependências Python
├── README.md
│
├── config/
│   └── settings.py                # Configurações globais e prompt de sistema do Gemini
│
├── modules/
│   ├── auth.py                    # Autenticação Gemini API e Google Earth Engine
│   ├── analysis_catalog.py        # Catálogo das 20+ análises pré-configuradas
│   ├── satellite_catalog.py       # Catálogo de satélites com mapeamento de bandas
│   ├── map_tools.py               # Mapa interativo com Leafmap e Folium
│   ├── gemini_generator.py        # Construção de prompt e chamada à API Gemini
│   ├── gee_connection.py          # Utilitários de verificação de conexão GEE
│   └── execution_engine.py        # Execução do código gerado em namespace isolado
│
└── utils/
    └── geometry_converter.py      # Conversão GeoJSON ↔ ee.Geometry e utilidades de bbox
```

---

## Como a análise personalizada funciona

Quando você seleciona **"Análise Personalizada 🤖"** e descreve o que deseja, o fluxo é:

```
Descrição em linguagem natural
        ↓
Prompt estruturado com contexto (AOI, datas, satélites disponíveis)
        ↓
Gemini 1.5 Pro gera código Python puro para GEE
        ↓
Código executado no namespace do aplicativo com ee.Initialize()
        ↓
Resultado exibido: mapa, estatísticas, gráficos
```

**Exemplo de entrada:**
> "Mapear áreas queimadas entre 2020 e 2023 usando Sentinel-2 e calcular a área total afetada em hectares."

**O Gemini retornará** código Python completo que calcula o dNBR, classifica severidade de queima e exporta estatísticas — pronto para execução.

---

## Importação e exportação de geometrias

O aplicativo suporta os principais formatos geoespaciais:

| Operação | Formatos suportados |
|----------|-------------------|
| **Importar AOI** | GeoJSON · Shapefile (`.zip`) · KML |
| **Exportar AOI** | GeoJSON |
| **Exportar código** | Python (`.py`) |

---

## Regras de geração de código pelo Gemini

O Gemini é instruído para seguir regras estritas:

- Retornar **apenas código Python** — sem explicações, conversas ou markdown
- Usar sempre a variável `aoi` (já definida como `ee.Geometry`)
- Usar `start_date` e `end_date` como strings `YYYY-MM-DD`
- Aplicar filtro de cobertura de nuvens automaticamente
- Calcular estatísticas com `reduceRegion` (mean, min, max, std)
- Gerar mapa com `geemap.Map()` e legenda quando aplicável
- Aplicar fatores de escala corretos para cada coleção Landsat

---

## Contribuindo

Contribuições são bem-vindas! Veja como participar:

```bash
# Fork o repositório e clone localmente
git clone https://github.com/seu-usuario/geopilot-ai.git

# Crie uma branch para sua feature
git checkout -b feature/nova-analise

# Faça suas alterações e commit
git commit -m "feat: adiciona análise de salinidade do solo"

# Envie para o GitHub
git push origin feature/nova-analise

# Abra um Pull Request
```

### Áreas onde contribuições são especialmente úteis

- Novas análises no `analysis_catalog.py`
- Suporte a novos satélites no `satellite_catalog.py`
- Melhorias no prompt do Gemini em `config/settings.py`
- Testes automatizados
- Documentação e exemplos de uso

---

## Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Créditos e referências

- [Google Earth Engine](https://earthengine.google.com/) — plataforma de análise geoespacial em nuvem
- [geemap](https://geemap.org/) — biblioteca Python para visualização GEE
- [Leafmap](https://leafmap.org/) — mapeamento interativo com Python
- [Google Gemini](https://deepmind.google/technologies/gemini/) — modelo de linguagem multimodal

---

<div align="center">

Feito com 🛰️ para a comunidade de sensoriamento remoto e geoprocessamento

</div>
