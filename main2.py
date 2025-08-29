from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
#pip install scikit-learn
#Para lista todas as libs instaladas no python use pip list 

app = Flask(__name__)
caminhoBd = config.DB_PATH
rotas = config.ROTAS

def init_db():
    with sqlite3.connect(caminhoBd) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia (
                mes TEXT PRIMARY KEY,
                inadimplencia REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selic (
                mes TEXT PRIMARY KEY,
                selic_diaria REAL
            )
        ''')
        conn.commit()
vazio = 0

@app.route(rotas[0])
def index():
    return render_template_string(f'''
        <h1>Upload de dados Economicos</h1>
        <form action="{rotas[1]}" method="POST" enctype="multipart/form-data">
            <label for="campo_inadimplencia">Arquivo de Inadimplencia (CSV)</label>
            <input name="campo_inadimplencia" type="file" required>
            <label for="campo_selic">Arquivo da Taxa Selic (CSV)</label>
            <input name="campo_selic" type="file" required>
            <input type="submit" value="Fazer Upload">
        </form>
        <br><br>
        <hr>
        <a href="{rotas[2]}">Consultar dados Armazenados</a><br>
        <a href="{rotas[3]}">Visualizar Graficos</a><br>
        <a href="{rotas[4]}">Editar dados de Inadimplencia</a><br>
        <a href="{rotas[5]}">Analisar Correlação </a><br>
        <a href="{rotas[6]}">Observabilidade em 3D</a><br>
        <a href="{rotas[7]}">Editar Selic</a><br>
    ''')

@app.route(rotas[1], methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados!"})
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names = ['data','inadimplencia'],
        header = 0
    )
    selic_df = pd.read_csv(
        selic_file,
        sep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(
        inad_df['data'], 
        format = "%d/%m/%Y"
    )
    selic_df['data'] = pd.to_datetime(
          selic_df['data'], 
          format="%d/%m/%Y"
        )
    
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(caminhoBd) as conn:
        inad_df.to_sql(
            'inadimplencia',
            conn,
            if_exists = 'replace',
            index = False
        )
        selic_df.to_sql(
            'selic',
            conn,
            if_exists = 'replace',
            index = False
        )
    return jsonify({"Mensagem":"Dados cadastrados com sucesso!"})

@app.route(rotas[2], methods=['GET','POST'])
def consultar():
#alquimistas digitais
    if request.method == "POST":
        tabela = request.form.get("campo_tabela")
        if tabela not in ["inadimplencia","selic"]:
            return jsonify({"Erro":"Tabela Invalida"}),400
        with sqlite3.connect(caminhoBd) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}",conn)
        return df.to_html(index=False)
    
    return render_template_string(f'''
        <h1> Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplencia </option>
                <option value="selic"> Taxa Selic </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br><a href="{rotas[0]}"> Voltar </a>
    ''')

@app.route(rotas[3])
def graficos():
    with sqlite3.connect(caminhoBd) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
    
    ####### Aqui criei um grafico para inadimplencia
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
            x = inad_df['mes'],
            y = inad_df['inadimplencia'],
            mode = 'lines+markers',
            name = 'Inadimplencia'
        )
    )
    # 'ggplot2', 'seaborn', 'simple_white', 'plotly','plotly_white', 'plotly_dark', 'presentation', 'xgridoff','ygridoff', 'gridon', 'none'
    fig1.update_layout(
        title = 'Evolução da Inadimplencia',
        xaxis_title = 'Mês',
        yaxis_title = '%',
        template = 'plotly_dark'
    )

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
            x = selic_df['mes'],
            y = selic_df['selic_diaria'],
            mode = 'lines+markers',
            name = 'selic'
        )
    )
    fig2.update_layout(
        title = "Media mensal da Selic",
        xaxis_title = "Mês",
        yaxis_title = "Taxa",
        template = "plotly_dark"
    )

    graph_html_1 = fig1.to_html(
        full_html = False,
        include_plotlyjs = "cdn"        
        )
    graph_html_2 = fig2.to_html(
        full_html = False,
        include_plotlyjs = False        
        )
    return render_template_string('''
        <html>
            <head>
                <title> Graficos Economicos </title>
                <style>
                    .container{
                        display:flex;
                        justify-content:space-around;
                    }
                    .graph{
                          width: 48%;        
                    }
                </style>
            </head>
            <body>
                <h1>
                    <marquee> Graficos Economicos </marquee>
                </h1>
                <div class="container">
                    <div class="graph">{{ reserva01|safe }}</div>
                    <div class="graph">{{ reserva02|safe }}</div>
                </div>
            </body>
        </html>
    ''', reserva01 = graph_html_1, reserva02 = graph_html_2)

@app.route(rotas[4], methods=['POST','GET'])
def editar_inadimplencia():
    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({"Erro":"Valor Invalido"})
        with sqlite3.connect(caminhoBd) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inadimplencia 
                SET inadimplencia = ? 
                WHERE mes = ?
            ''', (novo_valor, mes))
            conn.commit()
        return jsonify({"Mensagem":f"Valor atualozado para o mês {mes}"})

    return render_template_string(f'''
        <h1> Editar Inadimplencia </h1>
        <form method="POST" action="{rotas[4]}">
            <label for="campo_mes"> Mês (AAAA-MM)</label>
            <input type="text" name="campo_mes"><br>
                                  
            <label for="campo_valor"> Novo valor de Inadimplencia </label>
            <input type="text" name="campo_valor"><br>
                                  
            <input type="submit" value="Atualizar Dados">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>                         
    ''')

@app.route(rotas[7], methods=['POST','GET'])
def editar_selic():
    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        if not mes or not novo_valor:
            return jsonify({"Erro":"Informe a data e valor"}), 400
        try:
            novo_valor = float(novo_valor.replace(',','.'))
        except ValueError:
            return jsonify({"Erro":"Valor Invalido"})
        
        with sqlite3.connect(caminhoBd) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE selic SET selic_diaria = ? WHERE mes = ?
            ''',(novo_valor, mes))
            conn.commit()
        return jsonify({"Mensagem":f"Valor da selic para {mes} atualizado para {novo_valor}"})


    return render_template_string('''
        <h1> Editar Taxa Selic </h1>
        <form method="POST" action="{rotas[7]}">
            <label for="campo_mes"> Mês (AAAA-MM)</label>
            <input type="text" name="campo_mes" placeholder="2025-01"><br>
                                  
            <label for="campo_valor"> Novo valor da Taxa Selic </label>
            <input type="text" name="campo_valor" placeholder="12.5"><br>

            <input type="submit" value="Atualizar Dados">
        </form>
        <br>
        <a href="{rotas[0]}">Voltar</a>   
    ''')

@app.route(rotas[5])
def analisar_correlacao():
    with sqlite3.connect(caminhoBd) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
    
        # realiza uma junção entre dois dataframes usando a coluna de mes como chave junção
    merged = pd.merge(inad_df, selic_df, on='mes')
    #calcula p coeficiente da correlação de person entre as duas variaveis(inadimplencia e selic)
    correl = merged['inadimplencia'].corr(merged['selic_diaria'])
    # registra as variaveis para a regressao linear onde x é a variavel independente (no caso a selic)
    x = merged['selic_diaria']
    # y é a variável dependente
    y = merged['inadimplencia']
    # calcula o coeficiente da reta de regressão linear onde 'm' é a inclinação e 'b' é o intercepto
    m, b = np.polyfit(x, y, 1)

    # a partir daqui vamos gerar o gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = x,
        y = y,
        mode = 'markers',
        name = 'Dados'
        marker=dict(
            color = 'rgba(152, 0, 0, .8)',
            size = 12, 
            line = dict(width = 2, color = 'white'),
            symbol = 'circle'),
        hovertemplate = 'Selic: %{x:.2f}%<br>Inadimplencia: %{y:.2f}%<extra></extra>'
    ) 
    )

    # adicionar a linha de tendencia da regressão linear
    fig.add_trace(go.Scatter(
        x = x, # mesmo eixo dos dados
        y = m * x + b, # a equeção da linha de tendencia
        mode = 'lines',
        name = 'Linha de Tendência',
        line = dict(color = 'rgba(0, 0, 152, .8)', width = 2, dash = 'dash')


    )
    )

if __name__ == '__main__':
    init_db()
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )