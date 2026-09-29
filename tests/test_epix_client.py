from dataclasses import replace

from mosaic_client.epix import Deduplication, Domain, DomainConfiguration, IdentifierDomain, Identity, Reason, Source
from tests.helpers import random_identity, random_string


def test_request_mpi(epix_client, epix_domain, epix_source):
    r = epix_client.request_mpi(domain_name=epix_domain, source_name=epix_source, identity=random_identity())

    assert r.mpi_error_code is None

    epix_client.deactivate_person(domain_name=epix_domain, mpi_id=r.person.mpi())
    epix_client.delete_person(domain_name=epix_domain, mpi_id=r.person.mpi())


def test_request_mpi_batch(epix_client, epix_domain, epix_source):
    r = epix_client.request_mpi_batch(
        domain_name=epix_domain,
        source_name=epix_source,
        identities=[random_identity() for _ in range(5)],
    )

    assert all(entry.mpi_error_code is None for entry in r)

    for entry in r:
        epix_client.deactivate_person(domain_name=epix_domain, mpi_id=entry.person.mpi())
        epix_client.delete_person(domain_name=epix_domain, mpi_id=entry.person.mpi())


def test_get_person_by_mpi(epix_client, epix_domain, epix_source, person):
    r = epix_client.get_person_by_mpi(domain_name=epix_domain, mpi_id=person.mpi())

    assert person.mpi() == r.mpi()


def test_update_person(epix_client, epix_domain, epix_source, person):
    new_first_name = random_string()
    identity = person.reference_identity
    new_identity = Identity(
        first_name=new_first_name,
        last_name=identity.last_name,
        birth_date=identity.birth_date,
        gender=identity.gender,
    )

    r = epix_client.update_person(
        domain_name=epix_domain,
        source_name=epix_source,
        mpi_id=person.mpi(),
        identity=new_identity,
        force=True,
    )

    assert r.person.reference_identity.first_name == new_first_name


def test_get_persons_for_domain(epix_client, epix_domain, epix_source, person):
    persons = epix_client.get_persons_for_domain(domain_name=epix_domain)

    assert person.mpi() in [p.mpi() for p in persons]


def test_get_identities_for_domain(epix_client, epix_domain, person):
    identities = epix_client.get_identities_for_domain(domain_name=epix_domain)

    assert person.reference_identity.identity_id in [i.identity_id for i in identities]


def test_deactivate_identity(epix_client, epix_domain, epix_source, person):
    id_ = person.reference_identity.identity_id

    assert isinstance(id_, int)  # There should be an identity since the person was just created.

    epix_client.deactivate_identity(identity_id=id_)

    identities = epix_client.get_identities_for_domain(domain_name=epix_domain)

    assert person.reference_identity.identity_id not in [i.identity_id for i in identities]


def test_deactivate_person(epix_client, epix_domain, epix_source, person):
    epix_client.deactivate_person(domain_name=epix_domain, mpi_id=person.mpi())

    persons = epix_client.get_persons_for_domain(domain_name=epix_domain)

    assert person.mpi() not in [p.mpi() for p in persons]


def test_delete_identity(epix_client, epix_domain, epix_source, person):
    id_ = person.reference_identity.identity_id

    assert isinstance(id_, int)  # There should be an identity since the person was just created.

    epix_client.deactivate_identity(identity_id=id_)
    epix_client.delete_identity(identity_id=id_)

    identities = epix_client.get_identities_for_domain(domain_name=epix_domain)

    assert person.reference_identity.identity_id not in [i.identity_id for i in identities]


def test_get_identifier_domain(epix_client, epix_identifier_domain):
    fetched_domain = epix_client.get_identifier_domain(identifier_domain_name=epix_identifier_domain)

    assert fetched_domain.name == epix_identifier_domain
    assert fetched_domain.label == epix_identifier_domain


def test_get_identifier_domains(epix_client, epix_identifier_domain):
    fetched_domains = epix_client.get_identifier_domains()

    assert epix_identifier_domain in [d.name for d in fetched_domains]
    assert epix_identifier_domain in [d.label for d in fetched_domains]


def test_update_identifier_domain(epix_client):
    name = random_string()
    epix_client.add_identifier_domain(identifier_domain=IdentifierDomain(name=name, label=name))

    oid = random_string()
    epix_client.update_identifier_domain(identifier_domain=IdentifierDomain(name=name, label=name, oid=oid))

    assert oid == epix_client.get_identifier_domain(identifier_domain_name=name).oid

    epix_client.delete_identifier_domain(identifier_domain_name=name)


def test_get_source(epix_client, epix_source):
    fetched_source = epix_client.get_source(source_name=epix_source)

    assert fetched_source.name == epix_source
    assert fetched_source.label == epix_source


def test_get_sources(epix_client, epix_source):
    fetched_sources = epix_client.get_sources()

    assert epix_source in [s.name for s in fetched_sources]
    assert epix_source in [s.label for s in fetched_sources]


def test_update_source(epix_client):
    name = random_string()
    epix_client.add_source(source=Source(name=name))

    description = random_string()
    epix_client.update_source(source=Source(name=name, description=description))

    assert description == epix_client.get_source(source_name=name).description

    epix_client.delete_source(source_name=name)


def test_get_domain(epix_client, epix_domain):
    fetched_domain = epix_client.get_domain(domain_name=epix_domain)

    assert fetched_domain.name == epix_domain
    assert fetched_domain.label == epix_domain


def test_get_domains(epix_client, epix_domain):
    fetched_domains = epix_client.get_domains()

    assert epix_domain in [d.name for d in fetched_domains]
    assert epix_domain in [d.label for d in fetched_domains]


def test_get_config_for_domain(epix_client, epix_domain):
    fetched_config = epix_client.get_config_for_domain(domain_name=epix_domain)

    assert isinstance(fetched_config, DomainConfiguration)


def test_get_defined_deduplication_reasons(epix_client, epix_domain):
    fetched_reasons = epix_client.get_defined_deduplication_reasons(domain_name=epix_domain)

    assert len(fetched_reasons) == 0


def test_update_domain_in_use(epix_client, epix_identifier_domain, epix_source):
    name = random_string()
    epix_client.add_domain(
        domain=Domain(
            name=name,
            label=name,
            mpi_domain=epix_client.get_identifier_domain(identifier_domain_name=epix_identifier_domain),
            safe_source=epix_client.get_source(source_name=epix_source),
        )
    )

    new_description = random_string()
    new_domain = epix_client.update_domain_in_use(domain_name=name, label=name, description=new_description)

    assert new_domain.description == new_description

    epix_client.delete_domain(domain_name=name, force=True)


def test_update_domain(epix_client, epix_identifier_domain, epix_source):
    name = random_string()
    domain = Domain(
        name=name,
        label=name,
        mpi_domain=epix_client.get_identifier_domain(identifier_domain_name=epix_identifier_domain),
        safe_source=epix_client.get_source(source_name=epix_source),
    )
    epix_client.add_domain(domain=domain)

    reason = random_string()
    new_domain = replace(
        domain,
        config_objects=DomainConfiguration(deduplication=Deduplication(reasons=[Reason(name=reason)])),
    )
    updated_domain = epix_client.update_domain(domain=new_domain)

    assert updated_domain.config_objects.deduplication is not None
    assert len(updated_domain.config_objects.deduplication.reasons) == 1
    assert updated_domain.config_objects.deduplication.reasons[0].name == reason

    epix_client.delete_domain(domain_name=name, force=True)
