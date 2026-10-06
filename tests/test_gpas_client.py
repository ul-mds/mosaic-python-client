import pytest
from zeep.exceptions import Fault

from mosaic_client.gpas import (
    DeletionResponse,
    Domain,
    DomainConfig,
    DomainResponse,
    Pseudonym,
    PseudonymNet,
    PseudonymTree,
    ValueToPseudonyms,
)
from tests.helpers import random_date, random_string


def test_get_or_create_pseudonym_for(gpas_client, gpas_domain):
    relation = gpas_client.get_or_create_pseudonyms_for(domain_name=gpas_domain, value=random_string())

    assert isinstance(relation, ValueToPseudonyms)


def test_get_or_create_pseudonym_for_list(gpas_client, gpas_domain):
    values = [random_string() for _ in range(5)]
    response = gpas_client.get_or_create_pseudonyms_for_list(
        domain_name=gpas_domain,
        values=values,
    )

    assert set(values) == {item.value for item in response}
    assert all(isinstance(item.pseudonyms, list) for item in response)


def test_get_value_for(gpas_client, gpas_domain, value_psn_pair):
    fetched_value = gpas_client.get_value_for(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)

    assert fetched_value == value_psn_pair.value


def test_get_value_for_list(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    fetched_pairs = gpas_client.get_value_for_list(
        domain_name=gpas_domain,
        pseudonyms=[pair.pseudonym for pair in pairs],
    )

    assert {pair.value for pair in pairs} == {value for _, value in fetched_pairs}


def test_get_pseudonym_for(gpas_client, gpas_domain, value_psn_pair):
    fetched = gpas_client.get_pseudonyms_for(domain_name=gpas_domain, value=value_psn_pair.value)

    assert fetched.pseudonyms == value_psn_pair.pseudonyms


def test_get_pseudonym_for_list(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    fetched_pairs = gpas_client.get_or_create_pseudonyms_for_list(
        domain_name=gpas_domain,
        values=[pair.value for pair in pairs],
    )

    assert {pair.pseudonym for pair in pairs} == {pair.pseudonym for pair in fetched_pairs}


def test_delete_entry(gpas_client, gpas_domain, value_psn_pair):
    gpas_client.delete_entry(domain_name=gpas_domain, value=value_psn_pair.value)

    with pytest.raises(Fault) as e:
        gpas_client.get_pseudonyms_for(domain_name=gpas_domain, value=value_psn_pair.value)

    assert str(e.value) == f"value {value_psn_pair.value} for domain {gpas_domain} not found"


def test_delete_entries(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    gpas_client.delete_entries(domain_name=gpas_domain, values=[pair.value for pair in pairs])

    for pair in pairs:
        with pytest.raises(Fault) as e:
            gpas_client.get_pseudonyms_for(domain_name=gpas_domain, value=pair.value)

        assert str(e.value) == f"value {pair.value} for domain {gpas_domain} not found"


def test_delete_pseudonym(gpas_client, gpas_domain, value_psn_pair):
    gpas_client.delete_pseudonym(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)

    with pytest.raises(Fault) as e:
        gpas_client.get_value_for(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)

    assert str(e.value) == f"value for pseudonym {value_psn_pair.pseudonym} not found within domain {gpas_domain}"


def test_delete_pseudonyms(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    responses = gpas_client.delete_pseudonyms(domain_name=gpas_domain, pseudonyms=[pair.pseudonym for pair in pairs])

    assert all(isinstance(response, DeletionResponse) for response in responses)
    assert all(response.result == "SUCCESS" for response in responses)


def test_insert_value_pseudonym_pair(gpas_client, gpas_domain, value_psn_pair):
    # Let gPAS create the pseudonym so it is valid for the domain when inserting it again.

    # Delete the entry first to check if the insertion really works.
    gpas_client.delete_entry(domain_name=gpas_domain, value=value_psn_pair.value)

    gpas_client.insert_value_pseudonym_pair(
        domain_name=gpas_domain,
        value=value_psn_pair.value,
        pseudonym=value_psn_pair.pseudonym,
    )

    assert gpas_client.get_pseudonyms_for(domain_name=gpas_domain, value=value_psn_pair.value) == value_psn_pair
    assert (
        gpas_client.get_value_for(
            domain_name=gpas_domain,
            pseudonym=value_psn_pair.pseudonym,
        )
        == value_psn_pair.value
    )


def test_insert_value_pseudonym_pairs(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]

    gpas_client.delete_entries(domain_name=gpas_domain, values=[pair.value for pair in pairs])

    gpas_client.insert_value_pseudonym_pairs(
        domain_name=gpas_domain,
        pairs=[(pair.value, pair.pseudonym) for pair in pairs],
    )

    search_for_pseudonyms = gpas_client.get_pseudonyms_for_list(
        domain_name=gpas_domain,
        values=[pair.value for pair in pairs],
    )
    assert {relation.pseudonym for relation in search_for_pseudonyms} == {pair.pseudonym for pair in pairs}

    search_for_values = gpas_client.get_value_for_list(
        domain_name=gpas_domain,
        pseudonyms=[pair.pseudonym for pair in pairs],
    )
    assert {value for _, value in search_for_values} == {pair.value for pair in pairs}


def test_get_domain(gpas_client, gpas_domain):
    fetched_domain = gpas_client.get_domain(domain_name=gpas_domain)

    assert fetched_domain.name == gpas_domain
    assert fetched_domain.label == gpas_domain


def test_list_domains(gpas_client, gpas_domain):
    fetched_domains = gpas_client.list_domains()

    assert gpas_domain in [d.name for d in fetched_domains]
    assert gpas_domain in [d.label for d in fetched_domains]


def test_validate_pseudonym(gpas_client, gpas_domain, value_psn_pair):
    # This should just not raise an error.
    gpas_client.validate_pseudonym(pseudonym=value_psn_pair.pseudonym, domain_name=gpas_domain)

    with pytest.raises(Fault) as e:
        psn = random_string()
        gpas_client.validate_pseudonym(pseudonym=psn, domain_name=gpas_domain)

    assert "invalid value" in str(e.value)


def test_is_anonym(gpas_client, gpas_domain, value_psn_pair):
    assert gpas_client.is_anonym(value=value_psn_pair.value) is False


def test_is_anonymized(gpas_client, gpas_domain, value_psn_pair):
    assert gpas_client.is_anonymized(pseudonym=value_psn_pair.pseudonym, domain_name=gpas_domain) is False


def test_update_pseudonym_expiration_date(gpas_client, gpas_domain, value_psn_pair):
    with pytest.raises(Fault) as e:
        gpas_client.update_pseudonym_expiration_date(
            domain_name=gpas_domain,
            pseudonym=value_psn_pair.pseudonym,
            expiration_date=random_date(),
        )

    assert str(e.value) == f"the domain {gpas_domain} does not allow pseudonyms with expiration date"


def test_anonymize_pseudonym(gpas_client, gpas_domain, value_psn_pair):
    gpas_client.anonymize_pseudonym(pseudonym=value_psn_pair.pseudonym, domain_name=gpas_domain)

    assert gpas_client.is_anonymized(pseudonym=value_psn_pair.pseudonym, domain_name=gpas_domain) is True

    # Delete anonymized entry because otherwise no new pseudonyms can be added.
    gpas_client.delete_pseudonym(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)


def test_anonymize_pseudonyms(gpas_client, gpas_domain, value_psn_pair_factory):
    pseudonyms = [value_psn_pair_factory().pseudonym for _ in range(5)]
    gpas_client.anonymize_pseudonyms(pseudonyms=pseudonyms, domain_name=gpas_domain)

    assert all(gpas_client.is_anonymized(pseudonym=psn, domain_name=gpas_domain) for psn in pseudonyms)

    # Delete anonymized entries because otherwise no new pseudonyms can be added.
    gpas_client.delete_pseudonyms(domain_name=gpas_domain, pseudonyms=pseudonyms)


def test_anonymize_entry(gpas_client, gpas_domain, value_psn_pair):
    gpas_client.anonymize_entry(domain_name=gpas_domain, value=value_psn_pair.value)

    assert gpas_client.is_anonymized(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym) is True

    # Delete anonymized entry because otherwise no new pseudonyms can be added.
    gpas_client.delete_pseudonym(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)


def test_anonymize_entries(gpas_client, gpas_domain, value_psn_pair_factory):
    pairs = [value_psn_pair_factory() for _ in range(5)]
    gpas_client.anonymize_entries(domain_name=gpas_domain, values=[pair.value for pair in pairs])

    assert all(gpas_client.is_anonymized(domain_name=gpas_domain, pseudonym=pair.pseudonym) for pair in pairs)

    # Delete anonymized entries because otherwise no new pseudonyms can be added.
    gpas_client.delete_pseudonyms(domain_name=gpas_domain, pseudonyms=[pair.pseudonym for pair in pairs])


def test_get_pseudonyms_for_value_prefix(gpas_client, gpas_domain, value_psn_pair):
    fetched_pairs = gpas_client.get_pseudonyms_for_value_prefix(
        domain_name=gpas_domain,
        value_prefix=value_psn_pair.value[0:3],
    )

    assert len(fetched_pairs) >= 1
    assert all(isinstance(pair, ValueToPseudonyms) for pair in fetched_pairs)
    assert any(pair.value == value_psn_pair.value for pair in fetched_pairs)


def test_get_pseudonym_tree(gpas_client, gpas_domain, value_psn_pair):
    tree = gpas_client.get_pseudonym_tree(domain_name=gpas_domain, pseudonym=value_psn_pair.pseudonym)

    assert isinstance(tree, PseudonymTree)


def test_get_pseudonym_net(gpas_client, value_psn_pair):
    net = gpas_client.get_pseudonym_net(value_or_pseudonym=value_psn_pair.value)

    assert isinstance(net, PseudonymNet)


def test_get_domains_for_prefix(gpas_client, gpas_domain):
    prefix, name = random_string(), random_string()
    gpas_client.add_domain(domain=Domain(name=name, label=name, config=DomainConfig(psn_prefix=prefix)))

    domains = gpas_client.get_domains_for_prefix(prefix=prefix)

    assert len(domains) == 1
    assert isinstance(domains[0], DomainResponse)
    assert domains[0].config.psn_prefix == prefix

    gpas_client.delete_domain(domain_name=name)


def test_get_domains_for_suffix(gpas_client, gpas_domain):
    suffix, name = random_string(), random_string()
    gpas_client.add_domain(domain=Domain(name=name, label=name, config=DomainConfig(psn_suffix=suffix)))

    domains = gpas_client.get_domains_for_suffix(suffix=suffix)

    assert len(domains) == 1
    assert isinstance(domains[0], DomainResponse)
    assert domains[0].config.psn_suffix == suffix

    gpas_client.delete_domain(domain_name=name)


def test_are_pseudonyms_deletable(gpas_client, gpas_domain):
    assert gpas_client.are_pseudonyms_deletable(domain_name=gpas_domain) is True


def test_list_pseudonyms(gpas_client, gpas_domain, value_psn_pair):
    psns = gpas_client.list_pseudonyms(domain_name=gpas_domain)

    assert all(isinstance(psn, Pseudonym) for psn in psns)
    assert any(psn.pseudonym == value_psn_pair.pseudonym for psn in psns)
