# -*- coding: utf-8 -*-
"""
Reconhecedor preditivo LL(1) dirigido por tabela.

Equivale a um autômato com pilha (AP) que lê a entrada da esquerda para a
direita e usa a pilha para guardar o que ainda falta casar:

    topo = terminal       -> compara com o token atual; se igual, desempilha e avança (CASAR)
    topo = não-terminal A -> consulta M[A, token]; desempilha A e empilha o corpo
                             da produção, de trás para frente (EXPANDIR)
    topo = $ e entrada $  -> ACEITA
    qualquer outra coisa  -> ERRO

Durante o processo guarda cada passo (para a tabela de simulação) e constrói a
árvore de derivação.
"""
from collections import namedtuple
from gramatica import EPS

Passo = namedtuple("Passo", "n pilha entrada acao")


class No:
    __slots__ = ("simbolo", "filhos", "lexema")

    def __init__(self, simbolo):
        self.simbolo, self.filhos, self.lexema = simbolo, [], None


class Resultado:
    def __init__(self):
        self.aceito = False
        self.erro = None          # (mensagem, linha, coluna)
        self.passos = []
        self.arvore = None


def _fmt_pilha(pilha, limite=14):
    simbolos = [s for s, _ in reversed(pilha)]        # topo à esquerda
    txt = " ".join(simbolos[:limite])
    return txt + (" …" if len(simbolos) > limite else "")


def _fmt_entrada(tokens, pos, limite=5):
    lex = [t.lexema for t in tokens[pos:pos + limite]]
    return " ".join(lex) + (" …" if pos + limite < len(tokens) else "")


def reconhecer(tokens, g):
    res = Resultado()
    raiz = No(g.inicial)
    res.arvore = raiz
    pilha = [("$", No("$")), (g.inicial, raiz)]       # topo = fim da lista
    pos, n = 0, 0

    def registrar(acao):
        nonlocal n
        n += 1
        res.passos.append(Passo(n, _fmt_pilha(pilha), _fmt_entrada(tokens, pos), acao))

    while True:
        topo, no = pilha[-1]
        tok = tokens[pos]
        a = tok.tipo

        if topo == "$":
            if a == "$":
                registrar("ACEITAR")
                res.aceito = True
            else:
                registrar("ERRO")
                res.erro = ("esperado fim do programa, encontrado %r" % tok.lexema,
                            tok.linha, tok.coluna)
            return res

        if not g.eh_nt(topo):                          # terminal no topo
            if topo == a:
                registrar("casar '%s'" % tok.lexema)
                no.lexema = tok.lexema
                pilha.pop()
                pos += 1
            else:
                registrar("ERRO")
                res.erro = ("esperado '%s', encontrado %s" % (
                    topo, "fim do arquivo" if a == "$" else "'%s'" % tok.lexema),
                    tok.linha, tok.coluna)
                return res
            continue

        idx = g.tabela[topo].get(a)                    # não-terminal no topo
        if idx is None:
            registrar("ERRO")
            esperados = sorted(g.tabela[topo])
            res.erro = ("em %s: encontrado %s; esperado um de: %s" % (
                topo, "fim do arquivo" if a == "$" else "'%s'" % tok.lexema,
                " ".join(esperados)), tok.linha, tok.coluna)
            return res

        _, corpo = g.prods[idx]
        registrar("expandir (%d) %s" % (idx + 1, g.prod_str(idx)))
        pilha.pop()
        filhos = [No(s) for s in corpo] if corpo else [No(EPS)]
        no.filhos = filhos
        for s, f in reversed(list(zip(corpo, filhos))):
            pilha.append((s, f))


def imprimir_passos(passos, out, ate=None):
    w1 = max(len(p.pilha) for p in passos) if passos else 10
    print("%5s | %-*s | %-32s | %s" % ("passo", w1, "pilha (topo à esquerda)", "entrada", "ação"), file=out)
    print("-" * (w1 + 60), file=out)
    for p in passos[:ate]:
        print("%5d | %-*s | %-32s | %s" % (p.n, w1, p.pilha, p.entrada, p.acao), file=out)
    if ate and len(passos) > ate:
        print("  ... (%d passos omitidos)" % (len(passos) - ate), file=out)


def imprimir_arvore(no, out, prefixo="", ultimo=True, raiz=True):
    rotulo = no.simbolo + (("  «%s»" % no.lexema) if no.lexema is not None else "")
    if raiz:
        print(rotulo, file=out)
        filho_pref = ""
    else:
        print(prefixo + ("└── " if ultimo else "├── ") + rotulo, file=out)
        filho_pref = prefixo + ("    " if ultimo else "│   ")
    for i, f in enumerate(no.filhos):
        imprimir_arvore(f, out, filho_pref, i == len(no.filhos) - 1, False)
