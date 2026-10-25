# TVHisenseSala

Experiências para dar um menu de apps estilo Android TV a uma Hisense A6100 (VIDAA U2.5) através da porta de debug do launcher.

- `NOTAS.md` — o que se descobriu, o que funciona e o que correu mal. Ler primeiro.
- `scripts/` — scripts Python para correr no Termux (telemóvel na mesma rede da TV). Precisam de `pip install websocket-client`.
- `pagina/index.html` — página-início simples para o browser da TV.

Segurança: a porta 9223 da TV não tem autenticação. Tudo o que se injeta fica em memória e desaparece num reinício; `scripts/off.py` repõe as teclas e remove o menu.
