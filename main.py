# Mapa interativo de Custos (NY x Rio) com pontos e mapa de calor
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# utilidades de padronização

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tentar detectar automaticamente as colunas latitude e longitube, custos e nome.
    Aceita varios nomes comuns como lat/latitude, custo, valor e etc
    preenche custos ausentes com a mediana (ou 1 se tudo tiver ausente)
    padroniza os nomes das colunas para minusculas, sem espacos e sem parenteses
    """
    df = df.copy()
    lat_candidates =  ['lat', 'latitude', 'lati', 'latt', 'lattitude', 'LAT', 'LATI', 'LATT', 'LATTITUDE']
    lon_candidates =  ['lon', 'long', 'longitude', 'lng', 'longi', 'LONG', 'LON', 'LONGITUDE', 'LNG', 'LONGI']
    cost_candidates = ['cost', 'custo', 'value', 'valor', 'price', 'preco', 'price_usd', 'priceusd']
    name_candidates = ['name', 'nome', 'location', 'local', 'place', 'address', 'endereco']

    def pick(colnames, candidates):
        for c in candidates:
            if c in colnames:
                return c
        for c in candidates:
            for col in colnames:
                if c.lower() in col.lower():
                    return col
        return None

        lt_col =   pick (df.columns, lat_candidates)
        lon_col =  pick (df.columns, lon_candidates)
        cost_col = pick (df.columns, cost_candidates)
        name_col = pick (df.columns, name_candidates)

        if lt_col is None or lon_col is None:
            raise ValueError("Não foi possível identificar automaticamente as colunas de latitude, longitude ou custo. Por favor, renomeie as colunas manualmente.")    
        
        out = pd.DataFrame()
        out['latitude'] = pd.to_numeric(df[lat_col], errors='coerce') 
        out['longitude'] = pd.to_numeric(df[lon_col], errors='coerce')
        out['cost'] = pd.to_numeric(df[cost_col], errors='coerce') if cost_col is not None else np.nan 
        out['name'] = df[name_col].astype(str) if name_col is not Nome else [f"Ponto{i}" for i in range(len(df))]

        out = out.dropna(subset=['latitude', 'longitude']). reset_index(drop=True)
        if out['cost'].notna.any():
            med = float(out['cost'].median())
            if not np.isfinite(med):
                med = 1.0
            out['cost'] = out['cost'].fillna(med)
        else:
            out['cost'] = 1.0   

def city_center(df: pd.DataFrame) -> dict:
    """
    define a função city_center
    - recebe como parametro um dataframe o pandas (df)
    - deve retornar um dicionario (-> dict)
    """
    return dict(
        lat = float(df['lat'].mean()),
        lon = float(df['lon'].mean()),

    )
#--------------------------Traces-----------------------------

def make_point_trace(df: pd.DataFrame, name: str) -> go.Scattermapbox:
    hover = ("<b>%{customdata[0]}</b><br>"
            "Custo: %{customdata[1]}<br"
            "Lat: %{lat:.5f}<br>LOn: %{lon:.5f}")
    
    c = df['cost'].astype(float).values
    c_min, c_max = float(np.min(c)), float(np.max(c))
    if not np.isfinite(c_min) or not np.isfinite(c_max) or abs(c_max - c_min) < 1e-9:
        size = np.full_likes(c,10.0, dtype=float)
    else:
        size = (c-c_min) / (c_max - c_min) * 20 + 6
    sizes = np.clip(size, 6, 26)

    custom = np.stack([df['name'].values, df['cost'].values], axis=1)
    return go.Scattermapbox(
        lat = df['latitude'].values,
        lon = df['longitude'].values,
        mode = 'markers',
        marker = dict(
            size = sizes,
            color = df['cost'],
            colorscale = 'Viridis',
            colorbar = dict(title = 'Custo'),
        ),
        name = f"{name} - Pontos",
        customdata = custom,
        )
       
    def make_density_trace(df: pd.DataFrame, name: str) -> go.Densitymapbox:
           return go.Densitymapbox(
                lat = df['lat'],
                lon = df['lon'],
                z = df['cost'],
                radius = 20,
                colorscale = "Inferno",
                name = f"{name} • pontos",
                showscale = True,
                colorbar = dict(title='Cost')
           )    
    
    #_______________________________________________________

def main():
        # Carregar dados
        folder = "C:/Users/noturno/Desktop/python2 luis/sistema/"
        ny = standardize_columns(pd.read_csv(f"{folder}ny.csv"))
        rj = standardize_columns(pd.read_csv(f"{folder}rj.csv"))

        ny_point = make_point_trace(ny, "New York")
        ny_heat = make_density_trace(ny, "New York")
        rj_point = make_point_trace(rj, "Rio de Janeiro")   
        rj_heat = make_density_trace(rj, "Rio de Janeiro")

        fig = go.Figure([ny_point, ny_heat, rj_point, rj_heat])

        def center_zoom(df, zoom):
            return dict(
                center = city_center(df),
                zoom = zoom,
            )   

        buttons = [
            dict(label = "NY • Pontos", method="update", args = [{"visible": [True, False, False, False]},{"mapbox":center_zoom(ny, 9)} ]),
            dict(label = "NY • Pontos", method="update", args = [{"visible": [False, True, False, False]},{"mapbox":center_zoom(ny, 10)} ]),
            dict(label = "RJ • Pontos", method="update", args = [{"visible": [False, False, True, False]},{"mapbox":center_zoom(ny, 11)} ]),
            dict(label = "RJ • Pontos", method="update", args = [{"visible": [False, False, False, True]},{"mapbox":center_zoom(ny, 12)} ])
            ]


        fig.update_layout(
            title = "Mapa Interativo de Custos - Pontos e Mapa de Calor",
            mapbox_style = "open-street-map",
            mapbox = dict(center=city_center(rj), zoom=10),
            margins = dict(l=10, r=10, t=50, b=10),
            updatemenus = [dict( 
                buttons = buttons,
                direction = "down",
                x = 0.01,
                y = 0.99,
                xanchor = "left",
                yanchor = "top",
                bgcolor = "lightgrey",
                bordercolor = "black",
      )],
        legend = dict(
            orientation = "h",
            x = 0.99,
            y = 0.01,
            xanchor = "right",
            yanchor = "bottom",
        )
            )
        
        # salva html de apresentação
        fig.write_html(f"{folder}mapa_interativo_custos.html", include_plotlyjs='cdn', full_html=True)
        print("Mapa salvo em {folder}'mapa_interativo_custos.html'")
    
        fig.show()
# inicia o servidor
if __name__ == "__main__":
    main()

   
