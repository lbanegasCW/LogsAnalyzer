from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="processingrun",
            name="status_codes",
            field=models.CharField(default="500", max_length=200),
        ),
    ]
