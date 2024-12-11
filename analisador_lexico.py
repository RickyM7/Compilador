class AnalisadorLexico:  # Classe para realizar a análise léxica
    def __init__(self, arquivo):  # Construtor da classe
        self.linhas = self.ler_arquivo(arquivo)  # Lê as linhas do arquivo fornecido
        self.tokens = []  # Inicializa a lista de tokens

    def ler_arquivo(self, arquivo):  # Função para ler o arquivo de entrada
        # Lê o arquivo linha por linha
        with open(arquivo, 'r') as f:  # Abre o arquivo em modo de leitura
            return f.readlines()  # Retorna as linhas do arquivo como uma lista

    def analisar(self):  # Função principal para análise léxica
        delimitadores = ["=", ";", " "]  # Define os delimitadores
        for numero_linha, linha in enumerate(self.linhas, start=1):  # Itera sobre as linhas do arquivo
            palavra = ""  # Inicializa uma palavra temporária
            for char in linha:  # Itera sobre os caracteres da linha
                if char in delimitadores:  # Verifica se o caractere é um delimitador
                    if palavra:  # Se houver uma palavra acumulada
                        self.classificar_token(palavra.strip(), numero_linha)  # Classifica o token
                        palavra = ""  # Reseta a palavra
                    self.classificar_token(char.strip(), numero_linha)  # Classifica o delimitador
                else:
                    palavra += char  # Acumula o caractere na palavra
            if palavra:  # Token remanescente no final da linha
                self.classificar_token(palavra.strip(), numero_linha)  # Classifica o token remanescente

        return self.tokens  # Retorna a lista de tokens gerados

    def classificar_token(self, token, linha):  # Classifica um token com base em seu tipo
        # Ignorar espaços em branco ou novas linhas
        if token.strip() == '':  # Verifica se o token está vazio
            return None  # Ignora tokens vazios

        # Regras para classificar o token
        palavras_reservadas = ['int', 'boo', 'proc', 'func', 'se', 'senao', 
                               'enquanto', 'leia', 'escreva', 'retorne', 
                               'continue', 'pare']  # Lista de palavras reservadas
        if token in palavras_reservadas:  # Verifica se o token é uma palavra reservada
            self.tokens.append(('RESERVADA', token, linha))  # Adiciona o token à lista como reservado

        elif token in ['VERDADEIRO', 'FALSO']:  # Verifica se o token é um valor booleano
            self.tokens.append(('BOOLEANO', token, linha))  # Adiciona o token à lista como booleano

        elif token.isidentifier():  # Verifica se o token é um identificador válido
            self.tokens.append(('IDENTIFICADOR', token, linha))  # Adiciona o token à lista como identificador
       
        elif token.isdigit():  # Verifica se o token é um número inteiro
            self.tokens.append(('INTEIRO', token, linha))  # Adiciona o token à lista como inteiro
       
        elif token in [' ', '\t', '\n', ',', ';', '(', ')', '{', '}', '[', ']',
                         '.', ':']:  # Verifica se o token é um delimitador      
            self.tokens.append(('DELIMITADOR', token, linha))  # Adiciona o token à lista como delimitador
       
        elif token in ['ou', 'e']:  # Verifica se o token é um operador lógico
            self.tokens.append(('LOGICOS', token, linha))  # Adiciona o token à lista como lógico
      
        elif token in ['!=', '>', '<', '>=', '<=']:  # Verifica se o token é um operador relacional
            self.tokens.append(('RELACIONAIS', token, linha))  # Adiciona o token à lista como relacional
       
        elif token in ['+', '-', '*', '/', 'div']:  # Verifica se o token é um operador aritmético
            self.tokens.append(('ARITMETICOS', token, linha))  # Adiciona o token à lista como aritmético
       
        elif token in ['=']:  # Verifica se o token é um operador de atribuição
            self.tokens.append(('ATRIBUICAO', token, linha))  # Adiciona o token à lista como atribuição
    
        else:  # Token não reconhecido
            raise ValueError(f"Erro léxico na linha {linha}: '{token}' não reconhecido.")  # Levanta um erro para tokens inválidos
