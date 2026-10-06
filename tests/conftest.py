import os
from collections.abc import Callable, Iterator
from pathlib import Path

import docker
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from mosaic_client import EPIXClient, GPASClient
from mosaic_client.epix import Domain as EPIXDomain
from mosaic_client.epix import IdentifierDomain, Person, Source
from mosaic_client.gpas import Domain as GPASDomain
from mosaic_client.gpas import DomainConfig, ValueToPseudonyms
from tests.helpers import random_identity, random_string


@pytest.fixture(scope="session")
def use_testcontainers() -> bool:
    return bool(int(os.getenv("PYTEST_USE_TESTCONTAINERS", "0")))


@pytest.fixture(scope="session")
def network() -> Iterator[Network]:
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def conftest_dir() -> Path:
    return Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def epix_mariadb(use_testcontainers, network, conftest_dir) -> Iterator[DockerContainer | None]:
    if use_testcontainers:
        container = (
            DockerContainer("mariadb:11.8")
            .with_network(network)
            .with_network_aliases("mariadb")
            .with_env("MARIADB_ROOT_PASSWORD", "root")
            .with_env("TZ", "Europe/Berlin")
            .with_name("epix-mariadb")
            .with_command(
                ["--max_allowed_packet=20M", "--default-time-zone=Europe/Berlin", "--innodb_buffer_pool_size=2G"]
            )
            .with_volume_mapping(
                conftest_dir / "docker" / "epix" / "mariadb-sqls",
                "/docker-entrypoint-initdb.d",
                mode="ro",
            )
        )

        with container:
            yield container
        return

    yield None


@pytest.fixture(scope="session")
def epix_wildfly(use_testcontainers, network, epix_mariadb) -> Iterator[DockerContainer | None]:
    if use_testcontainers:
        epix_image_tag = os.environ.get("PYTEST_EPIX_IMAGE_TAG", "latest")
        image = f"mosaicgreifswald/epix:{epix_image_tag}"

        if epix_image_tag == "latest":
            docker.from_env().images.pull(image)

        container = (
            DockerContainer(image)
            .waiting_for(LogMessageWaitStrategy("all processes started"))
            .with_exposed_ports(8080)
            .with_network(network)
            .with_network_aliases("epix-wildfly")
            .with_name("epix-wildfly")
            .with_env("TTP_DB_DBMS", "mariadb")
            .with_env("WF_WAIT_FOR_PORTS", "mariadb:3306:120")
            .with_env(
                "WF_HEALTHCHECK_URLS",
                "\n".join(["http://localhost:8080", "http://localhost:8080/epix-rest/health/state"]),  # noqa: FLY002
            )
        )

        with container:
            yield container
        return

    yield None


@pytest.fixture(scope="session")
def epix_wsdl_url(use_testcontainers, epix_wildfly) -> str:
    if use_testcontainers and epix_wildfly is not None:
        host = epix_wildfly.get_container_host_ip()
        port = epix_wildfly.get_exposed_port(8080)
        return f"http://{host}:{port}/epix/epixService?wsdl"

    return os.getenv("PYTEST_EPIX_WSDL_URL", "")


@pytest.fixture(scope="session")
def epix_management_wsdl_url(use_testcontainers, epix_wildfly) -> str:
    if use_testcontainers and epix_wildfly is not None:
        host = epix_wildfly.get_container_host_ip()
        port = epix_wildfly.get_exposed_port(8080)
        return f"http://{host}:{port}/epix/epixManagementService?wsdl"

    return os.getenv("PYTEST_EPIX_MANAGEMENT_WSDL_URL", "")


@pytest.fixture(scope="session")
def gpas_postgres(use_testcontainers, network, conftest_dir) -> Iterator[DockerContainer | None]:
    if use_testcontainers:
        container = (
            DockerContainer("postgres:17.11")
            .with_network(network)
            .with_network_aliases("postgresql")
            .with_env("POSTGRES_PASSWORD", "root")
            .with_env("TZ", "Europe/Berlin")
            .with_name("gpas-postgres")
            .with_command(["-cmax_connections=100", "-cshared_buffers=512MB", "-ceffective_cache_size=5GB"])
            .with_volume_mapping(
                conftest_dir / "docker" / "gpas" / "postgres-sqls",
                "/docker-entrypoint-initdb.d",
                mode="ro",
            )
        )

        with container:
            yield container
        return

    yield None


@pytest.fixture(scope="session")
def gpas_wildfly(use_testcontainers, network, gpas_postgres) -> Iterator[DockerContainer | None]:
    if use_testcontainers:
        gpas_image_tag = os.environ.get("PYTEST_GPAS_IMAGE_TAG", "latest")
        image = f"mosaicgreifswald/gpas:{gpas_image_tag}"

        if gpas_image_tag == "latest":
            docker.from_env().images.pull(image)

        container = (
            DockerContainer(image)
            .waiting_for(LogMessageWaitStrategy("all processes started"))
            .with_exposed_ports(8080)
            .with_network(network)
            .with_network_aliases("gpas-wildfly")
            .with_name("gpas-wildfly")
            .with_env("TTP_DB_DBMS", "postgresql")
            .with_env("WF_WAIT_FOR_PORTS", "postgresql:5432:120")
            .with_env(
                "WF_HEALTHCHECK_URLS",
                "\n".join(["http://localhost:8080", "http://localhost:8080/gpas-rest/health/state"]),  # noqa: FLY002
            )
        )

        with container:
            yield container
        return

    yield None


@pytest.fixture(scope="session")
def gpas_wsdl_url(use_testcontainers, gpas_wildfly) -> str:
    if use_testcontainers and gpas_wildfly is not None:
        host = gpas_wildfly.get_container_host_ip()
        port = gpas_wildfly.get_exposed_port(8080)
        return f"http://{host}:{port}/gpas/gpasService?wsdl"

    return os.getenv("PYTEST_GPAS_WSDL_URL", "")


@pytest.fixture(scope="session")
def gpas_domain_wsdl_url(use_testcontainers, gpas_wildfly) -> str:
    if use_testcontainers and gpas_wildfly is not None:
        host = gpas_wildfly.get_container_host_ip()
        port = gpas_wildfly.get_exposed_port(8080)
        return f"http://{host}:{port}/gpas/DomainService?wsdl"

    return os.getenv("PYTEST_GPAS_DOMAIN_WSDL_URL", "")


@pytest.fixture(scope="session")
def epix_client(epix_wsdl_url, epix_management_wsdl_url) -> EPIXClient:
    return EPIXClient(epix_wsdl_url, epix_management_wsdl_url)


@pytest.fixture(scope="session")
def gpas_client(gpas_wsdl_url, gpas_domain_wsdl_url) -> GPASClient:
    return GPASClient(gpas_wsdl_url, gpas_domain_wsdl_url)


@pytest.fixture(scope="session")
def epix_identifier_domain(epix_client) -> Iterator[str]:
    name = random_string()
    identifier_domain = IdentifierDomain(name=name, label=name, oid=random_string())
    epix_client.add_identifier_domain(identifier_domain=identifier_domain)

    yield name

    epix_client.delete_identifier_domain(identifier_domain_name=name)


@pytest.fixture(scope="session")
def epix_source(epix_client) -> Iterator[str]:
    name = random_string()
    epix_client.add_source(source=Source(name=name, label=name))

    yield name

    epix_client.delete_source(source_name=name)


@pytest.fixture(scope="session")
def epix_domain(epix_client, epix_identifier_domain, epix_source) -> Iterator[str]:
    name = random_string()
    epix_client.add_domain(
        domain=EPIXDomain(
            name=name,
            label=name,
            mpi_domain=epix_client.get_identifier_domain(identifier_domain_name=epix_identifier_domain),
            safe_source=epix_client.get_source(source_name=epix_source),
        )
    )

    yield name

    epix_client.delete_domain(domain_name=name, force=True)


@pytest.fixture(scope="session")
def gpas_domain(gpas_client) -> Iterator[str]:
    name = random_string()
    gpas_client.add_domain(domain=GPASDomain(name=name, label=name, config=DomainConfig(psns_deletable=True)))

    yield name

    gpas_client.delete_domain(domain_name=name)


@pytest.fixture()
def person(epix_client, epix_domain, epix_source) -> Iterator[Person]:
    r = epix_client.request_mpi(domain_name=epix_domain, source_name=epix_source, identity=random_identity())

    assert r.mpi_error_code is None

    yield r.person

    epix_client.deactivate_person(domain_name=epix_domain, mpi_id=r.person.mpi())
    epix_client.delete_person(domain_name=epix_domain, mpi_id=r.person.mpi())


@pytest.fixture(scope="session")
def value_psn_pair_factory(gpas_client, gpas_domain) -> Callable[[], ValueToPseudonyms]:
    def factory() -> ValueToPseudonyms:
        value = random_string()
        relation = gpas_client.get_or_create_pseudonyms_for(domain_name=gpas_domain, value=value)

        return relation

    return factory


@pytest.fixture()
def value_psn_pair(value_psn_pair_factory) -> ValueToPseudonyms:
    return value_psn_pair_factory()
