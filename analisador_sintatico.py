class AnalisadorSintatico:  # Classe para realizar a análise sintática
    def __init__(self, tokens, tabela_simbolos):  # Construtor da classe
        self.tokens = tokens  # Lista de tokens gerados pela análise léxica
        self.tabela_simbolos = tabela_simbolos  # Instância da tabela de símbolos
        self.pos = 0  # Posição atual na lista de tokens

    def analisar(self):  # Método principal para análise sintática
        while self.pos < len(self.tokens):  # Itera até o final da lista de tokens
            token = self.tokens[self.pos]  # Obtém o token atual
            if token[0] == "RESERVADA":  # Verifica se é uma palavra reservada
                self.declaracao_variavel()  # Trata como uma declaração de variável
            else:
                print(f"Erro sintático na linha {token[2]}: Esperado tipo de variável.")  # Exibe erro
                self.pos += 1  # Avança para o próximo token

    def declaracao_variavel(self):  # Método para tratar declarações de variáveis
        tipo = self.tokens[self.pos][1]  # Obtém o tipo da variável
        self.pos += 1  # Avança para o próximo token

        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == "IDENTIFICADOR":  # Verifica se há um identificador
            identificador = self.tokens[self.pos][1]  # Obtém o nome do identificador
            self.pos += 1  # Avança para o próximo token

            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "=":  # Verifica se há um operador de atribuição
                self.pos += 1  # Avança para o próximo token

                if self.pos < len(self.tokens) and (self.tokens[self.pos][0] == "INTEIRO" or self.tokens[self.pos][0] == "BOOLEANO"):
                    valor = self.tokens[self.pos][1]  # Obtém o valor da atribuição
                    self.tabela_simbolos.adicionar(identificador, tipo, valor)  # Adiciona à tabela de símbolos
                    self.pos += 1  # Avança para o próximo token

                else:
                    print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado valor após '='.")  # Erro de sintaxe
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado '=' após identificador.")  # Erro de sintaxe

            if self.pos < len(self.tokens) and self.tokens[self.pos][1] == ";":  # Verifica se há um ponto e vírgula no final
                self.pos += 1  # Avança para o próximo token
            else:
                print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado ';' no final da declaração.")  # Erro de sintaxe
        else:
            print(f"Erro sintático na linha {self.tokens[self.pos - 1][2]}: Esperado identificador após tipo de variável.")  # Erro de sintaxe
