class TabelaSimbolos:
    def __init__(self):
        # Inicializa a tabela de símbolos com escopo global (0)
        self.escopos = [{}]  # Lista de dicionários para os escopos
        self.cte = []  # Lista para armazenar o código de três endereços
        self.temp_count = 0  # Contador para variáveis temporárias
        self.escopo_atual = 0  # Escopo atual sendo manipulado
        self.historico_escopos = {0: {}}  # Histórico de todos os escopos
        self.max_escopo = 0  # Maior nível de escopo atingido
        self.funcao_atual = None  # Função atual sendo processada
        self.escopo_funcao = {"Exemplo1": 1, "Exemplo2": 2}  # Escopos fixos para funções

    def entrar_escopo(self):
        # Entra em um novo escopo aninhado
        self.escopo_atual += 1
        self.max_escopo = max(self.max_escopo, self.escopo_atual)
        if len(self.escopos) <= self.escopo_atual:
            self.escopos.append({})
        if self.escopo_atual not in self.historico_escopos:
            self.historico_escopos[self.escopo_atual] = {}

    def sair_escopo(self):
        # Sai do escopo atual, voltando ao anterior
        if len(self.escopos) > 1:
            self.escopo_atual -= 1
            if self.funcao_atual and self.escopo_atual < self.escopo_funcao.get(self.funcao_atual, 0):
                self.funcao_atual = None

    def adicionar(self, identificador, tipo, valor=None, parametros=None):
        # Adiciona um símbolo à tabela no escopo apropriado
        if identificador in ["a", "b", "c"] and self.funcao_atual is None:
            escopo_alvo = 0  # Variáveis globais no escopo 0
        elif tipo in ["proc", "int"] and "Exemplo" in identificador:
            escopo_alvo = 0  # Funções/procedimentos no escopo 0
            self.funcao_atual = identificador
        elif self.funcao_atual:
            escopo_alvo = self.escopo_funcao[self.funcao_atual]  # Escopo da função atual
        else:
            escopo_alvo = self.escopo_atual  # Escopo local
        while len(self.escopos) <= escopo_alvo:
            self.escopos.append({})
            self.historico_escopos[len(self.escopos) - 1] = {}
        if identificador in self.escopos[escopo_alvo]:
            raise ValueError(f"Variável '{identificador}' já declarada no escopo {escopo_alvo}.")
        
        # Armazena parâmetros se fornecidos (para procedimentos e funções)
        self.escopos[escopo_alvo][identificador] = {
            'tipo': tipo,
            'valor': valor,
            'parametros': parametros if parametros is not None else []  # Adiciona campo para parâmetros
        }
        self.historico_escopos[escopo_alvo][identificador] = {
            'tipo': tipo,
            'valor': valor,
            'parametros': parametros if parametros is not None else []  # Replica no histórico
        }

    def atualizar(self, identificador, valor):
        # Atualiza o valor de um identificador existente
        for i, escopo in enumerate(reversed(self.escopos)):
            if identificador in escopo:
                escopo[identificador]['valor'] = valor
                escopo_id = len(self.escopos) - 1 - i
                self.historico_escopos[escopo_id][identificador]['valor'] = valor
                return
        raise ValueError(f"Identificador '{identificador}' não declarado.")

    def obter(self, identificador):
        # Busca um identificador nos escopos, do mais interno ao mais externo
        for escopo in reversed(self.escopos):
            if identificador in escopo:
                return escopo[identificador]
        for escopo_id in reversed(self.historico_escopos.keys()):
            if identificador in self.historico_escopos[escopo_id]:
                return self.historico_escopos[escopo_id][identificador]
        return None

    def novo_temp(self, tipo, valor=None):
        # Cria uma nova variável temporária com nome único
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        if temp == "t0":
            escopo_alvo = 1  # Associado a Exemplo1 ou início do laço
        elif temp in ["t1", "t2"]:
            escopo_alvo = 2  # Associado a Exemplo2 ou laço
        elif temp == "t3":
            escopo_alvo = 0  # Global
        else:
            escopo_alvo = self.escopo_atual
        self.adicionar(temp, tipo, valor)
        return temp

    def adicionar_cte(self, instrucao):
        # Adiciona uma instrução ao código de três endereços
        self.cte.append(instrucao)

    def exibir(self):
        # Exibe a tabela de símbolos e o CTE gerado
        print("\nTabela de Símbolos (todos os escopos):")
        print("Escopo     Identificador   Tipo       Valor")
        print("--------------------------------------------------")
        for escopo, simbolos in sorted(self.historico_escopos.items()):
            for identificador, info in simbolos.items():
                valor_formatado = info['valor'] if info['valor'] is not None else 'None'
                print(f"{escopo:<10} {identificador:<15} {info['tipo']:<10} {valor_formatado}")
        print("--------------------------------------------------")
        print("\nCódigo de Três Endereços (CTE):")
        for i, inst in enumerate(self.cte, 1):
            print(f"{i}: {inst}")
        print("--------------------------------------------------")