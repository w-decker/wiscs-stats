#!/usr/bin/bash

from utils import grid, agg

import wiscs
from wiscs.utils import make_tasks
from wiscs.simulate import DataGenerator
from wiscs.formula import Formula

import numpy as np

# create a baseline model
n_question = 2
n_item = 2
n_subject = 2
task = make_tasks(low=100, high=200, n=n_question, seed=2025)
re_formula = Formula("(1 + question | subject) + (1 + question | item)")
question_sd = [10, 12, 15, 18, 11] # must be n_q - 1
params = {'word.perceptual': 100, 'image.perceptual': 95, 'word.conceptual': 100, 'image.conceptual': 100, 'word.task': task, 'image.task': task,
        # noise parameters     
        'sd.item': 30,     'sd.question': question_sd[:n_question-1],    'sd.subject': 20,       "sd.modality": 10, "sd.error": 50, "sd.re_formula": str(re_formula),
        # correlations among random effects    
        "corr.subject": np.eye(n_question), 'corr.item':np.eye(n_question),
        # design parameters
        'n.subject': n_subject, 'n.question': n_question, 'n.item': n_item
}
wiscs.set_params(params, verbose=False)

# generate baseline data
DG = DataGenerator()
df = DG.fit_transform(seed=2025).to_pandas()

# save baseline
df.to_csv("baseline.csv")
print(f"Baseline saved\n")

# set up some simulation vars
n_iter = 3 # how many interations to do?
desired_power = 0.8
p_threshold = 0.05
n_subjects_range = np.arange(2, 4, 1) # range of subjects to test
n_items_range = np.arange(2, 4, 1) # range of items to test
n_questions_range = np.arange(2, 4, 1) # range of questions to test
combinations = grid(subjects=n_subjects_range, items=n_items_range, questions=n_questions_range) # get all combinatinos

results = agg(DG, p_threshold, desired_power, combinations, question_sd, n_iter=n_iter, parallelize=False)

results.to_csv("power.csv")