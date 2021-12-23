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


###################################################################
#  forecasr data
###################################################################
class PoissonForecasting(object):
    def get_forecast_data(self):
        win_value  = self.skill_h_win * self.skill_a_lose
        lose_value = self.skill_a_win * self.skill_h_lose
        min_value = None
        max_value = None

        if self.value_type_slug == "main":
            min_value = 0
            if self.period == 0:
                max_value = 7
            elif self.period in [1,2,]:
                max_value = 5
            else:
                max_value = 4

        forecast_data = []
        if max_value != None:
            for value_h in range(min_value,max_value):
                probability_h = poisson.pmf(value_h, float(win_value)) 
                for value_a in range(min_value,max_value):
                    probability_a = poisson.pmf(value_a, float(lose_value)) 
                    forecast_data.append([value_h,value_a,probability_h*probability_a])
        return forecast_data


