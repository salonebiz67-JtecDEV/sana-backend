-- ============================================
-- JTECH AI
-- MIGRATION 002 — CONVERSATIONS
-- ============================================

create table if not exists public.conversations (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    title text,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.conversations
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own conversations"
on public.conversations
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own conversations"
on public.conversations
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own conversations"
on public.conversations
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own conversations"
on public.conversations
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.conversations
to authenticated;
