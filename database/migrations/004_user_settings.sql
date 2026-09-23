-- ============================================
-- SANA AI
-- MIGRATION 004 — USER SETTINGS
-- ============================================

create table if not exists public.user_settings (
    user_id uuid primary key
        references auth.users(id)
        on delete cascade,

    assistant_name text not null default 'Sana',

    voice_enabled boolean not null default true,

    voice_name text,

    response_style text not null default 'natural',

    notifications_enabled boolean not null default true,

    memory_enabled boolean not null default true,

    proactive_assistance_enabled boolean not null default true,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.user_settings
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own settings"
on public.user_settings
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own settings"
on public.user_settings
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own settings"
on public.user_settings
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own settings"
on public.user_settings
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.user_settings
to authenticated;
