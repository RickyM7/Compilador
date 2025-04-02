from tabela_simbolos import TabelaSimbolos

class AnalisadorSemantico:
    def __init__(self, tokens, tabela_simbolos):
        # Inicializa o analisador semântico com tokens e tabela de símbolos
        self.tokens = tokens
        self.tabela_simbolos = tabela_simbolos
        self.pos = 0
        self.token_atual = None
        self.avancar()

    def avancar(self):
        # Avança para o próximo token, ou define EOF se acabar
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
            self.pos += 1
        else:
            ultima_linha = self.token_atual[2] if self.token_atual else None
            self.token_atual = ('EOF', None, ultima_linha)

    def consumir(self, tipo):
        # Consome um token esperado, ou levanta erro
        if self.token_atual[0] == tipo:
            self.avancar()
        else:
            raise SyntaxError(f"Esperado '{tipo}', encontrado '{self.token_atual[0]}' na linha {self.token_atual[2]}.")

    def analisar(self):
        # Analisa todos os tokens e retorna uma lista de estruturas
        estruturas = []
        while self.token_atual[0] != "EOF":
            estruturas.append(self.declaracao())
        return estruturas

    def declaracao(self):
        # Identifica e processa o tipo de declaração ou comando
        if self.token_atual[0] == "RESERVADA":
            if self.token_atual[1] in ["int", "boo"]:
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "func":
                    return self.declaracao_funcao()
                else:
                    return self.declaracao_variavel()
            elif self.token_atual[1] == "proc":
                return self.declaracao_procedimento()
            elif self.token_atual[1] in ["se", "enquanto", "leia", "escreva", "retorne", "continue", "pare"]:
                return self.comando()
        elif self.token_atual[0] == "IDENTIFICADOR":
            return self.atribuicao_chamada()
        raise SyntaxError(f"Token não reconhecido {self.token_atual[0]} na linha {self.token_atual[2]}.")

    def declaracao_procedimento(self):
        # Processa a declaração de um procedimento
        self.consumir("RESERVADA")  # "proc"
        nome = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # "("
        self.tabela_simbolos.adicionar(nome, "proc", parametros=[])  # Inicializa com lista vazia
        self.tabela_simbolos.entrar_escopo()
        params = []
        if self.token_atual[1] in ("int", "boo"):
            param = self.parametro()
            params.append(param)
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                param = self.parametro()
                params.append(param)
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        corpo = []
        try:
            while self.token_atual[1] != "}":
                corpo.append(self.declaracao())
        finally:
            self.tabela_simbolos.sair_escopo()
        self.consumir("DELIMITADOR")  # "}"
        # Atualiza a tabela com os parâmetros coletados após a declaração
        self.tabela_simbolos.escopos[0][nome]['parametros'] = params
        self.tabela_simbolos.historico_escopos[0][nome]['parametros'] = params
        return ("proc", nome, params, corpo)

    def declaracao_funcao(self):
        # Processa a declaração de uma função
        tipo_retorno = self.token_atual[1]
        self.consumir("RESERVADA")  # "int" ou "boo"
        self.consumir("RESERVADA")  # "func"
        nome = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # "("
        self.tabela_simbolos.adicionar(nome, tipo_retorno, parametros=[])  # Inicializa com lista vazia
        self.tabela_simbolos.entrar_escopo()
        params = []
        if self.token_atual[1] in ("int", "boo"):
            param = self.parametro()
            params.append(param)
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                param = self.parametro()
                params.append(param)
        self.consumir("DELIMITADOR")  # ")"
        # Atualiza a tabela com os parâmetros coletados
        self.tabela_simbolos.escopos[0][nome]['parametros'] = params
        self.tabela_simbolos.historico_escopos[0][nome]['parametros'] = params
        self.consumir("DELIMITADOR")  # "{"
        corpo = []
        try:
            while self.token_atual[1] != "}":
                if self.token_atual[0] == "RESERVADA" and self.token_atual[1] == "retorne":
                    self.consumir("RESERVADA")
                    valor = self.expressao(tipo_retorno)
                    corpo.append(("retorne", valor))
                    self.consumir("DELIMITADOR")
                else:
                    corpo.append(self.declaracao())
        finally:
            self.tabela_simbolos.sair_escopo()
        self.consumir("DELIMITADOR")  # "}"
        return ("func", nome, tipo_retorno, params, corpo)

    def parametro(self):
        # Processa um parâmetro de função ou procedimento
        tipo = self.token_atual[1]
        self.consumir("RESERVADA")
        identificador = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.tabela_simbolos.adicionar(identificador, tipo, None)
        return (tipo, identificador)

    def declaracao_variavel(self):
        # Processa a declaração de uma variável
        tipo = self.token_atual[1]
        self.consumir("RESERVADA")
        identificador = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        valor = None
        self.tabela_simbolos.adicionar(identificador, tipo, None)
        if self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            # Verifica se é uma chamada de procedimento
            if self.token_atual[0] == "IDENTIFICADOR" and self.pos < len(self.tokens) and self.tokens[self.pos][1] == "(":
                nome_chamada = self.token_atual[1]
                simbolo = self.tabela_simbolos.obter(nome_chamada)
                if simbolo and simbolo['tipo'] == "proc":
                    raise ValueError(f"Procedimento '{nome_chamada}' não retorna valor e não pode ser usado em uma atribuição na linha {self.token_atual[2]}.")
            valor = self.expressao(tipo)
            if not self.verificar_tipos(valor, tipo):
                raise ValueError(f"Tipo '{tipo}' esperado, mas tipo incompatível encontrado na linha {self.token_atual[2]}.")
            self.tabela_simbolos.atualizar(identificador, valor)
        self.consumir("DELIMITADOR")
        return (tipo, identificador, valor)

    def atribuicao_chamada(self):
        # Processa uma atribuição ou chamada de função/procedimento
        identificador = self.token_atual[1]
        simbolo = self.tabela_simbolos.obter(identificador)
        if not simbolo:
            raise ValueError(f"Identificador '{identificador}' não declarado na linha {self.token_atual[2]}.")
        self.consumir("IDENTIFICADOR")
        if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            resultado = self.chamada(identificador)
            self.consumir("DELIMITADOR")  # ";"
            return ("chamada", identificador, resultado)
        elif self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            valor = self.expressao(simbolo['tipo'])
            self.tabela_simbolos.atualizar(identificador, valor)
            self.consumir("DELIMITADOR")
            return ("atribuicao", identificador, valor)

    def chamada(self, nome):
        # Processa uma chamada de função ou procedimento
        simbolo = self.tabela_simbolos.obter(nome)
        if not simbolo:
            raise ValueError(f"Identificador '{nome}' não declarado na linha {self.token_atual[2]}.")
        # Verifica se é uma função ou procedimento: deve ter 'parametros' não vazio ou ser 'proc'
        if 'parametros' not in simbolo or not simbolo['parametros']:
            if simbolo['tipo'] != "proc":  # Procedimentos podem não ter parâmetros
                raise ValueError(f"'{nome}' não é uma função ou procedimento na linha {self.token_atual[2]}.")

        self.consumir("DELIMITADOR")  # "("
        args = []
        if self.token_atual[1] != ")":
            args.append(self.expressao())
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                args.append(self.expressao())
        self.consumir("DELIMITADOR")  # ")"

        params = simbolo.get('parametros', [])
        if len(args) != len(params):
            raise ValueError(f"Número incorreto de argumentos para '{nome}' na linha {self.token_atual[2]}: esperados {len(params)}, fornecidos {len(args)}.")

        for i, (arg, param) in enumerate(zip(args, params)):
            tipo_arg = self.obter_tipo(arg)
            tipo_param = param[0]
            if tipo_arg != tipo_param:
                raise ValueError(f"Tipo incompatível para o argumento {i+1} de '{nome}' na linha {self.token_atual[2]}: esperado '{tipo_param}', encontrado '{tipo_arg}'.")

        tipo_retorno = simbolo['tipo'] if simbolo['tipo'] != "proc" else None
        if tipo_retorno:
            temp = self.tabela_simbolos.novo_temp(tipo_retorno)
            self.tabela_simbolos.atualizar(temp, f"{nome}({', '.join(str(arg) for arg in args)})")
            return temp
        # Para procedimentos, retorna a string da chamada com argumentos
        return f"{nome}({', '.join(str(arg) for arg in args)})"

    def comando(self):
        # Identifica e processa comandos da linguagem
        if self.token_atual[1] == "se":
            return self.tratar_condicional()
        elif self.token_atual[1] == "enquanto":
            return self.tratar_laco()
        elif self.token_atual[1] == "retorne":
            self.consumir("RESERVADA")
            valor = self.expressao()
            self.consumir("DELIMITADOR")
            return ("retorne", valor)
        elif self.token_atual[1] in ["continue", "pare"]:
            comando = self.token_atual[1]
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")
            return (comando,)
        elif self.token_atual[1] in ["leia", "escreva"]:
            return self.comandos_simples()

    def tratar_condicional(self):
        # Processa uma estrutura condicional (se/senão)
        self.consumir("RESERVADA")  # "se"
        self.consumir("DELIMITADOR")  # "("
        self.tabela_simbolos.entrar_escopo()
        condicao = self.expressao("boo")
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        bloco_se = []
        while self.token_atual[1] != "}":
            bloco_se.append(self.declaracao())
        self.consumir("DELIMITADOR")  # "}"
        bloco_senao = []
        if self.token_atual[1] == "senao":
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")  # "{"
            while self.token_atual[1] != "}":
                bloco_senao.append(self.declaracao())
            self.consumir("DELIMITADOR")  # "}"
        self.tabela_simbolos.sair_escopo()
        return ("se", condicao, bloco_se, bloco_senao)

    def tratar_laco(self):
        # Processa uma estrutura de laço (enquanto)
        self.consumir("RESERVADA")  # "enquanto"
        self.consumir("DELIMITADOR")  # "("
        self.tabela_simbolos.entrar_escopo()
        condicao = self.expressao("boo")
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        corpo = []
        while self.token_atual[1] != "}":
            corpo.append(self.declaracao())
        self.consumir("DELIMITADOR")  # "}"
        self.tabela_simbolos.sair_escopo()
        return ("enquanto", condicao, corpo)

    def comandos_simples(self):
        # Processa comandos simples como leia/escreva
        comando = self.token_atual[1]
        self.consumir("RESERVADA")
        self.consumir("DELIMITADOR")  # "("
        identificador = self.token_atual[1]
        simbolo = self.tabela_simbolos.obter(identificador)
        if not simbolo:
            raise ValueError(f"Identificador '{identificador}' não declarado na linha {self.token_atual[2]}.")
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # ";"
        return (comando, identificador)

    def expressao(self, tipo_esperado=None):
        # Processa uma expressão com operadores relacionais
        valor = self.expressao_simples()
        while self.token_atual[0] == "RELACIONAIS":
            op = self.token_atual[1]
            self.consumir("RELACIONAIS")
            valor_dir = self.expressao_simples()
            
            # Verifica os tipos dos operandos antes de realizar a operação relacional
            tipo_esq = self.obter_tipo(valor)
            tipo_dir = self.obter_tipo(valor_dir)
            if tipo_esq != tipo_dir:
                raise ValueError(f"Tipos incompatíveis '{tipo_esq}' e '{tipo_dir}' na operação '{op}' na linha {self.token_atual[2]}.")
            
            # Gera uma temporária booleana para o resultado
            temp = self.tabela_simbolos.novo_temp("boo")
            self.tabela_simbolos.atualizar(temp, f"{valor} {op} {valor_dir}")
            valor = temp
        if tipo_esperado and not self.verificar_tipos(valor, tipo_esperado):
            raise ValueError(f"Tipo '{tipo_esperado}' esperado, mas tipo incompatível encontrado na linha {self.token_atual[2]}.")
        return valor

    def expressao_simples(self):
        # Processa uma expressão simples com operadores aritméticos ou lógicos
        if self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("+", "-"):
            sinal = self.token_atual[1]
            self.consumir("ARITMETICOS")
            valor = self.termo()
            if sinal == "-":
                # Verifica se o operando do operador unário é do tipo int
                tipo_valor = self.obter_tipo(valor)
                if tipo_valor != "int":
                    raise ValueError(f"Operador unário '{sinal}' exige tipo 'int', encontrado '{tipo_valor}' na linha {self.token_atual[2]}.")
                temp = self.tabela_simbolos.novo_temp("int")
                self.tabela_simbolos.atualizar(temp, f"-{valor}")
                valor = temp
        else:
            valor = self.termo()
        while (self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("+", "-")) or \
              (self.token_atual[0] == "LOGICOS" and self.token_atual[1] == "ou"):
            op = self.token_atual[1]
            self.consumir(self.token_atual[0])
            valor_dir = self.termo()
            
            # Verifica tipos para operadores aritméticos e lógicos
            tipo_esq = self.obter_tipo(valor)
            tipo_dir = self.obter_tipo(valor_dir)
            if op in ("+", "-"):
                if tipo_esq != "int" or tipo_dir != "int":
                    raise ValueError(f"Operador '{op}' exige operandos do tipo 'int', encontrados '{tipo_esq}' e '{tipo_dir}' na linha {self.token_atual[2]}.")
                temp = self.tabela_simbolos.novo_temp("int")
            elif op == "ou":
                if tipo_esq != "boo" or tipo_dir != "boo":
                    raise ValueError(f"Operador '{op}' exige operandos do tipo 'boo', encontrados '{tipo_esq}' e '{tipo_dir}' na linha {self.token_atual[2]}.")
                temp = self.tabela_simbolos.novo_temp("boo")
            self.tabela_simbolos.atualizar(temp, f"{valor} {op} {valor_dir}")
            valor = temp
        return valor

    def obter_tipo(self, valor):
        # Método auxiliar para determinar o tipo de um valor
        if valor in ["VERDADEIRO", "FALSO"]:
            return "boo"
        elif isinstance(valor, str) and valor.isdigit():
            return "int"
        elif isinstance(valor, str) and valor.isidentifier():
            simbolo = self.tabela_simbolos.obter(valor)
            if simbolo:
                return simbolo['tipo']
            raise ValueError(f"Identificador '{valor}' não declarado na linha {self.token_atual[2]}.")
        return None

    def termo(self):
        # Processa um termo com operadores de multiplicação ou lógico "e"
        valor = self.fator()
        while (self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("*", "/")) or \
              (self.token_atual[0] == "LOGICOS" and self.token_atual[1] == "e"):
            op = self.token_atual[1]
            self.consumir(self.token_atual[0])
            valor_dir = self.fator()
            temp = self.tabela_simbolos.novo_temp("int" if op in ("*", "/") else "boo")
            self.tabela_simbolos.atualizar(temp, f"{valor} {op} {valor_dir}")
            valor = temp
        return valor

    def fator(self):
        # Processa um fator (identificador, literal ou expressão entre parênteses)
        if self.token_atual[0] == "IDENTIFICADOR":
            identificador = self.token_atual[1]
            simbolo = self.tabela_simbolos.obter(identificador)
            if not simbolo:
                raise ValueError(f"Identificador '{identificador}' não declarado na linha {self.token_atual[2]}.")
            self.consumir("IDENTIFICADOR")
            if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
                return self.chamada(identificador)
            # Verifica se é uma função ou procedimento com parâmetros ou tipo "proc"
            if ('parametros' in simbolo and simbolo['parametros']) or simbolo['tipo'] == "proc":
                raise ValueError(f"'{identificador}' é uma função ou procedimento e deve ser chamado com argumentos na linha {self.token_atual[2]}.")
            return identificador
        elif self.token_atual[0] in ("BOOLEANO", "INTEIRO"):
            valor = self.token_atual[1]
            self.consumir(self.token_atual[0])
            return valor
        elif self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            self.consumir("DELIMITADOR")
            valor = self.expressao()
            self.consumir("DELIMITADOR")
            return valor
        raise SyntaxError(f"Fator inválido {self.token_atual[1]} na linha {self.token_atual[2]}.")

    def verificar_tipos(self, valor, tipo_esperado):
        # Verifica se o tipo do valor é compatível com o esperado
        if valor in ["VERDADEIRO", "FALSO"]:
            return tipo_esperado == "boo"
        elif isinstance(valor, str) and valor.isdigit():
            return tipo_esperado == "int"
        elif isinstance(valor, str) and valor.isidentifier():
            simbolo = self.tabela_simbolos.obter(valor)
            return simbolo and simbolo['tipo'] == tipo_esperado
        return False