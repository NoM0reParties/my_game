# Generated by Django 3.2.7 on 2021-11-12 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0025_alter_quizgame_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizgame',
            name='room_name',
            field=models.CharField(default='qdl9ya7pw9oeamcuamf72osdqztjre', max_length=32),
        ),
    ]
