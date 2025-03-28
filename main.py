from analisador_lexico import AnalisadorLexico
from analisador_sintatico import AnalisadorSintatico
from analisador_semantico import AnalisadorSemantico
from gerador_cte import GeradorCTE
from tabela_simbolos import TabelaSimbolos

def main():
    # Define o caminho do arquivo de entrada
    caminho_arquivo = "codigo_geral.txt"
    
    # Executa a análise léxica
    try:
        analisador_lexico = AnalisadorLexico(caminho_arquivo)
        tokens = analisador_lexico.analisar()
        print("Tabela de Tokens:")
        print("Token           Valor           Linha")
        print("--------------------------------------------------")
        for token in tokens:
            print(f"{token[0]:<15} {token[1]:<15} {token[2]}")
        print("--------------------------------------------------")
        print("Análise léxica concluída com sucesso!")
    except Exception as e:
        print(f"Erro na análise léxica: {e}")
        return

    # Executa a análise sintática
    try:
        analisador_sintatico = AnalisadorSintatico(tokens)
        analisador_sintatico.analisar()
        print("Análise sintática concluída com sucesso!")
    except Exception as e:
        print(f"Erro na análise sintática: {e}")
        return

    # Executa a análise semântica
    try:
        tabela_simbolos = TabelaSimbolos()
        analisador_semantico = AnalisadorSemantico(tokens, tabela_simbolos)
        estruturas = analisador_semantico.analisar()
        print("Análise semântica concluída com sucesso!")
    except Exception as e:
        print(f"Erro na análise semântica: {e}")
        return

    # Gera o código de três endereços (CTE)
    try:
        gerador_cte = GeradorCTE(tabela_simbolos)
        gerador_cte.gerar(estruturas)
        print("Geração de CTE concluída com sucesso!")
        print("--------------------------------------------------")
        tabela_simbolos.exibir()
    except Exception as e:
        print(f"Erro na geração de CTE: {e}")

if __name__ == "__main__":
    main()  # Executa o programa principal