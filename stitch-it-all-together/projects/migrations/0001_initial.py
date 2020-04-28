# Generated by Django 3.0.5 on 2020-04-28 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stitchers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, default='')),
                ('type', models.SmallIntegerField(choices=[(1, 'Music'), (2, 'Lyrics'), (3, 'Joke'), (4, 'Story')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='stitchers.Stitcher')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]