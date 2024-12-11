class TabelaSimbolos:  # Classe para manipulação da tabela de símbolos
    def __init__(self):  # Construtor da classe
        self.simbolos = []  # Inicializa a lista de símbolos

    def adicionar(self, identificador, tipo, valor=None):  # Adiciona um novo símbolo na tabela
        simbolo = {'identificador': identificador, 'tipo': tipo, 'valor': valor}  # Cria um dicionário para o símbolo
        self.simbolos.append(simbolo)  # Adiciona o símbolo à lista

    def exibir(self):  # Exibe a tabela de símbolos de forma organizada
        print("\nTabela de Símbolos:")  # Cabeçalho
        print("Identificador    Tipo      Valor")  # Títulos das colunas
        print("--------------------------------------------------")
        for simbolo in self.simbolos:  # Itera sobre os símbolos na tabela
            print(f"{simbolo['identificador']:<15} {simbolo['tipo']:<15} {simbolo['valor']}")  # Exibe cada símbolo formatado
        print("==================================================")  # Linha final para organização
