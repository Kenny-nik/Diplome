
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0006_remove_book_preview_text_alter_book_cover_url_and_more"),
    ]

    operations = [

        migrations.RunSQL(
            "ALTER TABLE books DROP CONSTRAINT IF EXISTS books_slug_key;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP INDEX IF EXISTS books_slug_30be353b_like;",
            reverse_sql=migrations.RunSQL.noop,
        ),


        migrations.AddField(
            model_name="book",
            name="slug",
            field=models.SlugField(
                verbose_name="Слаг",
                max_length=255,
                unique=False,
                blank=True,
                null=True,
            ),
        ),


        migrations.AddField(
            model_name="book",
            name="cover_image",
            field=models.ImageField(
                verbose_name="Файл обложки",
                upload_to="covers/",
                null=True,
                blank=True,
            ),
        ),
    ]
