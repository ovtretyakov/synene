from decimal import Decimal
from scipy.stats import poisson


###################################################################
#  extract skill
###################################################################
class StandartExtraction(object):
    def extract_skills(self):
        self.skill_h_win = self.skill_h.value1
        self.skill_h_lose = self.skill_h.value2
        self.skill_a_win = self.skill_a.value1
        self.skill_a_lose = self.skill_a.value2
        # self.skill_h_win = self.skill_h.value9
        # self.skill_h_lose = self.skill_h.value10
        # self.skill_a_win = self.skill_a.value9
        # self.skill_a_lose = self.skill_a.value10


###################################################################
#  forecasr data
###################################################################
class PoissonForecasting(object):
    def get_forecast_data(self):
        win_value  = float(self.skill_h_win * self.skill_a_lose)
        lose_value = float(self.skill_a_win * self.skill_h_lose)


# 0,3 0,7843  0,85    0,9237  0,9237
# 0,5 0,9556  0,94    0,9913  1,02
# 0,7 1,0443  1,05    1,0968  1,0968
# 0,9 1,1296  1,11    1,0768  1,15
# 1,1 1,192   1,17    1,2508  1,2
# 1,3 1,138   1,18    1,129   1,21
# 1,5 1,2014  1,17    1,2941  1,22
# 1,7 1,1249  1,15    1,1356  1,23
# 1,9 1,0649  1,13    1,3381  1,23
# 2,1 1,0731  1,13    1,2098  1,23
# 2,3 1,2103  1,12    1,1253  1,23
# 2,5 1,04    1,11    1,2 1,23
# 2,7 1,0826  1,1 1,2963  1,23
# 2,9 1,1379  1,09        
# 3,1 0,9677  1,08        


        if win_value <= 0.2:
            win_value = (0.85 + (0.2 - 0.3)*(0.94 - 0.85)/0.2) * win_value
        elif win_value <= 0.5:
            win_value = (0.85 + (win_value - 0.3)*(0.94 - 0.85)/0.2) * win_value
        elif win_value <= 0.7:
            win_value = (0.94 + (win_value - 0.5)*(1.05 - 0.94)/0.2) * win_value
        elif win_value <= 0.9:
            win_value = (1.05 + (win_value - 0.7)*(1.11 - 1.05)/0.2) * win_value
        elif win_value <= 1.1:
            win_value = (1.11 + (win_value - 0.9)*(1.17 - 1.11)/0.2) * win_value
        elif win_value <= 1.3:
            win_value = (1.17 + (win_value - 1.1)*(1.18 - 1.17)/0.2) * win_value
        elif win_value <= 1.5:
            win_value = (1.18 + (win_value - 1.3)*(1.17 - 1.18)/0.2) * win_value
        elif win_value <= 1.7:
            win_value = (1.17 + (win_value - 1.5)*(1.15 - 1.17)/0.2) * win_value
        elif win_value <= 1.9:
            win_value = (1.15 + (win_value - 1.7)*(1.13 - 1.15)/0.2) * win_value
        elif win_value <= 2.1:
            win_value = (1.13 + (win_value - 1.9)*(1.13 - 1.13)/0.2) * win_value
        elif win_value <= 2.3:
            win_value = (1.13 + (win_value - 2.1)*(1.12 - 1.13)/0.2) * win_value
        elif win_value <= 2.5:
            win_value = (1.11 + (win_value - 2.3)*(1.10 - 1.11)/0.2) * win_value
        elif win_value <= 2.7:
            win_value = (1.10 + (win_value - 2.7)*(1.09 - 1.10)/0.2) * win_value
        else:
            win_value = 1.09 * win_value

        if lose_value <= 0.2:
            lose_value = (0.92 + (0.2 - 0.3)*(1.02 - 0.92)/0.2) * lose_value
        elif lose_value <= 0.5:
            lose_value = (0.92 + (lose_value - 0.3)*(1.02 - 0.92)/0.2) * lose_value
        elif lose_value <= 0.7:
            lose_value = (1.02 + (lose_value - 0.5)*(1.09 - 1.02)/0.2) * lose_value
        elif lose_value <= 0.9:
            lose_value = (1.09 + (lose_value - 0.7)*(1.15 - 1.09)/0.2) * lose_value
        elif lose_value <= 1.1:
            lose_value = (1.15 + (lose_value - 0.9)*(1.20 - 1.15)/0.2) * lose_value
        elif lose_value <= 1.3:
            lose_value = (1.20 + (lose_value - 1.1)*(1.21 - 1.20)/0.2) * lose_value
        elif lose_value <= 1.5:
            lose_value = (1.21 + (lose_value - 1.3)*(1.22 - 1.21)/0.2) * lose_value
        elif lose_value <= 1.7:
            lose_value = (1.22 + (lose_value - 1.5)*(1.23 - 1.22)/0.2) * lose_value
        else:
            lose_value = 1.23 * lose_value


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
                probability_h = Decimal(poisson.pmf(value_h, win_value))
                for value_a in range(min_value,max_value):
                    probability_a = Decimal(poisson.pmf(value_a, lose_value))
                    forecast_data.append([value_h,value_a,probability_h*probability_a])
        return forecast_data


