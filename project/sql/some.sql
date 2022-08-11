WITH d AS (
SELECT p.slug AS predictor, b.name AS bookie,
       bo.match_id, m.match_date, th.name || ' - ' || ta.name AS match_name, m.score,
       l.name AS league_name, bt.name AS bet_type, 
       o.period, o.yes, o.team, o.param, o.result, o.odd_value, o.result_value,
       bo.success_chance, bo.lose_chance, bo.result_value AS expect_value, bo.kelly, 
       o.result_value-1 AS win,
       1 - bo.kelly + bo.kelly*bo.result_value AS growth,
       CASE WHEN o.odd_value < 1.15 THEN 1.1 
            WHEN o.odd_value < 1.25 THEN 1.2 
            WHEN o.odd_value < 1.4  THEN 1.3 
            WHEN o.odd_value < 1.65 THEN 1.5 
            WHEN o.odd_value < 1.9  THEN 1.7 
            WHEN o.odd_value < 2.2  THEN 2.0 
            WHEN o.odd_value < 3.0  THEN 3.0 
            ELSE 4.0
       END odd_rnd,
       CASE WHEN bo.success_chance < 0.4 THEN 0.2 
            WHEN bo.success_chance < 0.6 THEN 0.5 
            WHEN bo.success_chance < 0.7 THEN 0.6 
            WHEN bo.success_chance < 0.8 THEN 0.7 
            WHEN bo.success_chance < 0.9 THEN 0.8 
            ELSE 0.9
       END success_rnd,
       CASE WHEN bo.kelly = 0.0  THEN 0.0 
            WHEN bo.kelly < 0.07 THEN 0.05 
            WHEN bo.kelly < 0.16 THEN 0.1 
            WHEN bo.kelly < 0.25 THEN 0.2 
            WHEN bo.kelly < 0.4  THEN 0.3 
            ELSE 0.5
       END kelly_rnd
  FROM synene.betting_forecast bo,
       synene.betting_predictor p,
       synene.core_match m,
       synene.core_team th,
       synene.core_team ta,
       synene.core_league l,
       synene.betting_odd o,
       synene.betting_bettype bt,
       synene.core_loadsource b
  WHERE bo.status = 's' AND bo.forecast_set_id = 2
    AND bo.predictor_id = p.id
    AND bo.match_id = m.id
    AND m.team_h_id = th.id
    AND m.team_a_id = ta.id
    AND m.league_id = l.id
    AND bo.odd_id = o.id
    AND o.bet_type_id = bt.id
    AND o.bookie_id = b.id
)
SELECT d.*,
       --kelly
       row_number() OVER(PARTITION BY predictor, bookie, match_id ORDER BY kelly DESC, expect_value DESC) AS kelly_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, odd_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, success_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, kelly_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_kelly_rn,

       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, odd_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, success_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, kelly_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_kelly_rn,
       
       
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_period_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, odd_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_period_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, success_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_period_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, kelly_rnd ORDER BY kelly DESC, expect_value DESC) AS kelly_btype_period_kelly_rn,

       
       
       --growth
       row_number() OVER(PARTITION BY predictor, bookie, match_id ORDER BY growth DESC, expect_value DESC) AS growth_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, odd_rnd ORDER BY growth DESC, expect_value DESC) AS growth_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, success_rnd ORDER BY growth DESC, expect_value DESC) AS growth_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, kelly_rnd ORDER BY growth DESC, expect_value DESC) AS growth_kelly_rn,
       
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes ORDER BY growth DESC, expect_value DESC) AS growth_btype_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, odd_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, success_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, kelly_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_kelly_rn,
       
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period ORDER BY growth DESC, expect_value DESC) AS growth_btype_period_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, odd_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_period_odd_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, success_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_period_success_rn,
       row_number() OVER(PARTITION BY predictor, bookie, match_id, bet_type, yes, period, kelly_rnd ORDER BY growth DESC, expect_value DESC) AS growth_btype_period_kelly_rn
  FROM d  
  WHERE kelly > 0  
  ORDER BY match_id DESC, period DESC
  LIMIT 1000
;  




SELECT *
  FROM 
    (
    SELECT s.*,
           row_number() OVER(ORDER BY event_date DESC) AS rn
      FROM synene.betting_teamskill s
      WHERE harvest_id = 1 AND team_id = 400 AND event_date <= DATE '2021-12-01' AND param = 'h'
    ) d
  WHERE rn <= 10
;

WITH m AS 
  (
    SELECT m.id AS match_id, m.*, 
           h.name AS h_name, a.name AS a_name, l.name AS league_name,
           TO_NUMBER(s1.value,'99999999.9999') AS gH,
           TO_NUMBER(s2.value,'99999999.9999') AS gA,
           TO_NUMBER(gh.value,'99999999.9999') AS gxH,
           TO_NUMBER(ga.value,'99999999.9999') AS gxA
      FROM synene.core_match m
           JOIN synene.core_matchstats s1  ON(s1.stat_type = 'g' AND s1.period = 0 AND s1.match_id = m.id AND s1.competitor = 'h' )
           JOIN synene.core_matchstats s2 ON(s2.stat_type = 'g' AND s2.period = 0 AND s2.match_id = m.id AND s2.competitor = 'a')
           JOIN synene.core_matchstats gh ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
           JOIN synene.core_matchstats ga ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
           JOIN synene.core_team h ON (m.team_h_id = h.id)
           JOIN synene.core_team a ON (m.team_a_id = a.id)
           JOIN synene.core_league l ON (m.league_id = l.id)
      WHERE m.league_id = 7 AND m.season_id = 1048 --AND m.match_date < DATE '2022-01-23'
        AND m.status = 'F'
  ),
t AS (
  SELECT m.team_h_id AS team_id, h_name AS team_name, 
         result, 
         gH, gA
    FROM m
  UNION ALL
  SELECT m.team_a_id AS team_id, a_name AS team_name, 
         CASE WHEN result = 'w' THEN 'l' WHEN result = 'l' THEN 'w' ELSE result END AS result, 
         gA, gH
    FROM m
),
agg AS (
  SELECT team_id, team_name,
         COUNT(*) AS match_cnt, SUM(gH) AS gH, SUM(gA) AS gA,
         COUNT(*) FILTER(WHERE result='w') AS w,
         COUNT(*) FILTER(WHERE result='d') AS d,
         COUNT(*) FILTER(WHERE result='l') AS l,
         SUM(CASE WHEN result='w' THEN 3 WHEN result='d' THEN 1 ELSE 0 END) AS points 
    FROM t
    GROUP BY team_id, team_name
)
SELECT  ROW_NUMBER() OVER(ORDER BY points DESC, gH - gA DESC, gH DESC, team_id) AS rn,
        team_id, team_name, match_cnt, w, d, l, gH, gA, points 
  FROM agg
  ORDER BY rn
;





WITH m AS 
  (
    SELECT *
      FROM 
        (
        SELECT d.*, ROW_NUMBER() OVER(ORDER BY match_date DESC, match_id DESC) AS rn
          FROM 
            (
        SELECT m.result, 
               'h' AS ha, m.id AS match_id, m.match_date, m.score, m.team_h_id, m.team_a_id, 
               h.name AS h_name, a.name AS a_name, 
               TO_NUMBER(gh.value,'99999999.9999') AS gxH,
               TO_NUMBER(ga.value,'99999999.9999') AS gxA
          FROM synene.core_match m
               JOIN synene.core_matchstats gh ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
               JOIN synene.core_matchstats ga ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
               JOIN synene.core_team h ON (m.team_h_id = h.id)
               JOIN synene.core_team a ON (m.team_a_id = a.id)
          WHERE m.league_id = 7 AND m.match_date < DATE '2022-01-18' AND m.team_h_id = 400
            AND m.status = 'F'
        UNION ALL
        SELECT CASE WHEN m.result='w' THEN 'l' WHEN m.result='l' THEN 'w' ELSE m.result END AS result, 
               'a' AS ha, m.id AS match_id, m.match_date, m.score, m.team_h_id, m.team_a_id,
               h.name AS h_name, a.name AS a_name, 
               TO_NUMBER(gh.value,'99999999.9999') AS gxH,
               TO_NUMBER(ga.value,'99999999.9999') AS gxA
          FROM synene.core_match m
               JOIN synene.core_matchstats gh ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
               JOIN synene.core_matchstats ga ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
               JOIN synene.core_team h ON (m.team_h_id = h.id)
               JOIN synene.core_team a ON (m.team_a_id = a.id)
          WHERE m.league_id = 7 AND m.match_date < DATE '2022-01-18' AND m.team_a_id = 400
            AND m.status = 'F'
            ) d
        ) d2
      WHERE rn <= 10
  ),
mh AS 
  (
    SELECT *
      FROM 
        (
        SELECT m.*,
               sh.value1 AS hv1, sh.value2 AS hv2, sh.value9 AS hv9, sh.value10 AS hv10,
               row_number() OVER(PARTITION BY m.match_id ORDER BY sh.event_date DESC, sh.match_id DESC)  AS rnh
          FROM m 
               JOIN synene.betting_teamskill sh
                   ON(sh.harvest_id = 1 AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date AND sh.match_cnt > 3)
        ) d
      WHERE rnh = 1
  ),
ma AS 
  (
    SELECT d.*,
           hv1*av2 AS gxH1, av1*hv2 AS gxA1, hv9*av10 AS gxH1, av9*hv10 AS gxA2,
           ROUND(hv1*av2,3) AS ph1, ROUND(av1*hv2,3) AS pa1, ROUND(hv9*av10,3) AS ph2, ROUND(av9*hv10,3) AS pa2
      FROM 
        (
        SELECT mh.*,
               sh.value1 AS av1, sh.value2 AS av2, sh.value9 AS av9, sh.value10 AS av10,
               row_number() OVER(PARTITION BY mh.match_id ORDER BY sh.event_date DESC, sh.match_id DESC) AS rna
          FROM mh 
               JOIN synene.betting_teamskill sh
                   ON(sh.harvest_id = 1 AND sh.team_id = mh.team_a_id AND sh.param = 'a' AND sh.event_date < mh.match_date AND sh.match_cnt > 3)
        ) d
      WHERE rna = 1
  )
SELECT match_id AS id, result, ha, match_date, score, team_h_id, team_a_id, h_name, a_name,
       gxH::text || '-' || gxA::text  AS gx,
       ph1::text || '-' || pa1::text  AS fore_gx,
       ph2::text || '-' || pa2::text  AS fore_g
  FROM ma
;



WITH m AS 
  (
    SELECT m.id AS match_id, m.*,
           h.name AS h_name, a.name AS a_name, l.name AS league_name,
           TO_NUMBER(s1.value,'99999999.9999') AS gH,
           TO_NUMBER(s2.value,'99999999.9999') AS gA,
           TO_NUMBER(gh.value,'99999999.9999') AS gxH,
           TO_NUMBER(ga.value,'99999999.9999') AS gxA
      FROM synene.core_match m
           JOIN synene.core_matchstats s1  ON(s1.stat_type = 'g' AND s1.period = 0 AND s1.match_id = m.id AND s1.competitor = 'h' )
           JOIN synene.core_matchstats s2 ON(s2.stat_type = 'g' AND s2.period = 0 AND s2.match_id = m.id AND s2.competitor = 'a')
           JOIN synene.core_matchstats gh ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
           JOIN synene.core_matchstats ga ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
           JOIN synene.core_team h ON (m.team_h_id = h.id)
           JOIN synene.core_team a ON (m.team_a_id = a.id)
           JOIN synene.core_league l ON (m.league_id = l.id)
      WHERE m.league_id IN(7,12,19,26,27,77) AND m.match_date BETWEEN DATE '2015-01-01' AND DATE '2021-01-01'
        AND m.status = 'F'
        --AND m.id = 47633
  ),
mh AS 
  (
    SELECT *
      FROM 
        (
        SELECT m.*,
               sh.value1 AS hv1, sh.value2 AS hv2, sh.value9 AS hv9, sh.value10 AS hv10,
               row_number() OVER(PARTITION BY m.id ORDER BY sh.event_date DESC, sh.match_id DESC)  AS rnh
          FROM m 
               JOIN synene.betting_teamskill sh
                   ON(sh.harvest_id = 1 AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date AND sh.match_cnt > 3)
        ) d
      WHERE rnh = 1
  ),
ma AS 
  (
    SELECT d.*,
           hv1*av2 AS gxH1, av1*hv2 AS gxA1, hv9*av10 AS gxH1, av9*hv10 AS gxA2,
           ROUND(hv1*av2,1) AS ph1, ROUND(av1*hv2,1) AS pa1, ROUND(hv9*av10,1) AS ph2, ROUND(av9*hv10,1) AS pa2
      FROM 
        (
        SELECT mh.*,
               sh.value1 AS av1, sh.value2 AS av2, sh.value9 AS av9, sh.value10 AS av10,
               row_number() OVER(PARTITION BY mh.id ORDER BY sh.event_date DESC, sh.match_id DESC) AS rna
          FROM mh 
               JOIN synene.betting_teamskill sh
                   ON(sh.harvest_id = 1 AND sh.team_id = mh.team_a_id AND sh.param = 'a' AND sh.event_date < mh.match_date AND sh.match_cnt > 3)
        ) d
      WHERE rna = 1
  ),
p1 AS (
    SELECT d.*, 1-win AS lose
      FROM 
        (
        SELECT ma.*,
               COALESCE((SELECT SUM(data) 
                           FROM synene.betting_distributiondata 
                           WHERE ditribution_id = 1 AND param = '0h' 
                             AND value = ma.ph1 
                             AND result_value = 0),0)
/*               *
               COALESCE((SELECT SUM(data) 
                           FROM synene.betting_distributiondata 
                           WHERE ditribution_id = 1 AND param = '0a' 
                             AND value = ma.pa1 
                             AND result_value = 0),0)
*/                           
                AS win
          FROM ma
        ) d
),
p2 AS (
    SELECT d.*, 1-win AS lose
      FROM 
        (
        SELECT ma.*,
               COALESCE((SELECT SUM(data) 
                           FROM synene.betting_distributiondata 
                           WHERE ditribution_id = 3 AND param = '0h' 
                             AND value = ma.ph2 
                             AND result_value >= 1),0)
               *
               COALESCE((SELECT SUM(data) 
                           FROM synene.betting_distributiondata 
                           WHERE ditribution_id = 3 AND param = '0a' 
                             AND value = ma.pa2 
                             AND result_value = 0),0)
                AS win
          FROM ma
        ) d
)
SELECT  ROUND(pa1,1), AVG(win), AVG(d.r), COUNT(*)
  FROM 
    (
    SELECT p.*,
           CASE WHEN gH = 0 THEN 1.0 ELSE 0.0 END AS r
      FROM p1 p
    ) d
  GROUP BY ROUND(pa1,1)
  ORDER BY 1
;