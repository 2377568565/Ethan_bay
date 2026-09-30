-- 《预言的恩赐》提问区：数据库设置脚本
-- 在腾讯云开发控制台的 PostgreSQL「SQL 编辑器 / 执行 SQL」里整段粘贴、运行一次即可。
-- 重复运行也不会出错；表里已有的数据不会被删除。

-- ① 先清掉两张表上原有的权限规则（后面按提问区的需要重新建）
do $$
declare r record;
begin
  for r in select policyname, tablename from pg_policies
           where schemaname = 'public' and tablename in ('questions', 'replies') loop
    execute format('drop policy %I on public.%I', r.policyname, r.tablename);
  end loop;
end $$;

-- ② 管理员名单与身份函数
create table if not exists public.q4_admins (uid text primary key, note text default '');

create or replace function public.q4_uid() returns text
language sql stable as $$
  select coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    nullif(current_setting('request.jwt.claims', true), '')::json ->> 'sub'
  )
$$;

create or replace function public.q4_is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.q4_admins where uid = public.q4_uid())
$$;

create or replace function public.q4_whoami() returns json
language sql stable as $$
  select json_build_object('uid', public.q4_uid(), 'admin', public.q4_is_admin())
$$;

-- ③ 问题表：补上内容列
alter table public.questions alter column user_id drop default;
alter table public.questions alter column user_id type text using user_id::text;
alter table public.questions alter column user_id set default public.q4_uid();
alter table public.questions
  add column if not exists name        text    not null default '',
  add column if not exists loc         text    not null default '',
  add column if not exists body        text    not null default '',
  add column if not exists allow_reply boolean not null default true;
alter table public.questions drop constraint if exists q4_q_len;
alter table public.questions add constraint q4_q_len
  check (char_length(body) between 4 and 500 and char_length(name) between 1 and 16 and char_length(loc) <= 30);
create index if not exists q4_questions_time on public.questions (created_at desc);

-- ④ 回复表：补上内容列
alter table public.replies alter column user_id drop default;
alter table public.replies alter column user_id type text using user_id::text;
alter table public.replies alter column user_id set default public.q4_uid();
alter table public.replies
  add column if not exists question_id uuid    references public.questions (id) on delete cascade,
  add column if not exists name        text    not null default '',
  add column if not exists loc         text    not null default '',
  add column if not exists body        text    not null default '',
  add column if not exists is_admin    boolean not null default false;
alter table public.replies drop constraint if exists q4_r_len;
alter table public.replies add constraint q4_r_len
  check (question_id is not null and char_length(body) between 2 and 300 and char_length(name) between 1 and 16 and char_length(loc) <= 30);
create index if not exists q4_replies_question on public.replies (question_id);

-- ⑤ 谁能读、谁能发、谁能删
alter table public.questions enable row level security;
alter table public.replies   enable row level security;

grant select, insert, delete on public.questions, public.replies to anon;
grant execute on function public.q4_uid(), public.q4_is_admin(), public.q4_whoami() to anon;
revoke all on public.q4_admins from anon;
do $$
begin
  if exists (select 1 from pg_roles where rolname = 'authenticated') then
    grant select, insert, delete on public.questions, public.replies to authenticated;
    grant execute on function public.q4_uid(), public.q4_is_admin(), public.q4_whoami() to authenticated;
    revoke all on public.q4_admins from authenticated;
  end if;
end $$;

-- 所有人都能看
create policy q4_q_read on public.questions for select using (true);
create policy q4_r_read on public.replies   for select using (true);
-- 只能以自己的身份发
create policy q4_q_add on public.questions for insert
  with check (user_id = public.q4_uid());
create policy q4_r_add on public.replies for insert
  with check (
    user_id = public.q4_uid()
    and (is_admin = false or public.q4_is_admin())
    and exists (select 1 from public.questions q
                where q.id = question_id
                  and (q.allow_reply or q.user_id = public.q4_uid() or public.q4_is_admin()))
  );
-- 只能删自己的；管理员能删任何一条
create policy q4_q_del on public.questions for delete
  using (user_id = public.q4_uid() or public.q4_is_admin());
create policy q4_r_del on public.replies for delete
  using (user_id = public.q4_uid() or public.q4_is_admin());

-- ⑥ 让数据接口马上认出新加的列
notify pgrst, 'reload schema';

-- 以后添加管理员（把引号里换成你在提问区点“我是整理者”看到的身份码）：
-- insert into public.q4_admins (uid, note) values ('你的身份码', '整理者') on conflict do nothing;
