from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationhistoryitem',
            name='object_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='notificationhistoryitem',
            name='object_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ] 