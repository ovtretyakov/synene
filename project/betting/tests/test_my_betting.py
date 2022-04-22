from datetime import date
from decimal import Decimal

from django.test import TestCase

from project.football.models import FootballSource, FootballLeague, FootballTeam
from project.core.models import Country, TeamType, Match, Season, Sport, MatchStats
from ..models import (ValueType, Odd, BetType,
                      HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague, 
                      ForecastHandler, Predictor, ForecastSet, Forecast,
                      SelectedOdd, Transaction, Saldo, Bet, BetOdd
                      )



#######################################################################################
######  MyBettingTest
#######################################################################################
class MyBettingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
        cls.load_source.is_betting=1
        cls.load_source.save()
        cls.russia = Country.objects.get(slug='rus')
        cls.country = cls.russia
        cls.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
        cls.league = FootballLeague.get_or_create(
                                                name='league', 
                                                load_source=cls.load_source
                                                )
        cls.team1 = FootballTeam.get_or_create(
                                                name='team1', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team2 = FootballTeam.get_or_create(
                                                name='team2', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team3 = FootballTeam.get_or_create(
                                                name='team3', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team4 = FootballTeam.get_or_create(
                                                name='team4', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team5 = FootballTeam.get_or_create(
                                                name='team5', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team6 = FootballTeam.get_or_create(
                                                name='team6', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.season1 = Season.objects.create(
                                            name='2017/2018',
                                            league=cls.league, start_date=date(2017, 8, 1), end_date=date(2018, 6, 10),
                                            load_source=cls.load_source
                                            )
        cls.season2 = Season.objects.create(
                                            name='2018/2019',
                                            league=cls.league, start_date=date(2018, 8, 1), end_date=date(2019, 6, 10),
                                            load_source=cls.load_source
                                            )
        cls.season3 = Season.objects.create(
                                            name='2019/2020',
                                            league=cls.league, start_date=date(2019, 8, 1), end_date=date(2020, 6, 10),
                                            load_source=cls.load_source
                                            )


        # Harvest params
        cls.harvest_handler = HarvestHandler.objects.create(
                                            slug = "test-xg", name = "xG Handler", handler = "xGHandler"
                                            )
        cls.harvest = Harvest.objects.create(
                                            slug = "test-hg-0",  name = "Calculate match xG",
                                            sport = Sport.objects.get(slug=Sport.FOOTBALL), 
                                            harvest_handler = cls.harvest_handler,
                                            value_type = ValueType.objects.get(slug=ValueType.MAIN),
                                            period =0, status = 'a'
                                            )
        HarvestConfig.objects.create(harvest = cls.harvest, code = "smooth-interval", value = "5")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "deviation-smooth-interval", value = "7")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "zero-value", value = "0.01")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "deviation-zero-value", value = "0.5")
 
        cls.harvest_group = HarvestGroup.objects.create(
                                            slug = "test-hg-0-league", name = "Harvest League",
                                            harvest = cls.harvest, country = cls.country,
                                            status = 'a', harvest_date = date(2021, 1, 1)
                                            )

        HarvestLeague.objects.create(harvest_group = cls.harvest_group, league = cls.league)


        # Matches
        #match1
        cls.match1 = Match.objects.create(league=cls.league, team_h=cls.team1, team_a=cls.team5, 
                                           match_date=date(2018,3,1), season=cls.season1,
                                           score = "1:0(0:0,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=1)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=0)
        #match2
        cls.match2 = Match.objects.create(league=cls.league, team_h=cls.team1, team_a=cls.team5, 
                                           match_date=date(2018,5,1), season=cls.season1,
                                           score = "1:2(0:2,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=1)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=2)

        # Forecasting
        cls.forecast_handler = ForecastHandler.objects.create(
                                            slug = "test-xg-forecast-standard", name = "xG Forecasting", handler = "PredictorStandardPoisson"
                                            )
        cls.forecast_set = ForecastSet.objects.create(
                                            slug = "test-main",
                                            name = "Main Forecasting",
                                            status = "p",
                                            keep_only_best = False,
                                            only_finished = False,
                                            start_date = date(2020,1,1),
                                            )
        cls.predictor1 = Predictor.objects.create(
                                            slug = "test-hg-standard",
                                            name = "xG Standard",
                                            forecast_handler = cls.forecast_handler,
                                            harvest = cls.harvest,
                                            priority = 10,
                                            status = 'a'
                                            )
        cls.predictor2 = Predictor.objects.create(
                                            slug = "test-hg-standard-2",
                                            name = "xG Standard 2",
                                            forecast_handler = cls.forecast_handler,
                                            harvest = cls.harvest,
                                            priority = 5,
                                            status = 'a'
                                            )
        cls.predictor3 = Predictor.objects.create(
                                            slug = "test-hg-standard-3",
                                            name = "xG Standard 3",
                                            forecast_handler = cls.forecast_handler,
                                            harvest = cls.harvest,
                                            priority = 15,
                                            status = 'a'
                                            )


    def setUp(self):
        # Odd
        self.odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='w', odd_value=2)
        self.odd2 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1:1', odd_value=6.1)
        self.odd3 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='even', odd_value=3.1)
        self.odd4 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1.75', odd_value=3.1)

        # Forecast
        self.fore1 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match1,
                                        odd = self.odd1,
                                        predictor = self.predictor1,
                                        match_date = self.match1.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.5,
                                        lose_chance  = 0.4,
                                        result_value = 1.2,
                                        kelly = 0.2
                                    )
        self.fore1.refresh_from_db()
        self.fore2 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match2,
                                        odd = self.odd2,
                                        predictor = self.predictor1,
                                        match_date = self.match2.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.3,
                                        lose_chance  = 0.7,
                                        result_value = 1.05,
                                        kelly = 0.05
                                    )
        self.fore2.refresh_from_db()
        self.fore3 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match2,
                                        odd = self.odd3,
                                        predictor = self.predictor1,
                                        match_date = self.match2.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.2,
                                        lose_chance  = 0.8,
                                        result_value = 1.5,
                                        kelly = 0.2
                                    )
        self.fore3.refresh_from_db()
        self.fore4 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match2,
                                        odd = self.odd4,
                                        predictor = self.predictor1,
                                        match_date = self.match2.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.55,
                                        lose_chance  = 0.3,
                                        result_value = 1.2,
                                        kelly = 0.4
                                    )
        self.fore4.refresh_from_db()



    #######################################################################
    def test_selected_odd(self):

        fore3 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match2,
                                        odd = self.odd2,
                                        predictor = self.predictor2,
                                        match_date = self.match2.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.3,
                                        lose_chance  = 0.3,
                                        result_value = 1.03,
                                        kelly = 0.03
                                    )
        fore3.refresh_from_db()
        fore4 = Forecast.objects.create(   
                                        forecast_set = self.forecast_set,
                                        match = self.match2,
                                        odd = self.odd2,
                                        predictor = self.predictor3,
                                        match_date = self.match2.match_date,
                                        harvest = self.harvest,
                                        success_chance  = 0.4,
                                        lose_chance  = 0.4,
                                        result_value = 1.04,
                                        kelly = 0.04
                                    )
        fore4.refresh_from_db()



        forecasts = Forecast.objects.filter(forecast_set = self.forecast_set).values()
        SelectedOdd.add(forecasts)

        cnt = SelectedOdd.objects.filter(forecast_set = self.forecast_set).count()
        self.assertEquals(cnt, 4)

        sel1 = SelectedOdd.objects.get(forecast_set=self.forecast_set, odd=self.odd1)
        self.assertEquals(sel1.match, self.match1)
        self.assertEquals(sel1.predictor, self.predictor1)
        self.assertEquals(sel1.match_date, self.match1.match_date)
        self.assertEquals(sel1.harvest, self.harvest)
        self.assertEquals(sel1.success_chance, self.fore1.success_chance)
        self.assertEquals(sel1.lose_chance, self.fore1.lose_chance)
        self.assertEquals(sel1.result_value, self.fore1.result_value)
        self.assertEquals(sel1.kelly, self.fore1.kelly)

        odd1 = Odd.objects.get(pk=self.odd1.id)
        self.assertEquals(odd1.selected, Odd.SELECTED)


        sel2 = SelectedOdd.objects.get(forecast_set=self.forecast_set, odd=self.odd2)
        self.assertEquals(sel2.match, self.match2)
        self.assertEquals(sel2.predictor, self.predictor2)
        self.assertEquals(sel2.match_date, self.match2.match_date)
        self.assertEquals(sel2.harvest, self.harvest)
        self.assertEquals(sel2.success_chance, fore3.success_chance)
        self.assertEquals(sel2.lose_chance, fore3.lose_chance)
        self.assertEquals(sel2.result_value, fore3.result_value)
        self.assertEquals(sel2.kelly, fore3.kelly)

        odd2 = Odd.objects.get(pk=self.odd2.id)
        self.assertEquals(odd2.selected, Odd.SELECTED)


        sel2.delete_object()
        odd2.refresh_from_db()
        self.assertEquals(odd2.selected, Odd.UNSELECTED)


    #######################################################################
    def test_transaction(self):
        trans1 = Transaction.add(bookie_id=self.load_source.id, 
                                 trans_type=Transaction.TYPE_IN, 
                                 amount=10, comment="Test 10", 
                                 trans_date=date(2022, 1, 1)
                                 )
        trans1.refresh_from_db()
        self.assertEquals(trans1.bookie_id, self.load_source.id)
        self.assertEquals(trans1.trans_type, Transaction.TYPE_IN)
        self.assertEquals(trans1.trans_date, date(2022, 1, 1))
        self.assertEquals(trans1.amount, 10)
        self.assertEquals(trans1.comment, "Test 10")

        saldo1 = Saldo.objects.get(bookie_id=self.load_source.id, saldo_date=date(2022, 1, 1))
        self.assertEquals(saldo1.saldo_amt, 10)
        self.assertEquals(saldo1.in_amt, 10)
        self.assertEquals(saldo1.out_amt, 0)

        bookie = FootballSource.objects.get(id=self.load_source.id)
        self.assertEquals(bookie.saldo_amt, 10)


        trans2 = Transaction.add(bookie_id=self.load_source.id, 
                                 trans_type=Transaction.TYPE_CORRECT, 
                                 amount=20, comment="Test 20", 
                                 trans_date=date(2022, 1, 2)
                                 )
        saldo2 = Saldo.objects.get(bookie_id=self.load_source.id, saldo_date=date(2022, 1, 2))
        self.assertEquals(saldo2.saldo_amt, 30)
        self.assertEquals(saldo2.in_amt, 20)
        self.assertEquals(saldo2.out_amt, 0)

        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, 30)


        trans3 = Transaction.add(bookie_id=self.load_source.id, 
                                 trans_type=Transaction.TYPE_OUT, 
                                 amount=-5, comment="Test 5", 
                                 trans_date=date(2022, 1, 3)
                                 )
        saldo3 = Saldo.objects.get(bookie_id=self.load_source.id, saldo_date=date(2022, 1, 3))
        self.assertEquals(saldo3.saldo_amt, 25)
        self.assertEquals(saldo3.in_amt, 0)
        self.assertEquals(saldo3.out_amt, 5)

        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, 25)

        trans2.delete_object()
        saldo2.refresh_from_db()
        self.assertEquals(saldo2.saldo_amt, 10)
        self.assertEquals(saldo2.in_amt, 0)
        self.assertEquals(saldo2.out_amt, 0)
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, 5)


    #######################################################################
    def test_bet(self):

        #create
        items = Forecast.objects.filter(forecast_set = self.forecast_set).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 4)
        self.assertEquals(bet.min_date, self.match1.match_date)
        self.assertEquals(bet.max_date, self.match2.match_date)
        self.assertEquals(bet.success_chance, 
                          self.fore1.success_chance*self.fore2.success_chance*self.fore3.success_chance*self.fore4.success_chance)
        self.assertEquals(bet.lose_chance, 
                          Decimal("1.0") - self.fore1.success_chance*self.fore2.success_chance*self.fore3.success_chance*self.fore4.success_chance)
        self.assertEquals(bet.odd_value, 
                          self.odd1.odd_value*self.odd2.odd_value*self.odd3.odd_value*self.odd4.odd_value)
        self.assertEquals(bet.expect_value, 
                          self.fore1.result_value*self.fore2.result_value*self.fore3.result_value*self.fore4.result_value)

        bet_odd = BetOdd.objects.get(bet_id=bet.id, odd_id = self.odd1.id)
        self.assertEquals(bet_odd.lose_chance, self.fore1.lose_chance)
        self.assertEquals(bet_odd.odd_value, self.odd1.odd_value)
        self.assertEquals(bet_odd.expect_value, self.fore1.result_value)
        self.assertEquals(bet_odd.kelly, self.fore1.kelly)

        odd1 = Odd.objects.get(pk=self.odd1.id)
        self.assertEquals(odd1.selected, Odd.BID)

        #update
        items = BetOdd.objects.filter(bookie = self.load_source).order_by("id").values()
        for item in items:
            is_del = 1 if item["odd_id"]==self.odd4.id else 0
            item["is_del"] = is_del
            if item["odd_id"]==self.odd3.id:
                item["odd_value"] = 8.5
        bet.update_odds(items)
        cnt = BetOdd.objects.filter(bookie = self.load_source).count()
        self.assertEquals(cnt, 3)
        self.assertEquals(bet.odd_cnt, 3)
        self.assertEquals(bet.success_chance, 
                          self.fore1.success_chance*self.fore2.success_chance*self.fore3.success_chance)
        self.assertEquals(bet.lose_chance, 
                          Decimal("1.0") - self.fore1.success_chance*self.fore2.success_chance*self.fore3.success_chance)
        self.assertEquals(bet.odd_value, 
                          self.odd1.odd_value*self.odd2.odd_value*Decimal("8.5"))

        bet_odd = BetOdd.objects.get(bet_id=bet.id, odd_id = self.odd3.id)
        self.assertEquals(bet_odd.lose_chance, self.fore3.lose_chance)
        self.assertEquals(bet_odd.odd_value, Decimal("8.5"))

        #delete
        items = BetOdd.objects.filter(bookie=self.load_source, match=self.match2).values()
        bet.delete_odds(items)
        cnt = BetOdd.objects.filter(bookie = self.load_source).count()
        self.assertEquals(cnt, 1)
        self.assertEquals(bet.odd_cnt, 1)
        self.assertEquals(bet.betting_type, "s")



    #######################################################################
    def test_create_bet_and_bid(self):

        #create
        items = Forecast.objects.filter(forecast_set=self.forecast_set).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items, bet_amt=100)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 4)
        self.assertEquals(bet.status, Bet.BID)
        self.assertIsNotNone(bet.bet_transaction)

        bet_transaction = bet.bet_transaction
        self.assertEquals(bet_transaction.trans_type, Transaction.TYPE_BID)
        self.assertEquals(bet_transaction.amount, -100)

        bookie = FootballSource.objects.get(id=self.load_source.id)
        self.assertEquals(bookie.saldo_amt, -100)
        self.assertEquals(bookie.unsettled_amt, 100)
        self.assertEquals(bookie.unsettled_cnt, 1)


    #######################################################################
    def test_update_bet_and_bid(self):

        #create
        items = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id__in=[self.odd1,self.odd2,]).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 2)
        self.assertEquals(bet.status, Bet.UNSETTLED)
        self.assertIsNone(bet.bet_transaction)

        bookie = FootballSource.objects.get(id=self.load_source.id)
        self.assertEquals(bookie.saldo_amt, 0)


        #update
        items = BetOdd.objects.filter(bookie=self.load_source).order_by("id").values()
        for item in items:
            if item["odd_id"]==self.odd1.id:
                item["odd_value"] = 2
            if item["odd_id"]==self.odd2.id:
                item["odd_value"] = 3
        bet.update_odds(items, bet_amt=100)
        self.assertEquals(bet.odd_value, 6)
        self.assertEquals(bet.status, Bet.BID)
        self.assertIsNotNone(bet.bet_transaction)

        bet_transaction = bet.bet_transaction
        self.assertEquals(bet_transaction.trans_type, Transaction.TYPE_BID)
        self.assertEquals(bet_transaction.amount, -100)

        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, -100)
        self.assertEquals(bookie.unsettled_amt, 100)
        self.assertEquals(bookie.unsettled_cnt, 1)

        #delete
        items = BetOdd.objects.filter(bookie=self.load_source, match=self.match2).values()
        with self.assertRaisesRegex(ValueError, 'Incorrect bet status'):
            bet.delete_odds(items)


    #######################################################################
    def test_settle(self):

        #create
        items = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id__in=[self.odd1,self.odd2,]).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            if odd.id == self.odd1.id:
                item["odd_value"] = 3
            else:
                item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items, bet_amt=100)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 2)
        self.assertEquals(bet.status, Bet.BID)

        odd1 = Odd.objects.get(pk=self.odd1.id)
        self.assertEquals(odd1.selected, Odd.BID)

        odd1.calculate_result()
        bet.refresh_from_db()
        self.assertEquals(bet.status, Bet.BID)
        self.assertIsNone(bet.settled_time)

        bet_odd1 = BetOdd.objects.get(bet_id=bet.id, odd_id = self.odd1.id)
        self.assertEquals(bet_odd1.status, BetOdd.SETTLED)
        self.assertEquals(bet_odd1.result_value, Decimal("3"))
        self.assertIsNotNone(bet_odd1.settled_time)
        self.assertEquals(bet_odd1.result, BetOdd.SUCCESS)

        bet_odd2 = BetOdd.objects.get(bet_id=bet.id, odd_id = self.odd2.id)
        items = [{"id":bet_odd2.id, "result_value":1, }]
        bet.settle_odds(items)
        self.assertEquals(bet.status, Bet.SETTLED)
        self.assertEquals(bet.result, Bet.PART_SUCCESS)
        self.assertEquals(bet.result_value, Decimal("3"))
        self.assertIsNotNone(bet.settled_time)


    #######################################################################
    def test_finish(self):

        #create
        items = Forecast.objects.filter(forecast_set=self.forecast_set).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 4)
        self.assertEquals(bet.status, Bet.UNSETTLED)

        #bid
        bet.update_odds(items=[], bet_amt=1000)
        self.assertEquals(bet.status, Bet.BID)
        bookie = FootballSource.objects.get(id=self.load_source.id)
        self.assertEquals(bookie.saldo_amt, Decimal("-1000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("1000"))
        self.assertEquals(bookie.unsettled_cnt, 1)

        #finish - error
        with self.assertRaisesRegex(ValueError, 'Not finished odd'):
            bet.settle_odds(items=[], finished=True, win_amt = 2000)

        #settle
        items = Forecast.objects.filter(forecast_set=self.forecast_set).order_by("id").values()
        i = 0
        for item in items:
            i += 1
            if i == 1:
                item["result_value"] = 2
            else:
                item["result_value"] = 3
        bet.settle_odds(items)
        self.assertEquals(bet.status, Bet.SETTLED)
        self.assertEquals(bet.result_value, Decimal("54"))

        #finish
        bet.settle_odds(items=[], finished=True, win_amt = 2000)
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("1000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("0"))
        self.assertEquals(bookie.unsettled_cnt, 0)

        #delete
        bet.delete_object()
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("0"))
        self.assertEquals(bookie.unsettled_amt, Decimal("0"))
        self.assertEquals(bookie.unsettled_cnt, 0)

        odd1 = Odd.objects.get(pk=self.odd1.id)
        self.assertEquals(odd1.selected, Odd.UNSELECTED)


    #######################################################################
    def test_finish2(self):

        #create
        items = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id__in=[self.odd1,self.odd2,]).values()
        for item in items:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet = Bet.create(self.load_source.id, items)
        self.assertEquals(bet.betting_type, "e")
        self.assertEquals(bet.odd_cnt, 2)
        self.assertEquals(bet.status, Bet.UNSETTLED)

        #finish - error
        with self.assertRaisesRegex(ValueError, 'Incorrect bet status'):
            bet.settle_odds(items=[], finished=True, win_amt = 2000)

        #bid
        bet.update_odds(items=[], bet_amt=1000)
        self.assertEquals(bet.status, Bet.BID)
        bookie = FootballSource.objects.get(id=self.load_source.id)
        self.assertEquals(bookie.saldo_amt, Decimal("-1000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("1000"))
        self.assertEquals(bookie.unsettled_cnt, 1)


        # create 2
        items2 = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id__in=[self.odd3,self.odd4,]).values()
        for item in items2:
            odd = Odd.objects.get(pk=item["odd_id"])
            item["odd_value"] = odd.odd_value
        bet2 = Bet.create(self.load_source.id, items2, bet_amt=2000)
        self.assertEquals(bet2.betting_type, "e")
        self.assertEquals(bet2.odd_cnt, 2)
        self.assertEquals(bet2.status, Bet.BID)
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("-3000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("3000"))
        self.assertEquals(bookie.unsettled_cnt, 2)


        #settle
        items = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id=self.odd1).order_by("id").values()
        i = 0
        for item in items:
            item["result_value"] = 2
        bet.settle_odds(items)
        self.assertEquals(bet.status, Bet.BID)

        #finish
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("-3000"))
        items = Forecast.objects.filter(forecast_set=self.forecast_set, odd_id__in=[self.odd1,self.odd2,]).order_by("id").values()
        i = 0
        for item in items:
            i += 1
            if i == 1:
                item["result_value"] = 2
            else:
                item["result_value"] = 3
        bet.settle_odds(items=items, finished=True, win_amt = 2000)
        self.assertEquals(bet.status, Bet.FINISHED)
        self.assertEquals(bet.result_value, Decimal("6"))
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("-1000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("2000"))
        self.assertEquals(bookie.unsettled_cnt, 1)

        #delete
        bet.delete_object()
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("-2000"))
        self.assertEquals(bookie.unsettled_amt, Decimal("2000"))
        self.assertEquals(bookie.unsettled_cnt, 1)

        #delete 2
        bet2.delete_object()
        bookie.refresh_from_db()
        self.assertEquals(bookie.saldo_amt, Decimal("0"))
        self.assertEquals(bookie.unsettled_amt, Decimal("0"))
        self.assertEquals(bookie.unsettled_cnt, 0)
