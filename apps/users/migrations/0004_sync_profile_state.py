from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_profile_avatar_alter_profile_user"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="profile",
                    name="avatar",
                    field=models.ImageField(
                        upload_to="avatars/",
                        null=True,
                        blank=True,
                        verbose_name="Аватар",
                    ),
                ),
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
            ],
        ),
    ]
