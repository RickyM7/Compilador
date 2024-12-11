class TabelaSimbolos:
    def __init__(self):
        self.simbolos = []

    def adicionar(self, identificador, tipo, valor=None):
        # Adiciona um novo símbolo na tabela
        simbolo = {'identificador': identificador, 'tipo': tipo, 'valor': valor}
        self.simbolos.append(simbolo)

    def exibir(self):
        # Exibe a tabela de símbolos de forma organizada
        print("\nTabela de Símbolos:")
        print("Identificador    Tipo      Valor")
        print("--------------------------------------------------")
        for simbolo in self.simbolos:
            print(f"{simbolo['identificador']:<15} {simbolo['tipo']:<15} {simbolo['valor']}")
        print("==================================================")
