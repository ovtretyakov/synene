# Generated by Django 2.2.1 on 2019-06-15 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_country_nationality'),
    ]

    operations = [
        migrations.RunSQL("""
BEGIN;
    CREATE OR REPLACE FUNCTION add_stat(piMatch        INTEGER, 
                                        pcStatType     VARCHAR,
                                        pcCompetitor   VARCHAR,
                                        piPeriod       INTEGER,
                                        pcValue        VARCHAR,
                                        piLoadSource   INTEGER,
                                        updated    OUT INTEGER, 
                                        stat_id    OUT INTEGER
                                        ) 
    AS 
    $BODY$
    DECLARE
        liReliability       INTEGER;
        liOldId             INTEGER;
        liOldLoadSource     INTEGER;
        lcOldValue          VARCHAR(255);
        liOldReliability    INTEGER;
        liUpdated           INTEGER;
        liStatID            INTEGER;
    BEGIN

        SELECT reliability INTO liReliability FROM core_loadsource WHERE id = piLoadSource;
        IF NOT FOUND THEN
            liReliability := NULL;
        END IF;

        SELECT s.id, s.load_source_id, s.value, l.reliability
            INTO liStatID, liOldLoadSource, lcOldValue, liOldReliability
            FROM core_matchstats s
            LEFT JOIN core_loadsource l ON(s.load_source_id = l.id)
            WHERE s.match_id = piMatch
              AND s.stat_type = pcStatType
              AND s.competitor = pcCompetitor
              AND s.period = piPeriod
        ;
        IF NOT FOUND THEN
            liStatID          := NULL;
            liOldLoadSource  := NULL;
            liOldReliability := NULL;
        END IF;


        IF liStatID IS NOT NULL THEN
            IF pcValue != lcOldValue AND
               liReliability IS NOT NULL AND 
               (liOldReliability IS NULL OR liReliability <= liOldReliability)
                THEN

                UPDATE core_matchstats
                    SET value = pcValue,
                        load_source_id = piLoadSource
                    WHERE id = liStatID
                ;
                liUpdated := 1;

            ELSIF pcValue = lcOldValue AND
               liReliability IS NOT NULL AND 
               (liOldReliability IS NULL OR liReliability < liOldReliability)
                THEN

                UPDATE core_matchstats
                    SET load_source_id = piLoadSource
                    WHERE id = liStatID
                ;
                liUpdated := 1;
            ELSE
                liUpdated := 0;
            END IF;

        ELSE
            INSERT INTO core_matchstats(match_id, stat_type, competitor, period, value, load_source_id)
                VALUES(piMatch, pcStatType, pcCompetitor, piPeriod, pcValue, piLoadSource)
                RETURNING id iNTO liStatID
            ;
            liUpdated := 1;
        END IF;
    
    
    updated := liUpdated; 
    stat_id := liStatID;
  END;
  $BODY$ LANGUAGE plpgsql
  SECURITY DEFINER;
  GRANT EXECUTE ON FUNCTION add_stat TO PUBLIC;
COMMIT;  
            """)
    ]
