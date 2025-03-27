from analisador_lexico import AnalisadorLexico
from analisador_semantico import AnalisadorSemantico
from tabela_simbolos import TabelaSimbolos

def main():
    caminho_arquivo = "codigo_geral.txt"  # Código-fonte
    
    # Análise Léxica
    try:
        analisador_lexico = AnalisadorLexico(caminho_arquivo)  # Inicializa o analisador léxico
        tokens = analisador_lexico.analisar()  # Gera os tokens a partir do arquivo
        print("Tokens:")
        for token in tokens:  # Itera sobre a lista de tokens gerados
            print(f"{token[0]:<15} {token[1]:<15} {token[2]}")  # Exibe o tipo, valor e linha de cada token
        print("Análise léxica concluída com sucesso!")
    except Exception as e:
        print(f"Erro na análise léxica: {e}")
        return

    # Análise Sintática e Semântica
    try:
        tabela_simbolos = TabelaSimbolos()  # Inicializa a tabela de símbolos
        analisador_semantico = AnalisadorSemantico(tokens, tabela_simbolos)  # Inicializa o analisador semântico com os tokens
        analisador_semantico.analisar()  # Realiza a análise sintática e semântica combinada
        print("Análise sintática e semântica concluída com sucesso!")
    except Exception as e:
        print(f"Erro na análise sintática/semântica: {e}")
        return

    # Tabela de símbolos e o Código de Três Endereços (CTE)
    try:
        tabela_simbolos.exibir()
        print("Exibição da tabela de símbolos e CTE concluída com sucesso!")
    except Exception as e:
        print(f"Erro na exibição da tabela de símbolos e CTE: {e}")

if __name__ == "__main__":
    main()