import json
from typing import Coroutine

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.http import HttpRequest

from quiz.models import Section, Quiz, QuestionCategory, Question, InGameQuestion, QuizGame, Participant, QuestionType


def _get_user(request: HttpRequest) -> User:
    return request.user


def _check_user_auth(request: HttpRequest) -> bool:
    return _get_user(request).is_anonymous


async def check_user_auth(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_check_user_auth)(request)


def _get_sections() -> dict:
    return {"sections": [[section.id, section.name] for section in Section.objects.all()]}


async def get_sections() -> Coroutine:
    return await sync_to_async(_get_sections)()


def _get_quiz_list(request: HttpRequest) -> list:
    return [{"id": quiz.id, "name": quiz.title, "color": quiz.section.special_color} for quiz in
            Quiz.objects.filter(creator_id=request.user).select_related('section')]


async def get_quiz_list(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_get_quiz_list)(request)


def _get_game_quiz_list() -> list:
    return [{"id": quiz.id, "name": quiz.title, "color": quiz.section.special_color} for quiz in
            Quiz.objects.filter(creator__isnull=False, completed=True).select_related('section')]


async def get_game_quiz_list() -> Coroutine:
    return await sync_to_async(_get_game_quiz_list)()


def _get_themes(id: int) -> list:
    return [{"id": theme.id, "name": theme.name, "round": theme.round} for theme in
            QuestionCategory.objects.filter(quiz_id=id).order_by('round')]


async def get_themes(id: int) -> Coroutine:
    return await sync_to_async(_get_themes)(id)


def _get_question_list(theme_id: int) -> list:
    return [{"id": question.id, "text": question.text, "value": question.value,
             "type": question.type_id} for question in
            Question.objects.filter(category_id=theme_id).order_by('value')]


async def get_question_list(theme_id: int) -> Coroutine:
    return await sync_to_async(_get_question_list)(theme_id)


def _get_theme_round(theme_id: int) -> dict:
    return {"round": QuestionCategory.objects.get(id=theme_id).round}


async def get_theme_round(theme_id: int) -> Coroutine:
    return await sync_to_async(_get_theme_round)(theme_id)


def _get_question_detail(question_id: int) -> dict:
    question = Question.objects.get(id=question_id)
    resp = {"text": question.text, "value": question.value, "type": question.type_id}
    if question.type_id == 2:
        resp['image'] = "/api" + question.image.url if question.image else None
    elif question.type_id == 3:
        resp['audio'] = "/api" + question.audio.url if question.audio else None
    return resp


async def get_question_detail(question_id: int) -> Coroutine:
    return await sync_to_async(_get_question_detail)(question_id)


def _get_ig_question_detail(question_id: int) -> dict:
    question = InGameQuestion.objects.get(id=question_id)
    resp = {"text": question.text, "value": question.value, "type": question.type_id}
    if question.type_id == 2:
        resp['image'] = "/api" + question.image.url if question.image else None
    elif question.type_id == 3:
        resp['audio'] = "/api" + question.audio.url if question.audio else None
    return resp


async def get_ig_question_detail(question_id: int) -> Coroutine:
    return await sync_to_async(_get_ig_question_detail)(question_id)


def _quiz_cr(title: str, section: int, request: HttpRequest) -> dict:
    quiz = Quiz.objects.create(title=title, section_id=section, creator=request.user)
    return {"id": quiz.id}


async def quiz_cr(title: str, section: int, request: HttpRequest) -> Coroutine:
    return await sync_to_async(_quiz_cr)(title, section, request)


def _theme_cr(quiz: int, name: str) -> dict:
    if QuestionCategory.objects.filter(quiz_id=quiz, name=name).exists():
        return {"detail": "Such theme already exists in this quiz"}
    theme = QuestionCategory.objects.create(name=name, quiz_id=quiz)
    return {"id": theme.id}


async def theme_cr(quiz: int, name: str) -> Coroutine:
    return await sync_to_async(_theme_cr)(quiz, name)


def _question_cr(request: HttpRequest) -> dict:
    theme = QuestionCategory.objects.prefetch_related('questions').get(id=request.POST['theme'])
    values = list()
    for q in theme.questions.all():
        values.append(q.value)
    new_value = 0
    for value in range(500, 0, -100):
        if value not in values:
            new_value = value
    question = Question.objects.create(text=request.POST['text'], category_id=int(request.POST['theme']),
                                       type_id=int(request.POST['type']), value=new_value,
                                       image=request.FILES['image'] if 'image' in request.FILES else None,
                                       audio=request.FILES['audio'] if 'audio' in request.FILES else None)
    return {"id": question.id}


async def question_cr(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_question_cr)(request)


def _quiz_upd(request: HttpRequest, quiz_id: int) -> None:
    quiz = Quiz.objects.get(id=quiz_id)
    update_fields = list()
    if request.method == 'PUT':
        data = json.loads(request.body)
        if 'title' in data:
            update_fields.append('title')
            quiz.title = data['title']
        if 'section' in data:
            update_fields.append('section')
            quiz.section = Section.objects.get(id=data['section'])
        quiz.save(update_fields=update_fields)
    elif request.method == 'DELETE':
        quiz.delete()


async def quiz_upd(request: HttpRequest, quiz_id: int) -> Coroutine:
    return await sync_to_async(_quiz_upd)(request, quiz_id)


def _theme_upd(request: HttpRequest, theme_id: int) -> None:
    theme = QuestionCategory.objects.get(id=theme_id)
    update_fields = list()
    if request.method == 'PUT':
        data = json.loads(request.body)
        if 'name' in data:
            update_fields.append('name')
            theme.name = data['name']
        theme.save(update_fields=update_fields)
    elif request.method == 'DELETE':
        theme.delete()


async def theme_upd(request: HttpRequest, theme_id: int) -> Coroutine:
    return await sync_to_async(_theme_upd)(request, theme_id)


def _question_upd(request: HttpRequest, question_id: int) -> None:
    question = Question.objects.get(id=question_id)
    update_fields = list()
    if request.method == 'POST':
        print(request.POST)
        if 'text' in request.POST:
            update_fields.append('text')
            question.text = request.POST['text']
        if 'audio' in request.FILES:
            update_fields.append('audio')
            question.audio = request.FILES['audio']
        if 'type' in request.POST:
            update_fields.append('type')
            question.type_id = int(request.POST['type'])
        if 'image' in request.FILES:
            update_fields.append('image')
            question.image = request.FILES['image']
        question.save(update_fields=update_fields)
    elif request.method == 'DELETE':
        question.delete()


async def question_upd(request: HttpRequest, question_id: int) -> Coroutine:
    return await sync_to_async(_question_upd)(request, question_id)


def _round_change(data: dict) -> None:
    origin_t = QuestionCategory.objects.get(id=data['theme_id'])
    destination_t = QuestionCategory.objects.get(id=int(data['target_id']))
    value_1 = origin_t.round
    value_2 = destination_t.round
    destination_t.round = value_1
    origin_t.round = value_2
    destination_t.save(update_fields=['round'])
    origin_t.save(update_fields=['round'])


async def round_change(data: dict) -> Coroutine:
    return await sync_to_async(_round_change)(data)


def _g_quiz_cr(request: HttpRequest) -> dict:
    data = json.loads(request.body)
    prototype_quiz = Quiz.objects.prefetch_related('q_category', 'q_category__question').get(id=data['data_id'])
    new_quiz = Quiz.objects.create(title=prototype_quiz.title, section=prototype_quiz.section, completed=True)
    new_quiz_game = QuizGame.objects.create(name=data['game_name'], quiz=new_quiz, game_master=request.user)
    themes = list()
    questions = list()
    for theme in prototype_quiz.q_category.all():
        new_theme = QuestionCategory(name=theme.name, round=theme.round, quiz=new_quiz)
        themes.append(new_theme)
        for question in theme.questions.all():
            new_question = InGameQuestion(text=question.text, value=question.value, type=question.type,
                                          category=new_theme, image=question.image, audio=question.audio)
            questions.append(new_question)
    QuestionCategory.objects.bulk_create(themes)
    InGameQuestion.objects.bulk_create(questions)
    return {"id": new_quiz_game.id}


async def g_quiz_cr(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_g_quiz_cr)(request)


def _qg_players(quiz_game_id: int) -> list:
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    return [{"id": player.id, "name": player.user.username} for player in
            quiz_game.participants.all().order_by('user__username')]


async def qg_players(quiz_game_id: int) -> Coroutine:
    return await sync_to_async(_qg_players)(quiz_game_id)


def _round_arrange(data: dict) -> dict:
    theme = QuestionCategory.objects.get(id=data['theme_id'])
    if QuestionCategory.objects.filter(quiz=theme.quiz, round=data['round']).count() >= 5:
        return {"detail": "Too many themes for single round"}
    theme.round = data['round']
    theme.save(update_fields=['round'])
    return {"id": theme.id}


async def round_arrange(data: dict) -> Coroutine:
    return await sync_to_async(_round_arrange)(data)


def _value_change(data: dict) -> None:
    origin_q = Question.objects.get(id=data['origin_id'])
    destination_q = Question.objects.get(id=data['destination_id'])
    value_1 = origin_q.value
    value_2 = destination_q.value
    destination_q.value = value_1
    origin_q.value = value_2
    destination_q.save(update_fields=['value'])
    origin_q.save(update_fields=['value'])


async def value_change(data: dict) -> Coroutine:
    return await sync_to_async(_value_change)(data)


def _round_qg(quiz_game_id: int, round: int) -> dict:
    quiz_game = QuizGame.objects.prefetch_related('quiz', 'quiz__q_category', 'quiz__q_category__question').get(
        id=quiz_game_id)
    result = dict()
    for theme in quiz_game.quiz.q_category.filter(round=round):
        result[theme.name] = [{"id": q.id, "text": q.text, "value": q.value, "type": q.type_id,
                               "audio": q.audio.url if q.audio else None,
                               "image": q.image.url if q.image else None,
                               "fresh": q.fresh} for q in
                              theme.question.all().order_by('value')]
    return result


async def round_qg(quiz_game_id: int, round: int) -> Coroutine:
    return await sync_to_async(_round_qg)(quiz_game_id, round)


def _r_completed(quiz_game_id: int, round: int) -> dict:
    quiz_game = QuizGame.objects.prefetch_related('quiz', 'quiz__q_category', 'quiz__q_category__question').get(
        id=quiz_game_id)
    result = False
    for theme in quiz_game.quiz.q_category.filter(round=round):
        for q in theme.question.all():
            if q.fresh:
                result = True
                return {"alive": result}
    quiz_game.current_round += 1
    quiz_game.save(update_fields=['current_round'])
    return {"alive": result}


async def r_completed(quiz_game_id: int, round: int) -> Coroutine:
    return await sync_to_async(_r_completed)(quiz_game_id, round)


def _corr_ans(data: dict) -> None:
    player = Participant.objects.get(user_id=data['player_id'], active=True)
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score += points
    player.answer_attempts += 1
    player.correct_answers += 1
    question.fresh = False
    player.save(update_fields=['score', 'answer_attempts', 'correct_answers'])
    question.save(update_fields=['fresh'])


async def corr_ans(data: dict) -> Coroutine:
    return await sync_to_async(_corr_ans)(data)


def _wrong_ans(data: dict) -> None:
    player = Participant.objects.get(user_id=data['player_id'], active=True)
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score -= points
    player.answer_attempts += 1
    player.save(update_fields=['score', 'answer_attempts'])


async def wrong_ans(data: dict) -> Coroutine:
    return await sync_to_async(_wrong_ans)(data)


def _super_corr_ans(data: dict) -> None:
    player = Participant.objects.get(id=data['player_id'], active=True)
    player.score += player.super_bet
    player.answer_attempts += 1
    player.correct_answers += 1
    player.save(update_fields=['score', 'answer_attempts', 'correct_answers'])


async def super_corr_ans(data: dict) -> Coroutine:
    return await sync_to_async(_super_corr_ans)(data)


def _super_wrong_ans(data: dict) -> None:
    player = Participant.objects.get(id=data['player_id'], active=True)
    player.score -= player.super_bet
    player.answer_attempts += 1
    player.save(update_fields=['score', 'answer_attempts'])


async def super_wrong_ans(data: dict) -> Coroutine:
    return await sync_to_async(_super_wrong_ans)(data)


def _game_start(data: dict) -> None:
    game = QuizGame.objects.get(id=data['game_id'])
    game.started = True
    game.save(update_fields=['started'])


async def game_start(data: dict) -> Coroutine:
    return await sync_to_async(_game_start)(data)


def _score_pl(request: HttpRequest) -> dict:
    quiz_game_id = request.GET.get('quiz_game_id')
    game = QuizGame.objects.get(id=quiz_game_id)
    participant = Participant.objects.get(user=request.user, active=True)
    return {"score": participant.score, "round": game.current_round}


async def score_pl(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_score_pl)(request)


def _dashboard(quiz_game_id: int) -> list:
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    return [{"id": p.id, "name": p.user.username, "score": p.score} for p in
            quiz_game.participants.all().order_by('-score')]


async def dashboard(quiz_game_id: int) -> Coroutine:
    return await sync_to_async(_dashboard)(quiz_game_id)


def _get_ans(quiz_game_id: int, q_id: int) -> dict:
    question = InGameQuestion.objects.get(id=q_id)
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    result = list()
    for p in quiz_game.participants.all().order_by('-score'):
        if not p.super_bet or not p.super_answer:
            return {"ready": False}
        result.append({"id": p.id, "name": p.user.username, "bet": p.super_bet, "answer": p.super_answer})
    question.fresh = False
    question.save(update_fields=['fresh'])
    return {"answers": result, "ready": True}


async def get_ans(quiz_game_id: int, q_id: int) -> Coroutine:
    return await sync_to_async(_get_ans)(quiz_game_id, q_id)


def _g_list() -> list:
    return [{"id": g.id, "name": g.name, "room": g.room_name} for g in QuizGame.objects.filter(started=False)]


async def g_list() -> Coroutine:
    return await sync_to_async(_g_list)()


def _connect_player(request: HttpRequest) -> None:
    data = json.loads(request.body)
    game = QuizGame.objects.get(id=data['game_id'])
    if not Participant.objects.filter(user=request.user, game=game, active=True).exists():
        Participant.objects.create(user=request.user, game=game)


async def connect_player(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_connect_player)(request)


def _bet(request: HttpRequest) -> None:
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_bet = data["bet"]
    participant.save(update_fields=['super_bet'])


async def bet(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_bet)(request)


def _super_ans(request: HttpRequest) -> None:
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_answer = data["answer"]
    participant.save(update_fields=['super_answer'])


async def super_ans(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_super_ans)(request)


def _res_table(game_id: int) -> list:
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=game_id)
    result = list()
    for p in quiz_game.participants.all().order_by('-score'):
        percent = p.correct_answers / p.answer_attempts * 100
        result.append({"id": p.id, "name": p.user.username, "score": p.score,
                       "percent": f'{int(percent)} %'})
    return result


async def res_table(game_id: int) -> Coroutine:
    return await sync_to_async(_res_table)(game_id)


def _game_end(data: dict) -> None:
    game = QuizGame.objects.prefetch_related('participants', 'quiz').get(id=data["game_id"])
    q_set = game.participants.all()
    for p in q_set:
        p.active = False
    Participant.objects.bulk_update(q_set, ['active'])
    game.quiz.delete()


async def game_end(data: dict) -> Coroutine:
    return await sync_to_async(_game_end)(data)


def _no_body(question_id: int) -> None:
    question = InGameQuestion.objects.get(id=question_id)
    question.fresh = False
    question.save(update_fields=['fresh'])


async def no_body(question_id: int) -> Coroutine:
    return await sync_to_async(_no_body)(question_id)


def _q_detail(question_id: int) -> dict:
    question = Question.objects.select_related('type').get(id=question_id)
    return {"text": question.text, "type": question.type.id}


async def q_detail(question_id: int) -> Coroutine:
    return await sync_to_async(_q_detail)(question_id)


def _th_detail(theme_id: int) -> dict:
    theme = QuestionCategory.objects.get(id=theme_id)
    return {"name": theme.name}


async def th_detail(theme_id: int) -> Coroutine:
    return await sync_to_async(_th_detail)(theme_id)


def _quiz_det(quiz_id: int) -> dict:
    quiz = Quiz.objects.select_related('section').get(id=quiz_id)
    return {"title": quiz.title, "section": quiz.section.id}


async def quiz_det(quiz_id: int) -> Coroutine:
    return await sync_to_async(_quiz_det)(quiz_id)


def _check_room(request: HttpRequest) -> dict:
    role = request.GET.get('role')
    if role == 'creator':
        game = QuizGame.objects.get(game_master=request.user)
        return {"room": game.room_name}
    else:
        player = Participant.objects.get(user=request.user, active=True)
        return {"room": player.game.room_name}


async def check_room(request: HttpRequest) -> Coroutine:
    return await sync_to_async(_check_room)(request)


def _get_types() -> dict:
    return {"types": [[type.id, type.name] for type in QuestionType.objects.all()]}


async def get_types() -> Coroutine:
    return await sync_to_async(_get_types)()