import pytest

from pricing import calculate_total


def test_discount_does_not_reduce_taxable_basis():
    assert calculate_total(10000, discount_cents=1000, tax_basis_points=1000) == 10000


def test_discount_applies_after_tax_and_floors_at_zero():
    assert calculate_total(5000, discount_cents=6000, tax_basis_points=1000) == 0


def test_no_discount_still_applies_tax():
    assert calculate_total(2000, tax_basis_points=750) == 2150


def test_negative_inputs_are_rejected():
    with pytest.raises(ValueError):
        calculate_total(-1)
    with pytest.raises(ValueError):
        calculate_total(100, discount_cents=-1)
    with pytest.raises(ValueError):
        calculate_total(100, tax_basis_points=-1)
