-- Mi Dieta Semanal (web independiente): cada usuario solo ve y cambia SUS datos.
-- Comparte el proyecto de Supabase con la lista de la compra de los Pizarro, pero con tablas propias.

-- Datos de cada usuario: plan, perfil, platos, semanas... (imitan los documentos de la app de Claude)
create table if not exists public.dieta_docs (
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  col text not null,
  id text not null,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id, col, id)
);
alter table public.dieta_docs enable row level security;
alter table public.dieta_docs replica identity full;

drop policy if exists "cada usuario lo suyo" on public.dieta_docs;
create policy "cada usuario lo suyo" on public.dieta_docs for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

do $$ begin
  alter publication supabase_realtime add table public.dieta_docs;
exception when duplicate_object then null; end $$;

-- Plantillas para empezar (tabla de alimentos base y platos de ejemplo): todos las leen, nadie las cambia desde la web
create table if not exists public.dieta_plantillas (
  id text primary key,
  nombre text not null,
  plan jsonb not null,
  platos jsonb not null default '{}'::jsonb
);
alter table public.dieta_plantillas enable row level security;
drop policy if exists "todos leen plantillas" on public.dieta_plantillas;
create policy "todos leen plantillas" on public.dieta_plantillas for select to authenticated using (true);

-- Fotos de platos: carpeta pública con nombres aleatorios; cada usuario sube y borra solo en su subcarpeta <user_id>/
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('dieta-fotos', 'dieta-fotos', true, 5242880, array['image/jpeg','image/png','image/webp'])
on conflict (id) do update set public = true, file_size_limit = 5242880;

drop policy if exists "dieta sube sus fotos" on storage.objects;
create policy "dieta sube sus fotos" on storage.objects for insert to authenticated
  with check (bucket_id = 'dieta-fotos' and (storage.foldername(name))[1] = auth.uid()::text);
drop policy if exists "dieta borra sus fotos" on storage.objects;
create policy "dieta borra sus fotos" on storage.objects for delete to authenticated
  using (bucket_id = 'dieta-fotos' and (storage.foldername(name))[1] = auth.uid()::text);
