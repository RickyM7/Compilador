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
        self.escopo_funcao = {}  # Dicionário dinâmico para escopos de funções

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
        if tipo == "proc" or (tipo in ["int", "boo"] and parametros is not None):  # Declaração de função/procedimento
            escopo_alvo = 0  # Sempre no escopo global
            if identificador not in self.escopos[escopo_alvo]:  # Verifica se a função/procedimento já não foi declarado
                self.funcao_atual = identificador
                if identificador not in self.escopo_funcao:
                    self.escopo_funcao[identificador] = self.max_escopo + 1  # Associa novo escopo dinamicamente
        elif self.funcao_atual:  # Dentro de uma função/procedimento
            escopo_alvo = self.escopo_funcao.get(self.funcao_atual, self.escopo_atual)  # Usa o escopo da função atual
        else:  # Variáveis fora de funções (escopo atual)
            escopo_alvo = self.escopo_atual

        while len(self.escopos) <= escopo_alvo:
            self.escopos.append({})
            self.historico_escopos[len(self.escopos) - 1] = {}
        
        # Verifica se o identificador já existe no escopo alvo e ignora silenciosamente duplicatas
        if identificador in self.escopos[escopo_alvo]:
            return  # Retorna para evitar duplicação
        
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
        self.adicionar(temp, tipo, valor)  # Adiciona a temporária ao escopo atual
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