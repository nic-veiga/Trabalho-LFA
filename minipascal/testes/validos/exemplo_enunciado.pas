myglobalvar: real;
procedure minhafuncao(a:integer; 
b: integer);
var
 v1: integer;
begin
 if a>10 then begin
 
 myglobalvar := 50;
 if b > 20 then
begin
end; 
 end;
end;
function minhafuncao(a:integer; b: 
integer): integer;
begin
 if a>10 then begin 
 if b > 20 then
begin
end; 
 end;
 Result:=10;
end;
