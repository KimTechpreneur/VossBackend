# Generated manually

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_initial'),
        ('offices', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='unit',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='offices',
                to='units.unit'
            ),
        ),
    ]
