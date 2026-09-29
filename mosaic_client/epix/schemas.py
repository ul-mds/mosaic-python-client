"""
This module contains classes for easy (de-)serialization of SOAP requests and responses
using marshmallow.
"""

from marshmallow import Schema, fields, post_load

from mosaic_client.epix.models import (
    Balanced,
    BatchRequestConfig,
    BloomFilterConfig,
    Contact,
    Deduplication,
    Domain,
    DomainConfiguration,
    FieldMatchingConfig,
    FullContact,
    FullIdentity,
    Identifier,
    IdentifierDomain,
    Identity,
    MatchingConfig,
    Person,
    PreprocessingField,
    Privacy,
    Reason,
    ResponseEntry,
    Source,
    SourceField,
    Validation,
    Validator,
    ValidatorConfig,
    ValidatorGroup,
)


class SourceSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(load_default=None)
    label = fields.Str(load_default=None)
    entry_date = fields.DateTime(data_key="entryDate")
    update_date = fields.DateTime(data_key="updateDate")

    @post_load
    def make_source(self, data, **kwargs):
        return Source(**data)


class IdentifierDomainSchema(Schema):
    name = fields.Str(required=True)
    label = fields.Str(required=True)
    oid = fields.Str(load_default=None)
    description = fields.Str(load_default=None)
    entry_date = fields.DateTime(data_key="entryDate", load_default=None)
    update_date = fields.DateTime(data_key="updateDate", load_default=None)

    @post_load
    def make_identifier_domain(self, data, **kwargs):
        return IdentifierDomain(**data)


class IdentifierSchema(Schema):
    value = fields.Str(required=True)
    identifier_domain = fields.Nested(IdentifierDomainSchema(), required=True, data_key="identifierDomain")
    entry_date = fields.DateTime(data_key="entryDate", load_default=None)
    description = fields.Str(load_default=None)
    fresh = fields.Bool()

    @post_load
    def make_identifier(self, data, **kwargs):
        return Identifier(**data)


class ContactSchema(Schema):
    city = fields.Str(load_default=None)
    country = fields.Str(load_default=None)
    country_code = fields.Str(data_key="countryCode", load_default=None)
    district = fields.Str(load_default=None)
    email = fields.Str(load_default=None)
    external_date = fields.DateTime(data_key="externalDate", load_default=None)
    municipality_key = fields.Str(data_key="municipalityKey", load_default=None)
    phone = fields.Str(load_default=None)
    state = fields.Str(load_default=None)
    street = fields.Str(load_default=None)
    zip_code = fields.Str(data_key="zipCode", load_default=None)

    @post_load
    def make_contact(self, data, **kwargs):
        return Contact(**data)


class FullContactSchema(ContactSchema):
    contact_created = fields.DateTime(data_key="contactCreated", load_default=None)
    contact_id = fields.Int(data_key="contactId", load_default=None)
    contact_last_edited = fields.DateTime(data_key="contactLastEdited", load_default=None)
    contact_version = fields.Int(data_key="contactVersion", load_default=None)
    deactivated = fields.Bool()
    identity_id = fields.Int(data_key="identityId", load_default=None)

    @post_load
    def make_contact(self, data, **kwargs):
        return FullContact(**data)


class IdentitySchema(Schema):
    birth_date = fields.DateTime(data_key="birthDate", load_default=None)
    birth_place = fields.Str(data_key="birthPlace", load_default=None)
    civil_status = fields.Str(data_key="civilStatus", load_default=None)
    degree = fields.Str(load_default=None)
    external_date = fields.DateTime(data_key="externalDate", load_default=None)
    first_name = fields.Str(data_key="firstName", load_default=None)
    gender = fields.Str(load_default=None)
    identifiers = fields.List(fields.Nested(IdentifierSchema()))
    last_name = fields.Str(data_key="lastName", load_default=None)
    middle_name = fields.Str(data_key="middleName", load_default=None)
    mother_tongue = fields.Str(data_key="motherTongue", load_default=None)
    mothers_maiden_name = fields.Str(data_key="mothersMaidenName", load_default=None)
    nationality = fields.Str(load_default=None)
    vital_status = fields.Str(data_key="vitalStatus", load_default=None)
    death_date = fields.DateTime(data_key="dateOfDeath", load_default=None)
    prefix = fields.Str(load_default=None)
    race = fields.Str(load_default=None)
    religion = fields.Str(load_default=None)
    suffix = fields.Str(load_default=None)
    value_1 = fields.Str(data_key="value1", load_default=None)
    value_2 = fields.Str(data_key="value2", load_default=None)
    value_3 = fields.Str(data_key="value3", load_default=None)
    value_4 = fields.Str(data_key="value4", load_default=None)
    value_5 = fields.Str(data_key="value5", load_default=None)
    value_6 = fields.Str(data_key="value6", load_default=None)
    value_7 = fields.Str(data_key="value7", load_default=None)
    value_8 = fields.Str(data_key="value8", load_default=None)
    value_9 = fields.Str(data_key="value9", load_default=None)
    value_10 = fields.Str(data_key="value10", load_default=None)
    contacts = fields.List(fields.Nested(ContactSchema()))

    @post_load
    def make_identity(self, data, **kwargs):
        return Identity(**data)


class FullIdentitySchema(IdentitySchema):
    deactivated = fields.Bool()
    identity_created = fields.DateTime(data_key="identityCreated", load_default=None)
    identity_id = fields.Int(data_key="identityId", load_default=None)
    identity_last_edited = fields.DateTime(data_key="identityLastEdited", load_default=None)
    identity_version = fields.Int(data_key="identityVersion", load_default=None)
    person_id = fields.Int(data_key="personId", load_default=None)
    source = fields.Nested(SourceSchema(), load_default=None)
    contacts = fields.List(fields.Nested(FullContactSchema()))

    @post_load
    def make_identity(self, data, **kwargs):
        return FullIdentity(**data)


class PersonSchema(Schema):
    deactivated = fields.Bool(required=True)
    mpi_id = fields.Nested(IdentifierSchema(), required=True, data_key="mpiId")
    person_created = fields.DateTime(required=True, data_key="personCreated")
    person_id = fields.Int(required=True, data_key="personId")
    person_last_edited = fields.DateTime(required=True, data_key="personLastEdited")
    other_identities = fields.List(fields.Nested(FullIdentitySchema()), data_key="otherIdentities")
    reference_identity = fields.Nested(FullIdentitySchema(), required=True, data_key="referenceIdentity")
    domain_name = fields.Str(data_key="domainName", required=True)

    @post_load
    def make_person(self, data, **kwargs):
        return Person(**data)


class ResponseEntrySchema(Schema):
    match_status = fields.Str(required=True, data_key="matchStatus")
    mpi_error_code = fields.Str(data_key="mpiErrorCode", load_default=None)
    person = fields.Nested(PersonSchema(), required=True)

    @post_load
    def make_response_entry(self, data, **kwargs):
        return ResponseEntry(**data)


class BatchRequestConfigSchema(Schema):
    force_reference_update = fields.Bool(required=True, data_key="forceReferenceUpdate")
    save_action = fields.Str(required=True, data_key="saveAction")

    @post_load
    def make_batch_request_config(self, data, **kwargs):
        return BatchRequestConfig(**data)


class ReasonSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(load_default=None)

    @post_load
    def make_reason(self, data, **kwargs):
        return Reason(**data)


class DeduplicationSchema(Schema):
    reasons = fields.List(fields.Nested(ReasonSchema()))

    @post_load
    def make_deduplication(self, data, **kwargs):
        return Deduplication(**data)


class SourceFieldSchema(Schema):
    name = fields.Str(required=True)
    seed = fields.Int(required=True)

    @post_load
    def make_source_field(self, data, **kwargs):
        return SourceField(**data)


class BalancedSchema(Schema):
    seed = fields.Int(required=True)

    @post_load
    def make_balanced(self, data, **kwargs):
        return Balanced(**data)


class BloomFilterConfigSchema(Schema):
    storing_field = fields.Str(required=True, data_key="field")
    algorithm = fields.Str(required=True)
    alphabet = fields.Str(required=True)
    balanced = fields.Nested(BalancedSchema(), load_default=None)
    bits_per_ngram = fields.Int(required=True, data_key="bitsPerNgram")
    fold = fields.Int(required=True)
    length = fields.Int(required=True)
    ngrams = fields.Int(required=True)
    source_fields = fields.List(fields.Nested(SourceFieldSchema()), data_key="sourceFields")

    @post_load
    def make_bloom_filter_config(self, data, **kwargs):
        return BloomFilterConfig(**data)


class PrivacySchema(Schema):
    boom_filter_configs = fields.List(fields.Nested(BloomFilterConfigSchema(), data_key="bloomFilterConfigs"))

    @post_load
    def make_privacy(self, data, **kwargs):
        return Privacy(**data)


class ValidatorSchema(Schema):
    qualified_class_name = fields.Str(required=True, data_key="qualifiedClassName")
    criterion = fields.Str(required=True)

    @post_load
    def make_validator(self, data, **kwargs):
        return Validator(**data)


class ValidatorGroupSchema(Schema):
    operator = fields.Str(required=True)
    validators = fields.List(fields.Nested(ValidatorSchema()))
    validator_groups = fields.List(fields.Nested("self"), data_key="validatorGroups")

    @post_load
    def make_validator_group(self, data, **kwargs):
        return ValidatorGroup(**data)


class ValidatorConfigSchema(Schema):
    field_name = fields.Str(required=True, data_key="fieldName")
    validator = fields.Nested(ValidatorSchema(), required=True)
    validator_group = fields.Nested(ValidatorGroupSchema(), load_default=None, data_key="validatorGroup")

    @post_load
    def make_validator_config(self, data, **kwargs):
        return ValidatorConfig(**data)


class ValidationSchema(Schema):
    validation_configs = fields.List(fields.Nested(ValidatorConfigSchema()), data_key="validationConfigs")

    @post_load
    def make_validation(self, data, **kwargs):
        return Validation(**data)


class PreprocessingFieldSchema(Schema):
    field_name = fields.Str(required=True, data_key="fieldName")
    complex_transformation_classes = fields.List(fields.Str(), data_key="complexTransformationClasses")
    simple_filter_types = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Dict()),
        data_key="simpleFilterTypes",
        load_default=None,
    )
    simple_transformation_types = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Dict()),
        data_key="simpleTransformationTypes",
        load_default=None,
    )

    @post_load
    def make_preprocessing_field(self, data, **kwargs):
        return PreprocessingField(**data)


class FieldMatchingConfigSchema(Schema):
    name = fields.Str(required=True)
    algorithm = fields.Str(required=True)
    blocking_mode = fields.Str(required=True, data_key="blockingMode")
    blocking_threshold = fields.Float(required=True, data_key="blockingThreshold")
    matching_threshold = fields.Float(required=True, data_key="matchingThreshold")
    weight = fields.Int(required=True)
    multiple_values_separator = fields.Int(data_key="multipleValuesSeparator")
    penalty_both_short = fields.Float(data_key="penaltyBothShort")
    penalty_not_a_perfect_match = fields.Float(data_key="penaltyNotAPerfectMatch")
    penalty_one_short = fields.Float(data_key="penaltyOneShort")

    @post_load
    def make_field_matching_config(self, data, **kwargs):
        return FieldMatchingConfig(**data)


class MatchingConfigSchema(Schema):
    matching_fields = fields.List(fields.Nested(FieldMatchingConfigSchema()), data_key="fields", attribute="fields")
    number_of_threads = fields.Int(data_key="numberOfThreads")
    parallel_matching_after = fields.Int(data_key="parallelMatchingAfter")
    threshold_automatic_match = fields.Float(data_key="thresholdAutomaticMatch")
    threshold_possible_match = fields.Float(data_key="thresholdPossibleMatch")
    use_cemfim = fields.Bool(data_key="useCEMFIM")

    @post_load
    def make_matching_config(self, data, **kwargs):
        return MatchingConfig(**data)


class DomainConfigurationSchema(Schema):
    mpi_generator = fields.Str(data_key="mpiGenerator")
    mpi_prefix = fields.Str(data_key="mpiPrefix", required=True)
    persist_mode = fields.Str(data_key="persistMode")
    deduplication = fields.Nested(DeduplicationSchema(), load_default=None)
    privacy = fields.Nested(PrivacySchema(), load_default=None)
    update_behaviour = fields.Str(data_key="updateBehaviour")
    validation = fields.Nested(ValidationSchema(), load_default=None)
    required_fields = fields.List(fields.Str(), data_key="requiredFields", required=True)
    use_notifications = fields.Bool(data_key="useNotifications")
    limit_search_for_low_memory = fields.Bool(data_key="limitSearchForLowMemory")
    value_field_mapping = fields.Dict(
        keys=fields.Str(),
        values=fields.List(fields.Dict()),
        data_key="valueFieldMapping",
        load_default=None,
    )
    preprocessing_fields = fields.List(fields.Nested(PreprocessingFieldSchema()), data_key="preprocessingFields")
    matching_config = fields.Nested(MatchingConfigSchema(), data_key="matchingConfig")
    matching_mode = fields.Str(data_key="matchingMode")

    @post_load
    def make_domain_configuration(self, data, **kwargs):
        return DomainConfiguration(**data)


class DomainSchema(Schema):
    name = fields.Str(required=True)
    label = fields.Str(required=True)
    mpi_domain = fields.Nested(IdentifierDomainSchema(), required=True, data_key="mpiDomain")
    safe_source = fields.Nested(SourceSchema(), required=True, data_key="safeSource")
    config_objects = fields.Nested(DomainConfigurationSchema(), data_key="configObjects", required=True)
    description = fields.Str(load_default=None)
    in_use = fields.Bool(data_key="inUse")
    matching_mode = fields.Str(data_key="matchingMode")
    entry_date = fields.DateTime(data_key="entryDate")
    update_date = fields.DateTime(data_key="updateDate")
    person_count = fields.Int(data_key="personCount")
    config = fields.Str()

    @post_load
    def make_domain(self, data, **kwargs):
        return Domain(**data)
