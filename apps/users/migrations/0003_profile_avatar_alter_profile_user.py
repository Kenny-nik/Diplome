from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def add_avatar_column_if_missing(apps, schema_editor):
    """
    На PostgreSQL добавляем колонку avatar только если её ещё нет.
    Для других БД этот хук не требуется, но он безопасен.
    """
    vendor = schema_editor.connection.vendor
    if vendor != "postgresql":
        # На SQLite/MySQL можно было бы сделать аналог, но обычно конфликта не бывает.
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'users_profile'
                      AND column_name = 'avatar'
                ) THEN
                    ALTER TABLE users_profile ADD COLUMN avatar varchar(255);
                END IF;
            END$$;
            """
        )


def drop_avatar_column_if_exists(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'users_profile'
                      AND column_name = 'avatar'
                ) THEN
                    ALTER TABLE users_profile DROP COLUMN avatar;
                END IF;
            END$$;
            """
        )


class Migration(migrations.Migration):

    # не меняй зависимости, оставь такие же, как были у тебя в этом файле
    dependencies = [
        ("users", "0002_create_roles"),  # <- если у тебя другое имя предыдущей миграции, оставь его
    ]

    operations = [
        # 1) На уровне БД: добавить колонку только если её нет
        migrations.RunPython(
            add_avatar_column_if_missing,
            reverse_code=drop_avatar_column_if_exists,
        ),
        # 2) На уровне Django state: поле avatar существует в модели
        migrations.AddField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(
                upload_to="avatars/", null=True, blank=True, verbose_name="Аватар"
            ),
        ),
        # 3) Из исходной миграции: корректируем связь с пользователем
        migrations.AlterField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
