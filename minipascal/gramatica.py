# -*- coding: utf-8 -*-
"""
Gramática do miniPascal (livre de contexto, fatorada à esquerda e sem recursão
à esquerda, para ser LL(1)) + construção automática de NULLABLE, FIRST, FOLLOW
e da tabela preditiva M[A, a].
"""

EPS = "ε"

GRAMATICA_TXT = """
Programa     -> ListaDecl
ListaDecl    -> Decl ListaDecl | ε
Decl         -> DeclVar | DeclProc | DeclFunc

DeclVar      -> id IdsCauda : Tipo ;
IdsCauda     -> , id IdsCauda | ε
Tipo         -> integer | real | boolean

DeclProc     -> procedure id Params ; Locais Bloco ;
DeclFunc     -> function id Params : Tipo ; Locais Bloco ;
Params       -> ( ListaParam ) | ε
ListaParam   -> Param ParamCauda
ParamCauda   -> ; Param ParamCauda | ε
Param        -> id IdsCauda : Tipo
Locais       -> var DeclVar ListaVar | ε
ListaVar     -> DeclVar ListaVar | ε

Bloco        -> begin ListaCmd end
ListaCmd     -> Cmd CmdCauda
CmdCauda     -> ; Cmd CmdCauda | ε
Cmd          -> id CmdId | if Expr then Cmd SenaoOpc | while Expr do Cmd | Bloco | ε
CmdId        -> := Expr | ( Args ) | ε
SenaoOpc     -> else Cmd | ε

Expr         -> ExprSimples ExprCauda
ExprCauda    -> Relop ExprSimples | ε
Relop        -> = | <> | < | <= | > | >=
ExprSimples  -> Termo SimplesCauda
SimplesCauda -> Addop Termo SimplesCauda | ε
Addop        -> + | - | or
Termo        -> Fator TermoCauda
TermoCauda   -> Mulop Fator TermoCauda | ε
Mulop        -> * | / | div | mod | and
Fator        -> num_int | num_real | true | false | id FatorId | ( Expr ) | not Fator | - Fator | + Fator
FatorId      -> ( Args ) | ε
Args         -> Expr ArgsCauda | ε
ArgsCauda    -> , Expr ArgsCauda | ε
"""


class Gramatica:
    def __init__(self, texto=GRAMATICA_TXT):
        self.prods = []                  # lista de (cabeça, [corpo])
        self.nao_terminais = []
        for linha in texto.strip().splitlines():
            if not linha.strip():
                continue
            cab, resto = linha.split("->", 1)
            cab = cab.strip()
            if cab not in self.nao_terminais:
                self.nao_terminais.append(cab)
            for alt in resto.split(" | "):
                corpo = alt.split()
                self.prods.append((cab, [] if corpo == [EPS] else corpo))
        self.inicial = self.prods[0][0]
        nts = set(self.nao_terminais)
        self.terminais = []
        for _, corpo in self.prods:
            for s in corpo:
                if s not in nts and s not in self.terminais:
                    self.terminais.append(s)
        self.terminais.append("$")
        self._nullable()
        self._first()
        self._follow()
        self._tabela()

    # ------------------------------------------------------------------
    def eh_nt(self, s):
        return s in self.nao_terminais

    def _nullable(self):
        self.nullable = set()
        mudou = True
        while mudou:
            mudou = False
            for a, corpo in self.prods:
                if a not in self.nullable and all(s in self.nullable for s in corpo):
                    self.nullable.add(a)
                    mudou = True

    def first_seq(self, seq):
        """FIRST de uma sequência de símbolos (sem ε; use nullable_seq para isso)."""
        res = set()
        for s in seq:
            if self.eh_nt(s):
                res |= self.first[s]
                if s not in self.nullable:
                    return res
            else:
                res.add(s)
                return res
        return res

    def nullable_seq(self, seq):
        return all(s in self.nullable for s in seq)

    def _first(self):
        self.first = {a: set() for a in self.nao_terminais}
        mudou = True
        while mudou:
            mudou = False
            for a, corpo in self.prods:
                novo = self.first_seq(corpo)
                if not novo <= self.first[a]:
                    self.first[a] |= novo
                    mudou = True

    def _follow(self):
        self.follow = {a: set() for a in self.nao_terminais}
        self.follow[self.inicial].add("$")
        mudou = True
        while mudou:
            mudou = False
            for a, corpo in self.prods:
                for k, s in enumerate(corpo):
                    if not self.eh_nt(s):
                        continue
                    resto = corpo[k + 1:]
                    novo = set(self.first_seq(resto))
                    if self.nullable_seq(resto):
                        novo |= self.follow[a]
                    if not novo <= self.follow[s]:
                        self.follow[s] |= novo
                        mudou = True

    def _tabela(self):
        """M[A][a] = índice da produção. Registra conflitos (não-LL(1))."""
        self.tabela = {a: {} for a in self.nao_terminais}
        self.conflitos = []              # (A, a, [prods], escolhida)
        self.predict = []                # conjunto de seleção de cada produção
        for idx, (a, corpo) in enumerate(self.prods):
            sel = set(self.first_seq(corpo))
            if self.nullable_seq(corpo):
                sel |= self.follow[a]
            self.predict.append(sel)
            for t in sel:
                if t in self.tabela[a]:
                    antiga = self.tabela[a][t]
                    # Resolução: preferir a produção NÃO vazia (casa o 'else'
                    # com o 'if' mais próximo — regra clássica do else pendente)
                    escolhida = idx if corpo else antiga
                    self.tabela[a][t] = escolhida
                    self.conflitos.append((a, t, [antiga, idx], escolhida))
                else:
                    self.tabela[a][t] = idx

    # ------------------------------------------------------------------
    def prod_str(self, idx):
        a, corpo = self.prods[idx]
        return "%s -> %s" % (a, " ".join(corpo) if corpo else EPS)

    def relatorio(self):
        L = []
        L.append("PRODUÇÕES (%d)" % len(self.prods))
        for i in range(len(self.prods)):
            L.append("  (%2d) %s" % (i + 1, self.prod_str(i)))
        L.append("")
        L.append("ANULÁVEIS: " + ", ".join(sorted(self.nullable)))
        L.append("")
        L.append("FIRST / FOLLOW")
        for a in self.nao_terminais:
            L.append("  %-13s FIRST  = { %s }" % (a, " ".join(sorted(self.first[a]))))
            L.append("  %-13s FOLLOW = { %s }" % ("", " ".join(sorted(self.follow[a]))))
        L.append("")
        L.append("TABELA PREDITIVA (conjunto de seleção de cada produção)")
        for i in range(len(self.prods)):
            L.append("  (%2d) %-38s seleciona { %s }" % (
                i + 1, self.prod_str(i), " ".join(sorted(self.predict[i]))))
        L.append("")
        if self.conflitos:
            L.append("CONFLITOS LL(1): %d" % len(self.conflitos))
            for a, t, ps, esc in self.conflitos:
                L.append("  M[%s, %s]: produções (%s) -> escolhida (%d) %s" % (
                    a, t, ", ".join(str(p + 1) for p in ps), esc + 1, self.prod_str(esc)))
        else:
            L.append("A gramática é LL(1): nenhum conflito.")
        return "\n".join(L)
