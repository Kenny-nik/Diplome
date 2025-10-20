from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0010_alter_book_genre"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="is_premium",
            field=models.BooleanField(
                default=False,
                verbose_name="Доступно по подписке",
                help_text="Если включено — книга доступна только для подписчиков и будет приоритетно показана на главной.",
            ),
        ),
    ]
