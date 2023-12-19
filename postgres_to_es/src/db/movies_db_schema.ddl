CREATE SCHEMA IF NOT EXISTS content;

CREATE TYPE filmwork_type AS ENUM ('movie', 'tv_show');

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title varchar(255) NOT NULL,
    description text,
    creation_date date,
    certificate text,
    file_path text,
    rating float(1) DEFAULT 0.0 CONSTRAINT min_max_rating CHECK (rating >= 0 AND rating <= 10),
    type filmwork_type NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name varchar(255) NOT NULL,
    birth_date date,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(255),
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TYPE person_role AS ENUM ('actor', 'director', 'writer');

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    film_work_id uuid REFERENCES content.film_work(id) ON DELETE CASCADE,
    person_id uuid REFERENCES content.person(id) ON DELETE CASCADE,
    role person_role NOT NULL,
    created_at timestamp with time zone
);

CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    film_work_id uuid REFERENCES content.film_work(id) ON DELETE CASCADE,
    genre_id uuid REFERENCES content.genre(id) ON DELETE CASCADE,
    created_at timestamp with time zone
);

CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

INSERT INTO content.film_work (id, title, description, creation_date, certificate, file_path, rating, type, created_at, updated_at)
VALUES ('19d5c41c-8067-4267-b412-12a06f943391','test1','test1','2023-02-18','\N', '\N',10, 'movie', '2023-06-16 20:14:09.25447+00', '2023-06-16 20:14:09.254485+00'),
    ('ffc3df9f-a17e-4bae-b0b6-c9c4da290fdd','MegaMan',	'\N',	'1974-05-11', '\N','\N',7.1,'movie','2021-06-16 20:14:09.259084+00','2021-06-16 20:14:09.2591+00'),
    ('ffc3df9f-a17e-4bae-b0b6-c9c4da289a00','test2',	'\N',	'2023-05-11', '\N','\N',9,'movie','2023-09-16 20:14:09.259084+00','2023-06-16 20:14:09.2591+00'--),
    --('ffc3df9f-a17e-4bae-b0b6-c9c4da289a01','test3',	'\N',	'2023-05-11', '\N','\N',9,'movie','2023-09-16 20:14:09.259084+00','2023-06-16 20:14:09.2591+00'
);
INSERT INTO content.genre (id, name, description, created_at, updated_at)
VALUES ('3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff','Action','\N', '2023-06-16 20:14:09.25447+00', '2023-06-16 20:14:09.254485+00'),
('120a21cf-9097-479e-904a-13dd7198c1dd', 'Adventure',	'\N'	,'2021-06-16 20:14:09.309818+00','2021-06-16 20:14:09.309836+00'),
('3d8d9bf5-0d90-4353-88ba-4ccc5d556633','comedy','\N', '2022-06-16 20:14:09.25447+00', '2022-08-18 20:14:09.254485+00'--),
  --  ('3d8d9bf5-0d90-4353-88ba-4ccc5d556634','comedy','\N', '2022-03-13 20:14:09.25447+00', '2022-08-18 20:14:09.254485+00'
);
INSERT INTO content.genre_film_work (id, film_work_id, genre_id, created_at)
VALUES ('d1684d62-58c1-4784-914b-9028dcc67955','045f2518-5c38-48df-9c48-639520ab57af','237fd1e4-c98e-454e-aa13-8a13fb7547b5','2023-06-17 20:14:09.579988+00'),
('1c0efc19-1545-4184-ac38-2d4a71be46fa',	'0fcfe6c1-8b9e-444c-b458-2787af80533c',	'3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',	'2023-09-26 20:14:09.580056+00'),
('1c0efc19-1545-4184-ac38-2d4a71b77777',	'0fcfe6c1-8b9e-444c-b458-2787af855555',	'3d8d9bf5-0d90-4353-88ba-4ccc5d2c0000',	'2023-11-22 20:14:09.580056+00'--),
--('1c0efc19-1545-4184-ac38-2d4a71b77775',	'0fcfe6c1-8b9e-444c-b458-2787af855545',	'3d8d9bf5-0d90-4353-88ba-4ccc5d2c0040',	'2023-10-22 20:14:09.580056+00'
);

INSERT INTO  content.person (id, full_name, birth_date, created_at, updated_at)
VALUES ('040f3e5e-0f58-44b1-9f95-f8f88a43c934','Elena Fabri',	'1987-04-09','2021-06-16 20:14:09.440713+00',	'2021-06-16 20:14:09.440729+00'),
('0031feab-8f53-412a-8f53-47098a60ac73',	'John Sayles',	'2009-01-13','2021-06-16 20:14:09.320604+00','2021-06-16 20:14:09.320625+00'),
('0031feab-8f53-412a-8f53-47098a611111',	'John yyyy',	'2005-06-12','2022-03-16 20:14:09.320604+00','2022-09-18 20:14:09.320625+00' -- ),
--('0031feab-8f53-412a-8f53-47098a611331',	'xxx yyyy',	'2005-07-12','2022-03-16 20:14:09.320604+00','2022-09-18 20:14:09.320625+00'
);



INSERT INTO content.person_film_work (id, film_work_id, person_id, role, created_at)
VALUES ('2dba43a5-7e55-4bc8-993f-51c4d208bc8c','045f2518-5c38-48df-9c48-639520ab57af','232fd5ab-166f-47e4-afe1-28d3450721d5','director','2021-06-16 20:14:09.702729+00'),
('6852da17-aa75-4df9-aa5e-545055eab043','0fcfe6c1-8b9e-444c-b458-2787af80533c','038267d1-6ac4-4ca6-81dc-bab21466269b','writer','2021-06-16 20:14:09.702795+00'),
('6852da17-aa75-4df9-aa5e-545055eab555','0fcfe6c1-8b9e-444c-b458-2787af855555','038267d1-6ac4-4ca6-81dc-bab21466bbbb','writer','2019-05-15 20:14:09.702795+00'--),
--('6852da17-aa75-4df9-aa5e-545055eaccc5','0fcfe6c1-8b9e-444c-b458-2787af855545','038267d1-6ac4-4ca6-81dc-bab21466b22b','writer','2019-05-15 20:14:09.702795+00'
);