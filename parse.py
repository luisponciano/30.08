#  __  __ _   _ ____ ___ ____   ____  _______     __
# |  \/  | | | / ___|_ _/ ___| |  _ \| ____\ \   / /
# | |\/| | | | \___ \| | |     | | | |  _|  \ \ / / 
# | |  | | |_| |___) | | |___  | |_| | |___  \ V /  
# |_|  |_|\___/|____/___\____| |____/|_____|  \_/   

# Linguagem: Quarteto Language (Versão Musical)
# Autor: Luis
# Versão: 1.3
# Data: 28-08-2025

def interpretador(codigo, variaveis=None):
    # quebra o codigo em linhas
    if variaveis is None:
        # um dicionario para armazenar as variaveis
        variaveis = {}

    def eval_texto(expr):
        partes = [p.strip() for p in expr.split("+")]
        out = ""
        for p in partes:
            if len(p) >= 2 and p[0] == '"':
                out += p[1:-1] # trecho entre as aspas
            else:
                out += str(variaveis.get(p, p)) # variavel (literal se nao existir)
        return out
    
    linhas = codigo.split('\n')
    for linha in linhas:
        linha = linha.strip() # remove espaços desnecessarios
        if not linha: # ignora linhas vazias
            continue

        # se for uma linha de COMPOR (antigo definir)
        if linha.startswith("compor"):
            resto = linha[6:].strip()
            if ' como ' not in resto:
                print(f"Erro de sintaxe: {linha}")
                continue
            nome, valor = resto.split(" como ", 1) 
            nome = nome.strip()
            valor = valor.strip()
            if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
                valor = valor[1:-1]
            variaveis[nome] = valor
        
        # se for uma linha de APRESENTAR (antigo mostrar)
        elif linha.startswith("apresentar"):
            conteudo = linha[10:].strip()
            print(eval_texto(conteudo))

        # se for uma estrutura condicional HARMONIA (antigo se)
        elif linha.startswith("harmonia"):
            resto = linha[8:].strip()
            if " resulta em " not in resto:
                print(f"Erro de sintaxe: {linha}")
                continue
            condicao, comando = resto.split(" resulta em ", 1)
            # aqui podemos apenas checar se a condição é verdadeira ou falsa
            if condicao.strip() == "verdadeiro":
                interpretador(comando.strip(), variaveis) # executa o comando dentro da condição

        # se for um laço REPETIR (antigo enquanto)
        elif linha.startswith("repetir"):
            if " compasso " not in linha:
                print(f"Erro de sintaxe: {linha}")
                continue
            
            condicao = linha[7:].split(" compasso ")[0].strip()
            comando = linha.split(" compasso ")[1].strip()

            # verifica a condição do looping (por enquanto, consideramos verdadeiro ou falso)
            while condicao == 'verdadeiro':
                interpretador(comando, variaveis) # executa o comando dentro do loop
                break # evita loops infinitos para esse exemplo
        else:
            print(f'Comando não foi reconhecido: {linha}')

# Exemplo de código usando a nova sintaxe musical
partitura = """
    compor instrumento como "Bateria"
    apresentar "O instrumento principal é " + instrumento
    
    harmonia verdadeiro resulta em apresentar "A harmonia está perfeita!"
    
    repetir verdadeiro compasso apresentar "Tocando o compasso novamente."
"""

interpretador(partitura)