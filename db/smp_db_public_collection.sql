create table collection
(
    reference         varchar(200) not null,
    display_name      varchar(255) not null,
    catalog_reference varchar(100) not null
        constraint collection_catalog_reference_fkey
            references catalog,
    "default"         boolean   default false,
    disabled          boolean   default false,
    created_at        timestamp default now(),
    last_updated      timestamp,
    constraint collection_pk
        primary key (reference, catalog_reference)
);

alter table collection
    owner to postgres;

INSERT INTO public.collection (reference, display_name, catalog_reference, "default", disabled, created_at, last_updated) VALUES ('default_catalog#default_collection', 'Default Collection', 'default_catalog', true, false, '2021-05-28 21:00:52.721637', null);