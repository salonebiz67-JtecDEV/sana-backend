-- ============================================
-- JTECH AI
-- MIGRATION 006 — REMINDERS
-- ============================================

create table if not exists public.reminders (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    title text not null,

    message text,

    remind_at timestamptz not null,

    status text not null default 'scheduled'
        check (
            status in (
                'scheduled',
                'triggered',
                'cancelled'
            )
        ),

    repeat_rule text,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================
-- INDEXES
-- ============================================

create index if not exists reminders_user_id_idx
on public.reminders(user_id);

create index if not exists reminders_remind_at_idx
on public.reminders(remind_at);

create index if not exists reminders_status_idx
on public.reminders(status);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.reminders
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own reminders"
on public.reminders
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own reminders"
on public.reminders
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can update their own reminders"
on public.reminders
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);


create policy "Users can delete their own reminders"
on public.reminders
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, update, delete
on public.reminders
to authenticated;
