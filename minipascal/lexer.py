# -*- coding: utf-8 -*-
"""
Analisador léxico do miniPascal, implementado como um AFD (autômato finito
determinístico) escrito à mão, com a regra do "maior casamento" (maximal munch),
a mesma que o flex usa.

Cada token reconhecido vira uma tupla Token(tipo, lexema, linha, coluna).
O campo `tipo` já é o nome do terminal usado na gramática:
    'id', 'num_int', 'num_real'  -> classes de lexemas
    'begin', ':=', ';', ...      -> palavras reservadas e símbolos (o próprio lexema)
    '$'                          -> fim da entrada
"""
from collections import namedtuple

Token = namedtuple("Token", "tipo lexema linha coluna")

PALAVRAS_RESERVADAS = {
    "procedure", "function", "var", "begin", "end",
    "if", "then", "else", "while", "do",
    "integer", "real", "boolean", "true", "false",
    "and", "or", "not", "div", "mod",
}


class ErroLexico(Exception):
    def __init__(self, msg, linha, coluna):
        super().__init__(msg)
        self.msg, self.linha, self.coluna = msg, linha, coluna


# --------------------------------------------------------------------------
# Definição do AFD
# --------------------------------------------------------------------------
# Estados:
#   S0         inicial
#   ID         letra (letra|dígito|_)*
#   INT        dígito+
#   INT_PONTO  dígito+ '.'          (não final: exige dígito depois do ponto)
#   REAL       dígito+ '.' dígito+
#   DP         ':'
#   ATRIB      ':='
#   LT, LE, NE '<'  '<='  '<>'
#   GT, GE     '>'  '>='
#   SIMB       símbolos de 1 caractere:  + - * / = ( ) ; ,
S0, ID, INT, INT_PONTO, REAL, DP, ATRIB, LT, LE, NE, GT, GE, SIMB = (
    "S0", "ID", "INT", "INT_PONTO", "REAL", "DP", "ATRIB",
    "LT", "LE", "NE", "GT", "GE", "SIMB")

SIMBOLOS_1 = "+-*/=();,"

def _classe(c):
    """Classe de caractere (alfabeto do AFD)."""
    if c.isascii() and c.isalpha():
        return "letra"
    if c.isascii() and c.isdigit():
        return "digito"
    return c

DELTA = {
    (S0, "letra"): ID, (S0, "digito"): INT, (S0, ":"): DP,
    (S0, "<"): LT, (S0, ">"): GT,
    (ID, "letra"): ID, (ID, "digito"): ID, (ID, "_"): ID,
    (INT, "digito"): INT, (INT, "."): INT_PONTO,
    (INT_PONTO, "digito"): REAL,
    (REAL, "digito"): REAL,
    (DP, "="): ATRIB,
    (LT, "="): LE, (LT, ">"): NE,
    (GT, "="): GE,
}
for _s in SIMBOLOS_1:
    DELTA[(S0, _s)] = SIMB

# estados finais -> tipo de token ('*' = o próprio lexema)
FINAIS = {
    ID: "id", INT: "num_int", REAL: "num_real",
    DP: ":", ATRIB: ":=", LT: "<", LE: "<=", NE: "<>", GT: ">", GE: ">=",
    SIMB: "*",
}


class Lexer:
    def __init__(self, texto):
        self.t = texto
        self.n = len(texto)
        self.i = 0
        self.linha = 1
        self.col = 1

    # -- controle de posição ------------------------------------------------
    def _avancar(self, k):
        for c in self.t[self.i:self.i + k]:
            if c == "\n":
                self.linha += 1
                self.col = 1
            else:
                self.col += 1
        self.i += k

    def _pular_branco_e_comentarios(self):
        t = self.t
        while self.i < self.n:
            c = t[self.i]
            if c in " \t\r\n\f":
                self._avancar(1)
            elif c == "{":                                   # { comentário }
                fim = t.find("}", self.i + 1)
                if fim < 0:
                    raise ErroLexico("comentário '{' não fechado", self.linha, self.col)
                self._avancar(fim + 1 - self.i)
            elif t.startswith("(*", self.i):                 # (* comentário *)
                fim = t.find("*)", self.i + 2)
                if fim < 0:
                    raise ErroLexico("comentário '(*' não fechado", self.linha, self.col)
                self._avancar(fim + 2 - self.i)
            elif t.startswith("//", self.i):                 # // até o fim da linha
                fim = t.find("\n", self.i)
                self._avancar((self.n if fim < 0 else fim) - self.i)
            else:
                break

    # -- próximo token ------------------------------------------------------
    def proximo(self):
        self._pular_branco_e_comentarios()
        if self.i >= self.n:
            return Token("$", "$", self.linha, self.col)

        estado, j = S0, self.i
        ultimo = None                       # (posição, estado final) mais longo
        while j < self.n and (estado, _classe(self.t[j])) in DELTA:
            estado = DELTA[(estado, _classe(self.t[j]))]
            j += 1
            if estado in FINAIS:
                ultimo = (j, estado)

        if ultimo is None:
            raise ErroLexico("caractere inválido %r" % self.t[self.i], self.linha, self.col)

        fim, estado = ultimo
        lexema = self.t[self.i:fim]
        tipo = FINAIS[estado]
        if tipo == "*":
            tipo = lexema
        elif tipo == "id" and lexema.lower() in PALAVRAS_RESERVADAS:
            tipo = lexema.lower()           # Pascal não diferencia maiúsculas
        tok = Token(tipo, lexema, self.linha, self.col)
        self._avancar(fim - self.i)
        return tok

    def todos(self):
        toks = []
        while True:
            tk = self.proximo()
            toks.append(tk)
            if tk.tipo == "$":
                return toks


def tokenizar(texto):
    return Lexer(texto).todos()
