import math
from decimal import ROUND_HALF_UP, Decimal


def support(pair_baskets: int, eligible_baskets: int) -> float:
    if eligible_baskets <= 0:
        raise ValueError("Eligible baskets must be positive.")
    if not 0 <= pair_baskets <= eligible_baskets:
        raise ValueError("Pair baskets must be between zero and the population.")
    return pair_baskets / eligible_baskets


def main() -> None:
    rate = support(4, 100)
    print(f"Pair support: {rate:.1%}")
    print("Float equality:", 0.1 + 0.2 == 0.3)
    print("Close enough for this comparison:", math.isclose(0.1 + 0.2, 0.3))
    print("Floor division:", -5 // 2, "remainder:", -5 % 2)
    print("Round halves to even:", round(2.5), round(3.5))
    amount = Decimal("2.345")
    print(
        "Explicit decimal policy:",
        amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )

    # Invented commercial inputs in US dollars, not values measured from Olist.
    missing_b_baskets = 8_000
    margin_per_addition = Decimal("5.00")
    cost_to_recover = Decimal("1000.00")
    ceiling = missing_b_baskets * margin_per_addition
    break_even_rate = cost_to_recover / ceiling
    print(f"Hypothetical optimistic contribution ceiling: ${ceiling:,.2f}")
    print(f"Hypothetical break-even additional attachment: {break_even_rate:.1%}")
    print("This scenario is not a prediction of an intervention's effect.")


if __name__ == "__main__":
    main()
