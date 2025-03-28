class AnalisadorLexico:
    def __init__(self, arquivo):
        # Inicializa o analisador léxico com o arquivo de entrada
        self.linhas = self.ler_arquivo(arquivo)
        self.tokens = []  # Lista para armazenar os tokens gerados

    def ler_arquivo(self, arquivo):
        # Lê todas as linhas do arquivo de entrada
        with open(arquivo, 'r') as f:
            return f.readlines()

    def analisar(self):
        # Analisa cada linha do arquivo e gera tokens
        delimitadores = [";", "{", "}", "(", ")", ",", "+", "-", "*", "/"]
        operadores_compostos = ["==", "!=", ">=", "<="]  # Operadores de comparação de dois caracteres
        for numero_linha, linha in enumerate(self.linhas, start=1):
            palavra = ""  # Armazena caracteres até formar um token
            i = 0
            while i < len(linha):
                char = linha[i]
                # Verifica operadores compostos (ex.: ==, !=) antes de processar caracteres individuais
                if i + 1 < len(linha) and linha[i:i + 2] in operadores_compostos:
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                    self.classificar_token(linha[i:i + 2], numero_linha)
                    i += 1  # Pula o próximo caractere do operador composto
                # Processa delimitadores ou operador de atribuição
                elif char in delimitadores or char == "=":
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                    self.classificar_token(char, numero_linha)
                # Ignora espaços em branco e separa palavras
                elif char.isspace():
                    if palavra:
                        self.classificar_token(palavra.strip(), numero_linha)
                        palavra = ""
                # Acumula caracteres para formar palavras
                else:
                    palavra += char
                i += 1
            # Classifica a última palavra da linha, se houver
            if palavra:
                self.classificar_token(palavra.strip(), numero_linha)
        return self.tokens

    def classificar_token(self, token, linha):
        # Ignora tokens vazios
        if token.strip() == '':
            return None

        # Lista de palavras reservadas da linguagem
        palavras_reservadas = ['int', 'boo', 'proc', 'func', 'se', 'senao',
                               'enquanto', 'leia', 'escreva', 'retorne',
                               'continue', 'pare']
        # Classifica o token com base em sua categoria
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
            # Levanta erro para tokens não reconhecidos
            raise ValueError(f"Erro léxico na linha {linha}: '{token}' não reconhecido.")