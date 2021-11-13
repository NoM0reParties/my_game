import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpRequest

from quiz.async_methods import check_user_auth, get_sections, get_quiz_list, get_game_quiz_list, get_themes, \
    get_question_list, get_theme_round, get_question_detail, get_ig_question_detail, quiz_cr, theme_cr, question_cr, \
    quiz_upd, theme_upd, question_upd, round_change, g_quiz_cr, qg_players, round_arrange, value_change
from quiz.models import Quiz, QuestionType, QuestionCategory, Question, QuizGame, InGameQuestion, Participant


async def check_method(request: HttpRequest, expected: list) -> HttpResponse:
    if await check_user_auth(request):
        return HttpResponse(status=401)
    if request.method not in expected:
        return HttpResponse(status=405)


async def sections(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await get_sections())


async def types(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse({"types": [[type.id, type.name] for type in QuestionType.objects.all()]})


async def quiz_list(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await get_quiz_list(request), safe=False)


async def game_quiz_list(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await get_game_quiz_list(), safe=False)


async def theme_list(request: HttpRequest) -> HttpResponse:
    quiz_id = request.GET.get(key='quiz_id')
    themes = await get_themes(quiz_id)
    await check_method(request, ['GET'])
    return JsonResponse(themes, safe=False)


async def question_list(request: HttpRequest):
    await check_method(request, ['GET'])
    theme_id = request.GET.get('theme_id')
    return JsonResponse(await get_question_list(theme_id), safe=False)


async def theme_round(request: HttpRequest):
    await check_method(request, ['GET'])
    theme_id = request.GET.get('theme_id')
    return JsonResponse(await get_theme_round(theme_id))


async def question_detail(request: HttpRequest):
    await check_method(request, ['GET'])
    question_id = request.GET.get('question_id')
    return JsonResponse(await get_question_detail(question_id))


async def ig_question_detail(request: HttpRequest):
    await check_method(request, ['GET'])
    question_id = request.GET.get('question_id')
    return JsonResponse(await get_ig_question_detail(question_id), status=200)


async def create_quiz(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    return JsonResponse(await quiz_cr(data['title'], data['section'], request), status=201)


async def create_theme(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    resp = await theme_cr(data['quiz'], data['name'])
    return JsonResponse(resp, status=201 if "id" in resp.keys() else 200)


async def create_question(request: HttpRequest):
    await check_method(request, ['POST'])
    return JsonResponse(await question_cr(request), status=201)


async def update_quiz(request: HttpRequest, id: int):
    await check_method(request, ['PUT', 'DELETE'])
    await quiz_upd(request)
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


async def update_theme(request: HttpRequest, id: int):
    await check_method(request, ['PUT', 'DELETE'])
    await theme_upd(request, id)
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


async def update_question(request: HttpRequest, id: int):
    await check_method(request, ['POST', 'DELETE'])
    await question_upd(request, id)
    return HttpResponse(status=200 if request.method == 'POST' else 204)


async def arrange_theme_round(request: HttpRequest):
    await check_method(request, ['PUT'])
    data = json.loads(request.body)
    return JsonResponse(await round_arrange(data), status=200)


async def change_value(request: HttpRequest):
    await check_method(request, ['PUT'])
    data = json.loads(request.body)
    await value_change(data)
    return JsonResponse({"detail": "Success"}, status=200)


async def change_round(request: HttpRequest):
    await check_method(request, ['PUT'])
    data = json.loads(request.body)
    await round_change(data)
    return JsonResponse({"detail": "Success"}, status=200)


async def game_quiz_cr(request: HttpRequest):
    await check_method(request, ['POST'])
    return JsonResponse(await g_quiz_cr(request), status=200)


async def quiz_game_players(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    return JsonResponse(await qg_players(quiz_game_id), safe=False)


@login_required
def quiz_game_round(request: HttpRequest):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    round = request.GET.get('round')
    quiz_game = QuizGame.objects.prefetch_related('quiz', 'quiz__q_category', 'quiz__q_category__question').get(
        id=quiz_game_id)
    result = dict()
    for theme in quiz_game.quiz.q_category.filter(round=round):
        result[theme.name] = [{"id": q.id, "text": q.text, "value": q.value, "type": q.type_id,
                               "audio": q.audio.url if q.audio else None,
                               "image": q.image.url if q.image else None,
                               "fresh": q.fresh} for q in
                              theme.question.all().order_by('value')]
    return JsonResponse(result)


@login_required
def round_completed(request: HttpRequest):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    round = request.GET.get('round')
    quiz_game = QuizGame.objects.prefetch_related('quiz', 'quiz__q_category', 'quiz__q_category__question').get(
        id=quiz_game_id)
    result = False
    for theme in quiz_game.quiz.q_category.filter(round=round):
        for q in theme.question.all():
            if q.fresh:
                result = True
                return JsonResponse({"alive": result})
    quiz_game.current_round += 1
    quiz_game.save(update_fields=['current_round'])
    return JsonResponse({"alive": result})


@login_required
def corr_answer(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(user_id=data['player_id'], active=True)
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score += points
    player.answer_attempts += 1
    player.correct_answers += 1
    question.fresh = False
    player.save(update_fields=['score', 'answer_attempts', 'correct_answers'])
    question.save(update_fields=['fresh'])
    return HttpResponse(status=200)


@login_required
def wrong_answer(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(user_id=data['player_id'], active=True)
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score -= points
    player.answer_attempts += 1
    player.save(update_fields=['score', 'answer_attempts'])
    return HttpResponse(status=200)


@login_required
def corr_answer_super(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'], active=True)
    player.score += player.super_bet
    player.answer_attempts += 1
    player.correct_answers += 1
    player.save(update_fields=['score', 'answer_attempts', 'correct_answers'])
    return HttpResponse(status=200)


@login_required
def wrong_answer_super(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'], active=True)
    player.score -= player.super_bet
    player.answer_attempts += 1
    player.save(update_fields=['score', 'answer_attempts'])
    return HttpResponse(status=200)


@login_required
def start_game(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    game = QuizGame.objects.get(id=data['game_id'])
    game.started = True
    game.save(update_fields=['started'])
    return HttpResponse(status=200)


@login_required
def player_score(request: HttpRequest):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    game = QuizGame.objects.get(id=quiz_game_id)
    participant = Participant.objects.get(user=request.user, active=True)
    return JsonResponse({"score": participant.score, "round": game.current_round})


@login_required
def players_dashboard(request: HttpRequest):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    return JsonResponse([{"id": p.id, "name": p.user.username, "score": p.score} for p in
                         quiz_game.participants.all().order_by('-score')], safe=False)


@login_required
def get_answers(request: HttpRequest):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('game_id')
    q_id = request.GET.get('q_id')
    question = InGameQuestion.objects.get(id=q_id)
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    result = list()
    for p in quiz_game.participants.all().order_by('-score'):
        if not p.super_bet or not p.super_answer:
            return JsonResponse({"ready": False})
    question.save(update_fields=['fresh'])
    return JsonResponse({"answers": result, "ready": True})


@login_required
def games_available(request: HttpRequest):
    check_method(request, ['GET'])
    return JsonResponse(
        [{"id": g.id, "name": g.name, "room": g.room_name} for g in QuizGame.objects.filter(started=False)], safe=False)


@login_required
def connect(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    game = QuizGame.objects.get(id=data['game_id'])
    Participant.objects.create(user=request.user, game=game)
    return HttpResponse(status=200)


@login_required
def bet_super(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_bet = data["bet"]
    participant.save(update_fields=['super_bet'])
    return HttpResponse(status=200)


@login_required
def answer_super(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_answer = data["answer"]
    participant.save(update_fields=['super_answer'])
    return HttpResponse(status=200)


@login_required
def results_table(request: HttpRequest):
    check_method(request, ['GET'])
    game_id = request.GET.get('quiz_game_id')
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=game_id)
    result = list()
    for p in quiz_game.participants.all().order_by('-score'):
        percent = p.correct_answers / p.answer_attempts * 100
        result.append({"id": p.id, "name": p.user.username, "score": p.score,
                       "percent": f'{int(percent)} %'})
    return JsonResponse(result, safe=False)


@login_required
def end_game(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    game = QuizGame.objects.prefetch_related('participants', 'quiz').get(id=data["game_id"])
    q_set = game.participants.all()
    for p in q_set:
        p.active = False
    Participant.objects.bulk_update(q_set, ['active'])
    game.quiz.delete()
    return HttpResponse(status=200)


@login_required
def nobody(request: HttpRequest):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    question = InGameQuestion.objects.get(id=data['question_id'])
    question.fresh = False
    question.save(update_fields=['fresh'])
    return HttpResponse(status=200)


@login_required
def question_upd_detail(request: HttpRequest):
    check_method(request, ['GET'])
    question = Question.objects.select_related('type').get(id=request.GET.get("question_id"))
    return JsonResponse({"text": question.text, "type": question.type.id})


@login_required
def theme_upd_detail(request: HttpRequest):
    check_method(request, ['GET'])
    theme = QuestionCategory.objects.get(id=request.GET.get("theme_id"))
    return JsonResponse({"name": theme.name})


@login_required
def quiz_upd_detail(request: HttpRequest):
    check_method(request, ['GET'])
    quiz = Quiz.objects.select_related('section').get(id=request.GET.get("quiz_id"))
    return JsonResponse({"title": quiz.title, "section": quiz.section.id})


@login_required
def room(request: HttpRequest):
    check_method(request, ['GET'])
    role = request.GET.get('role')
    if role == 'creator':
        game = QuizGame.objects.get(game_master=request.user)
        return JsonResponse({"room": game.room_name})
    else:
        player = Participant.objects.get(user=request.user, active=True)
        return JsonResponse({"room": player.game.room_name})
