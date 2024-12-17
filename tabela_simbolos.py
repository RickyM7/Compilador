class TabelaSimbolos:
    def __init__(self):  # Construtor da classe
        self.simbolos = []  # Inicializa a lista de símbolos

    def adicionar(self, identificador, tipo, valor=None):
        for simbolo in self.simbolos:
            if simbolo['identificador'] == identificador:
                simbolo['tipo'] = simbolo['tipo'] or tipo
                simbolo['valor'] = valor
                return
        self.simbolos.append({'identificador': identificador, 'tipo': tipo, 'valor': valor})

    def atualizar(self, identificador, valor):
        for simbolo in self.simbolos:
            if simbolo['identificador'] == identificador:
                simbolo['valor'] = valor
                return
        raise ValueError(f"Identificador '{identificador}' não encontrado.")
    
    def funcao_existe(self, nome):
        # Verifica se a função já foi declarada
        return any(simbolo['identificador'] == nome and simbolo['tipo'] == 'func' for simbolo in self.simbolos)

    def exibir(self):  # Exibe a tabela de símbolos de forma organizada
        print("\nTabela de Símbolos:")  # Cabeçalho
        print("Identificador    Tipo      Valor")  # Títulos das colunas
        print("--------------------------------------------------")
        for simbolo in self.simbolos:  # Itera sobre os símbolos na tabela
            # Exibe o valor do símbolo, mesmo que seja None
            valor_formatado = simbolo['valor'] if simbolo['valor'] is not None else 'None'
            print(f"{simbolo['identificador']:<15} {simbolo['tipo']:<15} {valor_formatado}")  # Exibe cada símbolo formatado
        print("==================================================")  # Linha final para organização
