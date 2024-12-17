from analisador_lexico import AnalisadorLexico  # Importa a classe para análise léxica
from analisador_sintatico import AnalisadorSintatico  # Importa a classe para análise sintática
from tabela_simbolos import TabelaSimbolos  # Importa a classe para manipulação da tabela de símbolos

def main():  # Função principal do programa
    # Caminho do arquivo de código-fonte
    caminho_arquivo = "Compilador/codigo_geral.txt"  # Define o caminho do arquivo com o código fonte a ser analisado

    # Inicializa o analisador léxico
    analisador_lexico = AnalisadorLexico(caminho_arquivo)  # Cria uma instância do analisador léxico

    # Realiza a análise léxica e obtém os tokens
    tokens = analisador_lexico.analisar()  # Executa a análise léxica para gerar os tokens

    # Exibe os tokens encontrados
    print("Tokens:")  # Imprime o cabeçalho para a lista de tokens
    for token in tokens:  # Itera sobre a lista de tokens
        print(f"{token[0]:<15} {token[1]:<15} {token[2]}")  # Exibe o tipo, valor e linha do token

    # Inicializa a tabela de símbolos
    tabela_simbolos = TabelaSimbolos()  # Cria uma instância da tabela de símbolos

    # Inicializa o analisador sintático
    analisador_sintatico = AnalisadorSintatico(tokens, tabela_simbolos)  # Cria uma instância do analisador sintático

    # Realiza a análise sintática
    analisador_sintatico.analisar()  # Executa a análise sintática

    # Exibe a tabela de símbolos
    tabela_simbolos.exibir()  # Imprime a tabela de símbolos de forma formatada

if __name__ == "__main__":  # Verifica se o script está sendo executado diretamente
    main()  # Executa a função principal
