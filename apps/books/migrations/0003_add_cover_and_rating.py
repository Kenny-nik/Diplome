from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_url',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='book',
            name='rating',
            field=models.DecimalField(max_digits=3, decimal_places=2, default=0),
        ),
    ]
