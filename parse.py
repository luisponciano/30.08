#   ___                   _       _         
#  / _ \ _   _  __ _ _ __| |_ ___| |_ ___   
# | | | | | | |/ _` | '__| __/ _ \ __/ _ \  
# | |_| | |_| | (_| | |  | ||  __/ || (_) | 
#  \__\_\\__,_|\__,_|_|   \__\___|\__\___/  
#Linguagem: Quarteto Language
# Autor: Luis Henrique Ponciano
# Versão: 1.0
# Data: 28-08-25

def interpretador(codigo, variaveis=None):
    # quebra o codigo em linhas
    if variaveis is None:
        variaveis = {}
    
    def eval_texto(expr):
        partes = [p.strip() for p in expr.split('+')]
        out = ""
        for p in partes:
            if len(p) >= 2 and p[0] == '"':
                out += p[1:-1]
            else:
                out += str(variaveis.get(p, p))
        return out
    
    linhas = codigo.split('\n')
    for linha in linhas:
        linha = linha.strip() # remove espaços desnecessarios
        if not linha:
            continue


        if linha.startswith("definir"):
            resto = linha[7:].strip()
            if " como " not in resto:
                print(f'Erro de sintaxe na linha: {linha}')
                continue
            nome, valor = resto.split(" como ", 1)
            nome = nome.strip()
            valor = valor.strip()
            if len(valor) >= 2 and valor[0] == '"' and valor[1] == '"':
                valor = valor[1:-1]
                variaveis[nome] = valor


        elif linha.startswith("mostrar"):
            conteudo = linha[7:].strip()
            print(eval_texto(conteudo))

        elif linha.startswith("se"):
            resto = linha[3:].strip()
            if " então " not in resto:
                print(f'Erro de sintaxe na linha: {linha}')
                continue
            condicao, comando = resto.split(" então ", 1)
            if condicao.strip() == "verdadeiro":
                interpretador(comando.strip(), variaveis)
        elif linha.startswith("enquanto"):
            resto = linha[8:].strip()
            if " faça " not in resto:
                print(f'Erro de sintaxe na linha: {linha}')
                continue




            

            #verifica a condição do looping (por enquanto , consideramos verdadeiro ou falso)
            while condicao == 'verdadeiro':
                interpretador(comando) # executa o comando dentro do loop
                break # evita loops infinitos para esse exemplo
        else:
            print(f'Comando não foi reconhecido{linha}')
codigo = """
    definir nome como "lalala"
    mostrar "O nome é" + nome    
    se verdadeiro então mostrar "Isso é verdadeiro"
    enquanto verdadeiro faça mostrar "Dentro do laço"
"""
interpretador(codigo)


