from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from tqdm import tqdm # type: ignore
import statsmodels.formula.api as smf # type: ignore
import numpy as np
import numpy.typing as npt
import warnings
warnings.filterwarnings("ignore")

def mixedlm_wrapper(formula:str, data:pd.DataFrame, groups:pd.Series, re_formula:str=None):
  """
  Wrapper around `smf.mixedlm()`
  """
  if re_formula is None:
    model = smf.mixedlm(formula, data, groups=groups)
  else:
    model = smf.mixedlm(formula, data, groups=groups,
                        re_formula=re_formula)
  return model, model.fit(reml=False)

class WISCSPowerCalculator(object):
    """
    Class for simulating power 

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the data
    n_participants: npt.ArrayLike
        Number of participants to sample
    n_items: npt.ArrayLike
        Number of items to sample
    n_questions: npt.ArrayLike
        Number of questions to sample

    Attributes
    ----------
    data: pd.DataFrame
    n_participants: npt.ArrayLike
    n_items: npt.ArrayLike
    n_questions: npt.ArrayLike

    Methods
    -------
    grid(n_participants, n_items, n_questions)
        Generate all possible combinations of n_participants, n_questions and n_items

    sample(data, combinations_slice)
        Randomly sample n_participants, n_questions and n_items from the data

    power(desired_power, alpha, formula, re_formula, variable)
        Calculate minimum sample size, n_questoins and n_items required to achieve desired power
    """

    def __init__(
          self, 
          data:pd.DataFrame,
          n_participants:npt.ArrayLike,
          n_items:npt.ArrayLike,
          n_questions:npt.ArrayLike
                 ):
       self.data = data
       self.n_participants = n_participants
       self.n_items = n_items
       self.n_questions = n_questions

    @staticmethod
    def grid(n_participants:npt.ArrayLike, n_items:npt.ArrayLike,n_questions:npt.ArrayLike):
        """Generate all possible combinations of n_participants, n_questions and n_items"""
        combinations = [
                np.array([n_participant, n_question, n_item])
                for n_participant in n_participants
                for n_question in n_questions
                for n_item in n_items
            ]
        return combinations
    
    @staticmethod
    def sample(data:pd.DataFrame, combinations_slice:npt.ArrayLike) -> pd.DataFrame:
        """Randomly sample n_participants, n_questions and n_items from the data"""

        n_participants, n_questions, n_items = combinations_slice

        sampled_subjects = np.random.choice(
            data['subject'].unique(), size=min(n_participants, len(data['subject'].unique())), replace=False
        )
        sampled_data = data[data['subject'].isin(sampled_subjects)]

        sampled_questions = np.random.choice(
            sampled_data['question'].unique(), size=min(n_questions, len(sampled_data['question'].unique())), replace=False
        )
        sampled_data = sampled_data[sampled_data['question'].isin(sampled_questions)]

        sampled_items = np.random.choice(
            sampled_data['item'].unique(), size=min(n_items, len(sampled_data['item'].unique())), replace=False
        )
        sampled_data = sampled_data[sampled_data['item'].isin(sampled_items)]
        
        return sampled_data

    def power(
            self, desired_power:float, 
              alpha:float, formula:str, 
              re_formula:str=None,
              variable:str="modality[T.text]"
              ):
        """
        Calculate minimum sample size, n_questoins and n_items required to achieve desired power

        Parameters
        ----------
        desired_power: float
            Desired power of the test
        alpha: float
        formula: str
        re_formula: str
        variable: str
            Variable to calculate power for

            "Intercept"
            "modality[T.word]"
            "question"
            "modality[T.word]:question"

        Returns
        -------
        slice: npt.ArrayLike
            Slice of the data that achieves the desired power
        power: float
        """
        combinations = self.grid(self.n_participants, self.n_items, self.n_questions)
        skipped = 0
        count = 0
        power = 0
        iter = tqdm(combinations)
        for slice in iter:
            sampled_data = self.sample(self.data, slice)
            _, fit = mixedlm_wrapper(formula, sampled_data, 
            groups=sampled_data['subject'], re_formula=re_formula)

            pval = fit.pvalues.get(variable, 1)
            if pval <= alpha:
                count += 1
            else:
                skipped += 1

            power = count / len(combinations)
            iter.set_postfix({"Power": power, "Count": count, "Skipped": skipped})
            if power >= desired_power:
               break

        return slice, power
       
