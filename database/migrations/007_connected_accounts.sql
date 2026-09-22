-- ============================================
-- JTECH AI
-- MIGRATION 007 — CONNECTED ACCOUNTS
-- ============================================

create table if not exists public.connected_accounts (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    provider text not null,

    provider_user_id text,

    account_email text,

    access_token text,

    refresh_token text,

    token_expires_at timestamptz,

    scopes text[],

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now(),

    unique (user_id, provider)
);


-- ============================================
-- INDEXES
-- ============================================

create index if not exists connected_accounts_user_id_idx
on public.connected_accounts(user_id);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.connected_accounts
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own connected accounts"
on public.connected_accounts
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own connected accounts"
on public.connected_accounts
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own connected accounts"
on public.connected_accounts
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own connected accounts"
on public.connected_accounts
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.connected_accounts
to authenticated;
