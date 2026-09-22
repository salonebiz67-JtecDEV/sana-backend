-- ============================================
-- JTECH AI
-- MIGRATION 008 — USER PERMISSIONS
-- ============================================

create table if not exists public.user_permissions (
    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    permission text not null,

    enabled boolean not null default false,

    updated_at timestamptz not null default now(),

    primary key (user_id, permission)
);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.user_permissions
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own permissions"
on public.user_permissions
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own permissions"
on public.user_permissions
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own permissions"
on public.user_permissions
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own permissions"
on public.user_permissions
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.user_permissions
to authenticated;
