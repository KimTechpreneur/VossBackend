from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0003_transfercomment'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfer',
            name='escalated_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='escalated_transfers',
                to='users.user'
            ),
        ),
    ] 