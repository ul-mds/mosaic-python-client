"""
This module contains model classes of objects, which are commonly used in E-PIX and gPAS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, TypedDict

MatchingMode = Literal["MATCHING_IDENTITIES", "NO_DECISION"]
PersistMode = Literal["IDENTIFYING", "PRIVACY_PRESERVING"]
HashingAlgorithm = Literal["RandomHashingStrategy", "DoubleHashingStrategy", "DoubleHashingStrategyFaster"]
UpdateBehaviour = Literal["DEFAULT", "OVERWRITE_ALL", "UPDATE_ALL_ADD_MISSING"]
ValidatorOperator = Literal["ALL", "ALL_OR_NONE", "AT_LEAST_ONE", "EXACT_ONE"]
MatchingAlgorithm = Literal[
    "org.emau.icmvc.ttp.deduplication.impl.LevenshteinAlgorithm",
    "org.emau.icmvc.ttp.deduplication.impl.ColognePhoneticAlgorithm",
    "org.emau.icmvc.ttp.deduplication.impl.DeterministicAlgorithm",
    "org.emau.icmvc.ttp.deduplication.impl.SorensenDiceCoefficientAlgorithmCoded",
    "org.emau.icmvc.ttp.deduplication.impl.JaccardSimilarityAlgorithmCoded",
    "org.emau.icmvc.ttp.deduplication.impl.SorensenDiceCoefficient",
    "org.emau.icmvc.ttp.deduplication.impl.JaccardSimilarityAlgorithm",
]
BlockingMode = Literal["NUMBERS", "TEXT"]
MPIGenerator = Literal["org.emau.icmvc.ttp.epix.gen.impl.EAN13Generator"]


class EntryType(TypedDict):
    entry: list[dict[Any, Any]]


class FieldName(StrEnum):
    birth_date = "birthDate"
    birth_place = "birthPlace"
    civil_status = "civilStatus"
    death_date = "dateOfDeath"
    degree = "degree"
    external_date = "externalDate"
    first_name = "firstName"
    gender = "gender"
    last_name = "lastName"
    middle_name = "middleName"
    mothers_maiden_name = "mothersMaidenName"
    mother_tongue = "motherTongue"
    nationality = "nationality"
    prefix = "prefix"
    race = "race"
    religion = "religion"
    suffix = "suffix"
    value_1 = "value1"
    value_2 = "value2"
    value_3 = "value3"
    value_4 = "value4"
    value_5 = "value5"
    value_6 = "value6"
    value_7 = "value7"
    value_8 = "value8"
    value_9 = "value9"
    value_10 = "value10"
    vital_status = "vitalStatus"


@dataclass(frozen=True)
class IdentifierDomain:
    """
    Describes a value domain used to generate identifiers.
    """

    name: str
    label: str
    oid: str | None = None
    description: str | None = None
    entry_date: datetime | None = None
    update_date: datetime | None = None


@dataclass(frozen=True)
class Identifier:
    """
    Represents an identifier sourced from a specific value domain.
    """

    value: str
    identifier_domain: IdentifierDomain
    entry_date: datetime | None = None
    description: str | None = None
    fresh: bool | None = None


@dataclass(frozen=True)
class Contact:
    """
    Assigned to an identity to designate contact details.
    """

    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    district: str | None = None
    email: str | None = None
    external_date: datetime | None = None
    municipality_key: str | None = None
    phone: str | None = None
    state: str | None = None
    street: str | None = None
    zip_code: str | None = None


@dataclass(frozen=True)
class FullContact(Contact):
    """
    Contact with additional metadata.
    """

    contact_created: datetime | None = None
    contact_id: int | None = None
    contact_last_edited: datetime | None = None
    contact_version: int | None = None
    deactivated: bool | None = None
    identity_id: int | None = None


@dataclass(frozen=True)
class Identity:
    """
    Identifying information about a real-world entity.
    """

    birth_date: datetime | None = None
    birth_place: str | None = None
    civil_status: str | None = None
    degree: str | None = None
    external_date: datetime | None = None
    first_name: str | None = None
    gender: str | None = None
    identifiers: list[Identifier] = field(default_factory=list)
    last_name: str | None = None
    middle_name: str | None = None
    mother_tongue: str | None = None
    mothers_maiden_name: str | None = None
    nationality: str | None = None
    vital_status: str | None = None
    death_date: datetime | None = None
    prefix: str | None = None
    race: str | None = None
    religion: str | None = None
    suffix: str | None = None
    value_1: str | None = None
    value_2: str | None = None
    value_3: str | None = None
    value_4: str | None = None
    value_5: str | None = None
    value_6: str | None = None
    value_7: str | None = None
    value_8: str | None = None
    value_9: str | None = None
    value_10: str | None = None
    contacts: list[Contact] = field(default_factory=list)


@dataclass(frozen=True)
class Source:
    """
    Data source from which information is gathered.
    """

    name: str
    description: str | None = None
    label: str | None = None
    entry_date: datetime | None = None
    update_date: datetime | None = None


@dataclass(frozen=True)
class FullIdentity(Identity):
    """
    Identity with additional metadata.
    """

    deactivated: bool | None = None
    identity_created: datetime | None = None
    identity_id: int | None = None
    identity_last_edited: datetime | None = None
    identity_version: int | None = None
    person_id: int | None = None
    source: Source | None = None
    contacts: list[FullContact] = field(default_factory=list)


@dataclass(frozen=True)
class Person:
    """
    State of an identity inside a data source.
    """

    deactivated: bool
    mpi_id: Identifier
    person_created: datetime
    person_id: int
    person_last_edited: datetime
    other_identities: list[FullIdentity]
    reference_identity: FullIdentity
    domain_name: str

    def mpi(self) -> str:
        """
        Convenience function to quickly obtain the MPI of this person.

        :return: MPI associated to this person
        """
        return self.mpi_id.value

    def identity_id(self) -> int | None:
        """
        Convenience function to quickly obtain the identity ID of this person.

        :return: Identity ID associated to this person
        """
        return self.reference_identity.identity_id


@dataclass(frozen=True)
class ResponseEntry:
    """
    Response sent back by E-PIX on an MPI request. Contains information on whether the requested
    identity was already found in the data source.
    """

    match_status: str
    person: Person
    mpi_error_code: str | None


@dataclass(frozen=True)
class BatchResponseEntry(ResponseEntry):
    """
    Response sent back by E-PIX on a batch MPI request. Contains the same info as a normal
    MPI request, but also includes the request identity.
    """

    identity: Identity


@dataclass(frozen=True)
class BatchRequestConfig:
    """
    Configuration on how a batch request should be handled.
    """

    force_reference_update: bool
    save_action: str


@dataclass(frozen=True)
class Reason:
    """
    Reason for resolving a possible match. Gets used for the configuration of a domain.
    """

    name: str
    description: str | None = None


@dataclass(frozen=True)
class Deduplication:
    """
    List of reasons for resolving a possible match. Gets used for the configuration of a domain.
    """

    reasons: list[Reason] = field(default_factory=list)


@dataclass(frozen=True)
class SourceField:
    """
    Source fields that are hashed into Bloom filters.
    """

    name: FieldName
    seed: int


@dataclass(frozen=True)
class Balanced:
    """
    Indicates and seeds the balancing of Bloom filters.
    """

    seed: int


@dataclass(frozen=True)
class BloomFilterConfig:
    """
    Configuration on how Bloom filters should be generated.
    """

    storing_field: FieldName
    algorithm: HashingAlgorithm | str = "RandomHashingStrategy"
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ .-0123456789mfoux"
    balanced: Balanced | None = None
    bits_per_ngram: int = 15
    fold: int = 0
    length: int = 1_000
    ngrams: int = 2
    source_fields: list[SourceField] = field(default_factory=list)


@dataclass(frozen=True)
class Privacy:
    """
    Container for storing all Bloom filter configurations.
    """

    bloom_filter_configs: list[BloomFilterConfig] = field(default_factory=list)


@dataclass(frozen=True)
class Validator:
    """
    Defines the name of Java validator class and suitable criterion for that validator. Validators are part of a
    validation config which is part of the domain config.
    """

    qualified_class_name: str
    criterion: str


@dataclass(frozen=True)
class ValidatorGroup:
    """
    Groups validators and combines their result through a logical operator. Validator groups can be nested.
    """

    operator: ValidatorOperator
    validators: list[Validator] = field(default_factory=list)
    validator_groups: list["ValidatorGroup"] = field(default_factory=list)


@dataclass(frozen=True)
class ValidatorConfig:
    """
    Container of the configuration for a validator.
    """

    field_name: FieldName
    validator: Validator
    validator_group: ValidatorGroup | None = None


@dataclass(frozen=True)
class Validation:
    """
    Container for all validator configs.
    """

    validation_configs: list[ValidatorConfig] = field(default_factory=list)


@dataclass(frozen=True)
class PreprocessingField:
    """
    Defines preprocessing transformations and filers for a specific field.
    """

    field_name: FieldName
    complex_transformation_classes: list[str] = field(default_factory=list)
    simple_filter_types: EntryType | None = None
    simple_transformation_types: EntryType | None = None


@dataclass(frozen=True)
class FieldMatchingConfig:
    """
    Container for a matching configuration per field.
    """

    name: FieldName
    algorithm: MatchingAlgorithm | str
    blocking_mode: BlockingMode
    blocking_threshold: float
    matching_threshold: float
    weight: float
    multiple_values_separator: int = 0  # ASCII-value of a character.
    penalty_both_short: float = 0.0
    penalty_not_a_perfect_match: float = 0.0
    penalty_one_short: float = 0.0


def _default_field_matching_configs() -> list[FieldMatchingConfig]:
    """
    Field matching config defaults that are used in the E-PIX web UI.

    :return: list of default field matching configs
    """
    return [
        FieldMatchingConfig(
            name=FieldName.first_name,
            algorithm="org.emau.icmvc.ttp.deduplication.impl.LevenshteinAlgorithm",
            blocking_mode="TEXT",
            blocking_threshold=0.4,
            matching_threshold=0.8,
            weight=8.0,
        ),
        FieldMatchingConfig(
            name=FieldName.last_name,
            algorithm="org.emau.icmvc.ttp.deduplication.impl.LevenshteinAlgorithm",
            blocking_mode="TEXT",
            blocking_threshold=0.0,
            matching_threshold=0.8,
            weight=6.0,
        ),
        FieldMatchingConfig(
            name=FieldName.gender,
            algorithm="org.emau.icmvc.ttp.deduplication.impl.LevenshteinAlgorithm",
            blocking_mode="TEXT",
            blocking_threshold=0.0,
            matching_threshold=0.75,
            weight=3.0,
        ),
        FieldMatchingConfig(
            name=FieldName.birth_date,
            algorithm="org.emau.icmvc.ttp.deduplication.impl.LevenshteinAlgorithm",
            blocking_mode="NUMBERS",
            blocking_threshold=0.6,
            matching_threshold=1.0,
            weight=9.0,
        ),
    ]


@dataclass(frozen=True)
class MatchingConfig:
    """
    Container for the matching config for all fields of a specific domain.
    """

    fields: list[FieldMatchingConfig] = field(default_factory=_default_field_matching_configs)
    number_of_threads: int = 16
    parallel_matching_after: int = 1_000
    threshold_automatic_match: float = 1001.0
    threshold_possible_match: float = 1001.0
    use_cemfim: bool = False


@dataclass(frozen=True)
class DomainConfiguration:
    """
    Container for all configurations of a domain.
    """

    mpi_generator: MPIGenerator | str = "org.emau.icmvc.ttp.epix.gen.impl.EAN13Generator"
    mpi_prefix: str = "1001"
    persist_mode: PersistMode = "IDENTIFYING"
    deduplication: Deduplication | None = None
    privacy: Privacy | None = None
    update_behaviour: UpdateBehaviour = "DEFAULT"
    validation: Validation | None = None
    required_fields: list[FieldName] = field(
        default_factory=lambda: [FieldName.first_name, FieldName.last_name, FieldName.gender, FieldName.birth_date]
    )
    use_notifications: bool = False
    limit_search_for_low_memory: bool = False
    value_field_mapping: EntryType | None = field(default_factory=lambda: EntryType(entry=[]))
    preprocessing_fields: list[PreprocessingField] = field(default_factory=list)
    matching_config: MatchingConfig = field(default_factory=MatchingConfig)
    matching_mode: MatchingMode = "MATCHING_IDENTITIES"


@dataclass(frozen=True)
class Domain:
    """
    Describes an E-PIX domain.
    """

    name: str
    label: str
    mpi_domain: IdentifierDomain
    safe_source: Source
    config_objects: DomainConfiguration = field(default_factory=DomainConfiguration)
    description: str | None = ""
    in_use: bool = True
    matching_mode: MatchingMode = "MATCHING_IDENTITIES"
    entry_date: datetime | None = None
    update_date: datetime | None = None
    person_count: int = -1
    config: str | None = None
