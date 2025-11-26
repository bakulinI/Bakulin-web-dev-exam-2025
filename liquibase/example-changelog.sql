--changeset your.name:4
create table test (
    id int primary key auto_increment not null,
    info text
)
--rollback DROP TABLE test;
