from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Alphabet = (
    Literal[
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.Hex",
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.Numbers",
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.NumbersWithoutZero",
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.NumbersX",
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.Symbol31",
        "org.emau.icmvc.ganimed.ttp.psn.alphabets.Symbol32",
    ]
    | str
)
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
    alphabet: Alphabet = "org.emau.icmvc.ganimed.ttp.psn.alphabets.Numbers"
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
