# Generated by Django 3.2.7 on 2021-11-12 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0020_alter_quizgame_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizgame',
            name='room_name',
            field=models.CharField(default='1aeksj82tpy3lcbdy0kh8nzfq6clnr', max_length=32),
        ),
    ]
