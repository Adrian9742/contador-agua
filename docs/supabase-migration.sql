-- ============================================================
-- Migration: Setup Contador de Água no Supabase
-- Execute no SQL Editor do seu projeto Supabase
-- ============================================================

-- 1. Tabela de perfis (extends auth.users)
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  email        text,
  goal_ml      integer not null default 2000,
  interval_min integer not null default 30,
  best_streak  integer not null default 0,
  created_at   timestamptz default now()
);

-- 2. Tabela de consumo diário
create table if not exists public.water_entries (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references public.profiles(id) on delete cascade not null,
  date        date not null,
  consumed_ml integer not null default 0,
  goal_ml     integer not null default 2000,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  unique(user_id, date)
);

-- 3. Trigger: cria perfil automaticamente quando usuário se cadastra
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$;

create or replace trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();

-- 4. RLS — Row Level Security
alter table public.profiles enable row level security;
alter table public.water_entries enable row level security;

-- Cada usuário só vê/editou seus próprios dados
create policy "users can view own profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "users can update own profile"
  on public.profiles for update
  using (auth.uid() = id);

create policy "users can view own entries"
  on public.water_entries for select
  using (auth.uid() = user_id);

create policy "users can insert own entries"
  on public.water_entries for insert
  with check (auth.uid() = user_id);

create policy "users can update own entries"
  on public.water_entries for update
  using (auth.uid() = user_id);
