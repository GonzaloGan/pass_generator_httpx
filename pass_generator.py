import asyncio
import json
import re
from random import shuffle, randrange as rng
from sys import stderr

import httpx

# Constants
URL = "https://www.randomlists.com/data/things.json"
MIN_LENGTH = 10
NUM_SPECIAL_CHARS = 2
# Yep, some es_ES.utf-8 only chars in here
TRANSFORMABLE_CHARS = {"a": "@", "e": "€", "i": "¡", "o": "0", "s": "$"}
TRANSFORMABLE_CHARS_REGEX = r"[@€¡\$]"


async def get_call(url) -> dict:
    deserialized_json = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            deserialized_json = json.loads(response.text)
    except Exception as e:
        print(e, file=stderr)
    return deserialized_json


def has_special_characters(s_to_check) -> bool:
    regex = re.compile(TRANSFORMABLE_CHARS_REGEX)
    return regex.search(s_to_check) is not None


def add_special_characters(s_to_add_chars) -> str:
    new_str = ""
    change_count = NUM_SPECIAL_CHARS
    for char in s_to_add_chars:
        if change_count > 0 and char in list(TRANSFORMABLE_CHARS.keys()):
            new_str += TRANSFORMABLE_CHARS[char]
            change_count -= 1
        else:
            new_str += char
    if not has_special_characters(new_str):
        new_str += "@"
    return new_str


def reformat_phrase(phrase) -> str:
    reformatted_phrase = phrase.title()
    return "".join(reformatted_phrase.split())


def reformat_phrase_list(phrase_list) -> list:
    reformat_list = []
    for ph in phrase_list:
        reformat_list.append(reformat_phrase(ph))
    return reformat_list


def get_pass_from_list(password_list, iterations) -> str:
    phrases = []
    password_conditions_done = False
    # Repeat until conditions done
    while not password_conditions_done:
        phrases.clear()
        for i in range(iterations):
            phrases.append(password_list[rng(len(password_list))])
        tmp_phrase = phrases[0]
        phrases[0] = add_special_characters(phrases[0])
        password_length = len(phrases[0]) + len(phrases[1]) + 2
        password_conditions_done = \
            password_length >= MIN_LENGTH and tmp_phrase != phrases[0]
    return "{}{}{}".format(phrases[0], phrases[1], rng(10, 100))


async def main() -> None:
    try:
        dt = await get_call(URL)
        unformatted_phrase_list = dt["RandL"]["items"]
        phrase_list = reformat_phrase_list(unformatted_phrase_list)
        shuffle(phrase_list)
        print(get_pass_from_list(phrase_list, 2))
    except Exception as e:
        print(e, file=stderr)


if __name__ == "__main__":
    asyncio.run(main())
