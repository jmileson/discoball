# Side quest 3: Numbers, units, and calculations

A program can execute a calculation perfectly and still produce a meaningless
answer. In this side quest, you will work with Python numbers while keeping their
units, denominators, and limitations visible.

Allow 45–60 minutes. Complete [Text, bytes, and files](text_bytes_files.md) first.
Use the lesson's `practice.py` for experiments.

## 1. Distinguish whole counts from approximate values

```python
pair_baskets = 4
eligible_baskets = 100
support = pair_baskets / eligible_baskets
print(type(pair_baskets))
print(type(support))
print(f"Support: {support:.1%}")
```

Counts here are `int` values. Division produces a `float`, even when both operands
are integers. Floats use a binary representation that approximates many decimal
fractions. Python integers are not limited to a fixed 32-bit range, although huge
values still consume memory and computation.

Type is not a unit. Python does not know whether `100` means baskets, customers,
pounds, or pence. Use names and documented assumptions to keep them distinct.

## 2. Read arithmetic explicitly

| Operation | Example | Result |
| --- | --- | --- |
| Addition | `5 + 2` | `7` |
| Subtraction | `5 - 2` | `3` |
| Multiplication | `5 * 2` | `10` |
| Division | `5 / 2` | `2.5` |
| Floor division | `5 // 2` | `2` |
| Remainder | `5 % 2` | `1` |
| Exponentiation | `5 ** 2` | `25` |

Multiplication and division have priority over addition and subtraction.
Exponentiation has higher priority still. Prefer parentheses when the intended
calculation would otherwise be hard to read: `pair_baskets / (a_baskets * b_rate)`.
Python's `^` is not exponentiation.

Floor division rounds the quotient down toward negative infinity, not toward zero:
`-5 // 2` is `-3`. The corresponding remainder is `1`, preserving the relationship
`a == (a // b) * b + (a % b)` for these integers.

**Your turn:** predict `2 + 3 * 4` and `(2 + 3) * 4`. Then compare `-5 // 2` with
`int(-5 / 2)`. Why should “remove the decimal part” not be your explanation of `//`?

## 3. Validate conversions and denominators

`int("4")` converts valid integer text. `float("0.04")` converts valid decimal
text to a float. `int("4.5")` fails; converting a float with `int(4.5)` instead
truncates toward zero. Do not silently turn fractional quantities into counts.

`None` is not zero. If the denominator is missing, a rate is unknown. If it is zero,
the rate is undefined. Neither should automatically become a reported rate of zero.

Read the `support` function in [examples/numbers.py](examples/numbers.py). It checks
that the population is positive and the pair count lies within it. Its type hints
document integers but do not enforce them at runtime; this is an exercise function
with an explicit expected input contract, not a universal numeric validator.

**Your turn:** call it with `(0, 100)`, `(4, 100)`, `(4, 0)`, and `(101, 100)`.
Explain the difference between a valid zero result and a rejected calculation.

## 4. Compare approximate results appropriately

```python
import math

print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(math.isclose(0.1 + 0.2, 0.3))
```

Expect a small representation difference, `False`, and `True`. `isclose` compares
with a tolerance. Choose tolerances according to the scale and purpose, not just
to make a failed test pass. Near zero, an appropriate absolute tolerance can be
important. Counts usually need exact equality; approximate rates may not.

Other useful tools:

- `sum(values)` adds values; an empty list sums to zero by default.
- `min(values)` and `max(values)` find extremes; empty inputs raise an error unless
  you explicitly provide a default.
- `abs(value)` gives magnitude.
- `math.floor` and `math.ceil` round down and up to integer boundaries.
- `math.isfinite` checks whether a float is neither infinity nor NaN.

Some conversions accept non-finite values, such as `float("nan")`. A successful
conversion is therefore not complete validation. A NaN does not compare equal to
itself; check it deliberately rather than treating it as ordinary missing data.

## 5. Separate rounding from presentation

```python
rate = 1 / 3
print(round(rate, 2))
print(f"{rate:.2%}")
print(rate)
print(round(2.5), round(3.5))
```

`round(rate, 2)` produces a rounded numerical result. Formatting produces display
text. Neither assignment nor display above replaces `rate`, so it retains its
original value.

Python's built-in `round` uses ties-to-even for exact halfway cases: `2.5` becomes
`2` and `3.5` becomes `4`. Binary approximation can also affect whether a decimal-
looking value is actually halfway. Do not assume every system uses the same
financial rounding policy.

Keep useful precision through intermediate steps. Rounding every rate before
combining them can introduce avoidable differences.

## 6. Use Decimal when decimal arithmetic is the requirement

```python
from decimal import ROUND_HALF_UP, Decimal

amount = Decimal("2.345")
rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(rounded)
```

Expect `2.35`. Construct from strings such as `"2.345"`, not from a binary float
whose approximation you have already introduced. Decimal arithmetic has its own
precision context and division can still require rounding; it does not eliminate
the need for an agreed calculation policy.

Do not casually mix `Decimal` and `float` arithmetic. Decide where conversion
belongs. Decimal can be useful for financial calculations, while floats remain
appropriate for many rates, measurements, and statistical operations.

JSON's default writer does not serialize `Decimal` automatically. Decide whether
to transmit a decimal string, scaled integer, or another agreed representation;
converting to float just to silence an error can lose the precision you wanted.

## 7. Use a hypothetical scenario without inventing evidence

Run:

```powershell
uv run python -m discoball.lesson_5.examples.numbers
```

The final calculation uses **invented** inputs: 8,000 A baskets without B, £5 of
contribution per additional purchase, and £1,000 to recover. If every one of those
baskets added B, the contribution ceiling would be £40,000 before other effects.
Recovering £1,000 would require 200 additional purchases, or 2.5% of those 8,000
opportunities, under these assumptions.

This is an optimistic scenario and a break-even calculation, not an estimate of
actual intervention effects. The dataset does not supply those margins or costs.
Discounting existing purchases, cannibalization, exposure, and fulfillment costs
could change the result. Historical headroom is not a count of willing buyers.

**Your turn:** change the cost or margin, predict the direction of change, then
calculate it. What information would you request before proposing an experiment?

## Finish with an explanation

Describe which quantities need exact counts, which use approximate rates, and
which require an explicit monetary rounding policy. State the denominator and
units of every rate in your scenario.

Continue to [Functions and clear inputs](functions.md), or return to
[Lesson 5](README.md).
