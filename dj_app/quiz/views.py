import datetime
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

# Create your views here.
from quiz.models import Section, Quiz, QuestionType, QuestionCategory, Question, QuizGame, InGameQuestion, Participant


def calm_down_players(game: QuizGame):
    q_set = game.participants.all()
    for participant in q_set:
        participant.answer_time = None
        participant.ready = False
    Participant.objects.bulk_update(q_set, ['answer_time', 'ready'])


def check_method(request, expected: list) -> HttpResponse:
    if request.user.is_anonymous:
        return HttpResponse(status=401)
    if request.method not in expected:
        return HttpResponse(status=405)


@login_required
def sections(request):
    check_method(request, ['GET'])
    return JsonResponse({"sections": [[section.id, section.name] for section in Section.objects.all()]})


@login_required
def types(request):
    check_method(request, ['GET'])
    return JsonResponse({"types": [[type.id, type.name] for type in QuestionType.objects.all()]})


@login_required
def quiz_list(request):
    check_method(request, ['GET'])
    return JsonResponse([{"id": quiz.id, "name": quiz.title, "color": quiz.section.special_color} for quiz in
                         Quiz.objects.filter(creator=request.user).select_related('section')], safe=False)


@login_required
def game_quiz_list(request):
    check_method(request, ['GET'])
    return JsonResponse([{"id": quiz.id, "name": quiz.title, "color": quiz.section.special_color} for quiz in
                         Quiz.objects.filter(creator__isnull=False, completed=True).select_related('section')], safe=False)


@login_required
def theme_list(request):
    check_method(request, ['GET'])
    quiz_id = request.GET.get('quiz_id')
    return JsonResponse([{"id": theme.id, "name": theme.name, "round": theme.round} for theme in
                         QuestionCategory.objects.filter(quiz_id=quiz_id).order_by('round')], safe=False)


@login_required
def question_list(request):
    check_method(request, ['GET'])
    theme_id = request.GET.get('theme_id')
    return JsonResponse([{"id": question.id, "text": question.text, "value": question.value,
                          "type": question.type_id} for question in
                         Question.objects.filter(category_id=theme_id).order_by('value')], safe=False)


@login_required
def theme_round(request):
    check_method(request, ['GET'])
    theme_id = request.GET.get('theme_id')
    return JsonResponse({"round": QuestionCategory.objects.get(id=theme_id).round}, status=200)


@login_required
def question_detail(request):
    check_method(request, ['GET'])
    question_id = request.GET.get('question_id')
    question = Question.objects.get(id=question_id)
    resp = {"text": question.text, "value": question.value, "type": question.type_id}
    if question.type_id == 2:
        resp['image'] = "/api" + question.image.url if question.image else None
    elif question.type_id == 3:
        resp['audio'] = "/api" + question.audio.url if question.audio else None
    return JsonResponse(resp, status=200)


@login_required
def ig_question_detail(request):
    check_method(request, ['GET'])
    game_id = request.GET.get('game_id')
    calm_down_players(QuizGame.objects.get(id=game_id))
    question_id = request.GET.get('question_id')
    question = InGameQuestion.objects.get(id=question_id)
    resp = {"text": question.text, "value": question.value, "type": question.type_id}
    if question.type_id == 2:
        resp['image'] = "/api" + question.image.url if question.image else None
    elif question.type_id == 3:
        resp['audio'] = "/api" + question.audio.url if question.audio else None
    return JsonResponse(resp, status=200)


@login_required
def create_quiz(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    quiz = Quiz.objects.create(title=data['title'], section_id=data['section'], creator=request.user)
    return JsonResponse({"id": quiz.id}, status=201)


@login_required
def create_theme(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    if QuestionCategory.objects.filter(quiz_id=data['quiz'], name=data['name']).exists():
        return JsonResponse({"detail": "Such theme already exists in this quiz"}, status=200)
    theme = QuestionCategory.objects.create(name=data['name'], quiz_id=data['quiz'])
    return JsonResponse({"id": theme.id}, status=201)


@login_required
def create_question(request):
    check_method(request, ['POST'])
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
    return JsonResponse({"id": question.id}, status=201)


@login_required
def update_quiz(request, id: int):
    check_method(request, ['PUT', 'DELETE'])
    quiz = Quiz.objects.get(id=id)
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
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


@login_required
def update_theme(request, id: int):
    check_method(request, ['PUT', 'DELETE'])
    theme = QuestionCategory.objects.get(id=id)
    update_fields = list()
    if request.method == 'PUT':
        data = json.loads(request.body)
        if 'name' in data:
            update_fields.append('name')
            theme.name = data['name']
        theme.save(update_fields=update_fields)
    elif request.method == 'DELETE':
        theme.delete()
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


@login_required
def update_question(request, id: int):
    check_method(request, ['POST', 'DELETE'])
    question = Question.objects.get(id=id)
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
    return HttpResponse(status=200 if request.method == 'POST' else 204)


@login_required
def arrange_theme_round(request):
    check_method(request, ['PUT'])
    data = json.loads(request.body)
    theme = QuestionCategory.objects.get(id=data['theme_id'])
    if QuestionCategory.objects.filter(quiz=theme.quiz, round=data['round']).count() >= 5:
        return JsonResponse({"detail": "Too many themes for single round"}, status=400)
    theme.round = data['round']
    theme.save(update_fields=['round'])
    return JsonResponse({"id": theme.id}, status=200)


@login_required
def change_value(request):
    check_method(request, ['PUT'])
    data = json.loads(request.body)
    origin_q = Question.objects.get(id=data['origin_id'])
    destination_q = Question.objects.get(id=data['destination_id'])
    value_1 = origin_q.value
    value_2 = destination_q.value
    destination_q.value = value_1
    origin_q.value = value_2
    destination_q.save(update_fields=['value'])
    origin_q.save(update_fields=['value'])
    return JsonResponse({"detail": "Success"}, status=200)


@login_required
def change_round(request):
    check_method(request, ['PUT'])
    data = json.loads(request.body)
    origin_t = QuestionCategory.objects.get(id=data['theme_id'])
    destination_t = QuestionCategory.objects.get(id=int(data['target_id']))
    value_1 = origin_t.round
    value_2 = destination_t.round
    print(value_1, value_2)
    destination_t.round = value_1
    origin_t.round = value_2
    destination_t.save(update_fields=['round'])
    origin_t.save(update_fields=['round'])
    return JsonResponse({"detail": "Success"}, status=200)


@login_required
def game_quiz_cr(request):
    check_method(request, ['POST'])
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
    return JsonResponse({"id": new_quiz_game.id}, status=200)


@login_required
def quiz_game_players(request):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    return JsonResponse(
        [{"id": player.id, "name": player.user.username} for player in
         quiz_game.participants.all().order_by('user__username')],
        safe=False)


@login_required
def quiz_game_round(request):
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
def round_completed(request):
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
def corr_answer(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'])
    game = QuizGame.objects.prefetch_related('participants').get(id=data['game_id'])
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score += points
    player.ready = False
    player.answer_attempts += 1
    player.correct_answers += 1
    question.fresh = False
    player.answer_time = None
    player.save(update_fields=['score', 'ready', 'answer_time', 'answer_attempts', 'correct_answers'])
    question.save(update_fields=['fresh'])
    calm_down_players(game)
    return HttpResponse(status=200)


@login_required
def wrong_answer(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'])
    game = QuizGame.objects.prefetch_related('participants').get(id=data['game_id'])
    question = InGameQuestion.objects.prefetch_related('category').get(id=data['question_id'])
    points = question.category.round * question.value
    player.score -= points
    player.ready = False
    player.answer_attempts += 1
    player.answer_time = None
    player.save(update_fields=['score', 'ready', 'answer_time', 'answer_attempts'])
    for participant in game.participants.all().order_by('answer_time'):
        print(participant.answer_time)
        if participant.ready:
            return JsonResponse({"id": participant.id, "name": participant.user.username})
    return HttpResponse(status=200)


@login_required
def corr_answer_super(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'])
    player.score += player.super_bet
    player.ready = False
    player.answer_attempts += 1
    player.correct_answers += 1
    player.answer_time = None
    player.save(update_fields=['score', 'ready', 'answer_time', 'answer_attempts', 'correct_answers'])
    return HttpResponse(status=200)


@login_required
def wrong_answer_super(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    player = Participant.objects.get(id=data['player_id'])
    player.score -= player.super_bet
    player.ready = False
    player.answer_time = None
    player.answer_attempts += 1
    player.save(update_fields=['score', 'ready', 'answer_time', 'answer_attempts'])
    return HttpResponse(status=200)


@login_required
def player_ready(request):
    check_method(request, ['POST'])
    participant = Participant.objects.get(user=request.user, active=True)
    participant.ready = True
    participant.answer_time = datetime.datetime.now()
    participant.save(update_fields=['ready', 'answer_time'])
    return HttpResponse(status=200)


@login_required
def start_game(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    game = QuizGame.objects.get(id=data['game_id'])
    game.started=True
    game.save(update_fields=['started'])
    return HttpResponse(status=200)


@login_required
def check_ready_players(request):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    game = QuizGame.objects.get(id=quiz_game_id)
    for p in game.participants.filter(ready=True).order_by('answer_time'):
        return JsonResponse({"id": p.id, "name": p.user.username, "score": p.score})
    return HttpResponse(status=200)


@login_required
def player_score(request):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    game = QuizGame.objects.get(id=quiz_game_id)
    participant = Participant.objects.get(user=request.user, active=True)
    return JsonResponse({"score": participant.score, "round": game.current_round})


@login_required
def players_dashboard(request):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    return JsonResponse([{"id": p.id, "name": p.user.username, "score": p.score} for p in quiz_game.participants.all().order_by('-score')], safe=False)


@login_required
def get_answers(request):
    check_method(request, ['GET'])
    quiz_game_id = request.GET.get('game_id')
    q_id = request.GET.get('q_id')
    question = InGameQuestion.objects.get(id=q_id)
    quiz_game = QuizGame.objects.prefetch_related('participants', 'participants__user').get(id=quiz_game_id)
    result = list()
    all_ready = True
    for p in quiz_game.participants.all().order_by('-score'):
        if p.score > 0:
            if p.ready:
                result.append({"id": p.id, "name": p.user.username, "answer": p.super_answer, "bet": p.super_bet} )
            else:
                return JsonResponse({"answers": {}, "ready": False})
    question.fresh = False
    question.save(update_fields=['fresh'])
    return JsonResponse({"answers": result, "ready": all_ready})


@login_required
def games_available(request):
    check_method(request, ['GET'])
    return JsonResponse([{"id": g.id, "name": g.name} for g in QuizGame.objects.filter(started=False)], safe=False)


@login_required
def connect(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    game = QuizGame.objects.get(id=data['game_id'])
    participant = Participant.objects.create(user=request.user)
    game.participants.add(participant)
    return HttpResponse(status=200)


@login_required
def bet_super(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_bet = data["bet"]
    participant.save(update_fields=['super_bet'])
    return HttpResponse(status=200)


@login_required
def answer_super(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    participant = Participant.objects.get(user=request.user, active=True)
    participant.super_answer = data["answer"]
    participant.ready = True
    participant.save(update_fields=['super_answer', 'ready'])
    return HttpResponse(status=200)


@login_required
def results_table(request):
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
def end_game(request):
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
def nobody(request):
    check_method(request, ['POST'])
    data = json.loads(request.body)
    question = InGameQuestion.objects.get(id=data['question_id'])
    question.fresh = False
    question.save(update_fields=['fresh'])
    return HttpResponse(status=200)


@login_required
def question_upd_detail(request):
    check_method(request, ['GET'])
    question = Question.objects.select_related('type').get(id=request.GET.get("question_id"))
    return JsonResponse({"text": question.text, "type": question.type.id})


@login_required
def theme_upd_detail(request):
    check_method(request, ['GET'])
    theme = QuestionCategory.objects.get(id=request.GET.get("theme_id"))
    return JsonResponse({"name": theme.name})


@login_required
def quiz_upd_detail(request):
    check_method(request, ['GET'])
    quiz = Quiz.objects.select_related('section').get(id=request.GET.get("quiz_id"))
    return JsonResponse({"title": quiz.title, "section": quiz.section.id })