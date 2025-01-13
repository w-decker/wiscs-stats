#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/w-decker/wiscs-stats/blob/main/notebooks/stats_pipeline.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# # Stats pipeline
# 
# This notebook contains the necessary code for evaluating simulated data using [`wiscs`](https://github.com/w-decker/wiscs).

# In[14]:


# @title # Load data
# @markdown Data are generated using the `wiscs` module created specificially for this project. If you wish to generate other data, see `generate_data.ipynb`.

# @markdown ### Here you can select a particular dataset by checking a corresponding box

import requests
from typing import Union
import os
import pandas as pd

DATA_PATH = "https://raw.githubusercontent.com/w-decker/wiscs-stats/main/data/"
FILES = ["simulated_Potter1975.csv", "simulated_main.csv", "simulated_alt.csv"]
LOCAL_DATA_PATH = "data/"
# @markdown > Load simulated data associated with hypothesis described in [Potter and Faulconer (1975)](https://www.nature.com/articles/253437a0)

potter1975 = True # @param{type: "boolean"}

# @markdown > Load simulated data associated with MAIN hypothesis
main = True # @param{type: "boolean"}
# @markdown > Load simulated data associated with ALT hypothesis
alt = True # @param{type: "boolean"}

# @markdown This cell _must_ be run if you do not intend to generate and load your own data.

datasets = [potter1975, main, alt]
datasets_to_use = []
for idx, dataset in enumerate(datasets):
  if dataset:
    datasets_to_use.append(FILES[idx])

def download_data(url:str, file:Union[str, list[str]]):

    os.makedirs("data", exist_ok=True)

    # Download each file
    for fname in file:
        file_url = url + fname
        local_path = os.path.join("data", fname)
        response = requests.get(file_url)

        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {fname}")
        else:
            print(f"Failed to download: {fname} (Status Code: {response.status_code})")

def import_data(path:str, file:Union[str, list[str]]) -> list[pd.DataFrame]:

  df = {}
  for fname in file:
    df[fname] = pd.read_csv(os.path.join(path, fname))
  print('Data imported')
  return df

download_data(DATA_PATH, datasets_to_use)
df = import_data(LOCAL_DATA_PATH, datasets_to_use)

keys = list(df.keys())

potter1975 = df["simulated_Potter1975.csv"] if "simulated_Potter1975.csv" in keys else None
main = df['simulated_main.csv'] if 'simulated_main.csv' in keys else None
alt = df['simulated_alt.csv'] if 'simulated_alt.csv' in keys else None


# In[41]:


# @markdown This is what the data look like
main.head()


# In[48]:


# @title # Setup and helper functions

import warnings
warnings.filterwarnings('ignore')

# @markdown `aic()` $\rightarrow$ get AIC values from a statsmodels object \
# @markdown `mixedlm_wrapper()` $\rightarrow$ Runs a mixed linear model \
# @markdown `best_model()` $\rightarrow$ return model with lowest AIC value from a dictionary of models. (Keys = label, values = model)

from statsmodels.regression.mixed_linear_model import MixedLMResultsWrapper # type: ignore
import statsmodels.formula.api as smf # type: ignore
from statsmodels.regression.linear_model import RegressionResults
from typing import Mapping, Tuple
import pandas as pd
import itertools
from scipy.stats import chi2

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

def llr_test(models:Mapping[any, MixedLMResultsWrapper], print_results:bool=True):
    """
    log-likelihood ratio tests for all pairs of models.
    """
    llr_results = {}
    model_scores = {name: 0 for name in models.keys()}

    for (name1, model1), (name2, model2) in itertools.combinations(models.items(), 2):

        # ll
        ll1, ll2 = model1.llf, model2.llf

        # LLR test
        llr = 2 * (ll2 - ll1)
        df = model2.df_modelwc - model1.df_modelwc
        pval = chi2.sf(llr, df)

        # Which model is better?
        winner = name1 if ll1 > ll2 else name2
        llr_results[f"{name1} & {name2}"] = {
            "LLR": llr,
            "p-value": pval,
            "df": df,
            "winner": winner,
        }

    return llr_results

aic = lambda models: {label: model.aic for label, model in models.items()}
bic = lambda models: {label: model.bic for label, model in models.items()}

def best_model(models: Mapping[any, MixedLMResultsWrapper], # type: ignore
               metric:str="aic", print_results:bool=False) \
                ->Tuple[any, MixedLMResultsWrapper]: # type: ignore

    """Return the best model based on metric"""
    assert metric in ["aic", "bic", "wilks"], "Invalid metric"
    if metric == "wilks":
      results = llr_test(models, print_results=print_results)
    else:
      key = lambda item: getattr(item[1], metric)
      label, winner = min(models.items(), key=key)
      if print_results:
          for model, result in models.items():
              print(f'{model}: {getattr(result, metric)}')
      return label, winner


# # Fitting a model
# 
# This statistical analysis uses a $\text{Linear Mixed Effects Model}$. The term $\text{mixed}$ refers to experimental variables being modeled as _**random**_ and/or _**fixed**_ effects. The design is _mixed_.
# 
# ### Random versus fixed effects
# A _**random**_ effect is a variable which we expect to be a random sample from a larger population. Conceptually, a pool of participants are (and should) be considered a random effect, as we expect that this subject pool is a representative sample of an unknown population. It is up to the individual analyzing the data as to whether or not subjects are modeled as random effects.
# 
# In contrast, a _**fixed**_ effect is a variable which we assume is not part of a larger population, or, rather, that the mean of the fixed variable is constant.

# In[18]:


# @markdown Here is a vanilla fixed effects model that evaluates data associated with both main and alternative hypotheses

model_main_vanilla, fit_main_vanilla = mixedlm_wrapper("rt ~ modality", main, groups=main["subject"])

model_alt_vanilla, fit_alt_vanilla = mixedlm_wrapper("rt ~ modality", alt,
                                     groups=alt["subject"])


# In[45]:


# @markdown Let's add some variables as random effects into the model

model_main, fit_main = mixedlm_wrapper("rt ~ modality", main, groups=main["subject"], re_formula="~question + item")

model_alt, fit_alt = mixedlm_wrapper("rt ~ modality", alt, groups=alt["subject"], re_formula="~question + item")


# # Which data does the model best fit?
# 
# This pipeline makes use of the Akaike Information Criterion (AIC) as the default model comparison metric. But you can also easily see BIC (`metric="bic"`) and Log-Likelihood Ratio (`metric="wilks"`).
# 
# The model with the lowest AIC value is typically the model which fits the data the best.

# In[47]:


models = {
    "MAIN":fit_main,
    "ALT":fit_alt,
}

label, winner = best_model(models, metric="aic", print_results=True)

print('-'*50)
print(f'\nwinner: "{label}"\n')
print('-'*50)
print('Model Summary')
winner.summary()


# In[ ]:




