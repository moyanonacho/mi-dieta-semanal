"""Pone una foto a uno o varios platos de la cuenta de un usuario de la web Mi Dieta Semanal.

Uso:  .venv\\Scripts\\python.exe -I herramientas\\foto_plato_dieta.py <email> <imagen> <id de plato> [<id de plato> ...]
La foto se guarda en la carpeta privada del usuario (dieta-fotos/<user_id>/) y solo afecta a su cuenta.
"""
import io
import sys
import uuid
from pathlib import Path

import psycopg
import requests
from PIL import Image
from psycopg.types.json import Jsonb

RAIZ = Path(__file__).resolve().parent.parent
E = dict(l.split("=", 1) for l in (RAIZ / "herramientas" / ".supabase-pizarro.env").read_text(encoding="utf-8").splitlines() if "=" in l)
SB, SEC = E["SUPABASE_URL"], E["SUPABASE_SECRET"]
REF = SB.split("//")[1].split(".")[0]
DSN = f"host=aws-1-eu-central-1.pooler.supabase.com port=5432 dbname=postgres user=postgres.{REF} password={E['SUPABASE_DB_PASSWORD']} sslmode=require"


def main(email, img, ids):
    with psycopg.connect(DSN) as cx:
        r = cx.execute("select id from auth.users where lower(email) = lower(%s)", (email,)).fetchone()
        if not r:
            sys.exit(f"No hay cuenta con {email}")
        uid = r[0]
        im = Image.open(img).convert("RGB")
        im.thumbnail((900, 900))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88)
        path = f"{uid}/{uuid.uuid4().hex}.jpg"
        requests.post(f"{SB}/storage/v1/object/dieta-fotos/{path}", timeout=60, data=buf.getvalue(),
                      headers={"apikey": SEC, "Authorization": "Bearer " + SEC, "Content-Type": "image/jpeg"}).raise_for_status()
        for pid in ids:
            row = cx.execute("select data from public.dieta_docs where user_id=%s and col='platos' and id=%s", (uid, pid)).fetchone()
            if not row:
                sys.exit(f"No existe el plato {pid}")
            d = row[0]
            d["foto"] = path
            d.pop("credito", None)
            d.pop("fuente", None)
            cx.execute("update public.dieta_docs set data=%s, updated_at=now() where user_id=%s and col='platos' and id=%s", (Jsonb(d), uid, pid))
            print("foto puesta:", d["nombre"])
        cx.commit()
    print("comprobación:", requests.get(f"{SB}/storage/v1/object/public/dieta-fotos/{path}", timeout=30).status_code)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
