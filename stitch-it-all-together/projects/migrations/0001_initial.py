# Generated by Django 3.0.5 on 2020-05-01 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stitchers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, default='')),
                ('type', models.SmallIntegerField(choices=[(1, 'Music'), (2, 'Lyrics'), (3, 'Joke'), (4, 'Story')], default=1)),
                ('max_stitches', models.PositiveSmallIntegerField(default=None, null=True)),
                ('is_private', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='stitchers.Stitcher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
