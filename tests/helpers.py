import datetime
import random
import string

from mosaic_client.epix import Identity


def random_string(charset=string.ascii_letters, length: int = 20) -> str:
    assert length > 0
    assert len(charset) > 0

    return "".join([random.choice(charset) for _ in range(length)])


def random_identity() -> Identity:
    return Identity(
        first_name=random_string(),
        last_name=random_string(),
        birth_date=datetime.datetime.now(tz=datetime.UTC),
        gender=random.choice(["m", "f"]),
    )


def random_date(max_days: int = 100) -> datetime.date:
    delta = random.randint(1, max_days)
    return datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=delta)
