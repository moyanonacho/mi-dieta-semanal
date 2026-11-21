"""Copia los datos de la app de Claude (exportados en datos-dieta-claude/) a la cuenta de la web de un usuario.

Uso:  .venv\\Scripts\\python.exe -I herramientas\\migrar_datos_dieta.py <email de la cuenta>
- La cuenta debe existir ya (la persona se registra primero en la web).
- Sustituye plan, perfil, enlaces de Mercadona, platos y semanas de ESA cuenta por los exportados.
"""
import json
import sys
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "datos-dieta-claude"
ENV = dict(l.split("=", 1) for l in (RAIZ / "herramientas" / ".supabase-pizarro.env").read_text(encoding="utf-8").splitlines() if "=" in l)
REF = ENV["SUPABASE_URL"].split("//")[1].split(".")[0]
DSN = f"host=aws-1-eu-central-1.pooler.supabase.com port=5432 dbname=postgres user=postgres.{REF} password={ENV['SUPABASE_DB_PASSWORD']} sslmode=require"


def main(email: str):
    rows = []
    for colpath in sorted(p for p in SRC.iterdir() if p.is_dir()):
        for f in sorted(colpath.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            rows.append((colpath.name, f.stem, d.get("data", d) if set(d) <= {"id", "data", "version", "updatedAt"} else d))
    with psycopg.connect(DSN) as cx:
        r = cx.execute("select id from auth.users where lower(email) = lower(%s)", (email,)).fetchone()
        if not r:
            sys.exit(f"No existe ninguna cuenta con {email}: que se registre primero en la web.")
        uid = r[0]
        for col, id_, data in rows:
            cx.execute("insert into public.dieta_docs (user_id, col, id, data) values (%s,%s,%s,%s) "
                       "on conflict (user_id, col, id) do update set data = excluded.data, updated_at = now()",
                       (uid, col, id_, Jsonb(data)))
        cx.commit()
    print(f"OK: {len(rows)} documentos copiados a {email}: " + ", ".join(sorted({c for c, _, _ in rows})))


if __name__ == "__main__":
    main(sys.argv[1])
