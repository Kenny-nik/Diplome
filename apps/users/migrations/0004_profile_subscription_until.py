from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_profile_avatar_alter_profile_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="subscription_until",
            field=models.DateField(null=True, blank=True, verbose_name="Подписка действует до"),
        ),
    ]
