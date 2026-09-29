import pytest
from zeep.exceptions import Fault

from tests.helpers import random_string


def test_get_or_create_pseudonym_for(gpas_client, gpas_domain):
    psn = gpas_client.get_or_create_pseudonym_for(domain_name=gpas_domain, value=random_string())

    assert isinstance(psn, str)


def test_get_or_create_pseudonym_for_list(gpas_client, gpas_domain):
    values = [random_string() for _ in range(5)]
    key_value_pairs = gpas_client.get_or_create_pseudonym_for_list(
        domain_name=gpas_domain,
        values=values,
    )

    assert set(values) == {kv[0] for kv in key_value_pairs}
    assert all(isinstance(kv[1], str) for kv in key_value_pairs)


def test_get_value_for(gpas_client, gpas_domain, value_psn_pair):
    value, psn = value_psn_pair
    fetched_value = gpas_client.get_value_for(domain_name=gpas_domain, pseudonym=psn)

    assert fetched_value == value


def test_get_value_for_list(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    fetched_pairs = gpas_client.get_value_for_list(
        domain_name=gpas_domain,
        pseudonyms=[pair[1] for pair in pairs],
    )

    assert set(pairs) == {(psn, value) for value, psn in fetched_pairs}


def test_get_pseudonym_for(gpas_client, gpas_domain, value_psn_pair):
    value, psn = value_psn_pair
    fetched_psn = gpas_client.get_pseudonym_for(domain_name=gpas_domain, value=value)

    assert fetched_psn == psn


def test_get_pseudonym_for_list(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    fetched_pairs = gpas_client.get_or_create_pseudonym_for_list(
        domain_name=gpas_domain,
        values=[pair[0] for pair in pairs],
    )

    assert set(pairs) == set(fetched_pairs)


def test_delete_entry(gpas_client, gpas_domain, value_psn_pair):
    value, _ = value_psn_pair
    gpas_client.delete_entry(domain_name=gpas_domain, value=value)

    with pytest.raises(Fault) as e:
        gpas_client.get_pseudonym_for(domain_name=gpas_domain, value=value)

    assert str(e.value) == f"value {value} for domain {gpas_domain} not found"


def test_delete_entries(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    gpas_client.delete_entries(domain_name=gpas_domain, values=[pair[0] for pair in pairs])

    for value, _ in pairs:
        with pytest.raises(Fault) as e:
            gpas_client.get_pseudonym_for(domain_name=gpas_domain, value=value)

        assert str(e.value) == f"value {value} for domain {gpas_domain} not found"


def test_insert_value_pseudonym_pair(gpas_client, gpas_domain, value_psn_pair):
    value, psn = value_psn_pair  # Let gPAS create the pseudonym so it is valid for the domain when inserting it again.

    # Delete the entry first to check if the insertion really works.
    gpas_client.delete_entry(domain_name=gpas_domain, value=value)

    gpas_client.insert_value_pseudonym_pair(domain_name=gpas_domain, value=value, pseudonym=psn)

    assert gpas_client.get_pseudonym_for(domain_name=gpas_domain, value=value) == psn
    assert gpas_client.get_value_for(domain_name=gpas_domain, pseudonym=psn) == value


def test_insert_value_pseudonym_pairs(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]

    gpas_client.delete_entries(domain_name=gpas_domain, values=[pair[0] for pair in pairs])

    gpas_client.insert_value_pseudonym_pairs(domain_name=gpas_domain, pairs=pairs)

    assert set(
        gpas_client.get_pseudonym_for_list(
            domain_name=gpas_domain,
            values=[pair[0] for pair in pairs],
        )
    ) == set(pairs)
    assert set(
        gpas_client.get_value_for_list(
            domain_name=gpas_domain,
            pseudonyms=[pair[1] for pair in pairs],
        )
    ) == {(psn, value) for value, psn in pairs}


def test_get_domain(gpas_client, gpas_domain):
    fetched_domain = gpas_client.get_domain(domain_name=gpas_domain)

    assert fetched_domain.name == gpas_domain
    assert fetched_domain.label == gpas_domain


def test_list_domains(gpas_client, gpas_domain):
    fetched_domains = gpas_client.list_domains()

    assert gpas_domain in [d.name for d in fetched_domains]
    assert gpas_domain in [d.label for d in fetched_domains]
