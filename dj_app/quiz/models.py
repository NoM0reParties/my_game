import random
import string

from django.db import models

from users.models import CustomUser


def get_code(length):
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return code

class Section(models.Model):
    name = models.CharField(max_length=64, verbose_name='название тематической секции')
    special_color = models.CharField(max_length=10, verbose_name='цвет тематической секции')


class QuestionType(models.Model):
    name = models.CharField(max_length=16, verbose_name='название типа вопроса')


class Quiz(models.Model):
    creator = models.ForeignKey(CustomUser, verbose_name='создатель', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=64, verbose_name='название')
    section = models.ForeignKey(Section, verbose_name='тематика квиза', related_name='quiz', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)


class QuizGame(models.Model):
    name = models.CharField(max_length=64, verbose_name='название игры')
    quiz = models.ForeignKey(Quiz, verbose_name='квиз для игры', related_name='quiz_game', on_delete=models.CASCADE, null=True, blank=True)
    timer = models.BooleanField(default=False, verbose_name='игра с таймером')
    current_round = models.PositiveSmallIntegerField(default=1, verbose_name='текущий раунд')
    game_master = models.ForeignKey(CustomUser, verbose_name='ведущий', on_delete=models.CASCADE, related_name='games',
                                    null=True)
    started = models.BooleanField(default=False, verbose_name='стартовала ли игра')
    room_name = models.CharField(max_length=32, default='test')


class Participant(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='создатель', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    game = models.ForeignKey(QuizGame, related_name='participants', on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    super_bet = models.PositiveSmallIntegerField(null=True, blank=True)
    super_answer = models.CharField(max_length=128, null=True, blank=True)
    answer_attempts = models.PositiveSmallIntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)


class QuestionCategory(models.Model):
    name = models.CharField(max_length=64, verbose_name='название категории')
    round = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='текущий раунд')
    quiz = models.ForeignKey(Quiz, verbose_name='квиз', related_name='q_category', on_delete=models.CASCADE)


class Question(models.Model):
    text = models.CharField(max_length=512, verbose_name='текст вопроса')
    value = models.PositiveSmallIntegerField(verbose_name='стоимость вопроса', null=True, blank=True)
    type = models.ForeignKey(QuestionType, verbose_name='тип вопроса', on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, verbose_name='категории', related_name='questions', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='q_images/', null=True, blank=True)
    audio = models.FileField(upload_to='q_audio/', null=True, blank=True)


class InGameQuestion(models.Model):
    text = models.CharField(max_length=512, verbose_name='текст вопроса')
    value = models.PositiveSmallIntegerField(verbose_name='стоимость вопроса', null=True, blank=True)
    type = models.ForeignKey(QuestionType, verbose_name='тип вопроса', on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, verbose_name='категории', related_name='question', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='q_images/', null=True, blank=True)
    audio = models.FileField(upload_to='q_audio/', null=True, blank=True)
    fresh = models.BooleanField(default=True, verbose_name='бы ли дан ответ на вопрос')