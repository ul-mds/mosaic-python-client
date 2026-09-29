DROP SCHEMA IF EXISTS gpas ;
CREATE DATABASE gpas;

CREATE USER gpas_user WITH PASSWORD 'gpas_password';
GRANT ALL PRIVILEGES ON DATABASE gpas TO gpas_user;

\c gpas;

CREATE TABLE domain (
    name varchar(255) NOT NULL PRIMARY KEY,
    label varchar(255),
    alphabet varchar(255),
    comment varchar(255),
    generatorclass varchar(255),
    properties varchar(1023),
    expiration_properties varchar(1023) DEFAULT NULL,
    create_timestamp timestamp(3) DEFAULT NOW(),
    update_timestamp timestamp(3) DEFAULT NOW()
);
ALTER TABLE domain OWNER TO gpas_user;

CREATE TABLE domain_parents (
    domain varchar(255) NOT NULL,
    parentdomain varchar(255) NOT NULL,  -- Hinweis: PostgreSQL normalisiert Bezeichner standardmäßig in Kleinbuchstaben.
    PRIMARY KEY (domain, parentdomain),
    CONSTRAINT fk_domain_parents_domain FOREIGN KEY (domain) REFERENCES domain(name),
    CONSTRAINT fk_domain_parents_domain_2 FOREIGN KEY (parentdomain) REFERENCES domain(name)
);
ALTER TABLE domain_parents OWNER TO gpas_user;

-- Erstelle einen zusätzlichen Index für parentdomain,
-- der dem MySQL KEY FK_domain_parents_domain_2 entspricht.
CREATE INDEX ix_domain_parents_parentdomain ON domain_parents(parentdomain);


CREATE TABLE psn (
    originalvalue varchar(255) NOT NULL,
    pseudonym varchar(255) NOT NULL,
    domain varchar(255) NOT NULL,
    encoded_expiration_date SMALLINT,
    PRIMARY KEY (domain, originalvalue),
    CONSTRAINT psn_domain_pseudonym_unique UNIQUE (domain, pseudonym),
    CONSTRAINT fk_psn_domain FOREIGN KEY (domain) REFERENCES domain(name)
);
ALTER TABLE psn OWNER TO gpas_user;

CREATE TABLE mpsn (
    originalvalue varchar(255) NOT NULL,
    pseudonym varchar(255) NOT NULL,
    domain varchar(255) NOT NULL,
    encoded_expiration_date SMALLINT,
    PRIMARY KEY (domain, originalvalue, pseudonym),
    CONSTRAINT mpsn_domain_pseudonym_unique UNIQUE (domain, pseudonym),
    CONSTRAINT fk_mpsn_domain FOREIGN KEY (domain) REFERENCES domain(name)
);
ALTER TABLE mpsn OWNER TO gpas_user;

-- Separater Index für (domain, originalvalue) (optional, falls benötigt):
CREATE INDEX idx_mpsn_domain_originalvalue ON mpsn(domain, originalvalue);

CREATE TABLE IF NOT EXISTS stat_entry (
    stat_entry_id BIGSERIAL PRIMARY KEY,  -- BIGSERIAL ersetzt AUTO_INCREMENT
    entrydate TIMESTAMP(3) NOT NULL DEFAULT NOW()
);
ALTER TABLE stat_entry OWNER TO gpas_user;

CREATE TABLE IF NOT EXISTS stat_value (
    stat_value_id BIGINT NULL DEFAULT NULL,
    stat_value BIGINT NULL DEFAULT NULL,
    stat_attr VARCHAR(255) NULL DEFAULT NULL
);
ALTER TABLE stat_value OWNER TO gpas_user;

CREATE INDEX idx_stat_value_stat_value_id ON stat_value(stat_value_id);

-- Foreign-Key-Constraint:
ALTER TABLE stat_value
    ADD CONSTRAINT fk_stat_value_stat_entry
        FOREIGN KEY (stat_value_id) REFERENCES stat_entry(stat_entry_id);

CREATE TABLE sequence (
    seq_name varchar(50) PRIMARY KEY NOT NULL,
    seq_count numeric(38,0)
);
ALTER TABLE sequence OWNER TO gpas_user;

DROP VIEW IF EXISTS psn_domain_count;
CREATE OR REPLACE VIEW psn_domain_count(attribut, value) AS
SELECT
    'pseudonyms_per_domain.' || d.name AS attribut,
    COUNT(p.pseudonym) + COUNT(m.pseudonym) AS value
FROM
    domain d
        LEFT JOIN psn p ON p.domain = d.name
        LEFT JOIN mpsn m ON m.domain = d.name
WHERE
    d.name <> 'internal_anonymisation_domain'
GROUP BY d.name;
ALTER VIEW psn_domain_count OWNER TO gpas_user;

-- convert_to_multi_psn_domain (Postgres)
CREATE OR REPLACE PROCEDURE convert_to_multi_psn_domain(in_domain TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    conflict INTEGER;
BEGIN
    -- prüfe ob domain existiert
    SELECT COUNT(*) INTO conflict FROM domain WHERE name = in_domain;
    IF conflict = 0 THEN
        RAISE EXCEPTION 'Domain "%" not exists.', in_domain;
    END IF;

    -- prüfe ob domain bereits in multi-psn vorhanden
    SELECT COUNT(*) INTO conflict FROM mpsn WHERE domain = in_domain;
    IF conflict > 0 THEN
        RAISE EXCEPTION 'Domain "%" already exists in mpsn-table.', in_domain;
    END IF;

    -- INSERT (mit ON CONFLICT als Ersatz für MySQL REPLACE)
    -- -> Annahme: UNIQUE(originalValue, domain). Falls anders, bitte anpassen.
    INSERT INTO mpsn (originalValue, pseudonym, domain, encoded_expiration_date)
    SELECT originalValue, pseudonym, domain, encoded_expiration_date
    FROM psn
    WHERE domain = in_domain
    ON CONFLICT (originalValue, domain)
    DO UPDATE SET
        pseudonym = EXCLUDED.pseudonym,
        encoded_expiration_date = EXCLUDED.encoded_expiration_date;

    -- lösche die psn-zeilen
    DELETE FROM psn WHERE domain = in_domain;

    -- setze MULTI_PSN_DOMAIN=true in domain.properties
    UPDATE domain
    SET properties =
        -- entferne vorhandene MULTI_PSN_DOMAIN=... Einträge und führende ';'
        regexp_replace(
            regexp_replace(coalesce(properties, ''), ';?MULTI_PSN_DOMAIN=[^;]+', '', 'g'),
            '^;', '', 'g'
        )
        -- füge evtl. ein Trennzeichen ein
        || (CASE WHEN coalesce(properties, '') = '' OR right(coalesce(properties, ''), 1) = ';' THEN '' ELSE ';' END)
        || 'MULTI_PSN_DOMAIN=true;'
    WHERE name = in_domain;
END;
$$;
ALTER PROCEDURE convert_to_multi_psn_domain OWNER TO gpas_user;

-- convert_to_single_psn_domain (Postgres)
CREATE OR REPLACE PROCEDURE convert_to_single_psn_domain(in_domain TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    conflict INTEGER;
BEGIN
    -- prüfe ob domain existiert
    SELECT COUNT(*) INTO conflict FROM domain WHERE name = in_domain;
    IF conflict = 0 THEN
        RAISE EXCEPTION 'Domain "%" not exists.', in_domain;
    END IF;

    -- prüfe ob domain bereits in single-psn vorhanden
    SELECT COUNT(*) INTO conflict FROM psn WHERE domain = in_domain;
    IF conflict > 0 THEN
        RAISE EXCEPTION 'Domain "%" already exists in psn-table.', in_domain;
    END IF;

    -- prüfe Konflikte mit mehrfachen originalValue in mpsn
    SELECT COUNT(*) INTO conflict
    FROM (
        SELECT originalValue
        FROM mpsn
        WHERE domain = in_domain
        GROUP BY originalValue
        HAVING COUNT(*) > 1
        LIMIT 1
    ) t;
    IF conflict > 0 THEN
        RAISE EXCEPTION 'At least one originalValue is not unique in domain "%".', in_domain;
    END IF;

    -- INSERT in psn (kein REPLACE)
    INSERT INTO psn (originalValue, pseudonym, domain, encoded_expiration_date)
    SELECT originalValue, pseudonym, domain, encoded_expiration_date
    FROM mpsn
    WHERE domain = in_domain;

    -- lösche die mpsn-zeilen
    DELETE FROM mpsn WHERE domain = in_domain;

    -- setze MULTI_PSN_DOMAIN=false in domain.properties (falls vorhanden)
    UPDATE domain
    SET properties = regexp_replace(coalesce(properties, ''), 'MULTI_PSN_DOMAIN=[^;]+', 'MULTI_PSN_DOMAIN=false', 'g')
    WHERE name = in_domain;
END;
$$;
ALTER PROCEDURE convert_to_single_psn_domain OWNER TO gpas_user;
