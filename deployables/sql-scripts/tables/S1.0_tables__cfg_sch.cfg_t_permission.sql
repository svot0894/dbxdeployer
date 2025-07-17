-- table DDL
create table if not exists abch_certio_dwh_{{env}}.cfg_sch.cfg_t_permissions (
    id bigint primary key,
    object_type varchar(255) not null,      -- e.g., 'catalog', 'schema', 'table', 'job'
    object_name varchar(255) not null,
    principal_type varchar(255) not null,   -- e.g., 'user', 'group', 'service_principal'
    principal_name varchar(255) not null,
    permission_type varchar(255) not null,  -- e.g., 'usage', 'select', 'can_manage'
    operation varchar(255) not null,        -- e.g., 'grant', 'revoke'
    status varchar(50) not null,            -- e.g., 'completed', 'pending'
    inserted_datetime timestamp
);