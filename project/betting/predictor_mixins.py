from decimal import Decimal
from scipy.stats import poisson

from .models.probability import DistributionData

###################################################################
#  extract skill
###################################################################
class StandartExtraction(object):
    def extract_skills(self):
        self.skill_h_win = self.skill_h.value9
        self.skill_h_lose = self.skill_h.value10
        self.skill_a_win = self.skill_a.value9
        self.skill_a_lose = self.skill_a.value10


class OriginalDataExtraction(object):
    def extract_skills(self):
        self.skill_h_win = self.skill_h.value1
        self.skill_h_lose = self.skill_h.value2
        self.skill_a_win = self.skill_a.value1
        self.skill_a_lose = self.skill_a.value2

###################################################################
#  forecast data
###################################################################
class PoissonForecasting(object):
    def get_forecast_data(self):
        win_value  = float(self.skill_h_win * self.skill_a_lose)
        lose_value = float(self.skill_a_win * self.skill_h_lose)

        min_value, max_value = self.get_value_limit()

        forecast_data = []
        if max_value != None:
            for value_h in range(min_value,max_value):
                probability_h = Decimal(poisson.pmf(value_h, win_value))
                for value_a in range(min_value,max_value):
                    probability_a = Decimal(poisson.pmf(value_a, lose_value))
                    forecast_data.append([value_h,value_a,probability_h*probability_a])
        return forecast_data


class FixedDistributionForecasting(object):
    def get_forecast_data(self):
        win_value  = float(self.skill_h_win * self.skill_a_lose)
        lose_value = float(self.skill_a_win * self.skill_h_lose)

        min_value, max_value = self.get_value_limit()

        distribution_slug = self.get_distribution_slug()

        forecast_data = {}
        for period in [0,1,2,]:

            distribution_h = self.get_distribution_data(distribution_slug, win_value, param=f"{period}h")
            distribution_a = self.get_distribution_data(distribution_slug, lose_value, param=f"{period}a")

            fdata = []
            if max_value != None:
                for value_h in range(min_value,max_value):
                    probability_h = Decimal(distribution_h.get(value_h,0))
                    for value_a in range(min_value,max_value):
                        # param = f"0a{value_h}"
                        # distrib = self.get_distribution_data(distribution_slug, lose_value, param=param)
                        # if not distrib:
                        distrib = distribution_a
                        probability_a = Decimal(distrib.get(value_a,0))
                        fdata.append([value_h,value_a,probability_h*probability_a])
            forecast_data[period] = fdata
        return forecast_data


class FixedDistributionForecastingEx(object):
    def get_forecast_data(self):
        forecast_data = {}
        win_value  = float(self.skill_h_win * self.skill_a_lose)
        lose_value = float(self.skill_a_win * self.skill_h_lose)
        delta = win_value - lose_value
        delta_int = int(delta*10.0)
        min_value, max_value = self.get_value_limit()
        distribution_slug = self.get_distribution_slug()

        #simple
        distribution_h = self.get_distribution_data(distribution_slug, win_value, param="0h")
        distribution_a = self.get_distribution_data(distribution_slug, lose_value, param="0a")

        fdata = []
        if max_value != None:
            for value_h in range(min_value,max_value):
                probability_h = Decimal(distribution_h.get(value_h,0))
                for value_a in range(min_value,max_value):
                    distrib = distribution_a
                    probability_a = Decimal(distribution_a.get(value_a,0))
                    fdata.append([value_h,value_a,probability_h*probability_a])
        forecast_data["simple"] = fdata

        # #diff
        # fdata = []
        # distribution = self.get_distribution_data(distribution_slug, delta, param="0diff")
        # if distribution:
        #     for val in distribution.keys():
        #         if val < 0:
        #             fdata.append([0,-1*val,distribution[val]])
        #         else:
        #             fdata.append([val,0,distribution[val]])
        #     forecast_data["diff"] = fdata


        # #diff_team
        # distribution_h = self.get_distribution_data(distribution_slug, win_value, param="0diffh", object_id=delta_int)
        # distribution_a = self.get_distribution_data(distribution_slug, lose_value, param="0diffa", object_id=delta_int)

        # if distribution_h and distribution_a:
        #     fdata = []
        #     if max_value != None:
        #         for value_h in range(min_value,max_value):
        #             probability_h = Decimal(distribution_h.get(value_h,0))
        #             for value_a in range(min_value,max_value):
        #                 distrib = distribution_a
        #                 probability_a = Decimal(distribution_a.get(value_a,0))
        #                 fdata.append([value_h,value_a,probability_h*probability_a])
        #     forecast_data["diff_team"] = fdata

        return forecast_data
