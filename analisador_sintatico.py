# Classe responsável pela análise sintática do código fonte
class AnalisadorSintatico:
    # Inicializa o analisador sintático com os tokens e a tabela de símbolos
    def __init__(self, tokens, tabela_simbolos):
        self.tokens = tokens  # Lista de tokens gerados pelo analisador léxico
        self.tabela_simbolos = tabela_simbolos  # Instância da tabela de símbolos
        self.pos = 0  # Posição atual na lista de tokens

    # Método principal para realizar a análise sintática
    def analisar(self):
        while self.pos < len(self.tokens):  # Continua até o final da lista de tokens
            token = self.tokens[self.pos]  # Obtém o token atual
            if token[0] == "RESERVADA":  # Verifica se o token é uma palavra reservada
                if token[1] in ["se", "senao"]:  # Verifica se é um condicional
                    self.tratar_condicional()  # Chama o método para tratar o condicional
                elif token[1] == "enquanto":  # Verifica se é um laço
                    self.tratar_laco()  # Chama o método para tratar o laço
                else:
                    self.declaracao_variavel()  # Trata declarações de variáveis
            elif token[0] == "IDENTIFICADOR":  # Verifica se o token é um identificador
                self.atribuicao()  # Chama o método para tratar atribuições
            else:
                # Exibe erro sintático se o token não for esperado
                print(f"Erro sintático na linha {token[2]}: Comando inesperado.")
                self.pos += 1  # Avança para o próximo token

    # Método para tratar declarações condicionais (ex.: "se" e "senao")
    def tratar_condicional(self):
        self.pos += 1  # Avança o token para verificar a condição
        if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "(":  # Verifica abertura de parênteses
            self.pos += 1  # Avança para dentro da condição
            self.tratar_expressao()  # Chama o método para tratar a expressão
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ")":  # Verifica fechamento de parênteses
                print("contem )")
                self.pos += 1  # Avança após a condição
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "{":  # Verifica abertura de bloco
                    self.pos += 1  # Avança para dentro do bloco
                    self.tratar_bloco()  # Trata o conteúdo do bloco
                    if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "}":  # Verifica fechamento de bloco
                        self.pos += 1  # Avança após o bloco
                        if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "senao":  # Verifica "senao"
                            self.tratar_senao()  # Chama o método para tratar o "senao"
                    else:
                        # Exibe erro caso o bloco "se" não seja fechado corretamente
                        print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '}}' no final do bloco 'se'.")
                else:
                    # Exibe erro caso não haja abertura de bloco após a condição
                    print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '{{' após condição do 'se'.")
        else:
            # Exibe erro caso não haja abertura de parênteses após "se"
            print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '(' após 'se'.")

    # Método para tratar o bloco "senao" em condicionais
    def tratar_senao(self):
        self.pos += 1  # Avança para verificar o bloco "senao"
        if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "{":  # Verifica abertura do bloco
            self.pos += 1  # Avança para dentro do bloco "senao"
            self.tratar_bloco()  # Trata o conteúdo do bloco
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "}":  # Verifica fechamento do bloco
                self.pos += 1  # Avança após o bloco
            else:
                # Exibe erro caso o bloco "senao" não seja fechado corretamente
                print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '}}' no final do bloco 'senao'.")
        else:
            # Exibe erro caso não haja abertura de bloco após "senao"
            print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '{{' após 'senao'.")

    # Método para tratar laços (ex.: "enquanto")
    def tratar_laco(self):
        self.pos += 1  # Avança para verificar a condição do laço
        if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "(":  # Verifica abertura de parênteses
            self.pos += 1  # Avança para dentro da condição
            self.tratar_expressao()  # Trata a expressão condicional
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ")":  # Verifica fechamento de parênteses
                self.pos += 1  # Avança após a condição
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "{":  # Verifica abertura de bloco
                    self.pos += 1  # Avança para dentro do bloco
                    self.tratar_bloco()  # Trata o conteúdo do bloco
                    if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "}":  # Verifica fechamento do bloco
                        self.pos += 1  # Avança após o bloco
                    else:
                        # Exibe erro caso o bloco do "enquanto" não seja fechado
                        print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '}}' no final do bloco 'enquanto'.")
                else:
                    # Exibe erro caso não haja abertura de bloco após a condição
                    print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '{{' após condição do 'enquanto'.")
            else:
                # Exibe erro caso não haja fechamento de parênteses após a condição
                print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado ')' após a expressão condicional.")
        else:
            # Exibe erro caso não haja abertura de parênteses após "enquanto"
            print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado '(' após 'enquanto'.")

    def tratar_bloco(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos][1] != "}":
            self.analisar()

    def tratar_expressao(self):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] in ["INTEIRO", "BOOLEANO", "IDENTIFICADOR", "RELACIONAIS"]:
            self.pos += 1

    def declaracao_variavel(self):
        tipo = self.tokens[self.pos][1]
        self.pos += 1
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == "IDENTIFICADOR":
            identificador = self.tokens[self.pos][1]
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "=":
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos][0] in ["INTEIRO", "BOOLEANO"]:
                    valor = self.tokens[self.pos][1]
                    self.tabela_simbolos.adicionar(identificador, tipo, valor)
                    self.pos += 1
                else:
                    print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Valor inválido na atribuição.")
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado '=' após identificador.")
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ";":
                self.pos += 1
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado ';' no final da declaração.")
        else:
            print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado identificador após tipo de variável.")

    def atribuicao(self):
        if self.tokens[self.pos][0] == "IDENTIFICADOR":
            identificador = self.tokens[self.pos][1]
            self.pos += 1
            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "=":
                self.pos += 1
                if self.pos < len(self.tokens) and self.tokens[self.pos][0] in ["INTEIRO", "BOOLEANO", "IDENTIFICADOR"]:
                    valor = self.tokens[self.pos][1]
                    simbolo = next((s for s in self.tabela_simbolos.simbolos if s["identificador"] == identificador), None)
                    if simbolo:
                        if (simbolo["tipo"] == "int" and self.tokens[self.pos][0] == "INTEIRO") or \
                           (simbolo["tipo"] == "boo" and self.tokens[self.pos][0] == "BOOLEANO"):
                            simbolo["valor"] = valor
                        else:
                            print(f"Erro semântico na linha {self.tokens[self.pos][2]}: Tipo incompatível na atribuição.")
                    else:
                        print(f"Erro semântico na linha {self.tokens[self.pos][2]}: Identificador '{identificador}' não declarado.")
                    self.pos += 1
                else:
                    print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Valor inválido na atribuição.")
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ";":
                    self.pos += 1
                else:
                    print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado ';' no final da atribuição.")
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado '=' após identificador.")
        else:
            print(f"Erro sintático na linha {self.tokens[self.pos][2]}: Esperado identificador no início da atribuição.")
