#!/usr/bin/env python
# coding: utf-8

# # Generating data
# 
# This notebook contains a step-by-step walkthrough for data generation. Data are generated using a custom module, [`wiscs`](https://github.com/w-decker/wiscs). This module takes in a set of parameters in the form of a python dictionary. 
# 
# There are **three** ways to generate data in this notebook:
# 1. [Load in some pre-existing parameters and generate data based on these](#loading-in-pre-existing-parameters-and-generating-data)\
# This process involves loading in a few pre-made custom parameter files and generating data based on these. There are three options to choose from: 1) parameters that align with the alternative hypothesis described in [Potter & Faulconer (1975)](https://www.nature.com/articles/253437a0), 2) parameters that align with the main hypothesis and 3) parameters that align with the alternative hypothesis that two separate conceptual spaces exist for words and images. 
# 
# 2. [Dynamically generate data using the `ipywidgets` widget](#generate-parameters-and-data-with-ipywidgets)\
# This process involves a widget made with `ipywidgets`. This allows the user to manually set parameter values in a hierarchically-esque structured GUI.
# 
# 3. [Modify the parameters dictionary yourself](#generate-your-own-data-by-modifying-the-parameters-dictionary)\
# This process involves directly modifying an empty sample parameters dictionary with the values necessary for the simulation code. 
# 
# ## Recommendations
# 1. It is necessary that you install `wiscs`. The first cell under [Imports](#imports) installs the module via `pip`.
# 2. Read the comments in each cell carefully. There are instructions for what code may require modification. 

# ## Imports

# In[1]:


# If you have not installed `wiscs` locally, run this cell
get_ipython().system('pip install git+https://github.com/w-decker/wiscs.git --quiet # REQUIRED FOR THIS NOTEBOOK')


# In[ ]:


# always run this cell, no matter which method you choose
import wiscs
from wiscs.simulate import DataGenerator
from wiscs.utils import make_tasks


# In[2]:


# if you wish to load in the pre-existing parameters, run this cell
from src.utils import load_params, base
import os


# In[4]:


# if you wish to use the `ipywidgets` tool, then run this cell
import ipywidgets as widgets
from src.wiscs_widgets import wiscs_widget
from src.utils import extract_params_from_widget


# ## Loading in pre-existing parameters and generating data

# In[6]:


# there are three different parameter sets to choose from. To see them run this cell
base(os.listdir('../config'), [])


# In[4]:


# if you wish to load in the pre-existing parameters, modify + run this cell

# do you want to see ALL the parameter files?
######################################################
load_in_all_params = True # <-- CHANGE THIS AS NEEDED | True or False
######################################################

# do you want to load in ALL the files as a SINGLE dictionary object?
# NOTE: this can only be true if `load_in_all_params` is True
############################################################
load_in_as_single_object = False # <-- CHANGE THIS AS NEEDED | True or False
############################################################

if not load_in_all_params:
    file_tags = base(os.listdir("../config"), [])
    print(f'If you wish to load a single param, choose from the following:\n \
          {file_tags}')


# In[5]:


# if you wish to load in the pre-existing parameters, modify + run this cell
if load_in_all_params:
    if load_in_as_single_object:
        print('Loading in all parameters as a single object...')
        params = load_params(path='../config', all=True, merge=True)
    else:
        print('Loading in all parameters as separate objects...')
        potter1975, main, alt = params = load_params(path='../config', all=True, merge=False)
elif not load_in_all_params:     
    
    ################################################
    fname = 'Potter1975' # <-- CHANGE THIS AS NEEDED | For example, "Potter1975", "Main" or "Alt" (as type str)
    ################################################
    
    print(f'Loading in {fname} parameters...') 
    param = load_params(path='../config', fname=fname, all=False, merge=False)


# In[11]:


# If you are satisfied with the parameters and are ready to generate data, modify + run this cell

#####################
param_to_load = main # <-- CHANGE THIS AS NEEDED | For example, `potter1975` (variable) or params['potter1975']
#####################
  
wiscs.set_params(param_to_load)
DG = DataGenerator()
DG.fit_transform()


# In[12]:


# If you wish to save the data, modify + run this cell

########################################
output_name = "simulated_Main_data.csv" # <-- CHANGE THIS AS NEEDED | For example, "simulated_Main_data.csv"
########################################

DG.to_pandas().to_csv(f'../data/{output_name}', index=False)


# ## Generate parameters and data with `ipywidgets`
# 
# The widget is structured as follows. 
# 
# ```bash
# WISCS_WIDGET
# ├── **Cognitive Parameters**
# │   ├── Word -> Perceptual
# │   ├── Image -> Perceptual
# │   ├── Word -> Conceptual
# │   ├── Image -> Conceptual
# │   └── Tasks
# │       ├── Range of tasks parameters
# │       ├── Number of tasks 
# │       ├── Copy?
# ├── **Variance Parameters**
# │   ├── Word
# │   ├── Image
# │   ├── Question
# │   └── Participant
# ├── **Experiment Parameters**
# │   ├── Number of Participants
# │   ├── Number of items 
# │   ├── Number of tasks 
# │   └── Design
# │       ├── within
# │       └── between
# ```
# 
# Below is a desription of each in tabular format
# 
# | Tab | Description | 
# | --- | ----------- |
# | **Cognitive Parameters** | --- |
# | Word -> Perceptual | Expected value: integer. The theoretical value for activating the perceptual representation of a word |
# | Image -> Perceptual | Expected value: integer. The theoretical value for activating the perceptual representation of an image |
# | Word -> Conceptual | Expected value: integer. The theoretical value for activating the conceptual representation of a word |
# | Image -> Conceptual | Expected value: integer. The theoretical value for activating the conceptual representation of an image |
# | Tasks | This generates a random permutation of values between a desired range, corresponging to the task parameter for each question. You must also specify the number of tasks. Additionally, you may select whether to "copy" these values, which means that an identical array of task parameters will be created for both word and image. This is inline with the MAIN hypothesis. If not selected, then two different arrays will be used for word and image taske parameters | 
# | **Variance Parameters** | --- | 
# | Word | Expected value: integer or float. $\sigma^2$ for word | 
# | Image | Expected value: integer or float. $\sigma^2$ for image | 
# | Question | Expected value: integer or float. $\sigma^2$ for question | 
# | Participant | Expected value: integer or float. $\sigma^2$ for participant | 
# | **Experiment Parameters** | --- | 
# | Number of particpants | Expected value: integer. The number of participants to include in the study | 
# | Number of items | Expected value: integer. The number of items. E.g., if set to 45, participants will see 45 images and 45 words. |  
# | Number of tasks | Expected value: integer. The number of questions seen by participants. | 
# | Design | Whether **items** is a within or between subjects variable |
# 

# In[11]:


# to load the widget, run this cell

# fill out the necessary information in the tabs and dropdowns. 
w = wiscs_widget
w


# In[18]:


# If you are satisfied with the parameters and are ready to generate data, run this cell
wiscs.set_params(
    extract_params_from_widget(w)
    )
DG = DataGenerator()
DG.fit_transform()


# In[14]:


# If you wish to save the data, modify + run this cell

########################################
output_name = "simulated_data.csv" # <-- CHANGE THIS AS NEEDED | For example, "simulated_data.csv"
########################################

DG.to_pandas().to_csv(f'../data/{output_name}', index=False)


# ## Generate your own data by modifying the parameters dictionary

# In[15]:


# If you wish to generate data based on parameters you wish to define directly in the code, modify + run this cell

########################################################################################
params = {
    'word.perceptual': ...,
    'image.perceptual': ...,

    'word.concept': ...,
    'image.concept': ...,

    'word.task': ..., # expected type: np.ndarray such that len(word.task) == n.question
    'image.task': ..., # expected type: np.ndarray len(image.task) == n.question

    'var.image': ...,
    'var.word': ...,
    'var.question': ...,
    'var.participant': ...,

    'n.participant': ...,
    'n.question': ...,
    'n.trial': ..., # equivalent to number of items
    'design': {'items': ...} # 'between' or 'within'
}
########################################################################################


# In[ ]:


# If you are satisfied with the parameters and are ready to generate data, run this cell

wiscs.set_params(params)
DG = DataGenerator()
DG.fit_transform()


# In[ ]:


# If you wish to save the data, modify + run this cell

########################################
output_name = "simulated_data.csv" # <-- CHANGE THIS AS NEEDED | For example, "simulated_data.csv"
########################################

DG.to_pandas().to_csv(f'../data/{output_name}', index=False)

