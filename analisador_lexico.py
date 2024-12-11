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
        palavras_reservadas = ['int', 'boo', 'proc', 'func', 'se', 'senao', 
                               'enquanto', 'leia', 'escreva', 'retorne', 
                               'continue', 'pare']
        if token in palavras_reservadas:  # Palavras reservadas
            self.tokens.append(('RESERVADA', token, linha))

        elif token in ['VERDADEIRO', 'FALSO']:  # Valores booleanos
            self.tokens.append(('BOOLEANO', token, linha))

        elif token.isidentifier():  # Identificadores
            self.tokens.append(('IDENTIFICADOR', token, linha))
       
        elif token.isdigit():  # Números inteiros
            self.tokens.append(('INTEIRO', token, linha))
       
        elif token in [' ', '\t', '\n', ',', ';', '(', ')', '{', '}', '[', ']',
                         '.', ':']:  # Delimitadores      
            self.tokens.append(('DELIMITADOR', token, linha))
       
        elif token in ['ou', 'e']:  # Operadores Lógicos
            self.tokens.append(('LOGICOS', token, linha))
      
        elif token in ['!=', '>', '<', '>=', '<=']:  # Operadores Relacionais
            self.tokens.append(('RELACIONAIS', token, linha))
       
        elif token in ['+', '-', '*', '/', 'div']:  # Operadores Aritméticos
            self.tokens.append(('ARITMETICOS', token, linha))
       
        elif token in ['=']:  # Atribuição
            self.tokens.append(('ATRIBUICAO', token, linha))
    
        else:  # Token não reconhecido
            raise ValueError(f"Erro léxico na linha {linha}: '{token}' não reconhecido.")
