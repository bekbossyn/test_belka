from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from deck.models import Deck

from utils import http, codes, messages


def test(request):
    return HttpResponse("<h1>test</h1>")


def test_visual(request):
    deck = Deck.objects.last()
    context = {
        "hand_01": deck.hand01,
        "hand_02": deck.hand02,
        "hand_03": deck.hand03,
        "hand_04": deck.hand04,
    }
    return render(request, "deck/visual.html", context)


@http.json_response()
@csrf_exempt
def generate_deck(request):
    trump = int(request.POST.get("trump", 1))
    deck = Deck.objects.create(trump=trump)

    return {
        "deck": deck.json(),
    }


@http.json_response()
@http.required_parameters(["deck_id"])
@csrf_exempt
def make_move(request):
    try:
        deck = Deck.objects.get(pk=(request.POST.get("deck_id") or request.GET.get("deck_id")))
    except ObjectDoesNotExist:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.DECK_NOT_FOUND)
    moves_count = deck.moves["moves_count"]

    allowed_hand_list = deck.allowed_list(moves_count)

    return {
        "allowed": allowed_hand_list,
        "deck": deck.json(),
    }


@http.json_response()
@http.required_parameters(["deck_id"])
@csrf_exempt
def show(request):
    try:
        deck = Deck.objects.get(pk=(request.POST.get("deck_id") or request.GET.get("deck_id")))
    except ObjectDoesNotExist:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.DECK_NOT_FOUND)

    return {
        "deck": deck.json(),
    }


