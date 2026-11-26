# -*- coding: utf-8 -*-
"""Roda todos os arquivos de testes/validos (devem ser ACEITOS) e testes/invalidos (REJEITADOS)."""
import glob, io, os, sys, contextlib
import main

base = os.path.dirname(os.path.abspath(__file__))
falhas = 0
for pasta, esperado in (("validos", 0), ("invalidos", 1)):
    for arq in sorted(glob.glob(os.path.join(base, "testes", pasta, "*.pas"))):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cod = main.main([arq])
        saida = buf.getvalue().strip().splitlines()
        detalhe = [l for l in saida if "ERRO" in l]
        ok = cod == esperado
        falhas += not ok
        print("[%s] %-9s %-32s %s" % ("OK " if ok else "FALHA", pasta, os.path.basename(arq),
                                      (detalhe[0].split(": ",1)[1] if detalhe else "aceito")))
print("\n%s" % ("Todos os testes passaram." if not falhas else "%d teste(s) com falha." % falhas))
sys.exit(1 if falhas else 0)
