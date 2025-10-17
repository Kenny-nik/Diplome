from django.db import migrations

SQL_ADD_ADDED_BY = r"""
DO $$
BEGIN
    -- если у таблицы books ещё нет колонки added_by_id — добавим
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'books' AND column_name = 'added_by_id'
    ) THEN
        ALTER TABLE books ADD COLUMN added_by_id integer NULL;
        -- FK на таблицу пользователя (обычно users_user)
        ALTER TABLE books
            ADD CONSTRAINT books_added_by_id_fk
            FOREIGN KEY (added_by_id) REFERENCES users_user (id)
            DEFERRABLE INITIALLY DEFERRED;
        CREATE INDEX IF NOT EXISTS books_added_by_id_idx ON books(added_by_id);
    END IF;
END;
$$;
"""

SQL_DROP_ADDED_BY = r"""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'books' AND column_name = 'added_by_id'
    ) THEN
        ALTER TABLE books DROP CONSTRAINT IF EXISTS books_added_by_id_fk;
        DROP INDEX IF EXISTS books_added_by_id_idx;
        ALTER TABLE books DROP COLUMN IF EXISTS added_by_id;
    END IF;
END;
$$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0003_add_cover_and_rating"),  # если у тебя другой номер предыдущей миграции — укажи его
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_ADD_ADDED_BY, reverse_sql=SQL_DROP_ADDED_BY),
    ]
