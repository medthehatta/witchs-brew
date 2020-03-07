#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""witchs_brew"""



from collections import Counter
from functools import reduce
from functools import wraps
import itertools
import re


#
# Constants
#


DEBUG_TRACING = True


CHAPTER = "chapter"
OFFER = "offer"
OCCULT = "occult"
MAGIC = "magic"
INGREDIENT = "ingredient"
CLOVER = "clover"
TOAD = "toad"
MUSHROOM = "mushroom"
PIXIE = "pixie"


#
# Helpers
#


def trace_local_score(func):
    @wraps(func)
    def _wrapped(spell, score):
        (new_spell, new_score) = func(spell, score)
        if DEBUG_TRACING is True:
            print(f"{func.__name__}\t{new_spell}\t{new_score}")
        return (new_spell, new_score)
    return _wrapped


class Card(object):

    def __init__(self, kind, value=None, type=None, boiled=False):
        self.kind = kind
        self.value = value
        self.type = type
        self.boiled = boiled

    def __repr__(self):
        if self.kind == INGREDIENT:
            if self.boiled:
                return f"<{self.type[:3].title()} (B): {self.value}>"
            else:
                return f"<{self.type[:3].title()}: {self.value}>"
        elif self.kind == MAGIC:
            return f"<Magic: {self.value}>"
        else:
            if self.value is not None:
                return f"<{self.kind.title()}: {self.value}>"
            else:
                return f"<{self.kind.title()}>"


def ingredients(spell):
    return [card for card in spell if card.kind == INGREDIENT]


def chapters(spell):
    return [card for card in spell if card.kind == CHAPTER]


def clover(n):
    return Card(kind=INGREDIENT, value=n, type=CLOVER)


def toad(n):
    return Card(kind=INGREDIENT, value=n, type=TOAD)


def mushroom(n):
    return Card(kind=INGREDIENT, value=n, type=MUSHROOM)


def pixie(n):
    return Card(kind=INGREDIENT, value=n, type=PIXIE)


def magic(n):
    return Card(kind=MAGIC, value=n)


occult = Card(kind=OCCULT)


def offer(n):
    return Card(kind=OFFER, value=n)


chapter = Card(kind=CHAPTER)


def boiled(card):
    if card.boiled:
        return card
    else:
        return Card(
            kind=card.kind,
            value=card.value,
            type=card.type,
            boiled=True,
        )


def parsed_card(s):
    offer_ = re.compile(r'o(\d)')
    chapter_ = re.compile(r'x')
    ingredient_ = re.compile(r'(\w)(\d+)')
    boiled_ = re.compile(r'(\w)(\d+)b')

    m_offer = offer_.match(s)
    m_chapter = chapter_.match(s)
    m_ingredient = ingredient_.match(s)
    m_boiled = boiled_.match(s)

    if m_offer:
        return offer(int(m_offer.group(1)))
    elif m_chapter:
        return chapter
    elif m_boiled:
        if m_ingredient.group(1).lower() == "c":
            return boiled(clover(int(m_ingredient.group(2))))
        elif m_ingredient.group(1).lower() == "t":
            return boiled(toad(int(m_ingredient.group(2))))
        elif m_ingredient.group(1).lower() == "m":
            return boiled(mushroom(int(m_ingredient.group(2))))
        elif m_ingredient.group(1).lower() == "p":
            return boiled(pixie(int(m_ingredient.group(2))))
        else:
            raise ValueError("Bad ingredient card: {}".format(s))
    elif m_ingredient:
        if m_ingredient.group(1).lower() == "c":
            return clover(int(m_ingredient.group(2)))
        elif m_ingredient.group(1).lower() == "t":
            return toad(int(m_ingredient.group(2)))
        elif m_ingredient.group(1).lower() == "m":
            return mushroom(int(m_ingredient.group(2)))
        elif m_ingredient.group(1).lower() == "p":
            return pixie(int(m_ingredient.group(2)))
        else:
            raise ValueError("Bad ingredient card: {}".format(s))


def parse(spells):
    return [[parsed_card(x) for x in spell.split()] for spell in spells]


#
# Rules
#


def rule1(spell, score):
    """Intro to spellcraft."""
    extra = min(15, sum(card.value for card in ingredients(spell)))
    return (spell, score + extra)


def rule2(spell, score):
    """Beginner's warning."""
    volatiles = [card for card in ingredients(spell) if card.value > 3]
    if len(volatiles) > 2:
        return ([card for card in spell if card not in volatiles], score)
    else:
        return (spell, score)


def rule3(spell, score):
    """Cantrips."""
    all_types = {CLOVER, PIXIE, TOAD, MUSHROOM}
    if set(card.type for card in ingredients(spell)) == all_types:
        return (spell, score + 3)
    else:
        return (spell, score)


def rule4(spell, score):
    """Double double."""
    comparable_ingredients = [
        (card.type, card.value) for card in ingredients(spell)
    ]
    counted = Counter(comparable_ingredients)
    pair_scores = sum(v // 2 for (k, v) in counted.items())
    return (spell, score + 2*pair_scores)


def rule5(spell, score):
    """Tips and tricks."""
    return (spell, score + len(chapters(spell)))


def rule6_local(spell, score):
    """Natural magic (local)."""
    num_magical = len([
        card for card in spell
        if card.kind == CHAPTER or card.type == PIXIE
    ])
    if num_magical:
        return (spell + [magic(num_magical)], score)
    else:
        return (spell, score)


def rule6_global(spells_and_scores):
    """Natural magic (global)."""
    all_cards = itertools.chain.from_iterable(
        spell for (spell, score) in spells_and_scores
    )

    try:
        max_magic = max(
            card.value for card in all_cards
            if card.kind == MAGIC
        )
    # If there are no magical spells, this rule did not apply
    except ValueError:
        return spells_and_scores
    else:
        return [
            (
                (spell, score + 5)
                if any(
                    card.kind == MAGIC and card.value == max_magic
                    for card in spell
                ) else
                (spell, score)
            )
            for (spell, score) in spells_and_scores
        ]


def rule7(spell, score):
    """Cauldrons."""
    if ingredients(spell) and all(card.boiled for card in ingredients(spell)):
        return (spell, score + 4)
    else:
        return (spell, score)


def rule8(spell, score):
    """Botany."""
    boiled_clovers = [
        card for card in ingredients(spell)
        if card.type == CLOVER and card.boiled
    ]
    boiled_mushrooms = [
        card for card in ingredients(spell)
        if card.type == MUSHROOM and card.boiled
    ]
    return (spell, score + 2*len(boiled_clovers) - 2*len(boiled_mushrooms))


def rule9(spell, score):
    """Amphibians."""
    toads = [card for card in ingredients(spell) if card.type == TOAD]
    if len(toads) >= 3:
        return (spell, score - 3)
    else:
        return (spell, score)


def rule10_11_local(spell, score):
    """Fungus, and mastering the occult (local)."""
    poisonous = [
        card for card in ingredients(spell)
        if card.type == TOAD or card.type == MUSHROOM
    ]
    if (len(spell) - len(poisonous)) < len(poisonous):
        return (spell + [occult], score)
    else:
        return (spell, score)


def rule10_11_global(spells_and_scores):
    """Fungus, and mastering the occult (global)."""
    num_occult_spells = len([
        spell for (spell, score) in spells_and_scores
        if occult in spell
    ])
    num_non_occult_spells = len([
        spell for (spell, score) in spells_and_scores
        if occult not in spell
    ])
    return [
        (
            (spell, score + num_non_occult_spells) if occult in spell else
            (spell, score - num_occult_spells)
        )
        for (spell, score) in spells_and_scores
    ]


def rule13(spell, score):
    """Visions and premonitions."""
    offered = next((card.value for card in spell if card.kind == "offer"), 0)
    return (spell, score + offered)


#
# Harnesses
#


def apply_rules(spells):
    local_rules = [
        # rule 2 precedes rule 1 because rule 2 removes volatiles before
        # scoring
        rule2,
        rule1,
        rule3,
        rule4,
        rule5,
        rule6_local,
        rule7,
        rule8,
        rule9,
        rule10_11_local,
        rule13,
    ]
    global_rules = [
        rule6_global,
        rule10_11_global,
    ]
    spells_and_scores = [(spell, 0) for spell in spells]
    local_applied = [
        reduce(
            lambda ss, rule: trace_local_score(rule)(*ss),
            local_rules,
            initial_ss,
        )
        for initial_ss in spells_and_scores
    ]
    global_applied = reduce(
        lambda sss, rule: rule(sss),
        global_rules,
        local_applied,
    )
    return global_applied


def _score(*spells):
    return apply_rules(parse(spells))
