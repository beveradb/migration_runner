import mock
import pytest

import run_migrations as r


def test_extract_sequence_sql_filename_expected(sql_filename_expected):
    version = r.extract_sequence_num(sql_filename_expected)
    assert version == 45


def test_extract_sequence_sql_filename_hyphen(sql_filename_hyphen):
    version = r.extract_sequence_num(sql_filename_hyphen)
    assert version == 45


def test_extract_sequence_sql_filename_not_zero_padded(
        sql_filename_not_zero_padded):
    version = r.extract_sequence_num(sql_filename_not_zero_padded)
    assert version == 45


def test_extract_sequence_sql_filename_spaced(sql_filename_spaced):
    version = r.extract_sequence_num(sql_filename_spaced)
    assert version == 45


def test_extract_sequence_sql_filename_no_sql_suffix(
        sql_filename_no_sql_suffix):
    version = r.extract_sequence_num(sql_filename_no_sql_suffix)
    assert version == 45


def test_extract_sequence_sql_filename_no_separator(
        sql_filename_no_separator):
    version = r.extract_sequence_num(sql_filename_no_separator)
    assert version == 45


def test_extract_sequence_sql_filename_bigint(
        sql_filename_bigint):
    version = r.extract_sequence_num(sql_filename_bigint)
    assert version == 23514352834592347502351435283459234750


def test_extract_sequence_sql_filename_no_version(
        sql_filename_no_version):
    with pytest.raises(AttributeError):
        r.extract_sequence_num(sql_filename_no_version)


def test_append_migration_sql_filename_expected(sql_filename_expected):
    migrations = []
    r.append_migration(migrations, sql_filename_expected)
    assert migrations == [(45, sql_filename_expected)]


def test_append_migration_sql_filename_expected_existing_value(
        sql_filename_expected):
    migrations = [(2, "test.sql")]
    r.append_migration(migrations, sql_filename_expected)
    assert migrations == [(2, "test.sql"),
                          (45, sql_filename_expected)]


def test_find_migrations_expected(tmpdir, sql_filename_expected):
    filepath = tmpdir.join(sql_filename_expected)
    filepath.write("test")
    migrations = r.find_migrations(str(tmpdir))
    assert migrations == [(45, str(filepath))]


def test_find_migrations_empty(tmpdir):
    migrations = r.find_migrations(str(tmpdir))
    assert migrations == []


def test_find_migrations_no_suffix(tmpdir, sql_filename_no_sql_suffix):
    filepath = tmpdir.join(sql_filename_no_sql_suffix)
    filepath.write("test")
    migrations = r.find_migrations(str(tmpdir))
    assert migrations == []


def test_find_migrations_multiple(
        tmpdir,
        sql_filename_expected,
        sql_filename_bigint,
        sql_filename_no_sql_suffix,
        sql_filename_spaced
):
    sql_filename_expected_filepath = tmpdir.join(sql_filename_expected)
    sql_filename_expected_filepath.write("test")

    sql_filename_bigint_filepath = tmpdir.join(sql_filename_bigint)
    sql_filename_bigint_filepath.write("test")

    sql_filename_no_sql_suffix_path = tmpdir.join(sql_filename_no_sql_suffix)
    sql_filename_no_sql_suffix_path.write("test")

    sql_filename_spaced_path = tmpdir.join(sql_filename_spaced)
    sql_filename_spaced_path.write("test")

    migrations = r.find_migrations(str(tmpdir))
    assert migrations == [
        (45, str(sql_filename_expected_filepath)),
        (23514352834592347502351435283459234750,
         str(sql_filename_bigint_filepath)),
        (45, str(sql_filename_spaced_path))
    ]


def test_sort_migrations_expected(unsorted_migrations_tuples_list):
    r.sort_migrations(unsorted_migrations_tuples_list)
    assert unsorted_migrations_tuples_list == [
        (1, '/tmp/001.createtable.sql'),
        (2, '/tmp/2-createtable.sql'),
        (45, '/tmp/045.createtable.sql'),
        (60, '/tmp/60.createtable.sql'),
    ]


def test_sort_migrations_not_tuples(unsorted_migrations_non_tuple_list):
    with pytest.raises(TypeError):
        r.sort_migrations(unsorted_migrations_non_tuple_list)


def test_sort_migrations_not_versioned_tuples(
        unsorted_migrations_non_versioned_list):
    with pytest.raises(TypeError):
        r.sort_migrations(unsorted_migrations_non_versioned_list)


def test_populate_migrations_calls_find_migrations(tmpdir):
    with mock.patch('run_migrations.find_migrations') \
            as mocked_find_migrations:
        r.populate_migrations(str(tmpdir))
        mocked_find_migrations.assert_called_with(str(tmpdir))


def test_populate_migrations_calls_sort_migrations(tmpdir,
                                                   sql_filename_expected):
    sql_filename_expected_filepath = tmpdir.join(sql_filename_expected)
    sql_filename_expected_filepath.write("test")

    with mock.patch('run_migrations.sort_migrations') \
            as mocked_sort_migrations:
        r.populate_migrations(str(tmpdir))

        mocked_sort_migrations.assert_called_with(
            [(45, sql_filename_expected_filepath)]
        )


def test_connect_database_invalid_params(invalid_db_params):
    with pytest.raises(SystemExit):
        r.connect_database(invalid_db_params)


def test_connect_database_mariadb_library_called(invalid_db_params):
    with mock.patch('mysql.connector.connect') as mocked_mysql_connect:
        r.connect_database(invalid_db_params)

        host, user, password, name = invalid_db_params
        mocked_mysql_connect.assert_called_with(
            user=user,
            password=password,
            host=host,
            database=name
        )


def test_fetch_current_version_calls_connect(invalid_db_params):
    with mock.patch('mysql.connector.connect') as mocked_mysql_connect:
        r.fetch_current_version(invalid_db_params)
        mocked_mysql_connect.assert_called()
