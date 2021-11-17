import json
from asyncio import gather

from django.http import JsonResponse, HttpResponse, HttpRequest

from quiz.async_methods import check_user_auth, get_sections, get_quiz_list, get_game_quiz_list, get_themes, \
    get_question_list, get_theme_round, get_question_detail, get_ig_question_detail, quiz_cr, theme_cr, question_cr, \
    quiz_upd, theme_upd, question_upd, round_change, g_quiz_cr, qg_players, round_arrange, round_qg, corr_ans, \
    r_completed, wrong_ans, super_corr_ans, super_wrong_ans, game_start, score_pl, dashboard, get_ans, g_list, \
    connect_player, bet, super_ans, res_table, game_end, no_body, q_detail, th_detail, quiz_det, check_room, get_types


async def check_method(request: HttpRequest, expected: list) -> HttpResponse:
    if await check_user_auth(request):
        return HttpResponse(status=401)
    if request.method not in expected:
        return HttpResponse(status=405)


async def sections(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), get_sections())
    return JsonResponse(info[1])


async def types(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), get_types())
    return JsonResponse(info[1])


async def quiz_list(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), get_quiz_list(request))
    return JsonResponse(info[1], safe=False)


async def game_quiz_list(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), get_game_quiz_list())
    return JsonResponse(info[1], safe=False)


async def theme_list(request: HttpRequest) -> HttpResponse:
    quiz_id = request.GET.get(key='quiz_id')
    info = await gather(check_method(request, ['GET']), get_themes(quiz_id))
    return JsonResponse(info[1], safe=False)


async def question_list(request: HttpRequest):
    theme_id = request.GET.get('theme_id')
    info = await gather(check_method(request, ['GET']), get_question_list(theme_id))
    return JsonResponse(info[1], safe=False)


async def theme_round(request: HttpRequest):
    theme_id = request.GET.get('theme_id')
    info = await gather(check_method(request, ['GET']), get_theme_round(theme_id))
    return JsonResponse(info[1])


async def question_detail(request: HttpRequest):
    question_id = request.GET.get('question_id')
    info = await gather(check_method(request, ['GET']), get_question_detail(question_id))
    return JsonResponse(info[1])


async def ig_question_detail(request: HttpRequest):
    question_id = request.GET.get('question_id')
    info = await gather(check_method(request, ['GET']), get_ig_question_detail(question_id))
    return JsonResponse(info[1], status=200)


async def create_quiz(request: HttpRequest):
    data = json.loads(request.body)
    info = await gather(check_method(request, ['POST']), quiz_cr(data['title'], data['section'], request))
    return JsonResponse(info[1], status=201)


async def create_theme(request: HttpRequest):
    data = json.loads(request.body)
    info = await gather(check_method(request, ['POST']), theme_cr(data['quiz'], data['name']))
    return JsonResponse(info[1], status=201 if "id" in info[1].keys() else 200)


async def create_question(request: HttpRequest):
    info = await gather(check_method(request, ['POST']), question_cr(request))
    return JsonResponse(info[1], status=201)


async def update_quiz(request: HttpRequest, quiz_id: int):
    await gather(check_method(request, ['PUT', 'DELETE']), quiz_upd(request, quiz_id))
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


async def update_theme(request: HttpRequest, theme_id: int):
    await gather(check_method(request, ['PUT', 'DELETE']), theme_upd(request, theme_id))
    return HttpResponse(status=200 if request.method == 'PUT' else 204)


async def update_question(request: HttpRequest, question_id: int):
    await gather(check_method(request, ['POST', 'DELETE']), question_upd(request, question_id))
    return HttpResponse(status=200 if request.method == 'POST' else 204)


async def arrange_theme_round(request: HttpRequest):
    data = json.loads(request.body)
    info = await gather(check_method(request, ['PUT']), round_arrange(data))
    return JsonResponse(info[1], status=200)


async def change_value(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['PUT']), round_arrange(data))
    return JsonResponse({"detail": "Success"}, status=200)


async def change_round(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['PUT']), round_change(data))
    return JsonResponse({"detail": "Success"}, status=200)


async def game_quiz_cr(request: HttpRequest):
    info = await gather(check_method(request, ['POST']), g_quiz_cr(request))
    return JsonResponse(info[1], status=200)


async def quiz_game_players(request: HttpRequest):
    quiz_game_id = request.GET.get('quiz_game_id')
    info = await gather(check_method(request, ['GET']), qg_players(quiz_game_id))
    return JsonResponse(info[1], safe=False)


async def quiz_game_round(request: HttpRequest):
    quiz_game_id = request.GET.get('quiz_game_id')
    current_round = request.GET.get('round')
    info = await gather(check_method(request, ['GET']), round_qg(quiz_game_id, current_round))
    return JsonResponse(info[1])


async def round_completed(request: HttpRequest):
    await check_method(request, ['GET'])
    quiz_game_id = request.GET.get('quiz_game_id')
    current_round = request.GET.get('round')
    info = await gather(check_method(request, ['GET']), r_completed(quiz_game_id, current_round))
    return JsonResponse(info[1])


async def corr_answer(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), corr_ans(data))
    return HttpResponse(status=200)


async def wrong_answer(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), wrong_ans(data))
    return HttpResponse(status=200)


async def corr_answer_super(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), super_corr_ans(data))
    return HttpResponse(status=200)


async def wrong_answer_super(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), super_wrong_ans(data))
    return HttpResponse(status=200)


async def start_game(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), game_start(data))
    return HttpResponse(status=200)


async def player_score(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), score_pl(request))
    return JsonResponse(info[1])


async def players_dashboard(request: HttpRequest):
    quiz_game_id = request.GET.get('quiz_game_id')
    info = await gather(check_method(request, ['GET']), dashboard(quiz_game_id))
    return JsonResponse(info[1], safe=False)


async def get_answers(request: HttpRequest):
    quiz_game_id = request.GET.get('game_id')
    q_id = request.GET.get('q_id')
    info = await gather(check_method(request, ['GET']), get_ans(quiz_game_id, q_id))
    return JsonResponse(info[1])


async def games_available(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), g_list())
    return JsonResponse(info[1], safe=False)


async def connect(request: HttpRequest):
    await gather(check_method(request, ['POST']), connect_player(request))
    return HttpResponse(status=200)


async def bet_super(request: HttpRequest):
    await gather(check_method(request, ['POST']), bet(request))
    return HttpResponse(status=200)


async def answer_super(request: HttpRequest):
    await gather(check_method(request, ['POST']), super_ans(request))
    return HttpResponse(status=200)


async def results_table(request: HttpRequest):
    game_id = request.GET.get('quiz_game_id')
    info = await gather(check_method(request, ['GET']), res_table(game_id))
    return JsonResponse(info[1], safe=False)


async def end_game(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), game_end(data))
    return HttpResponse(status=200)


async def nobody(request: HttpRequest):
    data = json.loads(request.body)
    await gather(check_method(request, ['POST']), no_body(data['question_id']))
    return HttpResponse(status=204)


async def question_upd_detail(request: HttpRequest):
    question_id = request.GET.get("question_id")
    info = await gather(check_method(request, ['GET']), q_detail(question_id))
    return JsonResponse(info[1])


async def theme_upd_detail(request: HttpRequest):
    theme_id = request.GET.get("theme_id")
    info = await gather(check_method(request, ['GET']), th_detail(theme_id))
    return JsonResponse(info[1])


async def quiz_upd_detail(request: HttpRequest):
    quiz_id = request.GET.get("quiz_id")
    info = await gather(check_method(request, ['GET']), quiz_det(quiz_id))
    return JsonResponse(info[1])


async def room(request: HttpRequest):
    info = await gather(check_method(request, ['GET']), check_room(request))
    return JsonResponse(info[1])
