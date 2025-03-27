class AnalisadorSemantico:
    def __init__(self, tokens, tabela_simbolos):
        """Inicializa o analisador semântico com tokens e tabela de símbolos."""
        self.tokens = tokens  # Lista de tokens recebida do analisador léxico
        self.tabela_simbolos = tabela_simbolos  # Referência à tabela de símbolos
        self.pos = 0  # Posição atual na lista de tokens
        self.token_atual = None  # Token sendo processado atualmente
        self.labels = 0  # Contador para rótulos no CTE
        self.avancar()  # Avança para o primeiro token

    def avancar(self):
        """Avança para o próximo token na lista."""
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]  # Atualiza o token atual
            self.pos += 1
        else:
            ultima_linha = self.token_atual[2] if self.token_atual else None
            self.token_atual = ('EOF', None, ultima_linha)  # Define EOF com a última linha

    def consumir(self, tipo):
        """Consome um token do tipo esperado, caso contrário gera um erro."""
        if self.token_atual[0] == tipo:
            self.avancar()  # Move para o próximo token
        else:
            raise SyntaxError(f"Esperado '{tipo}', encontrado '{self.token_atual[0]}' na linha {self.token_atual[2]}.")

    def novo_label(self):
        """Gera um novo rótulo único para controle de fluxo no CTE."""
        self.labels += 1
        return f"L{self.labels}"

    def analisar(self):
        """Executa a análise semântica completa do código."""
        try:
            while self.token_atual[0] != "EOF":  # Processa até o fim dos tokens
                self.declaracao()  # Analisa cada declaração ou comando
            return True
        except (SyntaxError, ValueError) as e:
            print(f"Erro: {e}")  # Exibe erro sintático ou semântico
            return False

    def declaracao(self):
        """Processa uma declaração ou comando no nível atual."""
        if self.token_atual[0] == "RESERVADA":
            if self.token_atual[1] in ["int", "boo"]:
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "func":
                    self.declaracao_funcao()  # Declaração de função
                else:
                    self.declaracao_variavel()  # Declaração de variável
            elif self.token_atual[1] == "proc":
                self.declaracao_procedimento()  # Declaração de procedimento
            elif self.token_atual[1] in ["se", "enquanto", "leia", "escreva", "retorne", "continue", "pare"]:
                self.comando()  # Comando estruturado
            else:
                raise SyntaxError(f"Comando não reconhecido {self.token_atual[1]} na linha {self.token_atual[2]}.")
        elif self.token_atual[0] == "IDENTIFICADOR":
            self.atribuicao_chamada()  # Atribuição ou chamada
        else:
            raise SyntaxError(f"Token não reconhecido {self.token_atual[0]} na linha {self.token_atual[2]}.")

    def declaracao_variavel(self):
        """Processa a declaração de uma variável com ou sem atribuição."""
        tipo = self.token_atual[1]  # Tipo da variável (int ou boo)
        self.consumir("RESERVADA")  # Consome o tipo
        identificador = self.token_atual[1]  # Nome da variável
        self.consumir("IDENTIFICADOR")  # Consome o identificador
        valor = None
        if self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")  # Consome '='
            valor = self.expressao(tipo)  # Avalia a expressão com tipo esperado
        # Primeiro adiciona à tabela, depois registra a atribuição no CTE
        self.tabela_simbolos.adicionar(identificador, tipo, valor)  # Adiciona à tabela antes
        if valor is not None:  # Só adiciona ao CTE se houver atribuição
            self.tabela_simbolos.adicionar_cte(f"{identificador} = {valor}")  # Adiciona ao CTE depois
        self.consumir("DELIMITADOR")  # Consome ';'

    def declaracao_procedimento(self):
        """Processa a declaração de um procedimento."""
        self.consumir("RESERVADA")  # Consome 'proc'
        nome = self.token_atual[1]  # Nome do procedimento
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # Consome '('
        self.tabela_simbolos.adicionar(nome, "proc")  # Adiciona o procedimento à tabela
        self.tabela_simbolos.entrar_escopo()  # Novo escopo para o procedimento
        params = []
        if self.token_atual[1] in ("int", "boo"):
            params.append(self.parametro())  # Processa o primeiro parâmetro
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")  # Consome ','
                params.append(self.parametro())  # Processa parâmetros adicionais
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'
        self.tabela_simbolos.adicionar_cte(f"proc {nome}:")  # Adiciona definição ao CTE
        try:
            while self.token_atual[1] != "}":
                self.declaracao()  # Processa o corpo do procedimento
        finally:
            self.tabela_simbolos.sair_escopo()  # Sai do escopo
        self.consumir("DELIMITADOR")  # Consome '}'

    def declaracao_funcao(self):
        """Processa a declaração de uma função com tipo de retorno."""
        tipo_retorno = self.token_atual[1]  # Tipo de retorno (int ou boo)
        self.consumir("RESERVADA")  # Consome 'int' ou 'boo'
        self.consumir("RESERVADA")  # Consome 'func'
        nome = self.token_atual[1]  # Nome da função
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # Consome '('
        self.tabela_simbolos.adicionar(nome, tipo_retorno)  # Adiciona a função à tabela
        self.tabela_simbolos.entrar_escopo()  # Novo escopo para a função
        params = []
        if self.token_atual[1] in ("int", "boo"):
            params.append(self.parametro())  # Processa o primeiro parâmetro
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")  # Consome ','
                params.append(self.parametro())  # Processa parâmetros adicionais
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'
        self.tabela_simbolos.adicionar_cte(f"func {nome}:")  # Adiciona definição ao CTE
        try:
            while self.token_atual[1] != "}":
                if self.token_atual[0] == "RESERVADA" and self.token_atual[1] == "retorne":
                    self.consumir("RESERVADA")  # Consome 'retorne'
                    valor = self.expressao(tipo_retorno)  # Avalia o valor retornado
                    self.tabela_simbolos.adicionar_cte(f"return {valor}")  # Adiciona retorno ao CTE
                    self.consumir("DELIMITADOR")  # Consome ';'
                else:
                    self.declaracao()  # Processa outras declarações
        finally:
            self.tabela_simbolos.sair_escopo()  # Sai do escopo
        self.consumir("DELIMITADOR")  # Consome '}'

    def parametro(self):
        """Processa um parâmetro de função ou procedimento."""
        tipo = self.token_atual[1]  # Tipo do parâmetro
        self.consumir("RESERVADA")  # Consome 'int' ou 'boo'
        identificador = self.token_atual[1]  # Nome do parâmetro
        self.consumir("IDENTIFICADOR")  # Consome o identificador
        self.tabela_simbolos.adicionar(identificador, tipo)  # Adiciona à tabela
        return (tipo, identificador)

    def atribuicao_chamada(self):
        """Processa uma atribuição ou chamada de função/procedimento."""
        identificador = self.token_atual[1]  # Nome do identificador
        simbolo = self.tabela_simbolos.obter(identificador)  # Verifica se existe
        self.consumir("IDENTIFICADOR")
        if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            resultado = self.chamada(identificador)  # Processa a chamada
            if simbolo['tipo'] != "proc" and resultado is not None:
                self.tabela_simbolos.atualizar(identificador, resultado)  # Atualiza com o resultado
            self.consumir("DELIMITADOR")  # Consome ';'
        elif self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")  # Consome '='
            valor = self.expressao(simbolo['tipo'])  # Avalia a expressão com tipo esperado
            self.tabela_simbolos.adicionar_cte(f"{identificador} = {valor}")  # Adiciona ao CTE
            self.tabela_simbolos.atualizar(identificador, valor)  # Atualiza a tabela
            self.consumir("DELIMITADOR")  # Consome ';'

    def chamada(self, nome):
        """Processa a chamada de uma função ou procedimento."""
        self.consumir("DELIMITADOR")  # Consome '('
        args = []
        if self.token_atual[1] != ")":
            args.append(self.expressao())  # Processa o primeiro argumento
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")  # Consome ','
                args.append(self.expressao())  # Processa argumentos adicionais
        self.consumir("DELIMITADOR")  # Consome ')'
        simbolo = self.tabela_simbolos.obter(nome)  # Obtém informações do símbolo
        temp = self.tabela_simbolos.novo_temp(simbolo['tipo']) if simbolo['tipo'] != "proc" else None
        args_str = ", ".join(str(arg) for arg in args)  # Formata os argumentos
        # Adiciona a chamada ao CTE
        self.tabela_simbolos.adicionar_cte(f"{temp} = call {nome}({args_str})" if temp else f"call {nome}({args_str})")
        return temp

    def comando(self):
        """Processa comandos estruturados como 'se', 'enquanto', etc."""
        if self.token_atual[1] == "se":
            self.tratar_condicional()  # Processa 'se/senao'
        elif self.token_atual[1] == "enquanto":
            self.tratar_laco()  # Processa 'enquanto'
        elif self.token_atual[1] == "retorne":
            self.consumir("RESERVADA")  # Consome 'retorne'
            valor = self.expressao()  # Avalia o valor retornado
            self.tabela_simbolos.adicionar_cte(f"return {valor}")  # Adiciona ao CTE
            self.consumir("DELIMITADOR")  # Consome ';'
        elif self.token_atual[1] in ["continue", "pare"]:
            self.tabela_simbolos.adicionar_cte(self.token_atual[1])  # Adiciona ao CTE
            self.consumir("RESERVADA")  # Consome 'continue' ou 'pare'
            self.consumir("DELIMITADOR")  # Consome ';'
        elif self.token_atual[1] in ["leia", "escreva"]:
            self.comandos_simples()  # Processa 'leia' ou 'escreva'

    def tratar_condicional(self):
        """Processa uma estrutura condicional 'se/senao'."""
        self.consumir("RESERVADA")  # Consome 'se'
        self.consumir("DELIMITADOR")  # Consome '('
        self.tabela_simbolos.entrar_escopo()  # Novo escopo para o bloco 'se'
        condicao = self.expressao("boo")  # Avalia a condição (espera booleano)
        self.consumir("DELIMITADOR")  # Consome ')'
        label_else = self.novo_label()  # Rótulo para o 'senao'
        label_end = self.novo_label()  # Rótulo para o fim do bloco
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == FALSO goto {label_else}")  # Adiciona ao CTE
        self.consumir("DELIMITADOR")  # Consome '{'
        while self.token_atual[1] != "}":
            self.declaracao()  # Processa o corpo do 'se'
        self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.adicionar_cte(f"goto {label_end}")  # Salta para o fim
        self.tabela_simbolos.adicionar_cte(f"{label_else}:")  # Marca o início do 'senao'
        if self.token_atual[1] == "senao":
            self.consumir("RESERVADA")  # Consome 'senao'
            self.consumir("DELIMITADOR")  # Consome '{'
            while self.token_atual[1] != "}":
                self.declaracao()  # Processa o corpo do 'senao'
            self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.adicionar_cte(f"{label_end}:")  # Marca o fim do bloco
        self.tabela_simbolos.sair_escopo()  # Sai do escopo

    def tratar_laco(self):
        """Processa um laço 'enquanto'."""
        self.consumir("RESERVADA")  # Consome 'enquanto'
        label_start = self.novo_label()  # Rótulo para o início do laço
        label_end = self.novo_label()  # Rótulo para o fim do laço
        self.tabela_simbolos.adicionar_cte(f"{label_start}:")  # Marca o início no CTE
        self.consumir("DELIMITADOR")  # Consome '('
        self.tabela_simbolos.entrar_escopo()  # Novo escopo para o laço
        condicao = self.expressao("boo")  # Avalia a condição (espera booleano)
        self.consumir("DELIMITADOR")  # Consome ')'
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == FALSO goto {label_end}")  # Adiciona ao CTE
        self.consumir("DELIMITADOR")  # Consome '{'
        while self.token_atual[1] != "}":
            self.declaracao()  # Processa o corpo do laço
        self.tabela_simbolos.adicionar_cte(f"goto {label_start}")  # Volta ao início
        self.tabela_simbolos.adicionar_cte(f"{label_end}:")  # Marca o fim
        self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.sair_escopo()  # Sai do escopo

    def comandos_simples(self):
        """Processa comandos simples como 'leia' e 'escreva'."""
        comando = self.token_atual[1]  # Nome do comando
        self.consumir("RESERVADA")  # Consome 'leia' ou 'escreva'
        self.consumir("DELIMITADOR")  # Consome '('
        identificador = self.token_atual[1]  # Nome do identificador
        self.tabela_simbolos.obter(identificador)  # Verifica se existe
        self.consumir("IDENTIFICADOR")  # Consome o identificador
        self.consumir("DELIMITADOR")  # Consome ')'
        self.tabela_simbolos.adicionar_cte(f"{comando} {identificador}")  # Adiciona ao CTE
        self.consumir("DELIMITADOR")  # Consome ';'

    def expressao(self, tipo_esperado=None):
        """Avalia uma expressão e verifica o tipo esperado."""
        valor = self.expressao_simples()  # Avalia a parte simples
        while self.token_atual[0] == 'RELACIONAIS':
            op = self.token_atual[1]  # Operador relacional
            self.consumir('RELACIONAIS')
            valor_dir = self.expressao_simples()  # Próximo operando
            temp = self.tabela_simbolos.novo_temp("boo")  # Cria temporária para o resultado
            self.tabela_simbolos.adicionar_cte(f"{temp} = {valor} {op} {valor_dir}")  # Adiciona ao CTE
            valor = temp
        
        # Verifica compatibilidade de tipos, se especificado
        if tipo_esperado:
            if valor in ["VERDADEIRO", "FALSO"]:
                if tipo_esperado != "boo":
                    raise ValueError(f"Tipo '{tipo_esperado}' esperado, mas encontrado 'boo' na linha {self.token_atual[2]}.")
            elif valor.isdigit():
                if tipo_esperado != "int":
                    raise ValueError(f"Tipo '{tipo_esperado}' esperado, mas encontrado 'int' na linha {self.token_atual[2]}.")
            elif valor.isidentifier():
                simbolo = self.tabela_simbolos.obter(valor)
                if simbolo['tipo'] != tipo_esperado:
                    raise ValueError(f"Tipo '{tipo_esperado}' esperado, mas encontrado '{simbolo['tipo']}' na linha {self.token_atual[2]}.")
            elif tipo_esperado == "boo" and not valor.startswith("t"):
                raise ValueError(f"Tipo booleano esperado na linha {self.token_atual[2]}.")
            elif tipo_esperado == "int" and not valor.startswith("t"):
                raise ValueError(f"Tipo inteiro esperado na linha {self.token_atual[2]}.")
        return valor

    def expressao_simples(self):
        """Avalia uma expressão simples com operadores aritméticos ou lógicos."""
        if self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('+', '-'):
            sinal = self.token_atual[1]  # Sinal unário
            self.consumir('ARITMETICOS')  # Consome '+' ou '-'
            valor = self.termo()  # Avalia o termo
            if sinal == '-':
                temp = self.tabela_simbolos.novo_temp("int")  # Cria temporária para negação
                self.tabela_simbolos.adicionar_cte(f"{temp} = -{valor}")  # Adiciona ao CTE
                valor = temp
        else:
            valor = self.termo()  # Avalia o termo sem sinal
        while (self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('+', '-')) or \
              (self.token_atual[0] == 'LOGICOS' and self.token_atual[1] == 'ou'):
            op = self.token_atual[1]  # Operador (+, -, ou)
            self.consumir(self.token_atual[0])  # Consome o operador
            valor_dir = self.termo()  # Próximo operando
            temp = self.tabela_simbolos.novo_temp("int" if op in ('+', '-') else "boo")  # Cria temporária
            self.tabela_simbolos.adicionar_cte(f"{temp} = {valor} {op} {valor_dir}")  # Adiciona ao CTE
            valor = temp
        return valor

    def termo(self):
        """Avalia um termo com multiplicação, divisão ou 'e' lógico."""
        valor = self.fator()  # Avalia o fator inicial
        while (self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('*', '/')) or \
              (self.token_atual[0] == 'LOGICOS' and self.token_atual[1] == 'e'):
            op = self.token_atual[1]  # Operador (*, /, e)
            self.consumir(self.token_atual[0])  # Consome o operador
            valor_dir = self.fator()  # Próximo operando
            temp = self.tabela_simbolos.novo_temp("int" if op in ('*', '/') else "boo")  # Cria temporária
            self.tabela_simbolos.adicionar_cte(f"{temp} = {valor} {op} {valor_dir}")  # Adiciona ao CTE
            valor = temp
        return valor

    def fator(self):
        """Avalia um fator básico (identificador, literal, ou expressão entre parênteses)."""
        if self.token_atual[0] == 'IDENTIFICADOR':
            identificador = self.token_atual[1]  # Nome do identificador
            self.tabela_simbolos.obter(identificador)  # Verifica se existe
            self.consumir('IDENTIFICADOR')
            if self.token_atual[0] == 'DELIMITADOR' and self.token_atual[1] == '(':
                return self.chamada(identificador)  # Processa chamada de função
            return identificador
        elif self.token_atual[0] == 'BOOLEANO':
            valor = self.token_atual[1]  # Valor booleano
            self.consumir('BOOLEANO')
            return valor
        elif self.token_atual[0] == 'INTEIRO':
            valor = self.token_atual[1]  # Valor inteiro
            self.consumir('INTEIRO')
            return valor
        elif self.token_atual[0] == 'DELIMITADOR' and self.token_atual[1] == '(':
            self.consumir('DELIMITADOR')  # Consome '('
            valor = self.expressao()  # Avalia expressão entre parênteses
            self.consumir('DELIMITADOR')  # Consome ')'
            return valor
        else:
            raise SyntaxError(f"Fator inválido {self.token_atual[1]} na linha {self.token_atual[2]}.")