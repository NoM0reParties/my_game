# Generated by Django 3.2.7 on 2021-11-12 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0021_alter_quizgame_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizgame',
            name='room_name',
            field=models.CharField(default='os232jyfpdnu6z5xwbje87adktghg8', max_length=32),
        ),
    ]
