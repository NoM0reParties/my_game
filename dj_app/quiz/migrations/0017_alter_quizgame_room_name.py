# Generated by Django 3.2.7 on 2021-11-11 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0016_alter_quizgame_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizgame',
            name='room_name',
            field=models.CharField(default='7sa5cg3wqnbi7jgt0a9uc240bzoxkq', max_length=32),
        ),
    ]
