"""
This module contains functions for interacting with the gPAS SOAP interface.
"""

from datetime import date

from zeep import Client

from mosaic_client.gpas.models import (
    AnonymizationResponse,
    DeletionResponse,
    Domain,
    DomainResponse,
    InsertPairException,
    Pseudonym,
    PseudonymNet,
    PseudonymTree,
    ValueToPseudonyms,
)
from mosaic_client.gpas.schemas import (
    AnonymizationResponseSchema,
    DeletionResponseSchema,
    DomainResponseSchema,
    DomainSchema,
    InsertPairExceptionSchema,
    PseudonymNetSchema,
    PseudonymSchema,
    PseudonymTreeSchema,
    ValueToPseudonymsSchema,
)
from mosaic_client.helpers import WSDLClient, _cast_client, _read_key_value_list, _serialize_dict

KeyValueTuple = tuple[str, str]


def delete_entry(client: Client, domain_name: str, value: str) -> None:
    """
    Deletes a value and all of its associated pseudonyms from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is present
    :param value: value to remove
    """
    client.service.deleteAllEntriesForValue(domainName=domain_name, value=value)


def delete_entries(client: Client, domain_name: str, values: list[str]) -> list[DeletionResponse]:
    """
    Deletes a list of values and all associated pseudonyms from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the values are present
    :param values: list of values to remove
    :return: list of deletion response data class instances
    """
    response = client.service.deleteAllEntriesForValues(domainName=domain_name, values=values)
    return [DeletionResponseSchema().load(_serialize_dict(r)) for r in response]


def delete_pseudonym(client: Client, domain_name: str, pseudonym: str) -> None:
    """
    Deletes a pseudonym and the associated value from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the pseudonym is present
    :param pseudonym: pseudonym to delete
    """
    client.service.deletePseudonym(psn=pseudonym, domainName=domain_name)


def delete_pseudonyms(client: Client, domain_name: str, pseudonyms: list[str]) -> list[DeletionResponse]:
    """
    Deletes a list of pseudonyms and their associated values from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the pseudonyms are present
    :param pseudonyms: list of pseudonyms to remove
    :return: list of delete response data class instances
    """
    response = client.service.deletePseudonyms(domainName=domain_name, psns=pseudonyms)
    return [DeletionResponseSchema().load(_serialize_dict(r)) for r in response]


def get_or_create_pseudonyms_for(
    client: Client,
    domain_name: str,
    value: str,
    min_number: int = 1,
) -> ValueToPseudonyms:
    """
    Gets the pseudonyms or creates new pseudonyms for a given value in the specified domain. This function assures that
    at least the specified number of pseudonyms exist for the given value in the domain. Raises a Fault if the domain is
    full, expired or not found. Also raises a Fault if more than one pseudonym is requested for a domain that does not
    allow multiple pseudonyms per value.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value should be got from or created in
    :param value: value to get or create pseudonyms for
    :param min_number: minimum number of pseudonyms that should exist for the given value, defaults to one
    :return: value to pseudonyms data class instance
    """
    psns = client.service.getOrCreatePseudonymsFor(domainName=domain_name, value=value, minNumber=min_number)
    return ValueToPseudonyms(value=value, pseudonyms=psns)


def get_or_create_pseudonyms_for_list(
    client: Client,
    domain_name: str,
    values: list[str],
    min_number: int = 1,
) -> list[ValueToPseudonyms]:
    """
    Gets the pseudonyms or creates new pseudonyms for a given list of values in the specified domain. This function
    assures that at least the specified number of pseudonyms exist for each of the given values in the domain. Raises
    a Fault if the domain is full, expired or not found. Also raises a Fault if more than one pseudonym per value is
    requested for a domain that does not allow multiple pseudonyms per value.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the values should be got from or created in
    :param values: list of values to get or create pseudonyms for
    :param min_number: minimum number of pseudonyms that should exist for each value, defaults to one
    :return: list of value to pseudonyms data class instances
    """
    response = client.service.getOrCreatePseudonymsForList(domainName=domain_name, values=values, minNumber=min_number)
    return [ValueToPseudonymsSchema().load(_serialize_dict(r)) for r in response]


def get_value_for(client: Client, domain_name: str, pseudonym: str) -> str:
    """
    Gets the value for a pseudonym in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the pseudonym is present
    :param pseudonym: pseudonym to resolve
    :return: value assigned to the pseudonym
    """
    return client.service.getValueFor(domainName=domain_name, psn=pseudonym)


def get_value_for_list(client: Client, domain_name: str, pseudonyms: list[str]) -> list[KeyValueTuple]:
    """
    Gets the values for a list of pseudonyms in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the pseudonyms are present
    :param pseudonyms: pseudonyms to resolve
    :return: list of key-value pairs, structured as { pseudonym => value }
    """
    response = client.service.getValueForList(domainName=domain_name, psnList=pseudonyms)
    return _read_key_value_list(_serialize_dict(response))


def get_pseudonyms_for(client: Client, domain_name: str, value: str) -> ValueToPseudonyms:
    """
    Get all pseudonyms for a value in the specified data domain. Note that a domain can be configured to allow multiple
    pseudonyms per value.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is present
    :param value: value to resolve
    :return: value to pseudonyms data class instance
    """
    psns = client.service.getPseudonymsFor(domainName=domain_name, value=value)
    return ValueToPseudonyms(value=value, pseudonyms=psns)


def get_pseudonyms_for_list(client: Client, domain_name: str, values: list[str]) -> list[ValueToPseudonyms]:
    """
    Get all pseudonyms for each value in a list of values in the specified data domain. Note that a domain can be
    specified to allow multiple pseudonyms per value.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the values are present
    :param values: values to resolve
    :return: list of value to pseudonyms data class instances
    """
    response_soap = client.service.getPseudonymsForList(domainName=domain_name, values=values)
    return [ValueToPseudonymsSchema().load(_serialize_dict(r)) for r in response_soap]


def insert_value_pseudonym_pair(client: Client, domain_name: str, value: str, pseudonym: str) -> None:
    """
    Manually inserts a value and a pseudonym into the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain to insert the pair into
    :param value: value to add
    :param pseudonym: pseudonym to assign to the value
    """
    client.service.insertValuePseudonymPair(domainName=domain_name, value=value, pseudonym=pseudonym)


def insert_value_pseudonym_pairs(
    client: Client,
    domain_name: str,
    pairs: list[KeyValueTuple],
) -> list[InsertPairException]:
    """
    Manually inserts a list of values and pseudonyms tuples into the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain to insert the pairs into
    :param pairs: list of key-value pairs, structured as { value => pseudonym }
    :return: list of insert pair exception data class instances for cases that could not be inserted and raised an error
    """
    # for some reason this is the only case where the "entry" key is mandatory. it is not returned by any other
    # endpoints where there's supposedly an "entry" key, e.g. deleteEntries (???)
    response = client.service.insertValuePseudonymPairs(
        domainName=domain_name,
        pairs={
            "entry": [
                {
                    "key": kv_tuple[0],
                    "value": kv_tuple[1],
                }
                for kv_tuple in pairs
            ]
        },
    )

    if response is None:
        response = []

    return [InsertPairExceptionSchema().load(_serialize_dict(r)) for r in response]


def add_domain(client: Client, domain: Domain) -> None:
    """
    Adds a new domain.

    :param client: Zeep client with gPAS domain service definitions
    :param domain: domain data class to create
    """
    domain_soap = DomainSchema().dump(domain)
    client.service.addDomain(domainDTO=domain_soap)


def get_domain(client: Client, domain_name: str) -> DomainResponse:
    """
    Gets a domain that matches the specified name. Raises a Fault if there is no domain with such a name.

    :param client: Zeep client with gPAS domain service definitions
    :param domain_name: name of the domain to get
    :return: domain response instance
    """
    domain_soap = client.service.getDomain(domainName=domain_name)
    return DomainResponseSchema().load(_serialize_dict(domain_soap))


def get_domains_for_prefix(client: Client, prefix: str) -> list[DomainResponse]:
    """
    Lists all domains that configured the specified pseudonym prefix.

    :param client: Zeep client with gPAS domain service definitions
    :param prefix: configured pseudonym prefix
    :return: list of domain response instances
    """
    domains = client.service.getDomainsForPrefix(prefix=prefix)

    if domains is None:
        domains = []

    return [DomainResponseSchema().load(_serialize_dict(domain)) for domain in domains]


def get_domains_for_suffix(client: Client, suffix: str) -> list[DomainResponse]:
    """
    Lists all domains that configured the specified pseudonym suffix.

    :param client: Zeep client with gPAS domain service definitions
    :param suffix: configured pseudonym suffix
    :return: list of domain response instances
    """
    domains = client.service.getDomainsForSuffix(suffix=suffix)

    if domains is None:
        domains = []

    return [DomainResponseSchema().load(_serialize_dict(domain)) for domain in domains]


def list_domains(client: Client) -> list[DomainResponse]:
    """
    Lists all available domains in the gPAS instance.

    :param client: Zeep client with gPAS domain service definitions
    :return: list of all available domains as domain response instances
    """
    domains = _serialize_dict(client.service.listDomains())

    if domains is None:
        domains = []

    return [DomainResponseSchema().load(domain) for domain in domains]


def delete_domain(client: Client, domain_name: str) -> None:
    """
    Deletes a domain that matches the specified name. Raises a Fault if there is no domain with such a name.

    :param client: Zeep client with gPAS domain service definitions
    :param domain_name: name of the domain to delete
    """
    client.service.deleteDomainWithPSNs(domainName=domain_name)


def validate_pseudonym(client: Client, pseudonym: str, domain_name: str) -> None:
    """
    Validates a given pseudonym against the specified domain. Raise a Fault if the pseudonym is not valid.

    :param client: Zeep client with gPAS service definitions
    :param pseudonym: pseudonym to validate
    :param domain_name: domain for which the pseudonym should be validated
    """
    client.service.validatePSN(psn=pseudonym, domainName=domain_name)


def update_pseudonym_expiration_date(client: Client, pseudonym: str, domain_name: str, expiration_date: date) -> None:
    """
    Updates the expiration date of a pseudonym. Raises a Fault if there is no domain with the specified name, the
    expiration date is invalid, there is no such pseudonym or the domain has not been configured for expirations.

    :param client: Zeep client with gPAS service definitions
    :param pseudonym: pseudonym to update
    :param domain_name: domain which the pseudonym belongs to
    :param expiration_date: new expiration date of the pseudonym
    """
    client.service.updatePseudonymExpirationDate(
        psn=pseudonym,
        domainName=domain_name,
        newExpirationDate=expiration_date,
    )


def is_anonym(client: Client, value: str) -> bool:
    """
    Checks if the given value is an Anonym.

    :param client: Zeep client with gPAS service definitions
    :param value: value to check
    :return: True if the given value is an Anonym, False otherwise
    """
    return client.service.isAnonym(value)


def is_anonymized(client: Client, pseudonym: str, domain_name: str) -> bool:
    """
    Checks if the given pseudonym of the specified domain is anonymized. Raises a Fault if the given pseudonym is not
    found in the given domain or there is no domain with such a name.

    :param client: Zeep client with gPAS service definitions
    :param pseudonym: pseudonym to check if it is anonymized
    :param domain_name: domain for which the pseudonym should be checked
    :return: True if the given pseudonym is anonymized, False otherwise
    """
    return client.service.isAnonymised(psn=pseudonym, domainName=domain_name)


def anonymize_pseudonym(client: Client, pseudonym: str, domain_name: str) -> None:
    """
    Anonymizes the value of the given pseudonym in the specified domain. Raises a Fault if the pseudonym is not found in
    the given domain or there is no domain with such a name.

    :param client: Zeep client with gPAS service definitions
    :param pseudonym: pseudonym to anonymize
    :param domain_name: domain for which the pseudonym should be anonymized
    """
    client.service.anonymisePseudonym(psn=pseudonym, domainName=domain_name)


def anonymize_pseudonyms(
    client: Client,
    pseudonyms: list[str],
    domain_name: str,
) -> list[AnonymizationResponse]:
    """
    Anonymizes the values of the given pseudonyms in the specified domain. Raises a Fault if there is no domain with
    such a name.

    :param client: Zeep client with gPAS service definitions
    :param pseudonyms: list of pseudonyms to anonymize
    :param domain_name: domain for which the pseudonyms should be anonymized
    :return: list of anonymization response data class instances
    """
    response_soap = client.service.anonymisePseudonyms(psns=pseudonyms, domainName=domain_name)
    return [AnonymizationResponseSchema().load(_serialize_dict(r)) for r in response_soap]


def anonymize_entry(client: Client, value: str, domain_name: str) -> None:
    """
    Anonymizes a given value in the specified domain. If the specified domain allows multiple pseudonyms per value, all
    values will be anonymized. Raises a Fault if the value is not found in the specified domain, there is no domain with
    such a name, or the value is already anonymized.

    :param client: Zeep client with gPAS service definitions
    :param value: value to anonymize
    :param domain_name: domain for which the value should be anonymized
    """
    client.service.anonymiseAllEntriesForValue(value=value, domainName=domain_name)


def anonymize_entries(client: Client, values: list[str], domain_name: str) -> list[AnonymizationResponse]:
    """
    Anonymizes given values in the specified domain. If the specified domain allows multiple pseudonyms per value, all
    values will be anonymized. Raises a Fault if there is no domain with such a name.

    :param client: Zeep client with gPAS service definitions
    :param values: list of values to anonymize
    :param domain_name: domain for which the values should be anonymized
    :return: list of anonymization response data class instances
    """
    response_soap = client.service.anonymiseAllEntriesForValues(values=values, domainName=domain_name)
    return [AnonymizationResponseSchema().load(_serialize_dict(r)) for r in response_soap]


def get_pseudonyms_for_value_prefix(client: Client, value_prefix: str, domain_name: str) -> list[ValueToPseudonyms]:
    """
    Returns all pseudonyms for each value that starts with the specified prefix in the specified domain. Raises a Fault
    if there is no domain with such a name.

    :param client: Zeep client with gPAS service definitions
    :param value_prefix: the prefix of values for which the pseudonyms should be retrieved
    :param domain_name: domain for which the pseudonyms should be retrieved
    :return: list of value to pseudonyms data class instances
    """
    response_soap = client.service.getPseudonymsForValuePrefix(valuePrefix=value_prefix, domainName=domain_name)
    return [ValueToPseudonymsSchema().load(_serialize_dict(r)) for r in response_soap]


def get_pseudonym_tree(client: Client, pseudonym: str, domain_name: str) -> PseudonymTree:
    """
    Creates a pseudonym tree with all values that are somehow linked to the given pseudonym. Raises a Fault if the
    pseudonym is not found in the specified domain, there is no domain with such a name, or if the value is already
    anonymized.

    :param client: Zeep client with gPAS service definitions
    :param pseudonym: pseudonym to create the tree from
    :param domain_name: name of the domain for the given pseudonym
    :return: pseudonym tree data class instance
    """
    tree_soap = client.service.getPSNTreeForPSN(psn=pseudonym, domainName=domain_name)
    return PseudonymTreeSchema().load(_serialize_dict(tree_soap))


def get_pseudonym_net(client: Client, value_or_pseudonym: str) -> PseudonymNet:
    """
    Creates a pseudonym net with all values and pseudonyms that are somehow linked to the given value or pseudonym.

    :param client: Zeep client with gPAS service definitions
    :param value_or_pseudonym: value or pseudonym to create the net from
    :return: pseudonym net data class instance
    """
    net_soap = client.service.getPSNNetFor(valueOrPSN=value_or_pseudonym)
    return PseudonymNetSchema().load(_serialize_dict(net_soap))


def are_pseudonyms_deletable(client: Client, domain_name: str) -> bool:
    """
    Checks if the deletion of pseudonyms is allowed for the specified domain.

    :param client: Zeep client with gPAS domain service definitions
    :param domain_name: name of the domain to check
    :return: True if pseudonyms are allowed to be deleted, False otherwise
    """
    return client.service.arePSNDeletable(domainName=domain_name)


def list_pseudonyms(client: Client, domain_name: str) -> list[Pseudonym]:
    """
    Retrieves all pseudonyms for the specified domain. Raises a Fault if there is no domain with such a name.

    :param client: Zeep client with gPAS domain service definitions
    :param domain_name: name of the domain to retrieve pseudonyms for
    :return: list of pseudonym data class instances
    """
    psns = client.service.listPSNs(domainName=domain_name)
    return [PseudonymSchema().load(_serialize_dict(psn)) for psn in psns]


class GPASClient(WSDLClient):
    """
    This class is a wrapper around the gPAS service functions.
    """

    def __init__(self, client: Client | str, domain_client: Client | str):
        """
        Constructs a new SOAP client for gPAS service definitions.

        :param client: URL to WSDL endpoint or zeep instance with WSDL information for the gPAS service
        :param domain_client: URL to WSDL endpoint or zeep instance with WSDL information for the gPAS management
        service
        """
        super().__init__(client)
        self._domain_client = _cast_client(domain_client)

    def delete_entry(self, domain_name: str, value: str) -> None:
        """
        Deletes a value and all of its associated pseudonyms from the specified data domain.

        :param domain_name: name of the domain where the value is present
        :param value: value to remove
        """
        delete_entry(self._client, domain_name, value)

    def delete_entries(self, domain_name: str, values: list[str]) -> list[DeletionResponse]:
        """
        Deletes a list of values and all associated pseudonyms from the specified data domain.

        :param domain_name: name of the domain where the values are present
        :param values: list of values to remove
        :return: list of deletion response data class instances
        """
        return delete_entries(self._client, domain_name, values)

    def delete_pseudonym(self, domain_name: str, pseudonym: str) -> None:
        """
        Deletes a pseudonym and the associated value from the specified data domain.

        :param domain_name: name of the domain where the pseudonym is present
        :param pseudonym: pseudonym to delete
        """
        delete_pseudonym(self._client, domain_name, pseudonym)

    def delete_pseudonyms(self, domain_name: str, pseudonyms: list[str]) -> list[DeletionResponse]:
        """
        Deletes a list of pseudonyms and their associated values from the specified data domain.

        :param domain_name: name of the domain where the pseudonyms are present
        :param pseudonyms: list of pseudonyms to remove
        :return: list of delete response data class instances
        """
        return delete_pseudonyms(self._client, domain_name, pseudonyms)

    def get_or_create_pseudonyms_for(self, domain_name: str, value: str, min_number: int = 1) -> ValueToPseudonyms:
        """
        Gets the pseudonyms or creates new pseudonyms for a given value in the specified domain. This function assures
        that at the least specified number of pseudonyms exist for the given value in the domain. Raises a Fault if the
        domain is full, expired or not found. Also raises a Fault if more than one pseudonym is requested for a domain
        that does not allow multiple pseudonyms per value.

        :param domain_name: name of the domain where the value should be got from or created in
        :param value: value to get or create pseudonyms for
        :param min_number: minimum number of pseudonyms that should exist for the given value, defaults to one
        :return: value to pseudonyms data class instance
        """
        return get_or_create_pseudonyms_for(self._client, domain_name, value, min_number)

    def get_or_create_pseudonyms_for_list(
        self,
        domain_name: str,
        values: list[str],
        min_number: int = 1,
    ) -> list[ValueToPseudonyms]:
        """
        Gets the pseudonyms or creates new pseudonyms for a given list of values in the specified domain. This function
        assures that at least the specified number of pseudonyms exist for each of the given values in the domain.
        Raises a Fault if the domain is full, expired or not found. Also raises a Fault if more than one pseudonym per
        value is requested for a domain that does not allow multiple pseudonyms per value.

        :param domain_name: name of the domain where the values should be got from or created in
        :param values: list of values to get or create pseudonyms for
        :param min_number: minimum number of pseudonyms that should exist for each value, defaults to one
        :return: list of value to pseudonyms data class instances
        """
        return get_or_create_pseudonyms_for_list(self._client, domain_name, values, min_number)

    def get_value_for(self, domain_name: str, pseudonym: str) -> str:
        """
        Gets the value for a pseudonym in the specified data domain.

        :param domain_name: name of the domain where the pseudonym is present
        :param pseudonym: pseudonym to resolve
        :return: value assigned to the pseudonym
        """
        return get_value_for(self._client, domain_name, pseudonym)

    def get_value_for_list(self, domain_name: str, pseudonyms: list[str]) -> list[KeyValueTuple]:
        """
        Gets the values for a list of pseudonyms in the specified data domain.

        :param domain_name: name of the domain where the pseudonyms are present
        :param pseudonyms: pseudonyms to resolve
        :return: list of key-value pairs, structured as { pseudonym => value }
        """
        return get_value_for_list(self._client, domain_name, pseudonyms)

    def get_pseudonyms_for(self, domain_name: str, value: str) -> ValueToPseudonyms:
        """
        Get all pseudonyms for a value in the specified data domain. Note that a domain can be configured to allow
        multiple pseudonyms per value.

        :param domain_name: name of the domain where the value is present
        :param value: value to resolve
        :return: value to pseudonyms data class instance
        """
        return get_pseudonyms_for(self._client, domain_name, value)

    def get_pseudonyms_for_list(self, domain_name: str, values: list[str]) -> list[ValueToPseudonyms]:
        """
        Get all pseudonyms for each value in a list of values in the specified data domain. Note that a domain can be
        specified to allow multiple pseudonyms per value.

        :param domain_name: name of the domain where the values are present
        :param values: values to resolve
        :return: list of value to pseudonyms data class instances
        """
        return get_pseudonyms_for_list(self._client, domain_name, values)

    def insert_value_pseudonym_pair(self, domain_name: str, value: str, pseudonym: str) -> None:
        """
        Manually inserts a value and a pseudonym into the specified data domain.

        :param domain_name: name of the domain to insert the pair into
        :param value: value to add
        :param pseudonym: pseudonym to assign to the value
        """
        insert_value_pseudonym_pair(self._client, domain_name, value, pseudonym)

    def insert_value_pseudonym_pairs(self, domain_name: str, pairs: list[KeyValueTuple]) -> list[InsertPairException]:
        """
        Manually inserts a list of values and pseudonyms tuples into the specified data domain.

        :param domain_name: name of the domain to insert the pairs into
        :param pairs: list of key-value pairs, structured as { value => pseudonym }
        :return: list of insert pair exception data class instances for cases that could not be inserted and raised an
        error
        """
        return insert_value_pseudonym_pairs(self._client, domain_name, pairs)

    def add_domain(self, domain: Domain) -> None:
        """
        Adds a new domain.

        :param domain: domain data class to create
        """
        add_domain(self._domain_client, domain)

    def get_domain(self, domain_name: str) -> DomainResponse:
        """
        Gets a domain that matches the specified name. Raises a Fault if there is no domain with such a name.

        :param domain_name: name of the domain to get
        :return: domain response instance
        """
        return get_domain(self._domain_client, domain_name)

    def get_domains_for_prefix(self, prefix: str) -> list[DomainResponse]:
        """
        Lists all domains that configured the specified pseudonym prefix.

        :param prefix: configured pseudonym prefix
        :return: list of domain response instances
        """
        return get_domains_for_prefix(self._domain_client, prefix)

    def get_domains_for_suffix(self, suffix: str) -> list[DomainResponse]:
        """
        Lists all domains that configured the specified pseudonym suffix.

        :param suffix: configured pseudonym suffix
        :return: list of domain response instances
        """
        return get_domains_for_suffix(self._domain_client, suffix)

    def list_domains(self) -> list[DomainResponse]:
        """
        Lists all available domains in the gPAS instance.

        :return: list of all available domains as domain response instances
        """
        return list_domains(self._domain_client)

    def delete_domain(self, domain_name: str) -> None:
        """
        Deletes a domain that matches the specified name. Raises a Fault if there is no domain with such a name.

        :param domain_name: name of the domain to delete
        """
        delete_domain(self._domain_client, domain_name)

    def validate_pseudonym(self, pseudonym: str, domain_name: str) -> None:
        """
        Validates a given pseudonym against the specified domain. Raise a Fault if the pseudonym is not valid.

        :param pseudonym: pseudonym to validate
        :param domain_name: domain for which the pseudonym should be validated
        """
        validate_pseudonym(self._client, pseudonym, domain_name)

    def update_pseudonym_expiration_date(self, pseudonym: str, domain_name: str, expiration_date: date) -> None:
        """
        Updates the expiration date of a pseudonym. Raises a Fault if there is no domain with the specified name, the
        expiration date is invalid, there is no such pseudonym or the domain has not been configured for expirations.

        :param pseudonym: pseudonym to update
        :param domain_name: domain which the pseudonym belongs to
        :param expiration_date: new expiration date of the pseudonym
        """
        update_pseudonym_expiration_date(self._client, pseudonym, domain_name, expiration_date)

    def is_anonym(self, value: str) -> bool:
        """
        Checks if the given value is an Anonym.

        :param value: value to check
        :return: True if the given value is an Anonym, False otherwise
        """
        return is_anonym(self._client, value)

    def is_anonymized(self, pseudonym: str, domain_name: str) -> bool:
        """
        Checks if the given pseudonym of the specified domain is anonymized. Raises a Fault if the given pseudonym is
        not found in the given domain or there is no domain with such a name.

        :param pseudonym: pseudonym to check if it is anonymized
        :param domain_name: domain for which the pseudonym should be checked
        :return: True if the given pseudonym is anonymized, False otherwise
        """
        return is_anonymized(self._client, pseudonym, domain_name)

    def anonymize_pseudonym(self, pseudonym: str, domain_name: str) -> None:
        """
        Anonymizes the value of the given pseudonym in the specified domain. Raises a Fault if the pseudonym is not
        found in the given domain or there is no domain with such a name.

        :param pseudonym: pseudonym to anonymize
        :param domain_name: domain for which the pseudonym should be anonymized
        """
        anonymize_pseudonym(self._client, pseudonym, domain_name)

    def anonymize_pseudonyms(self, pseudonyms: list[str], domain_name: str) -> list[AnonymizationResponse]:
        """
        Anonymizes the values of the given pseudonyms in the specified domain. Raises a Fault if there is no domain with
        such a name.

        :param pseudonyms: list of pseudonyms to anonymize
        :param domain_name: domain for which the pseudonyms should be anonymized
        :return: list of anonymization response data class instances
        """
        return anonymize_pseudonyms(self._client, pseudonyms, domain_name)

    def anonymize_entry(self, value: str, domain_name: str) -> None:
        """
        Anonymizes a given value in the specified domain. If the specified domain allows multiple pseudonyms per value,
        all values will be anonymized. Raises a Fault if the value is not found in the specified domain, there is no
        domain with such a name, or the value is already anonymized.

        :param value: value to anonymize
        :param domain_name: domain for which the value should be anonymized
        """
        anonymize_entry(self._client, value, domain_name)

    def anonymize_entries(self, values: list[str], domain_name: str) -> list[AnonymizationResponse]:
        """
        Anonymizes given values in the specified domain. If the specified domain allows multiple pseudonyms per value,
        all values will be anonymized. Raises a Fault if there is no domain with such a name.

        :param values: list of values to anonymize
        :param domain_name: domain for which the values should be anonymized
        :return: list of anonymization response data class instances
        """
        return anonymize_entries(self._client, values, domain_name)

    def get_pseudonyms_for_value_prefix(self, value_prefix: str, domain_name: str) -> list[ValueToPseudonyms]:
        """
        Returns all pseudonyms for each value that starts with the specified prefix in the specified domain. Raises a
        Fault if there is no domain with such a name.

        :param value_prefix: the prefix of values for which the pseudonyms should be retrieved
        :param domain_name: domain for which the pseudonyms should be retrieved
        :return: list of value to pseudonyms data class instances
        """
        return get_pseudonyms_for_value_prefix(self._client, value_prefix, domain_name)

    def get_pseudonym_tree(self, pseudonym: str, domain_name: str) -> PseudonymTree:
        """
        Creates a pseudonym tree with all values that are somehow linked to the given pseudonym. Raises a Fault if the
        pseudonym is not found in the specified domain, there is no domain with such a name, or if the value is already
        anonymized.

        :param pseudonym: pseudonym to create the tree from
        :param domain_name: name of the domain for the given pseudonym
        :return: pseudonym tree data class instance
        """
        return get_pseudonym_tree(self._client, pseudonym, domain_name)

    def get_pseudonym_net(self, value_or_pseudonym: str) -> PseudonymNet:
        """
        Creates a pseudonym net with all values and pseudonyms that are somehow linked to the given value or pseudonym.

        :param value_or_pseudonym: value or pseudonym to create the net from
        :return: pseudonym net data class instance
        """
        return get_pseudonym_net(self._client, value_or_pseudonym)

    def are_pseudonyms_deletable(self, domain_name: str) -> bool:
        """
        Checks if the deletion of pseudonyms is allowed for the specified domain.

        :param domain_name: name of the domain to check
        :return: True if pseudonyms are allowed to be deleted, False otherwise
        """
        return are_pseudonyms_deletable(self._domain_client, domain_name)

    def list_pseudonyms(self, domain_name: str) -> list[Pseudonym]:
        """
        Retrieves all pseudonyms for the specified domain. Raises a Fault if there is no domain with such a name.

        :param domain_name: name of the domain to retrieve pseudonyms for
        :return: list of pseudonym data class instances
        """
        return list_pseudonyms(self._domain_client, domain_name)
