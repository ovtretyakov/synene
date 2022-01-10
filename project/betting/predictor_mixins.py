from decimal import Decimal
from scipy.stats import poisson


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
        distribution_h = self.get_distribution_data(distribution_slug, win_value, param="0h")
        distribution_a = self.get_distribution_data(distribution_slug, lose_value, param="0a")

        forecast_data = []
        if max_value != None:
            for value_h in range(min_value,max_value):
                probability_h = Decimal(distribution_h.get(value_h,0))
                for value_a in range(min_value,max_value):
                    param = f"0a{value_h}"
                    # distrib = self.get_distribution_data(distribution_slug, lose_value, param=param)
                    # if not distrib:
                    distrib = distribution_a
                    probability_a = Decimal(distrib.get(value_a,0))
                    forecast_data.append([value_h,value_a,probability_h*probability_a])
        return forecast_data

