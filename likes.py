# from pprint import pprint

import functools
import operator
import re

import emoji

def likes_list(likes):
    em_split_emoji = emoji.get_emoji_regexp().split(likes)
    em_split_whitespace = [substr.split() for substr in em_split_emoji]
    em_split = functools.reduce(operator.concat, em_split_whitespace)
    return em_split