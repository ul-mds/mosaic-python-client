[![PyPI](https://img.shields.io/pypi/v/mosaic-python-client?cacheSeconds=0&label=PyPI)](https://pypi.org/project/mosaic-python-client/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mosaic-python-client?cacheSeconds=0&label=Python)](https://pypi.org/project/mosaic-python-client/)
![Code Coverage](https://img.shields.io/badge/Coverage-96%25-brightgreen.svg)
[![License](https://img.shields.io/pypi/l/mosaic-python-client?cacheSeconds=0&label=License)](https://pypi.org/project/mosaic-python-client/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

# MOSAIC Client

The `mosaic_client` library provides wrappers around the SOAP (**S**imple **O**bject **A**ccess **P**rotocol) interfaces
of E-PIX and gPAS by the [THS Greifswald](https://www.ths-greifswald.de/en/projekte/mosaic-project/).
The main entrypoints are `mosaic_client.EPIXClient` and `mosaic_client.GPASClient`, which are classes that simply take
the URLs to the WSDL endpoints of their respective services and expose functions to interact with these services.
Both client classes are implemented as [Zeep](https://docs.python-zeep.org/en/master/) clients while validation is
leveraged by [marshmallow](https://marshmallow.readthedocs.io/en/latest/).

## Installation

To install the client, Python 3.11 or higher is required.

```shell
pip install mosaic-python-client
```

## Getting started

Both E-PIX and gPAS client can be either instantiated by passing the WSDL URLs as strings or by passing your own
`zeep.Client` instance.
This section briefly demonstrates the usage of both clients.
For more information, have a look at the clients available methods and the respective docstrings.

### E-PIX client

As a very first step, we need to instantiate the client.
`EPIXClient` expects a WSDL URL for the regular E-PIX service which enables operations like requesting an MPI
(**M**aster **P**atient **I**ndex) or deactivating/deleting identities and a WSDL URL for the management service which
leverages the management of domains.

```python
from mosaic_client import EPIXClient

epix = EPIXClient(
    client="http://localhost:8081/epix/epixService?wsdl",
    management_client="http://localhost:8081/epix/epixManagementService?wsdl",
)
```

To be able to request an MPI, we first need to create a data domain where the identity we want an MPI for is saved.
We name that new data domain `default`.
Note that E-PIX comes with a data source named `dummy_safe_source` and an identifier domain named `MPI` by default.

```python
from mosaic_client import EPIXClient
from mosaic_client.epix import Domain

epix = EPIXClient(
    client="http://localhost:8081/epix/epixService?wsdl",
    management_client="http://localhost:8081/epix/epixManagementService?wsdl",
)

epix.add_domain(
    domain=Domain(
        name="default",
        label="default",
        mpi_domain=epix.get_identifier_domain(identifier_domain_name="MPI"),
        safe_source=epix.get_source(source_name="dummy_safe_source"),
    )
)
```

Now, it is possible to request an MPI for an identity.
The default configuration of a data domain assumes that first and last name, gender and birthdate are required for new
identities.

```python
from dataclasses import asdict
import datetime
import json
from mosaic_client import EPIXClient
from mosaic_client.epix import Identity

epix = EPIXClient(
    client="http://localhost:8081/epix/epixService?wsdl",
    management_client="http://localhost:8081/epix/epixManagementService?wsdl",
)

mpi_response = epix.request_mpi(
    domain_name="default",
    source_name="dummy_safe_source",
    identity=Identity(
        first_name="Foo",
        last_name="Bar",
        gender="f",
        birth_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.UTC),
    ),
)

print(json.dumps(asdict(mpi_response), indent=2, default=str))
```

```text
{
  "match_status": "NO_MATCH",
  "person": {
    "deactivated": false,
    "mpi_id": {
      "value": "1001000000011",
      "identifier_domain": {
        "name": "MPI",
        "label": "MPI",
        "oid": "1.2.276.0.76.3.1.132.1.1.1",
        "description": null,
        "entry_date": "2026-09-29 15:57:00.492000+02:00",
        "update_date": "2026-09-29 15:57:00.492000+02:00"
      },
      "entry_date": "2026-09-29 15:57:43.496000+02:00",
      "description": "generated MPI id",
      "fresh": false
    },
    "person_created": "2026-09-29 15:57:43.496000+02:00",
    "person_id": 1,
    "person_last_edited": "2026-09-29 15:57:43.496000+02:00",
    "other_identities": [],
    "reference_identity": {
      "birth_date": "1970-01-01 01:00:00+01:00",
      "birth_place": null,
      "civil_status": null,
      "degree": null,
      "external_date": null,
      "first_name": "Foo",
      "gender": "F",
      "identifiers": [],
      "last_name": "Bar",
      "middle_name": null,
      "mother_tongue": null,
      "mothers_maiden_name": null,
      "nationality": null,
      "vital_status": null,
      "death_date": null,
      "prefix": null,
      "race": null,
      "religion": null,
      "suffix": null,
      "value_1": null,
      "value_2": null,
      "value_3": null,
      "value_4": null,
      "value_5": null,
      "value_6": null,
      "value_7": null,
      "value_8": null,
      "value_9": null,
      "value_10": null,
      "contacts": [],
      "deactivated": false,
      "identity_created": "2026-09-29 15:57:43.496000+02:00",
      "identity_id": 1,
      "identity_last_edited": "2026-09-29 15:57:43.496000+02:00",
      "identity_version": 1,
      "person_id": 1,
      "source": {
        "name": "dummy_safe_source",
        "description": "dummy because of the default-property \"safe_source\" in table domain",
        "label": "dummy_safe_source",
        "entry_date": "2026-09-29 15:57:00.531000+02:00",
        "update_date": "2026-09-29 15:57:00.531000+02:00"
      }
    },
    "domain_name": "default"
  },
  "mpi_error_code": null
}
```

### gPAS client

As before, we first need to instantiate the client.
`GPASClient` expects a WSDL URL for the regular gPAS service which enables operations like creating pseudonyms and a
WSDL URL for the domain service which leverages the management of domains.

```python
from mosaic_client import GPASClient

gpas = GPASClient(
    client="http://localhost:8080/gpas/gpasService?wsdl",
    domain_client="http://localhost:8080/gpas/DomainService?wsdl",
)
```

To be able to create pseudonyms, we first need to create a new domain since pseudonyms are organized in domains.
We name that new domain `default`.

```python
from mosaic_client import GPASClient
from mosaic_client.gpas import Domain

gpas = GPASClient(
    client="http://localhost:8080/gpas/gpasService?wsdl",
    domain_client="http://localhost:8080/gpas/DomainService?wsdl",
)

gpas.add_domain(domain=Domain(name="default", label="default"))
```

Now, we are able to create a new pseudonym for the value `value123`.

```python
from mosaic_client import GPASClient

gpas = GPASClient(
    client="http://localhost:8080/gpas/gpasService?wsdl",
    domain_client="http://localhost:8080/gpas/DomainService?wsdl",
)

pseudonym = gpas.get_or_create_pseudonym_for(domain_name="default", value="value123")

print(f"Pseudonym: {pseudonym}")
```

```text
Pseudonym: 199799437
```

## Running tests

This library implements its tests via [pytest](https://docs.pytest.org/en/stable/).
In order to run integration tests, a running instance of E-PIX and gPAS are needed.
The first option is to spin up the services independently and direct pytest to it.
Have a look at the provided docker compose file `./tests/docker/docker-compose.yml` for a quick solution.
For more sophisticated deployments, please read the documentation of
[E-PIX](https://www.ths-greifswald.de/forscher/e-pix/) and [gPAS](https://www.ths-greifswald.de/forscher/gpas/).
Alternatively, pytest can start Docker test-containers for the duration of the test run.
Since containers are started and stopped for each run individually, such a test run takes more time.

The following table shows all available options to configure pytest.

| **Environment variable**                     | **Description**                                     | **Default** |
|----------------------------------------------|-----------------------------------------------------|-------------|
| PYTEST_USE_TESTCONTAINERS                    | Whether pytest should use test-containers or not    | 0           |
| PYTEST_EPIX_WSDL_URL<sup>1)</sup>            | WSDL URL for the E-PIX service                      |             |
| PYTEST_EPIX_MANAGEMENT_WSDL_URL<sup>1)</sup> | WSDL URL for the E-PIX management service           |             |
| PYTEST_EPIX_IMAGE_TAG<sup>2)</sup>           | E-PIX image tag that is used for the test-container | latest      |
| PYTEST_GPAS_WSDL_URL<sup>1)</sup>            | WSDL URL for the gPAS service                       |             |
| PYTEST_GPAS_DOMAIN_WSDL_URL<sup>1)</sup>     | WSDL URL for the gPAS domain service                |             |
| PYTEST_GPAS_IMAGE_TAG<sup>2)</sup>           | gPAS image tag that is used for the test-container  | latest      |

<sup>1)</sup> Only needed, if `PYTEST_USE_TESTCONTAINERS` is set to `0`.<br>
<sup>2)</sup> Only used, if `PYTEST_USE_TESTCONTAINERS` is set to `1`.

It is possible to define these variables in a `.env.test` file.
The `.env.example` file provides a template.
You can copy the content of `.env.example` to directly get started with pytest using test-containers.

```shell
cp .env.example .env.test
```

## License

MIT.
