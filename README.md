# Compilador Simples - Disciplina de Compiladores

Este projeto é um compilador simples desenvolvido para a disciplina de **Compiladores** do curso de Bacharelado em Ciência da Computação da **Universidade Federal do Agreste de Pernambuco (UFAPE)**, no período **2024.2**. O objetivo é implementar um sistema que realiza análise léxica, sintática, semântica e geração de Código de Três Endereços (CTE) para uma linguagem de programação definida pela gramática criada anteriormente.

O compilador processa um arquivo de entrada (`codigo_geral.txt`) e suporta as características especificadas na gramática criada, como declarações de variáveis, funções, procedimentos, comandos condicionais, laços e expressões aritméticas e booleanas.

## Informações Gerais

- **Disciplina**: Compiladores
- **Docente**: Maria Aparecida Amorim Sibaldo de Carvalho
- **Discentes**: 
  - Gison Vilaça Morais
  - Ricardo Martins da Silva
- **Período**: 2024.2

## Características da Linguagem

A linguagem implementada segue a gramática definida em BNF (Backus-Naur Form) e suporta as seguintes funcionalidades:

1. Declaração de variáveis de tipo inteiro (`int`) e booleano (`boo`).
2. Declaração de procedimentos (`proc`) e funções (`func`), com ou sem parâmetros.
3. Comandos de atribuição (`=`).
4. Chamada de procedimentos e funções.
5. Comando de desvio condicional (`se` e `senao`).
6. Comando de laço (`enquanto`).
7. Comando de retorno de valor (`retorne`).
8. Comandos de desvio incondicional (`pare` e `continue`).
9. Comandos de impressão (`escreva`) de constantes e variáveis.
10. Expressões aritméticas (`+`, `-`, `*`, `/`).
11. Expressões booleanas (`==`, `!=`, `>`, `>=`, `<`, `<=`, `e`, `ou`).

Consulte a seção **Gramática** para detalhes da BNF.

## Estrutura do Projeto

O projeto é composto pelos seguintes arquivos:

- **`analisador_lexico.py`**: Realiza a análise léxica, convertendo o código-fonte em tokens.
- **`analisador_sintatico.py`**: Verifica a sintaxe do código com base na gramática.
- **`analisador_semantico.py`**: Executa a análise semântica, incluindo verificação de tipos e escopos.
- **`tabela_simbolos.py`**: Gerencia a tabela de símbolos com suporte a escopos aninhados e variáveis temporárias.
- **`gerador_cte.py`**: Gera o Código de Três Endereços (CTE) como representação intermediária.
- **`main.py`**: Integra todas as etapas e exibe os resultados.
- **`codigo_geral.txt`**: Arquivo de entrada contendo o código-fonte a ser analisado.

## Requisitos

- **Python 3.x**: O projeto foi desenvolvido em Python 3.
- Não há dependências externas; todos os módulos são nativos do Python.

## Como Usar

1. **Preparar o Código de Entrada**:
   - Crie um arquivo `codigo_geral.txt` no mesmo diretório do projeto.
   - Escreva o código conforme a gramática da linguagem. Exemplo:
     ```
     int a = 1;
     boo b = VERDADEIRO;
     
     proc Exemplo1(int a, boo b) {
	    escreva(a);
     }

     int func Exemplo2(int a) {
	    int valor;
	    valor = a;
	    retorne valor;
     }

     int c = Exemplo2(4);

     enquanto (c > 2) {
     	se (c < 2) {
     		pare;
     	} senao {
     		c = c - 1;
	        continue;
     	}
     }

     c = c + 2;
     ```

2. **Executar o Projeto**:
   - No terminal, navegue até o diretório do projeto.
   - Execute:
     ```bash
     python main.py
     ```
   - O programa exibirá:
     - Tabela de tokens (análise léxica).
     - Mensagens de sucesso ou erros em cada etapa.
     - Tabela de símbolos e Código de Três Endereços (CTE).

3. **Interpretar Resultados**:
   - Erros são reportados com a linha correspondente.
   - O CTE reflete a estrutura do programa em uma forma intermediária.

## Exemplo de Saída

Para o código acima, a saída pode ser semelhante a:

```
Tabela de Tokens:                         
Token           Valor           Linha   
--------------------------------------------------
RESERVADA       int             1          
IDENTIFICADOR   a               1         
ATRIBUICAO      =               1         
INTEIRO         1               1          
DELIMITADOR     ;               1         
RESERVADA       boo             2      
IDENTIFICADOR   b               2          
ATRIBUICAO      =               2          
BOOLEANO        VERDADEIRO      2                 
DELIMITADOR     ;               2
RESERVADA       proc            4
IDENTIFICADOR   Exemplo1        4
DELIMITADOR     (               4
RESERVADA       int             4
IDENTIFICADOR   a               4
DELIMITADOR     ,               4
RESERVADA       boo             4
IDENTIFICADOR   b               4
DELIMITADOR     )               4
DELIMITADOR     {               4
RESERVADA       escreva         5
DELIMITADOR     (               5
IDENTIFICADOR   a               5
DELIMITADOR     )               5
DELIMITADOR     ;               5
DELIMITADOR     }               6
RESERVADA       int             8
RESERVADA       func            8
IDENTIFICADOR   Exemplo2        8
DELIMITADOR     (               8
RESERVADA       int             8
IDENTIFICADOR   a               8
DELIMITADOR     )               8
DELIMITADOR     {               8
RESERVADA       int             9
IDENTIFICADOR   valor           9
DELIMITADOR     ;               9
IDENTIFICADOR   valor           10
ATRIBUICAO      =               10
IDENTIFICADOR   a               10
DELIMITADOR     ;               10                
RESERVADA       retorne         11                                                                                                                               
IDENTIFICADOR   valor           11
DELIMITADOR     ;               11
DELIMITADOR     }               12
RESERVADA       int             14
IDENTIFICADOR   c               14
ATRIBUICAO      =               14
IDENTIFICADOR   Exemplo2        14
DELIMITADOR     (               14
INTEIRO         4               14
DELIMITADOR     )               14
DELIMITADOR     ;               14
RESERVADA       enquanto        16
DELIMITADOR     (               16
IDENTIFICADOR   c               16
RELACIONAIS     >               16
INTEIRO         2               16
DELIMITADOR     )               16
DELIMITADOR     {               16
RESERVADA       se              17
DELIMITADOR     (               17
IDENTIFICADOR   c               17
RELACIONAIS     <               17
INTEIRO         2               17
DELIMITADOR     )               17
DELIMITADOR     {               17
RESERVADA       pare            18
DELIMITADOR     ;               18
DELIMITADOR     }               19
RESERVADA       senao           19
DELIMITADOR     {               19
IDENTIFICADOR   c               20
ATRIBUICAO      =               20
IDENTIFICADOR   c               20
ARITMETICOS     -               20
INTEIRO         1               20
DELIMITADOR     ;               20
RESERVADA       continue        21
DELIMITADOR     ;               21
DELIMITADOR     }               22
DELIMITADOR     }               23
IDENTIFICADOR   c               25
ATRIBUICAO      =               25
IDENTIFICADOR   c               25
ARITMETICOS     +               25
INTEIRO         2               25
DELIMITADOR     ;               25
--------------------------------------------------
Análise léxica concluída com sucesso!
Análise sintática concluída com sucesso!
Análise semântica concluída com sucesso!
Geração de CTE concluída com sucesso!
--------------------------------------------------

Tabela de Símbolos (todos os escopos):
Escopo     Identificador   Tipo       Valor
--------------------------------------------------
0          a               int        1
0          b               boo        VERDADEIRO
0          Exemplo1        proc       None
0          Exemplo2        int        None
0          c               int        t4
0          t0              int        Exemplo2(4)
0          t4              int        c + 2
1          a               int        None
1          b               boo        None
1          t1              boo        c > 2
2          a               int        None
2          valor           int        a
2          t2              boo        c < 2
2          t3              int        c - 1
--------------------------------------------------

Código de Três Endereços (CTE):
1: a = 1
2: b = VERDADEIRO
3: proc Exemplo1:
4: param a int
5: param b boo
6: escreva a
7: func Exemplo2:
8: param a int
9: decl valor int
10: valor = a
11: return valor
12: t0 = Exemplo2(4)
13: c = t0
14: L1:
15: t1 = c > 2
16: if t1 == FALSO goto L2
17: t2 = c < 2
18: if t2 == FALSO goto L3
19: pare
20: goto L4
21: L3:
22: t3 = c - 1
23: c = t3
24: continue
25: L4:
26: goto L1
27: L2:
28: t4 = c + 2
29: c = t4
--------------------------------------------------
```

## Gramática (BNF)

A gramática da linguagem é a seguinte:

```
<Programa> ::= <Declaração> {<Declaração>}
<Declaração> ::= (<Declaração de variáveis> | <Declaração de Procedimento> | <Declaração de Função> | <Comando>)

<Declaração de variáveis> ::= <Tipo> <Identificador> [ = <Expressão> ] ;
<Tipo> ::= (int | boo)

<Declaração de Procedimento> ::= proc <Identificador> ( [<Parâmetro> {, <Parâmetro>}] ) { <Bloco do Procedimento> }
<Bloco do Procedimento> ::= [<Declaração de variáveis>] <Comandos>
<Declaração de Função> ::= <Tipo> func <Identificador> ( [<Parâmetro> {, <Parâmetro>}] ) { <Bloco da Função> }
<Bloco da Função> ::= [<Declaração de variáveis>] <Comandos>
<Parâmetro> ::= <Tipo> <Identificador>

<Comandos> ::= <Comando> {<Comando>}
<Comando> ::= (<Comando Chamar> | <Comando Condicional> | <Comando Enquanto> | <Comando Leia> | <Comando Escreva> | retorne <Expressão> ; | continue ; | pare ;)
<Comando Chamar> ::= (<Comando Atribua> | <Chamada de Procedimento> | <Chamada de Função>)
<Comando Atribua> ::= <Identificador> = <Expressão> ;
<Chamada de Procedimento> ::= <Identificador> ( [<Argumentos>] ) ;
<Chamada de Função> ::= <Identificador> ( [<Argumentos>] )
<Comando Condicional> ::= se ( <Expressão> ) { <Comandos> } [ senao { <Comandos> } ]
<Comando Enquanto> ::= enquanto ( <Expressão> ) { <Comandos> }
<Comando Leia> ::= leia ( <Identificador> ) ;
<Comando Escreva> ::= escreva ( <Identificador> ) ;

<Expressão> ::= <Expressão Simples> [<Operador Relacional> <Expressão Simples>]
<Operador Relacional> ::= (== | != | > | >= | < | <=)
<Expressão Simples> ::= [ + | - ] <Termo> { (+ | - | ou) <Termo> }
<Termo> ::= <Fator> { (* | / | e) <Fator> }
<Fator> ::= (<Variável> | <Número> | <Chamada de Função> | ( <Expressão> ) | VERDADEIRO | FALSO)
<Variável> ::= <Identificador>
<Argumentos> ::= <Expressão> {, <Expressão>}

<Identificador> ::= <letra> {<letra> | <dígito>}
<Número> ::= <dígito> {<dígito>}
<Dígito> ::= (0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9)
<Letra> ::= (a | b | c | ... | z | A | B | C | ... | Z)
```

### Legendas da Gramática
- `<>`: Símbolos não-terminais.
- **Negrito**: Palavras reservadas ou terminais.
- `::=`: Representa a geração.
- `[ ]`: Conteúdo opcional (zero ou uma vez).
- `{}`: Conteúdo repetível (zero ou mais vezes).
- `()`: Delimitadores usados no código.
