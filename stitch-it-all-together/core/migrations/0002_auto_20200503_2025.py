# Generated by Django 3.0.5 on 2020-05-03 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statuschangehistory',
            name='status',
            field=models.IntegerField(choices=[(0, 'Enabled'), (1, 'Deleted'), (2, 'Suspended'), (3, 'Archived')], db_index=True, help_text='The status changed to this value'),
        ),
    ]
