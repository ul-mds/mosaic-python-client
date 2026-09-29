"""
This module contains functions for interacting with the E-PIX SOAP interface.
"""

from zeep import Client

from mosaic_client.epix.models import (
    BatchRequestConfig,
    BatchResponseEntry,
    Domain,
    DomainConfiguration,
    FullIdentity,
    IdentifierDomain,
    Identity,
    Person,
    Reason,
    ResponseEntry,
    Source,
)
from mosaic_client.epix.schemas import (
    BatchRequestConfigSchema,
    DomainConfigurationSchema,
    DomainSchema,
    FullIdentitySchema,
    IdentifierDomainSchema,
    IdentitySchema,
    PersonSchema,
    ReasonSchema,
    ResponseEntrySchema,
    SourceSchema,
)
from mosaic_client.helpers import WSDLClient, _cast_client, _read_key_value_entry_response, _serialize_dict


def request_mpi(
    client: Client, domain_name: str, source_name: str, identity: Identity, comment: str | None = None
) -> ResponseEntry:
    """
    Requests an MPI for an identity. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identity belongs
    :param source_name: source name from which the identity stems
    :param identity: identity to request MPI for
    :param comment: optional comment on this transaction
    :return: MPI response, indicating whether the identity already exists and containing the assigned MPI
    """
    identity_soap = IdentitySchema().dump(identity)
    response_entry_soap = client.service.requestMPI(
        domainName=domain_name,
        identity=identity_soap,
        sourceName=source_name,
        comment=comment,
    )

    return ResponseEntrySchema().load(_serialize_dict(response_entry_soap))


def get_person_by_mpi(client: Client, domain_name: str, mpi_id: str) -> Person:
    """
    Returns a person by their MPI. This function throws a Fault if the MPI is not present.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for the person
    :param mpi_id: MPI of the desired person
    :return: person assigned to the specified MPI
    """
    person_soap = client.service.getPersonByMPI(domainName=domain_name, mpiId=mpi_id)
    return PersonSchema().load(_serialize_dict(person_soap))


def _malformed_mpi_response(reason: str) -> ValueError:
    """
    Returns an error to indicate a malformed E-PIX response.

    :param reason: reason for error
    :return: ValueError with specified reason
    """
    return ValueError(f"MPI response is malformed: {reason}")


def update_person(
    client: Client,
    domain_name: str,
    source_name: str,
    mpi_id: str,
    identity: Identity,
    force: bool = False,
    comment: str | None = None,
) -> ResponseEntry:
    """
    Updates an identity, addressed by their MPI. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identity belongs
    :param source_name: source name from which the identity stems
    :param mpi_id: MPI of the person to update
    :param identity: identity with updated information
    :param force: undocumented API option
    :param comment: optional comment on this transaction
    :return: updated person record
    """
    identity_soap = IdentitySchema().dump(identity)
    response_entry_soap = client.service.updatePerson(
        domainName=domain_name,
        sourceName=source_name,
        mpiId=mpi_id,
        identity=identity_soap,
        force=force,
        comment=comment,
    )

    return ResponseEntrySchema().load(_serialize_dict(response_entry_soap))


def get_persons_for_domain(client: Client, domain_name: str) -> list[Person]:
    """
    Returns a list of persons stored in a domain. This function throws a Fault if the specified domain
    doesn't exist.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for persons
    :return: list of persons inside the specified domain
    """
    persons_lst = _serialize_dict(client.service.getPersonsForDomain(domainName=domain_name))

    return [PersonSchema().load(person) for person in persons_lst]


def get_identities_for_domain(client: Client, domain_name: str) -> list[FullIdentity]:
    """
    Returns a list of identities stored in a domain. This function throws a Fault if the specified domain
    doesn't exist.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look for identities
    :return: list of identities inside the specified domain
    """
    identity_lst = _serialize_dict(client.service.getIdentitiesForDomain(domainName=domain_name))

    return [FullIdentitySchema().load(identity) for identity in identity_lst]


def deactivate_identity(client: Client, identity_id: int) -> None:
    """
    Deactivates an identity based on their identity ID (not MPI!). This function throws a Fault if the
    specified identity ID cannot be found.

    :param client: Zeep client with E-PIX service definitions
    :param identity_id: ID of the identity to deactivate
    :return: nothing
    """
    client.service.deactivateIdentity(identityId=identity_id)


def deactivate_person(client: Client, domain_name: str, mpi_id: str) -> None:
    """
    Deactivates a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
    in the provided data domain.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look up the MPI
    :param mpi_id: MPI of the person to deactivate
    :return: nothing
    """
    client.service.deactivatePerson(domainName=domain_name, mpiId=mpi_id)


def delete_identity(client: Client, identity_id: int) -> None:
    """
    Deletes an identity based on their identity ID (not MPI!). This function throws a Fault if the
    specified identity ID cannot be found, or if the identity with the ID has not been deactivated yet.


    :param client: Zeep client with E-PIX service definitions
    :param identity_id: ID of the identity to delete
    :return: nothing
    """
    client.service.deleteIdentity(identityId=identity_id)


def delete_person(client: Client, domain_name: str, mpi_id: str) -> None:
    """
    Deletes a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
    in the provided data domain, or if the identity with the ID has not been deactivated yet.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain in which to look up the MPI
    :param mpi_id: MPI of the person to delete
    :return: nothing
    """
    client.service.deletePerson(domainName=domain_name, mpiId=mpi_id)


def request_mpi_batch(
    client: Client,
    domain_name: str,
    source_name: str,
    identities: list[Identity],
    config: BatchRequestConfig | None = None,
    comment: str | None = None,
) -> list[BatchResponseEntry]:
    """
    Requests MPIs for a list of identities. This function throws a Fault if any required identity fields
    are missing, as per the domain configuration.

    :param client: Zeep client with E-PIX service definitions
    :param domain_name: data domain to which the identities belong
    :param source_name: source name from which the identities stem
    :param identities: identities to request MPIs for
    :param config: optional configuration on how to handle this request
    :param comment: optional comment on this transaction
    :return: list of MPI responses, indicating whether an identity already exists and containing the assigned MPI
    """
    # load config if present
    if config is not None:
        config = BatchRequestConfigSchema().dump(config)

    response_soap = client.service.requestMPIBatch(
        mpiRequest={
            "comment": comment,
            "domainName": domain_name,
            "requestConfig": config,
            "requestEntries": [IdentitySchema().dump(identity) for identity in identities],
            "sourceName": source_name,
        }
    )

    key_value_lst = _read_key_value_entry_response(_serialize_dict(response_soap))
    batch_response_entry_lst: list[BatchResponseEntry] = []

    for kv_entry in key_value_lst:
        identity = IdentitySchema().load(kv_entry[0])
        response_entry = ResponseEntrySchema().load(kv_entry[1])

        batch_response_entry_lst.append(
            BatchResponseEntry(
                match_status=response_entry.match_status,
                person=response_entry.person,
                identity=identity,
                mpi_error_code=response_entry.mpi_error_code,
            )
        )

    return batch_response_entry_lst


def add_identifier_domain(client: Client, identifier_domain: IdentifierDomain) -> None:
    """
    Adds a new identifier domain.

    :param client: Zeep client with E-PIX management service definitions
    :param identifier_domain: identifier domain data class to create
    """
    domain_soap = IdentifierDomainSchema().dump(identifier_domain)
    client.service.addIdentifierDomain(domain_soap)


def get_identifier_domain(client: Client, domain_name: str) -> IdentifierDomain:
    """
    Gets an identifier domain by its name.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the identifier domain to get
    :return: identifier domain instance
    """
    domain_soap = client.service.getIdentifierDomain(identifierDomainName=domain_name)
    return IdentifierDomainSchema().load(_serialize_dict(domain_soap))


def get_identifier_domains(client: Client) -> list[IdentifierDomain]:
    """
    Lists all available identifier domains in the E-PIX instance.

    :param client: Zeep client with E-PIX management service definitions
    :return: list of all available identifier domains as identifier domain instances
    """
    domains = _serialize_dict(client.service.getIdentifierDomains())
    return [IdentifierDomainSchema().load(domain) for domain in domains]


def delete_identifier_domain(client: Client, domain_name: str) -> None:
    """
    Deletes an identifier domain that matches the specified name. Raises a Fault if there is no identifier domain with
    such a name.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the identifier domain to delete
    """
    client.service.deleteIdentifierDomain(identifierDomainName=domain_name)


def update_identifier_domain(client: Client, identifier_domain: IdentifierDomain) -> IdentifierDomain:
    """
    Updates an identifier domain with the given identifier domain instance.

    :param client: Zeep client with E-PIX management service definitions
    :param identifier_domain: identifier domain data class with update information
    :return: updated identifier domain instance
    """
    domain_soap = IdentifierDomainSchema().dump(identifier_domain)
    response_domain_soap = client.service.updateIdentifierDomain(identifierDomain=domain_soap)
    return IdentifierDomainSchema().load(_serialize_dict(response_domain_soap))


def add_source(client: Client, source: Source) -> None:
    """
    Adds a new data source.

    :param client: Zeep client with E-PIX management service definitions
    :param source: source data class to create
    """
    source_soap = SourceSchema().dump(source)
    client.service.addSource(source=source_soap)


def get_source(client: Client, source_name: str) -> Source:
    """
    Gets a data source by its name.

    :param client: Zeep client with E-PIX management service definitions
    :param source_name: name of the data source to get
    :return: source instance
    """
    source_soap = client.service.getSource(sourceName=source_name)
    return SourceSchema().load(_serialize_dict(source_soap))


def get_sources(client: Client) -> list[Source]:
    """
    Lists all available data sources in the E-PIX instance.

    :param client: Zeep client with E-PIX management service definitions
    :return: list of all available data sources as source instances
    """
    sources = _serialize_dict(client.service.getSources())
    return [SourceSchema().load(source) for source in sources]


def delete_source(client: Client, source_name: str) -> None:
    """
    Deletes a data source that matches the specified name. Raises a Fault if there is no data source with such a name.

    :param client: Zeep client with E-PIX management service definitions
    :param source_name: name of the data source to delete
    """
    client.service.deleteSource(sourceName=source_name)


def update_source(client: Client, source: Source) -> Source:
    """
    Updates a data source with the given source instance.

    :param client: Zeep client with E-PIX management service definitions
    :param source: source data class with update information
    :return: updated source instance
    """
    source_soap = SourceSchema().dump(source)
    response_source_soap = client.service.updateSource(source=source_soap)
    return SourceSchema().load(_serialize_dict(response_source_soap))


def add_domain(client: Client, domain: Domain) -> None:
    """
    Adds a new domain.

    :param client: Zeep client with E-PIX management service definitions
    :param domain: domain data class to create
    """
    domain_soap = DomainSchema().dump(domain)
    client.service.addDomain(domain=domain_soap)


def get_domain(client: Client, domain_name: str) -> Domain:
    """
    Gets a domain by its name.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the domain to get
    :return: domain instance
    """
    domain_soap = client.service.getDomain(domainName=domain_name)
    return DomainSchema().load(_serialize_dict(domain_soap))


def get_domains(client: Client) -> list[Domain]:
    """
    Lists all available domains in the E-PIX instance.

    :param client: Zeep client with E-PIX management service definitions
    :return: list of all available domains as domain instances
    """
    domains = _serialize_dict(client.service.getDomains())
    return [DomainSchema().load(domain) for domain in domains]


def delete_domain(client: Client, domain_name: str, force: bool = False) -> None:
    """
    Deletes a domain that matches the specified name. Raises a Fault if there is no domain with such a name. Set force
    to True, if the domain is already populated.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the domain to delete
    :param force: whether the deletion should be forced or not
    """
    client.service.deleteDomain(domainName=domain_name, force=force)


def get_config_for_domain(client: Client, domain_name: str) -> DomainConfiguration:
    """
    Gets the configuration for a specified domain.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the domain to get the configuration for
    :return: domain configuration instance
    """
    config = client.service.getConfigurationForDomain(domainName=domain_name)
    return DomainConfigurationSchema().load(_serialize_dict(config))


def update_domain_in_use(client: Client, domain_name: str, label: str, description: str) -> Domain:
    """
    Updates a domain that is already populated. If a domain is populated, it is only possible to update the label and
    description of a domain.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the domain to update
    :param label: new label
    :param description: new description
    :return: updated domain instance
    """
    domain_soap = client.service.updateDomainInUse(domainName=domain_name, label=label, description=description)
    return DomainSchema().load(_serialize_dict(domain_soap))


def update_domain(client: Client, domain: Domain) -> Domain:
    """
    Updates a domain with a given domain instance. Raises an error if the domain is already populated.

    :param client: Zeep client with E-PIX management service definitions
    :param domain: domain instance class to update
    :return: domain data class with update information
    """
    domain_soap = DomainSchema().dump(domain)
    response_domain_soap = client.service.updateDomain(domain=domain_soap)
    return DomainSchema().load(_serialize_dict(response_domain_soap))


def get_defined_deduplication_reasons(client: Client, domain_name: str) -> list[Reason]:
    """
    Gets a list of deduplication reasons for a given domain.

    :param client: Zeep client with E-PIX management service definitions
    :param domain_name: name of the domain to get the deduplication reasons for
    :return: list of deduplication reasons as reason data class instances
    """
    reasons = _serialize_dict(client.service.getDefinedDeduplicationReasons(domainName=domain_name))
    return [ReasonSchema().load(reason) for reason in reasons]


class EPIXClient(WSDLClient):
    """
    This class is a wrapper around the E-PIX service functions.
    """

    def __init__(self, client: Client | str, management_client: Client | str):
        """
        Constructs a new SOAP client for E-PIX service definitions.

        :param client: URL to WSDL endpoint or zeep instance with WSDL information for the E-PIX service
        :param management_client: URL to WSDL endpoint or zeep instance with WSDL information for the E-PIX management
        service
        """
        super().__init__(client)
        self._management_client = _cast_client(management_client)

    def request_mpi(
        self,
        domain_name: str,
        source_name: str,
        identity: Identity,
        comment: str | None = None,
    ) -> ResponseEntry:
        """
        Requests an MPI for an identity. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identity belongs
        :param source_name: source name from which the identity stems
        :param identity: identity to request MPI for
        :param comment: optional comment on this transaction
        :return: MPI response, indicating whether the identity already exists and containing the assigned MPI
        """
        return request_mpi(self._client, domain_name, source_name, identity, comment)

    def request_mpi_batch(
        self,
        domain_name: str,
        source_name: str,
        identities: list[Identity],
        config: BatchRequestConfig | None = None,
        comment: str | None = None,
    ) -> list[BatchResponseEntry]:
        """
        Requests MPIs for a list of identities. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identities belong
        :param source_name: source name from which the identities stem
        :param identities: identities to request MPIs for
        :param config: optional configuration on how to handle this request
        :param comment: optional comment on this transaction
        :return: list of MPI responses, indicating whether an identity already exists and containing the assigned MPI
        """
        return request_mpi_batch(self._client, domain_name, source_name, identities, config, comment)

    def get_person_by_mpi(self, domain_name: str, mpi_id: str) -> Person:
        """
        Returns a person by their MPI. This function throws a Fault if the MPI is not present.

        :param domain_name: data domain in which to look for the person
        :param mpi_id: MPI of the desired person
        :return: person assigned to the specified MPI
        """
        return get_person_by_mpi(self._client, domain_name, mpi_id)

    def update_person(
        self,
        domain_name: str,
        source_name: str,
        mpi_id: str,
        identity: Identity,
        force: bool = False,
        comment: str | None = None,
    ) -> ResponseEntry:
        """
        Updates an identity, addressed by their MPI. This function throws a Fault if any required identity fields
        are missing, as per the domain configuration.

        :param domain_name: data domain to which the identity belongs
        :param source_name: source name from which the identity stems
        :param mpi_id: MPI of the person to update
        :param identity: identity with updated information
        :param force: undocumented API option
        :param comment: optional comment on this transaction
        :return: updated person record
        """
        return update_person(self._client, domain_name, source_name, mpi_id, identity, force, comment)

    def get_persons_for_domain(self, domain_name: str) -> list[Person]:
        """
        Returns a list of persons stored in a domain. This function throws a Fault if the specified domain
        doesn't exist.

        :param domain_name: data domain in which to look for persons
        :return: list of persons inside the specified domain
        """
        return get_persons_for_domain(self._client, domain_name)

    def get_identities_for_domain(self, domain_name: str) -> list[FullIdentity]:
        """
        Returns a list of identities stored in a domain. This function throws a Fault if the specified domain
        doesn't exist.

        :param domain_name: data domain in which to look for identities
        :return: list of identities inside the specified domain
        """
        return get_identities_for_domain(self._client, domain_name)

    def deactivate_identity(self, identity_id: int) -> None:
        """
        Deactivates an identity based on their identity ID (not MPI!). This function throws a Fault if the
        specified identity ID cannot be found.

        :param identity_id: ID of the identity to deactivate
        :return: nothing
        """
        deactivate_identity(self._client, identity_id)

    def deactivate_person(self, domain_name: str, mpi_id: str) -> None:
        """
        Deactivates a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
        in the provided data domain.

        :param domain_name: data domain in which to look up the MPI
        :param mpi_id: MPI of the person to deactivate
        :return: nothing
        """
        deactivate_person(self._client, domain_name, mpi_id)

    def delete_identity(self, identity_id: int) -> None:
        """
        Deletes an identity based on their identity ID (not MPI!). This function throws a Fault if the
        specified identity ID cannot be found, or if the identity with the ID has not been deactivated yet.

        :param identity_id: ID of the identity to delete
        :return: nothing
        """
        delete_identity(self._client, identity_id)

    def delete_person(self, domain_name: str, mpi_id: str) -> None:
        """
        Deletes a person based on their MPI. This function throws a Fault if the specified MPI cannot be found
        in the provided data domain, or if the identity with the ID has not been deactivated yet.

        :param domain_name: data domain in which to look up the MPI
        :param mpi_id: MPI of the person to delete
        :return: nothing
        """
        delete_person(self._client, domain_name, mpi_id)

    def add_identifier_domain(self, identifier_domain: IdentifierDomain) -> None:
        """
        Adds a new identifier domain.

        :param identifier_domain: identifier domain data class to create
        """
        add_identifier_domain(self._management_client, identifier_domain)

    def get_identifier_domain(self, identifier_domain_name: str) -> IdentifierDomain:
        """
        Gets an identifier domain by its name.

        :param identifier_domain_name: name of the identifier domain to get
        :return: identifier domain instance
        """
        return get_identifier_domain(self._management_client, identifier_domain_name)

    def get_identifier_domains(self) -> list[IdentifierDomain]:
        """
        Lists all available identifier domains in the E-PIX instance.

        :return: list of all available identifier domains as identifier domain instances
        """
        return get_identifier_domains(self._management_client)

    def delete_identifier_domain(self, identifier_domain_name: str) -> None:
        """
        Deletes an identifier domain that matches the specified name. Raises a Fault if there is no identifier domain
        with such a name.

        :param identifier_domain_name: name of the identifier domain to delete
        """
        delete_identifier_domain(self._management_client, identifier_domain_name)

    def update_identifier_domain(self, identifier_domain: IdentifierDomain) -> IdentifierDomain:
        """
        Updates an identifier domain with the given identifier domain instance.

        :param identifier_domain: identifier domain data class with update information
        :return: updated identifier domain instance
        """
        return update_identifier_domain(self._management_client, identifier_domain)

    def add_source(self, source: Source) -> None:
        """
        Adds a new data source.

        :param source: source data class to create
        """
        add_source(self._management_client, source)

    def get_source(self, source_name: str) -> Source:
        """
        Gets a data source by its name.

        :param source_name: name of the data source to get
        :return: source instance
        """
        return get_source(self._management_client, source_name)

    def get_sources(self) -> list[Source]:
        """
        Lists all available data sources in the E-PIX instance.

        :return: list of all available data sources as source instances
        """
        return get_sources(self._management_client)

    def delete_source(self, source_name: str) -> None:
        """
        Deletes a data source that matches the specified name. Raises a Fault if there is no data source with such a
        name.

        :param source_name: name of the data source to delete
        """
        delete_source(self._management_client, source_name)

    def update_source(self, source: Source) -> Source:
        """
        Updates a data source with the given source instance.

        :param source: source data class with update information
        :return: updated source instance
        """
        return update_source(self._management_client, source)

    def add_domain(self, domain: Domain) -> None:
        """
        Adds a new domain.

        :param domain: domain data class to create
        """
        add_domain(self._management_client, domain)

    def get_domain(self, domain_name: str) -> Domain:
        """
        Gets a domain by its name.

        :param domain_name: name of the domain to get
        :return: domain instance
        """
        return get_domain(self._management_client, domain_name)

    def get_domains(self) -> list[Domain]:
        """
        Lists all available domains in the E-PIX instance.

        :return: list of all available domains as domain instances
        """
        return get_domains(self._management_client)

    def delete_domain(self, domain_name: str, force: bool = False) -> None:
        """
        Deletes a domain that matches the specified name. Raises a Fault if there is no domain with such a name. Set
        force to True, if the domain is already populated.

        :param domain_name: name of the domain to delete
        :param force: whether the deletion should be forced or not
        """
        delete_domain(self._management_client, domain_name, force)

    def get_config_for_domain(self, domain_name: str) -> DomainConfiguration:
        """
        Gets the configuration for a specified domain.

        :param domain_name: name of the domain to get the configuration for
        :return: domain configuration instance
        """
        return get_config_for_domain(self._management_client, domain_name)

    def update_domain_in_use(self, domain_name: str, label: str, description: str) -> Domain:
        """
        Updates a domain that is already populated. If a domain is populated, it is only possible to update the label
        and description of a domain.

        :param domain_name: name of the domain to update
        :param label: new label
        :param description: new description
        :return: updated domain instance
        """
        return update_domain_in_use(self._management_client, domain_name, label, description)

    def update_domain(self, domain: Domain) -> Domain:
        """
        Updates a domain with a given domain instance. Raises an error if the domain is already populated.

        :param domain: domain instance class to update
        :return: domain data class with update information
        """
        return update_domain(self._management_client, domain)

    def get_defined_deduplication_reasons(self, domain_name: str) -> list[Reason]:
        """
        Gets a list of deduplication reasons for a given domain.

        :param domain_name: name of the domain to get the deduplication reasons for
        :return: list of deduplication reasons as reason data class instances
        """
        return get_defined_deduplication_reasons(self._management_client, domain_name)
