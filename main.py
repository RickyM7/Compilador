from analisador_lexico import AnalisadorLexico  
from analisador_sintatico import AnalisadorSintatico  
from tabela_simbolos import TabelaSimbolos  

def main():  

    caminho_arquivo = "Compilador/codigo_geral.txt"  

    analisador_lexico = AnalisadorLexico(caminho_arquivo) # Inicializa o analisador léxico

    tokens = analisador_lexico.analisar() # Realiza a análise léxica e obtém os tokens

    print("Tokens:")  # Imprime o cabeçalho para a lista de tokens
    for token in tokens:  # Itera sobre a lista de tokens
        print(f"{token[0]:<15} {token[1]:<15} {token[2]}")  # Exibe o tipo, valor e linha do token

    
    tabela_simbolos = TabelaSimbolos() # Inicializa a tabela de símbolos

   
    analisador_sintatico = AnalisadorSintatico(tokens, tabela_simbolos) # Inicializa o analisador sintático

   
    analisador_sintatico.analisar() # Realiza a análise sintática 

    
    tabela_simbolos.exibir() # Exibe a tabela de símbolos

if __name__ == "__main__":  
    main() 