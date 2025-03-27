class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Pilha de escopos
        self.todos_escopos = []  # Histórico de escopos
        self.cte = [] # Lista para o Código de Três Endereços (CTE)
        self.temp_count = 0 # Contador para variáveis temporárias
        self.escopo_atual = 0  # Número do escopo atual
        self.historico_escopos = {0: {}}  # Mapeia escopos para seus identificadores
    
    def entrar_escopo(self):
        self.escopo_atual += 1
        self.escopos.append({})
        self.historico_escopos[self.escopo_atual] = {}
    
    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.escopo_atual -= 1
    
    def adicionar(self, identificador, tipo, valor=None): # Adiciona um símbolo ao escopo atual
        if identificador in self.escopos[-1]:
            raise ValueError(f"Variável '{identificador}' já declarada no escopo atual.")
        self.escopos[-1][identificador] = {'tipo': tipo, 'valor': valor}
        self.historico_escopos[self.escopo_atual][identificador] = {'tipo': tipo, 'valor': valor}
    
    def atualizar(self, identificador, valor): # Atualiza o valor de um símbolo no escopo mais recente onde ele existe
        for escopo in reversed(self.escopos):
            if identificador in escopo:
                escopo[identificador]['valor'] = valor
                for escopo_id, simbolos in self.historico_escopos.items():
                    if identificador in simbolos:
                        simbolos[identificador]['valor'] = valor
                return
        print(f"[Erro Semântico] Identificador '{identificador}' não declarado antes do uso.")
    
    def obter(self, identificador): # Retorna as informações de um símbolo, buscando do escopo atual ao global
        for escopo in reversed(self.escopos):
            if identificador in escopo:
                return escopo[identificador]
        if identificador in self.historico_escopos[0]:  # Buscar no escopo global
            return self.historico_escopos[0][identificador]
        return None
    
    def novo_temp(self, tipo, valor=None): # Cria uma nova variável temporária no escopo atual
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        self.adicionar(temp, tipo, valor)
        return temp
    
    def adicionar_cte(self, instrucao): # Adiciona uma instrução ao Código de Três Endereços (CTE)
        self.cte.append(instrucao)
        # Verifica se a instrução é uma atribuição e atualiza a tabela, se necessário
        if "=" in instrucao and "call" not in instrucao and "goto" not in instrucao:
            partes = instrucao.split(" = ")
            if len(partes) == 2:
                identificador, valor = partes[0].strip(), partes[1].strip()
                
                # Verifica se a variável foi declarada em qualquer escopo
                declarada = self.obter(identificador) is not None or identificador.startswith("t")
                
                if declarada:
                    self.atualizar(identificador, valor) # Atualiza o valor existente
                else:
                    print(f"[Erro Semântico] A variável '{identificador}' não foi declarada antes da atribuição.")
    
    def exibir(self): # Exibe a tabela de símbolos e o CTE gerado
        print("\nTabela de Símbolos (todos os escopos):")
        print("Escopo           Identificador    Tipo      Valor")
        print("--------------------------------------------------")
        for escopo, simbolos in self.historico_escopos.items():
            for identificador, info in simbolos.items():
                valor_formatado = info['valor'] if info['valor'] is not None else 'None'
                print(f"{escopo:<15} {identificador:<15} {info['tipo']:<10} {valor_formatado}")
        print("\nCódigo de Três Endereços (CTE):")
        for i, inst in enumerate(self.cte, 1):
            print(f"{i}: {inst}")
        print("==================================================")