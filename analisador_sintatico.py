class AnalisadorSintatico:
    def __init__(self, tokens, tabela_simbolos):
        self.tokens = tokens
        self.tabela_simbolos = tabela_simbolos
        self.pos = 0

    def analisar(self):
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token[0] == "RESERVADA":
                self.declaracao_variavel()
            else:
                print(f"Erro sintático na linha {token[2]}: Esperado tipo de variável.")
                self.pos += 1

    def declaracao_variavel(self):
        tipo = self.tokens[self.pos][1]
        self.pos += 1

        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == "IDENTIFICADOR":
            identificador = self.tokens[self.pos][1]
            self.pos += 1

            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "=":
                self.pos += 1

                if self.pos < len(self.tokens) and (self.tokens[self.pos][0] == "NUMERO" or self.tokens[self.pos][0] == "IDENTIFICADOR"):
                    valor = self.tokens[self.pos][1]
                    self.tabela_simbolos.adicionar(identificador, tipo, valor)
                    self.pos += 1
                else:
                    print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado valor após '='.")
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado '=' após identificador.")

            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ";":
                self.pos += 1
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado ';' no final da declaração.")
        else:
            print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado identificador após tipo de variável.")
