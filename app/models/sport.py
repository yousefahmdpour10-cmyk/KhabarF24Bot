"""
رشته‌های ورزشی
"""

from enum import Enum


class Sport(str, Enum):
    """
    رشته‌های ورزشی KhabarF24
    """

    FOOTBALL = "football"
    FUTSAL = "futsal"

    BASKETBALL = "basketball"
    VOLLEYBALL = "volleyball"

    TENNIS = "tennis"
    TABLE_TENNIS = "table_tennis"

    WRESTLING = "wrestling"
    BOXING = "boxing"

    MMA = "mma"
    UFC = "ufc"

    JUDO = "judo"
    TAEKWONDO = "taekwondo"
    KARATE = "karate"

    HANDBALL = "handball"

    ATHLETICS = "athletics"

    CYCLING = "cycling"

    SWIMMING = "swimming"

    GYMNASTICS = "gymnastics"

    MOTORSPORT = "motorsport"

    FORMULA1 = "formula1"

    MOTOGP = "motogp"

    CHESS = "chess"

    ESPORTS = "esports"

    OTHER = "other"
