# -*- coding: utf-8 -*-
"""
Reconhecedor de miniPascal  (LFA - UDESC)

Uso:
    python main.py arquivo.pas [opções]

Opções:
    --tokens        mostra os tokens produzidos pelo analisador léxico (AFD)
    --passos [N]    mostra a simulação do autômato com pilha (todos os passos, ou os N primeiros)
    --arvore        mostra a árvore de derivação (se aceito)
    --gramatica     mostra produções, FIRST, FOLLOW e tabela preditiva (não precisa de arquivo)
Código de saída: 0 = linguagem reconhecida, 1 = rejeitada, 2 = erro de uso.
"""
import sys
from lexer import tokenizar, ErroLexico
from gramatica import Gramatica
from reconhecedor import reconhecer, imprimir_passos, imprimir_arvore


def ler(caminho):
    with open(caminho, "rb") as f:
        dados = f.read()
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("latin-1")


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    g = Gramatica()

    if "--gramatica" in argv:
        print(g.relatorio())
        return 0

    args = [a for a in argv if not a.startswith("--")]
    mostrar_passos = "--passos" in argv
    limite = None
    if mostrar_passos:
        k = argv.index("--passos")
        if k + 1 < len(argv) and argv[k + 1].isdigit():
            limite = int(argv[k + 1])
            args = [a for a in args if a != argv[k + 1]]
    if len(args) != 1:
        print(__doc__)
        return 2
    caminho = args[0]

    try:
        texto = ler(caminho)
    except OSError as e:
        print("Não foi possível abrir %s: %s" % (caminho, e))
        return 2

    # ---- 1) análise léxica -------------------------------------------------
    try:
        tokens = tokenizar(texto)
    except ErroLexico as e:
        print("%s:%d:%d: ERRO LÉXICO: %s" % (caminho, e.linha, e.coluna, e.msg))
        print("Resultado: REJEITADO (não pertence à linguagem miniPascal)")
        return 1

    if "--tokens" in argv:
        print("TOKENS")
        print("%-8s %-10s %s" % ("lin:col", "tipo", "lexema"))
        for t in tokens:
            print("%-8s %-10s %s" % ("%d:%d" % (t.linha, t.coluna), t.tipo, t.lexema))
        print()

    # ---- 2) análise sintática (autômato com pilha) ------------------------
    res = reconhecer(tokens, g)

    if mostrar_passos:
        print("SIMULAÇÃO DO AUTÔMATO COM PILHA")
        imprimir_passos(res.passos, sys.stdout, limite)
        print()
    if "--arvore" in argv and res.aceito:
        print("ÁRVORE DE DERIVAÇÃO")
        imprimir_arvore(res.arvore, sys.stdout)
        print()

    print("Tokens: %d | Passos do autômato: %d" % (len(tokens) - 1, len(res.passos)))
    if res.aceito:
        print("Resultado: ACEITO (a entrada pertence à linguagem miniPascal)")
        return 0
    msg, lin, col = res.erro
    print("%s:%d:%d: ERRO SINTÁTICO: %s" % (caminho, lin, col, msg))
    print("Resultado: REJEITADO (não pertence à linguagem miniPascal)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
