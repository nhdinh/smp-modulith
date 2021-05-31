create table product
(
    product_id           uuid         not null
        constraint product_pkey
            primary key,
    reference            varchar(100) not null
        constraint product_reference_key
            unique,
    display_name         varchar(255) not null,
    collection_reference varchar(200),
    brand_reference      varchar(100)
        constraint product_brand_reference_fkey
            references brand
            on delete set null,
    created_at           timestamp default now(),
    last_updated         timestamp
);

alter table product
    owner to postgres;

INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('5bf6b672-4bbb-4357-9a66-972e01880472', 'banh-chung', 'Bánh chưng', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:00:52.721637', '2021-05-29 04:01:01.967117');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('d018d526-771b-4e2b-88b9-a616ef043166', 'banh-chung-dong-hop', 'Bánh chưng đóng hộp', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:01:54.916663', '2021-05-29 04:02:08.815933');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('f9cc1406-45b4-42e1-bf08-dbc4e1a8c8f7', 'banh-tet', 'Bánh tét', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:05:28.918065', '2021-05-29 04:05:33.828462');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('9f8bf94f-a245-4ab4-868b-29610c10e790', 'banh-troi', 'Bánh trôi', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:06:03.958420', '2021-05-29 04:06:03.947186');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('09938bce-ebc7-4394-b046-224c4ac9a1d4', 'banh-gi-do', 'Bánh gì đó', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:08:27.698126', '2021-05-29 04:08:27.750450');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('b9d71ee6-746d-4822-8a95-576c4c404459', 'banh-deo-gi-day', 'Banh deo gi day', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:08:50.778738', '2021-05-29 04:08:50.782120');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('785e1820-847c-4bec-8d82-24215e618860', 'hello-banh-nabati', 'Hello banh Nabati', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:10:32.361657', '2021-05-29 04:10:32.352736');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('dc5876d9-ef7a-4589-a7c4-616b8f2f6734', 'hello-kitty', 'Hello Kitty', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:10:58.378868', '2021-05-29 04:10:58.373791');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('cd15c966-c149-4811-b72e-8bc70bb844a7', 'banh-cong', 'Bánh cống', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:12:42.485810', '2021-05-29 04:12:42.499232');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('e0e1e7c0-758a-4933-ad80-db4c04b0908d', 'banh-xiaolin', 'Banh xiaolin', 'default_catalog#default_collection', 'default_brand', '2021-05-28 21:39:11.117264', '2021-05-29 04:39:11.149466');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('56bf2ddf-0dd1-4fb1-9dea-beb7f9df8211', 'ten-gia', 'Tên gia', 'default_catalog#default_collection', 'default_brand', '2021-05-30 04:16:11.219650', '2021-05-30 11:16:11.225438');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('fde557fc-1156-4dd1-8454-540b741356ef', 'diem-thong-nhat', 'Diêm Thống Nhất', 'default_catalog#default_collection', 'thong-nhat', '2021-05-28 14:04:42.334649', '2021-06-01 02:30:27.962652');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('33aef817-595a-4c9d-9576-38a0cb8c8758', 'phich-nuoc-rang-dong', 'Phích nước Rạng Đông', 'default_catalog#default_collection', 'rang-dong', '2021-05-28 14:44:00.969716', '2021-06-01 02:30:30.158294');
INSERT INTO public.product (product_id, reference, display_name, collection_reference, brand_reference, created_at, last_updated) VALUES ('826001b8-0ff0-4516-9636-95bf7e337d9b', 'sua-dinh-duong-vinamilk-co-duong-bich-220ml', 'SỮA DINH DƯỠNG VINAMILK CÓ ĐƯỜNG - BỊCH 220ML', 'default_catalog#default_collection', 'vinamilk', '2021-05-28 21:52:26.653582', '2021-06-01 02:30:32.227800');