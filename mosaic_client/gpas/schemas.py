from marshmallow import Schema, fields, post_load

from mosaic_client.gpas.models import (
    AnonymizationResponse,
    DeletionResponse,
    Domain,
    DomainConfig,
    DomainResponse,
    InsertPairException,
    Pseudonym,
    PseudonymNet,
    PseudonymNetNode,
    PseudonymTree,
    ValueToPseudonyms,
)


class DomainConfigSchema(Schema):
    psn_prefix = fields.Str(data_key="psnPrefix", allow_none=True)
    psn_suffix = fields.Str(data_key="psnSuffix", allow_none=True)
    include_prefix_in_check_digit_calculation = fields.Bool(data_key="includePrefixInCheckDigitCalculation")
    include_suffix_in_check_digit_calculation = fields.Bool(data_key="includeSuffixInCheckDigitCalculation")
    max_detected_errors = fields.Int(data_key="maxDetectedErrors")
    multi_psn_domain = fields.Bool(data_key="multiPsnDomain")
    psn_length = fields.Int(data_key="psnLength")
    psns_deletable = fields.Bool(data_key="psnsDeletable")
    send_notifications_web = fields.Bool(data_key="sendNotificationsWeb")
    use_last_char_as_delimiter_after_x_chars = fields.Int(data_key="useLastCharAsDelimiterAfterXChars")
    validate_values_via_parents = fields.Str(data_key="validateValuesViaParents")
    force_cache = fields.Str(data_key="forceCache")

    @post_load
    def make_domain_config(self, data, **kwargs) -> DomainConfig:
        return DomainConfig(**data)


class DomainSchema(Schema):
    label = fields.Str(required=True)
    name = fields.Str(required=True)
    config = fields.Nested(DomainConfigSchema())
    alphabet = fields.Str()
    check_digit_class = fields.Str(data_key="checkDigitClass")
    comment = fields.Str(allow_none=True)
    parent_domain_names = fields.List(fields.Str(), data_key="parentDomainNames")
    expiration_properties = fields.Constant(None, data_key="expirationProperties")

    @post_load
    def make_domain(self, data, **kwargs) -> Domain:
        return Domain(**data)


class DomainResponseSchema(DomainSchema):
    child_domain_names = fields.List(fields.Str(), data_key="childDomainNames")
    number_of_pseudonyms = fields.Int(data_key="numberOfPseudonyms")
    number_of_anonyms = fields.Int(data_key="numberOfAnonyms")
    cache_used = fields.Bool(data_key="cacheUsed")
    percent_psns_used = fields.Float(data_key="percentPsnsUsed")
    create_date = fields.DateTime(data_key="createDate")
    update_date = fields.DateTime(data_key="updateDate")
    create_date_string = fields.Str(data_key="createDateString")
    update_date_string = fields.Str(data_key="updateDateString")

    @post_load
    def make_domain(self, data, **kwargs) -> DomainResponse:
        return DomainResponse(**data)


class AnonymizationResponseSchema(Schema):
    key = fields.Str(required=True)
    result = fields.Str(required=True, data_key="value")

    @post_load
    def make_anonymization_response(self, data, **kwargs) -> AnonymizationResponse:
        return AnonymizationResponse(**data)


class DeletionResponseSchema(Schema):
    key = fields.Str(required=True)
    result = fields.Str(required=True, data_key="value")

    @post_load
    def make_deletion_response(self, data, **kwargs) -> DeletionResponse:
        return DeletionResponse(**data)


class ValueToPseudonymsSchema(Schema):
    value = fields.Str(required=True)
    pseudonyms = fields.List(fields.Str(), data_key="psn", required=True)

    @post_load
    def make_value_to_pseudonyms(self, data, **kwargs) -> ValueToPseudonyms:
        return ValueToPseudonyms(**data)


class PseudonymTreeSchema(Schema):
    domain_name = fields.Str(required=True, data_key="domainName")
    original_value = fields.Str(data_key="originalValue", load_default=None)
    pseudonym = fields.Str(load_default=None)
    expiration_date = fields.Date(data_key="expirationDate", load_default=None)
    level = fields.Int(required=True)
    path = fields.Str(load_default=None)
    children = fields.List(fields.Nested("PseudonymTreeSchema"))

    @post_load
    def make_pseudonym_tree(self, data, **kwargs) -> PseudonymTree:
        return PseudonymTree(**data)


class PseudonymNetNodeSchema(PseudonymTreeSchema):
    children = fields.List(fields.Nested("PseudonymNetNodeSchema"))
    circle_children = fields.List(fields.Nested("PseudonymNetNodeSchema"), data_key="circleChildren", load_default=list)

    make_pseudonym_tree = None  # Otherwise this will be called on load().

    @post_load
    def make_pseudonym_net_node(self, data, **kwargs) -> PseudonymNetNode:
        return PseudonymNetNode(**data)


class PseudonymNetSchema(Schema):
    root = fields.Nested(PseudonymNetNodeSchema, required=True)
    nodes = fields.List(fields.Nested(PseudonymNetNodeSchema))

    @post_load
    def make_pseudonym_net(self, data, **kwargs) -> PseudonymNet:
        return PseudonymNet(**data)


class InsertPairExceptionSchema(Schema):
    domain = fields.Str(required=True)
    pseudonym = fields.Str(required=True)
    value = fields.Str(required=True)
    message = fields.Str(required=True)
    error_type = fields.Str(required=True, data_key="errorType")

    @post_load
    def make_insert_pair_exception(self, data, **kwargs) -> InsertPairException:
        return InsertPairException(**data)


class PseudonymSchema(Schema):
    domain_name = fields.Str(required=True, data_key="domainName")
    original_value = fields.Str(required=True, data_key="originalValue")
    pseudonym = fields.Str(required=True)
    expiration_date = fields.Date(data_key="expirationDate", load_default=None)

    @post_load
    def make_pseudonym(self, data, **kwargs) -> Pseudonym:
        return Pseudonym(**data)
