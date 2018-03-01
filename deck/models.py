import random
from operator import itemgetter

from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from django.db.models.signals import pre_save
from django.dispatch import receiver

from utils.constants import SUITS, CARD_NUMBERS, SPADES_VALUE, CLUBS_VALUE, HEARTS_VALUE, MOVES_QUEUE, HAND01


class Card(models.Model):

    deck = models.ForeignKey('Deck',
                             blank=True,
                             null=True,
                             db_index=True,
                             related_name='cards',
                             on_delete=models.CASCADE)

    value = models.IntegerField(blank=True, null=True)
    worth = models.IntegerField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True, db_index=True, default=True)

    def __str__(self):
        return u"PK={}".format(self.pk)


class Deck(models.Model):
    trump = models.SmallIntegerField(default=1)
    hand01 = ArrayField(Card)
    hand02 = ArrayField(Card)
    hand03 = ArrayField(Card)
    hand04 = ArrayField(Card)
    # hand01 = JSONField(default=dict({}))
    # hand02 = JSONField(default=dict({}))
    # hand03 = JSONField(default=dict({}))
    # hand04 = JSONField(default=dict({}))
    next_move = models.IntegerField(choices=MOVES_QUEUE, blank=True, null=True, default=HAND01)
    total_moves = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return u"PK={}".format(self.pk)

    def json(self):
        return {
            "deck_id": self.pk,
            "trump": self.trump,
            "hand01": self.get_active_hand(self.hand01),
            "hand02": self.get_active_hand(self.hand02),
            "hand03": self.get_active_hand(self.hand03),
            "hand04": self.get_active_hand(self.hand04),
            "next_move": self.next_move,
            "total_moves": self.total_moves,
        }

    def deactivate(self, my_dict):
        #   Now HARDCODE, TODO MAKE SIMPLE AND ORGANIZED
        value = my_dict["value"]
        for hand in self.hand01:
            if hand["value"] == value:
                hand["active"] = False
                return
        for hand in self.hand02:
            if hand["value"] == value:
                hand["active"] = False
                return
        for hand in self.hand03:
            if hand["value"] == value:
                hand["active"] = False
                return
        for hand in self.hand04:
            if hand["value"] == value:
                hand["active"] = False
                return
        print(type(my_dict))
        pass
        # my_list[index]["active"] = False

    def get_active_hand(self, my_hand):
        my_filtered_hand = list()
        for i in my_hand:
            if i["active"]:
                my_filtered_hand.append(i)
        return my_filtered_hand

    def get_active_list(self, my_list):
        my__filtered_list = list()
        for i in my_list:
            if i["active"] is True:
                my__filtered_list.append(i)
        return my__filtered_list

    def allowed_hand_list(self):
        next_move = self.next_move
        total_moves = self.total_moves
        current_hand = getattr(self, "hand0{}".format(next_move))
        if total_moves % 4 == 0:
            #   Allowed list all
            return self.get_active_list(current_hand)

        current_suit = next_move - (total_moves % 4)
        if current_suit < 1:
            current_suit += 4

        # TODO get allowed list
        print(current_suit)

        my_list = list()

        return my_list

    def card_to_number(self, suit, card_number):
        card = dict()
        card["value"] = suit[0] * 100 + card_number[0]
        card["worth"] = card_number[1]
        if suit[0] == self.trump:
            card["trump_priority"] = card_number[2]
        else:
            card["trump_priority"] = 0
        card["name"] = card_number[3].lower() + "_of_" + suit[1].lower()
        card["url"] = "/static/cards/" + card["name"] + ".png"

        #   Priority for JACKS
        if card["name"] == "jack_of_clubs":
            card["trump_priority"] = 4 * 1000
        elif card["name"] == "jack_of_spades":
            card["trump_priority"] = 3 * 1000
        elif card["name"] == "jack_of_hearts":
            card["trump_priority"] = 2 * 1000
        elif card["name"] == "jack_of_diamonds":
            card["trump_priority"] = 1 * 1000
        card["active"] = True
        return card

    def special_sort(self, hand):
        trump_priority_list = list()
        value_priority_list = list()
        for i in range(len(hand)):
            if hand[i]["trump_priority"] != 0:
                trump_priority_list.append(hand[i])
            else:
                value_priority_list.append(hand[i])
        new_hand = list()
        trump_priority_list.sort(key=itemgetter("trump_priority"), reverse=True)
        value_priority_list.sort(key=itemgetter("value"), reverse=True)

        for i in range(len(trump_priority_list)):
            new_hand.append(trump_priority_list[i])

        clubs = 0
        spades = 0
        hearts = 0
        diamonds = 0
        #   Count of suits in the generated Deck
        for i in range(len(value_priority_list)):
            if value_priority_list[i]["value"] < 200:
                clubs += 1
            elif value_priority_list[i]["value"] < 300:
                spades += 1
            elif value_priority_list[i]["value"] < 400:
                hearts += 1
            else:
                diamonds += 1
        if self.trump in [CLUBS_VALUE, SPADES_VALUE]:
            if self.trump == CLUBS_VALUE:
                trump_min = 200
                trump_max = 300
            else:
                trump_min = 100
                trump_max = 200
            if diamonds == 0:
                #   include hearts
                for i in range(len(value_priority_list)):
                    if 400 > value_priority_list[i]["value"] > 300:
                        new_hand.append(value_priority_list[i])
                #   include spades or clubs
                for i in range(len(value_priority_list)):
                    if trump_max > value_priority_list[i]["value"] > trump_min:
                        new_hand.append(value_priority_list[i])
            else:
                #   include diamonds
                for i in range(len(value_priority_list)):
                    if 400 < value_priority_list[i]["value"]:
                        new_hand.append(value_priority_list[i])
                #   include spades or clubs
                for i in range(len(value_priority_list)):
                    if trump_max > value_priority_list[i]["value"] > trump_min:
                        new_hand.append(value_priority_list[i])
                #   include hearts [if exist]
                for i in range(len(value_priority_list)):
                    if 400 > value_priority_list[i]["value"] > 300:
                        new_hand.append(value_priority_list[i])
        else:
            if self.trump == HEARTS_VALUE:
                trump_min = 400
                trump_max = 500
            else:
                trump_min = 300
                trump_max = 400
            if clubs == 0:
                #   include spades
                for i in range(len(value_priority_list)):
                    if 300 > value_priority_list[i]["value"] > 200:
                        new_hand.append(value_priority_list[i])
                #   include hearts or diamonds
                for i in range(len(value_priority_list)):
                    if trump_max > value_priority_list[i]["value"] > trump_min:
                        new_hand.append(value_priority_list[i])
            else:
                #   include clubs
                for i in range(len(value_priority_list)):
                    if 200 > value_priority_list[i]["value"]:
                        new_hand.append(value_priority_list[i])
                #   include hearts or diamonds
                for i in range(len(value_priority_list)):
                    if trump_max > value_priority_list[i]["value"] > trump_min:
                        new_hand.append(value_priority_list[i])
                #   include spades [if exist]
                for i in range(len(value_priority_list)):
                    if 300 > value_priority_list[i]["value"] > 200:
                        new_hand.append(value_priority_list[i])

        return new_hand

    def generated_dealing(self):
        dealing = dict()
        bag = list()
        for suit in SUITS:
            for card_number in CARD_NUMBERS:
                bag.append(self.card_to_number(suit, card_number))
        randomized_bag = list()
        while len(bag):
            #   a <= n <= b
            #   random.randint(a,b)
            random_number = random.randint(0, len(bag) - 1)
            randomized_bag.append(bag[random_number])
            bag.remove(bag[random_number])

        for i in range(4):
            name = "hand" + "_" + self.generated_index(i + 1)
            dealing[name] = dict()
            cards_of_player = list()
            for j in range(8):
                cards_of_player.append(randomized_bag[i * 8 + j])
            dealing[name] = cards_of_player
        return dealing

    def generated_index(self, index):
        if index < 10:
            return "0" + str(index)
        return str(index)

    def number_to_card(self, number):
        suit = number // 100
        card = number % 100
        return suit, card


@receiver(pre_save, sender=Deck)
def set_info_details(sender, instance, **kwargs):
    #   Set initials
    if instance.pk is None:
        try:
            new_pk = Deck.objects.latest('id').pk + 1
        except ObjectDoesNotExist:
            new_pk = 1

        #   Set Primary Key
        instance.pk = new_pk
        my_deck = instance.generated_dealing()
        instance.hand01 = instance.special_sort(my_deck["hand_01"])
        instance.hand02 = instance.special_sort(my_deck["hand_02"])
        instance.hand03 = instance.special_sort(my_deck["hand_03"])
        instance.hand04 = instance.special_sort(my_deck["hand_04"])

        instance.total_moves = 0
