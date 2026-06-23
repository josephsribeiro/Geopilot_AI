# 🛰️ GeoPilot AI

> Análise geoespacial avançada com Google Earth Engine e Gemini AI — sem escrever uma linha de código.

---

## Estrutura do projeto

```
geopilot/
├── app.py                        # Aplicativo Streamlit principal
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py               # Configurações globais e prompt do Gemini
├── modules/
│   ├── __init__.py
│   ├── auth.py                   # Autenticação Gemini + GEE
│   ├── analysis_catalog.py       # Catálogo de análises pré-configuradas
│   ├── satellite_catalog.py      # Satélites e mapeamento de bandas
│   ├── map_tools.py              # Mapa interativo (Leafmap + Folium)
│   ├── gemini_generator.py       # Geração de código GEE via Gemini
│   ├── gee_connection.py         # Utilitários de conexão GEE
│   └── execution_engine.py       # Execução do código gerado
└── utils/
    ├── __init__.py
    └── geometry_converter.py     # Conversão GeoJSON ↔ ee.Geometry
```

---

## Instalação

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd geopilot

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Primeira vez) Autentique no Google Earth Engine
earthengine authenticate

# 5. Execute o aplicativo
streamlit run app.py
```

---

## Credenciais necessárias

| Serviço | Como obter |
|---------|-----------|
| **Gemini API Key** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| **Google Earth Engine** | [earthengine.google.com](https://earthengine.google.com/) |

---

## Análises disponíveis

### Vegetação
- NDVI, SAVI, EVI

### Recursos Hídricos
- NDWI, MNDWI, Índice de Turbidez

### Temperatura
- LST (Land Surface Temperature)

### Áreas Urbanas
- NDBI, Ilhas de Calor Urbanas

### Solo
- BSI (Bare Soil Index)

### Queimadas
- NBR, dNBR

### Mudanças Temporais
- Detecção de mudanças, Desmatamento, Expansão Urbana

### Classificação
- Uso e cobertura da terra, Supervisionada, Não supervisionada

### Análise Personalizada
- Descreva qualquer análise em linguagem natural — o Gemini gera o código automaticamente.

---

## Satélites suportados

| Satélite | Coleção GEE | Resolução |
|----------|-------------|-----------|
| Sentinel-2 | COPERNICUS/S2_SR_HARMONIZED | 10m |
| Landsat 9 | LANDSAT/LC09/C02/T1_L2 | 30m |
| Landsat 8 | LANDSAT/LC08/C02/T1_L2 | 30m |
| Landsat 7 | LANDSAT/LE07/C02/T1_L2 | 30m |
| Landsat 5 | LANDSAT/LT05/C02/T1_L2 | 30m |
| MODIS Terra | MODIS/061/MOD13A2 | 500m |

---

## Tecnologias

- **Frontend:** Streamlit
- **Mapas:** Leafmap, Folium
- **IA:** Google Gemini 1.5 Pro
- **Geoprocessamento:** Google Earth Engine, geemap
- **Dados:** GeoPandas, Shapely, NumPy, Pandas
