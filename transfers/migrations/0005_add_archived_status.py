from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('transfers', '0004_add_escalated_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('in_transit', 'In Transit'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                    ('recalled', 'Recalled'),
                    ('escalated', 'Escalated'),
                    ('returned', 'Returned'),
                    ('return_approved', 'Return Approved'),
                    ('return_rejected', 'Return Rejected'),
                    ('revision_requested', 'Revision Requested'),
                    ('force_returned', 'Force Returned'),
                    ('archived', 'Archived'),
                ],
                default='draft',
                max_length=20
            ),
        ),
    ] 