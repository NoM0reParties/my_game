# Generated by Django 3.2.7 on 2021-11-12 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0019_auto_20211112_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizgame',
            name='room_name',
            field=models.CharField(default='7thxcza1lfv5237o2j2sbumvwh40qn', max_length=32),
        ),
    ]