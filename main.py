from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from tabela_simbolos import TabelaSimbolos

def main():
    # Caminho do arquivo de código-fonte
    caminho_arquivo = "codigo.txt"

    # Inicializa o analisador léxico
    analisador_lexico = AnalisadorLexico(caminho_arquivo)

    # Realiza a análise léxica e obtém os tokens
    tokens = analisador_lexico.analisar()

    # Exibe os tokens encontrados
    print("Tokens:")
    for token in tokens:
        print(f"{token[0]:<15} {token[1]:<15} {token[2]}")

    # Inicializa a tabela de símbolos
    tabela_simbolos = TabelaSimbolos()

    # Inicializa o analisador sintático
    analisador_sintatico = AnalisadorSintatico(tokens, tabela_simbolos)

    # Realiza a análise sintática
    analisador_sintatico.analisar()

    # Exibe a tabela de símbolos
    tabela_simbolos.exibir()

if __name__ == "__main__":
    main()
