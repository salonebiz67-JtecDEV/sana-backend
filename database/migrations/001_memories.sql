-- ============================================
-- SANA AI
-- MIGRATION 001 — MEMORIES
-- ============================================

create table if not exists public.memories (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    category text not null,

    content text not null,

    importance integer not null default 5
        check (importance >= 1 and importance <= 10),

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.memories
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own memories"
on public.memories
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own memories"
on public.memories
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own memories"
on public.memories
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own memories"
on public.memories
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.memories
to authenticated;
