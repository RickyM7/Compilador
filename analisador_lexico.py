class AnalisadorLexico:
    def __init__(self, arquivo):
        self.linhas = self.ler_arquivo(arquivo)
        self.tokens = []

    def ler_arquivo(self, arquivo):
        with open(arquivo, 'r') as f:
            return f.readlines()

    def analisar(self):
        delimitadores = [";", "{", "}", "(", ")", ",", "+", "-", "*", "/"]
        operadores_compostos = ["==", "!=", ">=", "<="]  # Operadores compostos
        for numero_linha, linha in enumerate(self.linhas, start=1):
            palavra = ""
            i = 0
            while i < len(linha):
                char = linha[i]
                # Verificar operadores compostos antes de tudo
                if i + 1 < len(linha) and linha[i:i + 2] in operadores_compostos:
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                    self.classificar_token(linha[i:i + 2], numero_linha)
                    i += 1  # Pular o próximo caractere do operador composto
                elif char in delimitadores or char == "=":
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                    self.classificar_token(char, numero_linha)
                elif char.isspace():
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                else:
                    palavra += char
                i += 1
            if palavra:
                self.classificar_token(palavra.strip(), numero_linha)
        return self.tokens

    def classificar_token(self, token, linha):
        if token.strip() == '':
            return None

        palavras_reservadas = ['int', 'boo', 'proc', 'func', 'se', 'senao',
                               'enquanto', 'leia', 'escreva', 'retorne',
                               'continue', 'pare']
        if token in palavras_reservadas:
            self.tokens.append(('RESERVADA', token, linha))
        elif token in ['VERDADEIRO', 'FALSO']:
            self.tokens.append(('BOOLEANO', token, linha))
        elif token.isidentifier():
            self.tokens.append(('IDENTIFICADOR', token, linha))
        elif token.isdigit():
            self.tokens.append(('INTEIRO', token, linha))
        elif token in [";", ",", "{", "}", "(", ")"]:
            self.tokens.append(('DELIMITADOR', token, linha))
        elif token in ['ou', 'e']:
            self.tokens.append(('LOGICOS', token, linha))
        elif token in ['==', '!=', '>', '<', '>=', '<=']:
            self.tokens.append(('RELACIONAIS', token, linha))
        elif token in ['+', '-', '*', '/']:
            self.tokens.append(('ARITMETICOS', token, linha))
        elif token == '=':
            self.tokens.append(('ATRIBUICAO', token, linha))
        else:
            raise ValueError(f"Erro léxico na linha {linha}: '{token}' não reconhecido.")
