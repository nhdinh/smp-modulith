create table catalog
(
    reference    varchar(100) not null
        constraint catalog_pkey
            primary key,
    display_name varchar(255) not null,
    disabled     boolean   default false,
    created_at   timestamp default now(),
    last_updated timestamp,
    system       boolean   default false
);

alter table catalog
    owner to postgres;

INSERT INTO public.catalog (reference, display_name, disabled, created_at, last_updated, system) VALUES ('default_catalog', 'Default Catalog', false, '2021-05-28 21:00:52.721637', '2021-05-29 04:00:52.716596', true);