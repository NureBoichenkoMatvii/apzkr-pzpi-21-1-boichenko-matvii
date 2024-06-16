from enum import StrEnum

from fastapi import Header
from extensions.babel import babel


class AcceptedLanguages(StrEnum):
    en = "en_US"
    uk = "uk_UA"


def get_accept_language(accept_language: str = Header(AcceptedLanguages.en, title="Accept-Language")):
    """
    Custom dependency to extract and return the Accept-Language header from the request.
    """
    if babel.locale not in AcceptedLanguages.__members__.values():
        babel.locale = AcceptedLanguages.en

    return accept_language
