DELIMITADORES = {' ', '\t', '\n', ',', ';', '(', ')', '{', '}', '[', ']', '.', ':'}
OPERADORES_ARITMETICOS = {'+', '-', '*', '/', 'div'}
OPERADOR_ATRIBUICAO = '='
OPERADORES_RELACIONAIS = {'!=', '>', '<', '>=', '<='}
OPERADORES_LOGICOS = {'ou', 'e'}
PALAVRAS_RESERVADAS = {'int', 'boo', 'proc', 'func', 'se', 'senao', 'enquanto', 
                       'leia', 'escreva', 'retorne', 'continue', 'pare'}
VALORES_BOO = {'VERDADEIRO', 'FALSO'}

class AnalisadorLexico:
    def __init__(self, arquivo):
        self.linhas = self.ler_arquivo(arquivo)
        self.tokens = []

    def ler_arquivo(self, arquivo):
        # Lê o arquivo linha por linha
        with open(arquivo, 'r') as f:
            return f.readlines()

    def analisar(self):
        delimitadores = ["=", ";", " "]
        for numero_linha, linha in enumerate(self.linhas, start=1):
            palavra = ""
            for char in linha:
                if char in delimitadores:
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)  # strip para remover espaços extras
                        palavra = ""
                    self.classificar_token(char.strip(), numero_linha)  # strip para remover espaços extras
                else:
                    palavra += char
            if palavra:  # Token remanescente no final da linha
                self.classificar_token(palavra.strip(), numero_linha)  # strip para remover espaços extras

        return self.tokens

    def classificar_token(self, token, linha):
        # Ignorar espaços em branco ou novas linhas
        if token.strip() == '':
            return None

        # Regras para classificar o token
        if token in ["int", "boo"]:  # Palavras reservadas
            self.tokens.append(('RESERVADA', token, linha))
        elif token.isidentifier():  # Identificadores
            self.tokens.append(('IDENTIFICADOR', token, linha))
        elif token.isdigit():  # Números
            self.tokens.append(('NUMERO', token, linha))
        elif token in ['=', ';']:  # Delimitadores
            self.tokens.append(('DELIMITADOR', token, linha))
        else:  # Token não reconhecido
            raise ValueError(f"Erro léxico na linha {linha}: '{token}' não reconhecido.")
