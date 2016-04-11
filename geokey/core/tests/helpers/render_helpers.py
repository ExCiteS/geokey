"""Core render helpers."""

from re import sub


def remove_csrf(decoded_input):
    csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
    return sub(csrf_regex, '', decoded_input)
