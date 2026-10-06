from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

Alphabet = Literal[
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.Hex",
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.Numbers",
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.NumbersWithoutZero",
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.NumbersX",
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.Symbol31",
    "org.emau.icmvc.ganimed.ttp.psn.alphabets.Symbol32",
]
ForceCache = Literal["DEFAULT", "OFF", "ON"]
ValidateViaParents = Literal["CASCADE_DELETE", "ENSURE_EXISTS", "OFF", "VALIDATE"]


@dataclass(frozen=True)
class DomainConfig:
    """
    Configuration settings for gPAS domains.
    """

    psn_prefix: str | None = None
    psn_suffix: str | None = None
    include_prefix_in_check_digit_calculation: bool = False
    include_suffix_in_check_digit_calculation: bool = False
    max_detected_errors: int = 2
    multi_psn_domain: bool = False
    psn_length: int = 8
    psns_deletable: bool = False
    send_notifications_web: bool = False
    use_last_char_as_delimiter_after_x_chars: int = 0
    force_cache: ForceCache = "DEFAULT"
    validate_values_via_parents: ValidateViaParents = "OFF"


@dataclass(frozen=True)
class Domain:
    """
    Describes a gPAS domain.
    """

    label: str
    name: str
    config: DomainConfig = field(default_factory=DomainConfig)
    alphabet: Alphabet | str = "org.emau.icmvc.ganimed.ttp.psn.alphabets.Numbers"
    check_digit_class: str = "org.emau.icmvc.ganimed.ttp.psn.generator.Verhoeff"
    comment: str | None = None
    parent_domain_names: list[str] = field(default_factory=list)
    expiration_properties: None = None


@dataclass(frozen=True, kw_only=True)
class DomainResponse(Domain):
    """
    Further information about a domain that are available after a domain was created.
    """

    child_domain_names: list[str]
    number_of_pseudonyms: int
    number_of_anonyms: int
    cache_used: bool
    percent_psns_used: float
    create_date: datetime
    update_date: datetime
    create_date_string: str
    update_date_string: str


@dataclass(frozen=True)
class AnonymizationResponse:
    """
    In case of anonymizing a list of values, the response for each value is stored in this data class. The key is either
    represents the value or the pseudonym for which the value was anonymized.
    """

    key: str
    result: Literal["SUCCESS", "NOT_FOUND", "ALREADY_ANONYMISED", "ERROR"]


@dataclass(frozen=True)
class DeletionResponse:
    """
    In case of deleting a list of entries, the response for each value is stored in this data class.
    """

    key: str
    result: Literal["SUCCESS", "NOT_FOUND", "ERROR"]


@dataclass(frozen=True)
class ValueToPseudonyms:
    """
    Describes the relation from one value to its various pseudonyms.
    """

    value: str
    pseudonyms: list[str]

    @property
    def pseudonym(self) -> str:
        if len(self.pseudonyms) != 1:
            raise ValueError("There are more than one pseudonyms for this value.")
        return self.pseudonyms[0]


@dataclass(frozen=True)
class PseudonymTree:
    """
    Describes the relation of a pseudonym across related domains.
    """

    domain_name: str
    original_value: str | None
    pseudonym: str | None
    expiration_date: date | None
    level: int
    path: str | None
    children: list["PseudonymTree"]


@dataclass(frozen=True)
class PseudonymNetNode(PseudonymTree):
    """
    Describes a node in a pseudonym/value net.
    """

    children: list["PseudonymNetNode"]
    circle_children: list["PseudonymNetNode"]


@dataclass(frozen=True)
class PseudonymNet:
    """
    Describes all related values and pseudonyms for a specific pseudonym or value as a root.
    """

    root: PseudonymNetNode
    nodes: list[PseudonymNetNode]


@dataclass(frozen=True)
class InsertPairException:
    """
    Container that describes an error that could occur while inserting a value, pseudonym pair.
    """

    message: str
    value: str
    pseudonym: str
    domain: str
    error_type: Literal[
        "DIFFERENT_PSEUDONYM_FOR_VALUE_EXISTS",
        "DIFFERENT_VALUE_FOR_PSEUDONYM_EXISTS",
        "PSEUDONYM_INVALID",
        "VALUE_INVALID",
    ]


@dataclass(frozen=True)
class Pseudonym:
    """
    Container for holding metadata related to a pseudonym.
    """

    domain_name: str
    original_value: str
    pseudonym: str
    expiration_date: date
