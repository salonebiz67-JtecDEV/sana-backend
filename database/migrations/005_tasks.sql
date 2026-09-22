-- ============================================
-- JTECH AI
-- MIGRATION 005 — TASKS
-- ============================================

create table if not exists public.tasks (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    title text not null,

    description text,

    status text not null default 'pending'
        check (
            status in (
                'pending',
                'in_progress',
                'completed',
                'cancelled'
            )
        ),

    priority text not null default 'normal'
        check (
            priority in (
                'low',
                'normal',
                'high',
                'urgent'
            )
        ),

    due_at timestamptz,

    completed_at timestamptz,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================
-- INDEXES
-- ============================================

create index if not exists tasks_user_id_idx
on public.tasks(user_id);

create index if not exists tasks_status_idx
on public.tasks(status);

create index if not exists tasks_due_at_idx
on public.tasks(due_at);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.tasks
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own tasks"
on public.tasks
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own tasks"
on public.tasks
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own tasks"
on public.tasks
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own tasks"
on public.tasks
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.tasks
to authenticated;
