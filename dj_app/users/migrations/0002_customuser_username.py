# Generated by Django 3.2.7 on 2021-10-02 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default='fedorka', max_length=32, unique=True),
            preserve_default=False,
        ),
    ]
