from enum import Enum


class Crcy(Enum):
    EUR = 'EUR'
    USD = 'USD'
    VND = 'VND'

    @staticmethod
    def fin(val: str) -> "Crcy":
        if not val:
            # noinspection PyTypeChecker
            return None
        for k, v in Crcy.__members__.items():
            if val == k:
                return v
        # noinspection PyTypeChecker
        return None
