from functools import partial
from operator import itemgetter


def passes_threshold(pair_baskets: int, *, minimum: int = 10) -> bool:
    if pair_baskets < 0 or minimum < 0:
        raise ValueError("Counts and thresholds must not be negative.")
    return pair_baskets >= minimum


def add_note(note: str, notes: list[str] | None = None) -> list[str]:
    if notes is None:
        notes = []
    notes.append(note)
    return notes


def format_notes(*notes: str, separator: str = "; ") -> str:
    return separator.join(notes)


def describe_settings(**settings: int) -> str:
    return ", ".join(f"{name}={value}" for name, value in settings.items())


def main() -> None:
    print(passes_threshold(12))
    settings = {"minimum": 20}
    print(passes_threshold(12, **settings))
    print(add_note("Check coverage"))
    print(add_note("Check category mapping"))
    messages = ["Historical data", "Not a causal estimate"]
    print(format_notes(*messages, separator=" | "))
    print(describe_settings(minimum=10, category_minimum=50))
    strict_check = partial(passes_threshold, minimum=20)
    print("Configured check:", strict_check(12))
    rows = [{"pair": "A–B", "count": 4}, {"pair": "A–C", "count": 12}]
    print("Sorted:", sorted(rows, key=itemgetter("count"), reverse=True))


if __name__ == "__main__":
    main()
