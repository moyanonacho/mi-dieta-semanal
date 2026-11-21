"""Aplica web-dieta/supabase/esquema.sql y carga la plantilla base en Supabase.

Uso:  .venv\\Scripts\\python.exe -I web-dieta\\herramientas\\aplicar_esquema.py <plan.json> <carpeta platos>
La contraseña de la base de datos se lee de herramientas\\.supabase-pizarro.env (nunca se sube a GitHub).
"""
import json
import sys
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

RAIZ = Path(__file__).resolve().parents[2]
ENV = dict(l.split("=", 1) for l in (RAIZ / "herramientas" / ".supabase-pizarro.env").read_text(encoding="utf-8").splitlines() if "=" in l)
REF = ENV["SUPABASE_URL"].split("//")[1].split(".")[0]
DSN = f"host=aws-1-eu-central-1.pooler.supabase.com port=5432 dbname=postgres user=postgres.{REF} password={ENV['SUPABASE_DB_PASSWORD']} sslmode=require"


def main(plan_path: Path, platos_dir: Path):
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = plan.get("data", plan)
    plan["nombre"] = "Plan base (tabla FIT24X7)"
    platos = {}
    for f in sorted(platos_dir.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        platos[d.get("id", f.stem)] = d.get("data", d)
    sql = (RAIZ / "web-dieta" / "supabase" / "esquema.sql").read_text(encoding="utf-8")
    with psycopg.connect(DSN, autocommit=True) as cx:
        cx.execute(sql)
        cx.execute(
            "insert into public.dieta_plantillas (id, nombre, plan, platos) values ('fit24x7', %s, %s, %s) "
            "on conflict (id) do update set nombre = excluded.nombre, plan = excluded.plan, platos = excluded.platos",
            ("Tabla de alimentos base (FIT24X7)", Jsonb(plan), Jsonb(platos)))
        n = cx.execute("select count(*) from public.dieta_plantillas").fetchone()[0]
        pol = cx.execute("select count(*) from pg_policies where tablename in ('dieta_docs','dieta_plantillas')").fetchone()[0]
    print(f"OK: esquema aplicado, {n} plantilla(s), {pol} reglas de seguridad, {len(plan['alimentos'])} alimentos, {len(platos)} platos")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
