
from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Book = apps.get_model("books", "Book")

    for b in Book.objects.all():

        if not getattr(b, "slug", None):
            base = slugify(b.title or "") or f"book-{b.pk}"
            slug = base
            i = 2

            while Book.objects.filter(slug=slug).exclude(pk=b.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            b.slug = slug
            b.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0007_add_cover_image_and_slug"),
    ]

    operations = [
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="book",
            name="slug",
            field=models.SlugField(
                verbose_name="Слаг",
                max_length=255,
                unique=True,
                blank=True,
                null=False,
            ),
        ),
    ]
