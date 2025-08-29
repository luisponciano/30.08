# Importa as classes e funções necessárias das bibliotecas.
from flask import Flask, request, jsonify, render_template_string # Flask para o servidor web, request para acessar dados das requisições, jsonify para criar respostas JSON, render_template_string para renderizar HTML a partir de uma string.
import pandas as pd # Pandas para manipulação e análise de dados, especialmente com DataFrames.
import sqlite3 # SQLite3 para interagir com o banco de dados SQLite.
import os # Módulo do sistema operacional, não utilizado diretamente neste trecho.
import plotly.graph_objs as go # Plotly para criar gráficos interativos.
from dash import Dash, html, dcc # Dash para criar dashboards web.
import dash # Importa a biblioteca Dash novamente (redundante).
import numpy as np # NumPy para operações numéricas, especialmente com arrays.
import config # Importa um arquivo de configuração local (config.py) para variáveis como o caminho do banco de dados.
from sklearn.cluster import KMeans # KMeans do scikit-learn para algoritmos de clusterização.
from sklearn.preprocessing import StandardScaler # StandardScaler do scikit-learn para padronizar os dados.
#pip install scikit-learn # Comentário indicando como instalar a biblioteca scikit-learn.
#Para lista todas as libs instaladas no python use pip list # Comentário indicando como listar as bibliotecas instaladas.

# Cria uma instância da aplicação Flask.
app = Flask(__name__)
# Define o caminho para o arquivo do banco de dados SQLite, buscando a informação do arquivo de configuração.
caminhoBd = config.DB_PATH

# Função para inicializar o banco de dados.
def init_db():
    # Conecta-se ao banco de dados especificado em 'caminhoBd'. O 'with' garante que a conexão será fechada automaticamente.
    with sqlite3.connect(caminhoBd) as conn:
        # Cria um objeto cursor para executar comandos SQL.
        cursor = conn.cursor()
        # Executa um comando SQL para criar a tabela 'inadimplencia' se ela ainda não existir.
        # A tabela terá duas colunas: 'mes' (chave primária) e 'inadimplencia'.
        cursor.execute('''
              CREATE TABLE IF NOT EXISTS inadimplencia (
                  mes TEXT PRIMARY KEY,
                  inadimplencia REAL
              )           
        ''')
        # Executa um comando SQL para criar a tabela 'selic' se ela ainda não existir.
        # A tabela terá duas colunas: 'mes' (chave primária) e 'selic_diaria'.
        cursor.execute('''
              CREATE TABLE IF NOT EXISTS selic (
                  mes TEXT PRIMARY KEY,
                  selic_diaria REAL
                   )
        ''')
        # Confirma (commita) as transações no banco de dados, salvando as tabelas criadas.
        conn.commit()
# Declara uma variável 'vazio', mas não a utiliza no restante do código.
vazio = 0

# Define a rota para a página inicial da aplicação ('/').
@app.route('/')
def index():
    # Retorna uma string HTML que será renderizada no navegador.
    # Este HTML contém um formulário para upload de arquivos e links para outras páginas da aplicação.
    return render_template_string('''
        <h1>Upload de dados Economicos</h1>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <label for="campo_inadimplencia">Arquivo de inadimplencia (CSV)</label>
            <input name="campo_inadimplencia" type="file"required>
            <label for="campo_selic">Arquivo da taxa selic (CSV)</label>
            <input name="campo_selic" type="file" required>
            <input type="submit" value="Fazer Upload">
        </form>
        <br><br>
        <hr>
        <a href="/consultar">Consultar dados Armazenados</a><br>
        <a href="/graficos">Visualizar Graficos</a><br>
        <a href="/editar_inadimplencia"> Editar dados dos inadimplencia</a><br>
        <a href="/correlacao">Analisar correlação </a><br>
        <a href="/grafico3d">Observabilidade em 3d</a><br>
    ''')

# Define a rota '/upload', que aceita métodos POST (para receber dados) e GET.
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # Obtém os arquivos enviados no formulário com os nomes 'campo_inadimplencia' e 'campo_selic'.
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    # Verifica se algum dos arquivos não foi enviado.
    if not inad_file or not selic_file:
        # Se um arquivo estiver faltando, retorna uma mensagem de erro em formato JSON.
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados!"})
    
    # Lê o arquivo CSV de inadimplência usando o pandas.
    inad_df = pd.read_csv(
        inad_file, # O arquivo enviado.
        sep = ';', # Define o ponto e vírgula como separador de colunas.
        names = ['data','inadimplencia'], # Define os nomes das colunas.
        header = 0 # Indica que a primeira linha do CSV é o cabeçalho.
    )
    # Lê o arquivo CSV da taxa Selic usando o pandas.
    selic_df = pd.read_csv(
        selic_file, # O arquivo enviado.
        sep = ';', # Define o ponto e vírgula como separador de colunas.
        names = ['data','selic_diaria'], # Define os nomes das colunas.
        header = 0 # Indica que a primeira linha do CSV é o cabeçalho.
    )

    # Converte a coluna 'data' do DataFrame de inadimplência para o formato de data.
    inad_df['data'] = pd.to_datetime(
        inad_df['data'],
        format = "%d/%m/%Y" # Especifica o formato da data de entrada (dia/mês/ano).
    )
    # Converte a coluna 'data' do DataFrame da Selic para o formato de data.
    selic_df['data'] = pd.to_datetime(
        selic_df['data'],
        format = "%d/%m/%Y" # Especifica o formato da data de entrada.
        )
    
    # Cria uma nova coluna 'mes' no DataFrame de inadimplência, contendo o ano e o mês extraídos da data.
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    # Cria uma nova coluna 'mes' no DataFrame da Selic.
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    # Remove linhas duplicadas baseadas no mês para o DataFrame de inadimplência (não é a forma mais robusta de agregar).
    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    # Agrupa os dados da Selic por mês e calcula a média da 'selic_diaria' para cada mês.
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    # Conecta-se ao banco de dados SQLite.
    with sqlite3.connect(caminhoBd) as conn:
        # Salva o DataFrame de inadimplência na tabela 'inadimplencia' do banco de dados.
        inad_df.to_sql(
            'inadimplencia', # Nome da tabela.
            conn, # Conexão com o banco.
            if_exists = 'replace', # Se a tabela já existir, ela será substituída.
            index = False # Não salva o índice do DataFrame como uma coluna na tabela.
        )
        # Salva o DataFrame da Selic na tabela 'selic'.
        selic_df.to_sql(
            'selic', # Nome da tabela.
            conn, # Conexão com o banco.
            if_exists = 'replace', # Substitui a tabela se ela existir.
            index = False # Não salva o índice do DataFrame.
        )
        # Retorna uma mensagem de sucesso em formato JSON.
        return jsonify({"Mensagem":"Dados cadastrados com sucesso!"})
    
# Define a rota '/consultar', que aceita métodos GET e POST.
@app.route('/consultar', methods=['GET','POST'])
def consultar():

    # Verifica se o método da requisição é POST (ou seja, se o formulário foi enviado).
    if request.method == "POST":
        # Obtém o nome da tabela selecionada no formulário.
        tabela = request.form.get('campo_tabela')
        # Verifica se o nome da tabela é válido.
        if tabela not in ["inadimplencia","selic"]:
            # Se for inválido, retorna uma mensagem de erro.
            return jsonify({"Erro":"Tabela Invalida"}), 400
        # Conecta-se ao banco de dados.
        with sqlite3.connect(caminhoBd) as conn:
            # Executa uma consulta SQL para selecionar todos os dados da tabela escolhida e os carrega em um DataFrame.
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        # Converte o DataFrame para uma tabela HTML e a retorna para ser exibida no navegador.
        return df.to_html(index=False)

    # Se o método for GET (primeiro acesso à página), exibe o formulário de consulta.
    return render_template_string('''
        <h1> Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplencia </option>
                <option value="selic"> Taxa Selic </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br><a href="/"> Voltar </a>
    ''')

# Bloco de execução principal: só roda se o script for executado diretamente.
if __name__ == '__main__':
    # Chama a função para garantir que o banco de dados e as tabelas existam.
    init_db()
    # Inicia o servidor de desenvolvimento do Flask.
    app.run(
        debug = config.FLASK_DEBUG, # Ativa ou desativa o modo de depuração com base no arquivo de configuração.
        host = config.FLASK_HOST, # Define o host em que o servidor irá rodar.
        port = config.FLASK_PORT # Define a porta do servidor.
    )
