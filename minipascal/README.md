# Reconhecedor de miniPascal — Trabalho Final de LFA (UDESC)

Programa em **Python 3** (sem dependências externas) que decide se um arquivo `.pas`
pertence à linguagem miniPascal, mostrando os passos do algoritmo.

## Como rodar
```
python main.py testes/validos/teste.pas                  # só o veredito
python main.py testes/validos/pequeno.pas --tokens       # tokens (saída do AFD)
python main.py testes/validos/pequeno.pas --passos       # simulação do autômato com pilha
python main.py testes/validos/pequeno.pas --passos 20    # só os 20 primeiros passos
python main.py testes/validos/pequeno.pas --arvore       # árvore de derivação
python main.py --gramatica                               # produções, FIRST, FOLLOW, tabela
python rodar_testes.py                                   # roda todos os testes
```
Código de saída: `0` aceito, `1` rejeitado.

## Arquivos
| Arquivo | Função |
|---|---|
| `lexer.py` | Analisador léxico: AFD escrito à mão (maior casamento, como o flex) |
| `gramatica.py` | Gramática LL(1), NULLABLE/FIRST/FOLLOW e tabela preditiva |
| `reconhecedor.py` | Autômato com pilha dirigido pela tabela + árvore + log de passos |
| `main.py` | Linha de comando |
| `rodar_testes.py` | Testes automáticos (`testes/validos` aceitos, `testes/invalidos` rejeitados) |
| `saidas/` | Saídas geradas (tokens, passos, árvore, gramática) |

## Observação sobre o flex
O enunciado permite (mas não exige) o flex. Aqui o analisador léxico foi implementado
manualmente como AFD, com as mesmas regras do `pascal.l` do esqueleto fornecido
(inteiros, reais, identificadores, palavras reservadas, operadores, comentários `{...}`),
estendido para `:=`, comparações, `;`, `:`, `,`, parênteses, `(* *)` e `//`.
