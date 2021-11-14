import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpRequest

from quiz.async_methods import check_user_auth, get_sections, get_quiz_list, get_game_quiz_list, get_themes, \
    get_question_list, get_theme_round, get_question_detail, get_ig_question_detail, quiz_cr, theme_cr, question_cr, \
    quiz_upd, theme_upd, question_upd, round_change, g_quiz_cr, qg_players, round_arrange, value_change, round_qg, \
    r_completed, corr_ans, wrong_ans, super_corr_ans, super_wrong_ans, game_start, score_pl, dashboard, get_ans, g_list, \
    connect_player, bet, super_ans, res_table, game_end, no_body, q_detail, th_detail, quiz_det, check_room, get_types
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
    return JsonResponse(await get_types())


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


async def quiz_game_round(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    round = request.GET.get('round')
    return JsonResponse(await round_qg(quiz_game_id, round))


async def round_completed(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    round = request.GET.get('round')
    return JsonResponse(await r_completed(quiz_game_id, round))


async def corr_answer(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await corr_ans(data)
    return HttpResponse(status=200)


async def wrong_answer(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await wrong_ans(data)
    return HttpResponse(status=200)


async def corr_answer_super(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await super_corr_ans(data)
    return HttpResponse(status=200)


async def wrong_answer_super(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await super_wrong_ans(data)
    return HttpResponse(status=200)


async def start_game(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await game_start(data)
    return HttpResponse(status=200)


async def player_score(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await score_pl(request))


async def players_dashboard(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    return JsonResponse(await dashboard(quiz_game_id), safe=False)


async def get_answers(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('game_id')
    q_id = request.GET.get('q_id')
    return JsonResponse(await get_ans(quiz_game_id, q_id))


async def games_available(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await g_list(), safe=False)


async def connect(request: HttpRequest):
    await check_method(request, ['POST'])
    await connect_player(request)
    return HttpResponse(status=200)


async def bet_super(request: HttpRequest):
    await check_method(request, ['POST'])
    await bet(request)
    return HttpResponse(status=200)


async def answer_super(request: HttpRequest):
    await check_method(request, ['POST'])
    await super_ans(request)
    return HttpResponse(status=200)


async def results_table(request: HttpRequest):
    await check_method(request, ['GET'])
    game_id = request.GET.get('quiz_game_id')
    return JsonResponse(await res_table(game_id), safe=False)


async def end_game(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await game_end(data)
    return HttpResponse(status=200)


async def nobody(request: HttpRequest):
    await check_method(request, ['POST'])
    data = json.loads(request.body)
    await no_body(data['question_id'])
    return HttpResponse(status=204)


async def question_upd_detail(request: HttpRequest):
    await check_method(request, ['GET'])
    question_id = request.GET.get("question_id")
    return JsonResponse(await q_detail(question_id))


async def theme_upd_detail(request: HttpRequest):
    await check_method(request, ['GET'])
    theme_id = request.GET.get("theme_id")
    return JsonResponse(await th_detail(theme_id))


async def quiz_upd_detail(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_id = request.GET.get("quiz_id")
    return JsonResponse(await quiz_det(quiz_id))


async def room(request: HttpRequest):
    await check_method(request, ['GET'])
    return JsonResponse(await check_room(request))