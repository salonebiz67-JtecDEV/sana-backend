-- ============================================
-- JTECH AI
-- MIGRATION 003 — MESSAGES
-- ============================================

create table if not exists public.messages (
    id uuid primary key default gen_random_uuid(),

    conversation_id uuid not null
        references public.conversations(id)
        on delete cascade,

    user_id uuid not null
        references auth.users(id)
        on delete cascade,

    role text not null
        check (role in ('user', 'assistant', 'system')),

    content text not null,

    created_at timestamptz not null default now()
);


-- ============================================
-- INDEXES
-- ============================================

create index if not exists messages_conversation_id_idx
on public.messages(conversation_id);

create index if not exists messages_user_id_idx
on public.messages(user_id);

create index if not exists messages_created_at_idx
on public.messages(created_at);


-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

alter table public.messages
enable row level security;


-- ============================================
-- POLICIES
-- ============================================

create policy "Users can view their own messages"
on public.messages
for select
to authenticated
using (auth.uid() = user_id);


create policy "Users can create their own messages"
on public.messages
for insert
to authenticated
with check (auth.uid() = user_id);


create policy "Users can delete their own messages"
on public.messages
for delete
to authenticated
using (auth.uid() = user_id);


-- ============================================
-- PERMISSIONS
-- ============================================

grant select, insert, delete
on public.messages
to authenticated;
