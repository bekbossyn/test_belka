import random

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from deck.models import Deck

from utils import http, codes, messages
from utils.constants import SUITS


def test(request):
    return HttpResponse("<h1>test</h1>")


@csrf_exempt
def test_visual(request):
    try:
        deck_id = int(request.GET.get("deck_id") or request.POST.get("deck_id"))
        deck = Deck.objects.get(id=deck_id)
    except ObjectDoesNotExist:
        deck = Deck.objects.last()
    except:
        deck = Deck.objects.last()
    # except
    context = {
        # "hand_01": deck.get_active_hand(deck.hand01),
        # "hand_02": deck.get_active_hand(deck.hand02),
        # "hand_03": deck.get_active_hand(deck.hand03),
        # "hand_04": deck.get_active_hand(deck.hand04),
        "hand_01": deck.hand01,
        "hand_02": deck.hand02,
        "hand_03": deck.hand03,
        "hand_04": deck.hand04,
    }
    return render(request, "deck/visual.html", context)


@http.json_response()
@csrf_exempt
def generate_deck(request):
    try:
        trump = int(request.POST.get("trump", 1))
        if trump not in [suit[0] for suit in SUITS]:
            return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="trump")
    except:
        return http.code_response(code=codes.BAD_REQUEST, message=messages.INVALID_PARAMS, field="trump")
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
    allowed_hand_list = deck.allowed_hand_list()
    if len(allowed_hand_list) == 8:
        # ALL moves can be made
        move = random.randint(0, len(allowed_hand_list) - 1)
    else:
        #   TODO create movement
        move = 0
    # allowed_hand_list.remove(allowed_hand_list[move])
    deck.deactivate(allowed_hand_list[move])
    deck.save()
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


