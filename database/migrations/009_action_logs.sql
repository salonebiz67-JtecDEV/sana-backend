-- SANA AI
-- Stores the outcome of actions the backend requested and the
-- Android client attempted to execute (e.g. create_timer).
-- Useful for debugging, and so Sana's memory can reflect what
-- actually happened on the device, not just what was requested.

create table if not exists public.action_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users on delete cascade not null,
  action_type text not null,
  success boolean not null,
  message text,
  data jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_action_logs_user on public.action_logs (user_id, created_at desc);

alter table public.action_logs enable row level security;

create policy "Users can view their own action logs"
  on public.action_logs for select
  using (auth.uid() = user_id);

create policy "Users can insert their own action logs"
  on public.action_logs for insert
  with check (auth.uid() = user_id);
