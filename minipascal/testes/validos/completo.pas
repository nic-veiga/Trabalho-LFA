{ Programa de teste com mais recursos da linguagem }
total, contador: integer;
media: real;
ativo: boolean;

function fatorial(n: integer): integer;
var
  i, r: integer;
begin
  r := 1;
  i := 2;
  while i <= n do
  begin
    r := r * i;
    i := i + 1
  end;
  Result := r
end;

procedure imprime(x: integer; y: real);
begin
end;

procedure principal;
var
  k: integer;
begin
  // atribuições e expressões
  k := (3 + 4) * 2 - 10 div 3;
  media := 7.5 / 2;
  ativo := not (k > 5) or (k = 3) and true;
  if k >= 10 then
    total := fatorial(5)
  else
    if k <> 0 then total := -1 else total := +1;
  imprime(k, 2.5);
  imprime(fatorial(3) + 1, media);
  (* comentário
     de várias linhas *)
  BEGIN
    While ativo Do ativo := false
  END
end;
