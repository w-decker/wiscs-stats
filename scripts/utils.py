import numpy as np
import warnings
warnings.filterwarnings("ignore")

from rinterface.utils import to_r
import rinterface.rinterface as R
from wiscs.utils import make_tasks

from tqdm import tqdm
from joblib import Parallel, delayed
import os
import pandas as pd


def grid(**kwargs):
    """Generate all possible combinations of elements in K arrays
    
    **kwargs
    -------
    list, np.ndarray
        K arrays of elements to combine
    """
    return np.array(np.meshgrid(*list(kwargs.values()))).T.reshape(-1, len(kwargs))

# code for model eval in R
def code(df, p_threshold):
    return (f"""
    suppressMessages(library(lme4))
    suppressMessages(library(dplyr))
    suppressMessages(library(lmerTest))

    # import data from Python
    df <- {to_r(df)}

    # factorize + treatment coding
    df$question <- as.factor(df$question)
    df$subject <- as.factor(df$subject)
    df$item <- as.factor(df$item)
    df$modality <- factor(df$modality, levels = c("word", "image"))
    contrasts(df$modality) <- c(-0.5, 0.5)

    #  set reference levels
    df$question <- relevel(df$question, ref = "0")
    df$item <- relevel(df$item, ref = "0")

    # load data
    df <- {to_r(df)}

    # model
    # supress singular fit warnings
    control <- lmerControl(optimizer = "bobyqa", check.conv.singular = "ignore")
    shared <- lmer(rt ~ modality + question + (1 + question | subject) + (1 + question | item), data = df, REML = FALSE, control = control) # nolint
    separate <- lmer(rt ~ modality * question + (1 + question | subject) + (1 + question | item), data = df, REML = FALSE, control = control) # nolint

    # compare
    aicvalues <- c("Shared" = AIC(shared), "Separate" = AIC(separate))
    p_value <- anova(shared, separate, test="Chisq")$`Pr(>Chisq)`[2]

    # anova(shared, separate)

    # @grab{{int}}
    success <- ifelse(p_value > {p_threshold}, 1, 0)
    """)

def run(DG, p_threshold, desired_power, row, question_sd, n_iter=10, verbose=True):
    
    iter = tqdm(np.arange(0, n_iter+1)) # instantiate iter obj

    n_subject, n_item, n_question = row 
    if verbose:
        print(f"{n_subject} subjects | {n_item} items | {n_question} questions")
    success = np.zeros(n_iter, dtype=int)

    power = 0

    j = -1
    for j, _ in enumerate(iter):

        task = make_tasks(low=100, high=200, n=n_question, seed=2025)
        # update data
        update = {'word.task':task, 'image.task':task, 'sd.question': question_sd[:n_question-1], 'corr.subject': np.eye(n_question), 'corr.item':np.eye(n_question), 'n.question': n_question, 'n.item': n_item, 'n.subject': n_subject}
        DG.fit_transform(update, overwrite=True)

        # convert to dataframe
        df = DG.to_pandas()

        # Run the R model and determine winner
        success[j] = R(code(df, p_threshold), grab=True)

        # Calculate current power
        power = np.sum(success) / n_iter
        
        # update tqdm
        iter.set_postfix({
            "Power": round(power, 3), 
            "Iteration": j + 1, 
            "# Winners": np.sum(success[:j+1]), 
            "# Losers": np.sum(success[:j+1] == 0)
        })

        # Check power / if power is possible
        if np.sum(success[:j+1] == 0) >= n_iter - (0.8 * n_iter) + 1:
            iter.set_postfix({"Power": round(power, 3), "Status": "Stopping: Power not possible"})
            break

        if power >= desired_power:
            iter.set_postfix({"Power": round(power, 3), "Status": "Stopping early"})
            break
    results_df = pd.DataFrame({
            "n_subjects": [n_subject],
            "n_items": [n_item],
            "n_questions": [n_question],
            "power": [power],
            "iterations_run": [j + 1]
        })

    return results_df

def agg(DG, p_threshold, desired_power, combinations, question_sd, n_jobs=8, n_iter=10, parallelize=True, verbose=True):
    """
    Aggregates power calculations. Option to parallelize.
    """
    
    if parallelize:
        os.environ["JOBLIB_TEMP_FOLDER"] = "/scratch/$USER/tmp" # default
        os.environ["TMPDIR"] = "/scratch/$USER/tmp" # default
        results = _parallel_agg(DG, p_threshold, desired_power, combinations, question_sd, n_iter=n_iter, n_jobs=n_jobs)
    else:
        results = []
        for row in combinations:
            result_df = run(DG, p_threshold, desired_power, row, question_sd, n_iter=n_iter)
            results.append(result_df)

    # Concatenate results from all parallel runs
    results_df = pd.concat(results, ignore_index=True)
    return results_df

def _parallel_agg(DG, p_threshold, desired_power, combinations, question_sd, n_iter=10, n_jobs=8):

    results = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(run)(DG, p_threshold, desired_power, row, question_sd, n_iter) for row in tqdm(combinations, desc="Processing Grid")
    )

    return results