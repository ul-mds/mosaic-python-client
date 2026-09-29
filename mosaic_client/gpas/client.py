"""
This module contains functions for interacting with the gPAS SOAP interface.
"""

from zeep import Client

from mosaic_client.gpas.models import Domain, DomainResponse
from mosaic_client.gpas.schemas import DomainResponseSchema, DomainSchema
from mosaic_client.helpers import WSDLClient, _cast_client, _read_key_value_list, _serialize_dict

KeyValueTuple = tuple[str, str]


def delete_entry(client: Client, domain_name: str, value: str) -> None:
    """
    Deletes a value and its associated pseudonym from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is present
    :param value: value to remove
    """
    client.service.deleteEntry(domainName=domain_name, value=value)


def delete_entries(client: Client, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
    """
    Deletes a list of values and their associated pseudonyms from the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is present
    :param values: list of values to remove
    :return: list of key-value pairs where the key is the value that was requested to be deleted, and the value is
    an indicator whether deletion was successful or not
    """
    response = client.service.deleteEntries(domainName=domain_name, values=values)
    return _read_key_value_list(_serialize_dict(response))


def get_or_create_pseudonym_for(client: Client, domain_name: str, value: str) -> str:
    """
    Requests a new pseudonym for a value in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is supposed to be inserted
    :param value: value to insert
    :return: pseudonym that is assigned to the value
    """
    return client.service.getOrCreatePseudonymFor(domainName=domain_name, value=value)


def get_or_create_pseudonym_for_list(client: Client, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
    """
    Request new pseudonyms for a list of values in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is supposed to be inserted
    :param values: list of values to insert
    :return: list of key-value pairs where the key is the original value that is supposed to be pseudonymized,
    and the value is the assigned pseudonym
    """
    response = client.service.getOrCreatePseudonymForList(domainName=domain_name, values=values)
    return _read_key_value_list(_serialize_dict(response))


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


def get_pseudonym_for(client: Client, domain_name: str, value: str) -> str:
    """
    Gets the pseudonym for a value in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the value is present
    :param value: value to resolve
    :return: pseudonym assigned to the value
    """
    return client.service.getPseudonymFor(domainName=domain_name, value=value)


def get_pseudonym_for_list(client: Client, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
    """
    Gets the pseudonyms for a list of values in the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain where the values are present
    :param values: values to resolve
    :return: list of key-value pairs, structured as { value => pseudonym }
    """
    response = client.service.getPseudonymForList(domainName=domain_name, values=values)
    return _read_key_value_list(_serialize_dict(response))


def insert_value_pseudonym_pair(client: Client, domain_name: str, value: str, pseudonym: str) -> None:
    """
    Manually inserts a value and a pseudonym into the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain to insert the pair into
    :param value: value to add
    :param pseudonym: pseudonym to assign to the value
    """
    client.service.insertValuePseudonymPair(domainName=domain_name, value=value, pseudonym=pseudonym)


def insert_value_pseudonym_pairs(client: Client, domain_name: str, pairs: list[KeyValueTuple]) -> None:
    """
    Manually inserts a list of values and pseudonyms into the specified data domain.

    :param client: Zeep client with gPAS service definitions
    :param domain_name: name of the domain to insert the pairs into
    :param pairs: list of key-value pairs, structured as { value => pseudonym }
    """
    # for some reason this is the only case where the "entry" key is mandatory. it is not returned by any other
    # endpoints where there's supposedly an "entry" key, e.g. deleteEntries (???)
    client.service.insertValuePseudonymPairs(
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


def list_domains(client: Client) -> list[DomainResponse]:
    """
    Lists all available domains in the gPAS instance.

    :param client: Zeep client with gPAS domain service definitions
    :return: list of all available domains as domain response instances
    """
    domains = _serialize_dict(client.service.listDomains())
    return [DomainResponseSchema().load(domain) for domain in domains]


def delete_domain(client: Client, domain_name: str) -> None:
    """
    Deletes a domain that matches the specified name. Raises a Fault if there is no domain with such a name.

    :param client: Zeep client with gPAS domain service definitions
    :param domain_name: name of the domain to delete
    """
    client.service.deleteDomainWithPSNs(domainName=domain_name)


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
        Deletes a value and its associated pseudonym from the specified data domain.

        :param domain_name: name of the domain where the value is present
        :param value: value to remove
        """
        delete_entry(self._client, domain_name, value)

    def delete_entries(self, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
        """
        Deletes a list of values and their associated pseudonyms from the specified data domain.

        :param domain_name: name of the domain where the value is present
        :param values: list of values to remove
        :return: list of key-value pairs where the key is the value that was requested to be deleted, and the value is
        an indicator whether deletion was successful or not
        """
        return delete_entries(self._client, domain_name, values)

    def get_or_create_pseudonym_for(self, domain_name: str, value: str) -> str:
        """
        Requests a new pseudonym for a value in the specified data domain.

        :param domain_name: name of the domain where the value is supposed to be inserted
        :param value: value to insert
        :return: pseudonym that is assigned to the value
        """
        return get_or_create_pseudonym_for(self._client, domain_name, value)

    def get_or_create_pseudonym_for_list(self, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
        """
        Request new pseudonyms for a list of values in the specified data domain.

        :param domain_name: name of the domain where the value is supposed to be inserted
        :param values: list of values to insert
        :return: list of key-value pairs where the key is the original value that is supposed to be pseudonymized,
        and the value is the assigned pseudonym
        """
        return get_or_create_pseudonym_for_list(self._client, domain_name, values)

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

    def get_pseudonym_for(self, domain_name: str, value: str) -> str:
        """
        Gets the pseudonym for a value in the specified data domain.

        :param domain_name: name of the domain where the value is present
        :param value: value to resolve
        :return: pseudonym assigned to the value
        """
        return get_pseudonym_for(self._client, domain_name, value)

    def get_pseudonym_for_list(self, domain_name: str, values: list[str]) -> list[KeyValueTuple]:
        """
        Gets the pseudonyms for a list of values in the specified data domain.

        :param domain_name: name of the domain where the values are present
        :param values: values to resolve
        :return: list of key-value pairs, structured as { value => pseudonym }
        """
        return get_pseudonym_for_list(self._client, domain_name, values)

    def insert_value_pseudonym_pair(self, domain_name: str, value: str, pseudonym: str) -> None:
        """
        Manually inserts a value and a pseudonym into the specified data domain.

        :param domain_name: name of the domain to insert the pair into
        :param value: value to add
        :param pseudonym: pseudonym to assign to the value
        """
        insert_value_pseudonym_pair(self._client, domain_name, value, pseudonym)

    def insert_value_pseudonym_pairs(self, domain_name: str, pairs: list[KeyValueTuple]) -> None:
        """
        Manually inserts a list of values and pseudonyms into the specified data domain.

        :param domain_name: name of the domain to insert the pairs into
        :param pairs: list of key-value pairs, structured as { value => pseudonym }
        """
        insert_value_pseudonym_pairs(self._client, domain_name, pairs)

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
