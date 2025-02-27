import numpy as np
from glob import glob
import os
import ipywidgets as widgets # type: ignore
import pandas as pd
from rinterface.utils import to_r # type: ignore

from wiscs.utils import make_tasks # type: ignore
from wiscs.formula import Formula # type: ignore

def base(files, y):
    for i in files:
        y.append(os.path.basename(i).split('_')[1].split('.')[0])
    return y

base2filename = lambda x, y: f'{x}/params_{y}.npy'

def load_params(path:str, all:bool=True, fname:str=None, merge:bool=True):
    """Load data generation parameters.
    
    Parameterss
    ----------
    all: bool
        Load all parameters. Default is True.
        
    merge: bool
        Merge all parameters into a single dictionary. Default is True.
        
    Returns
    -------
    dict
        Dictionary of parameters.
    """
    fnames = glob(f'{path}/params_*.npy')

    if all and not merge:
        param1 = np.load(fnames[0], allow_pickle=True).item()
        param2 = np.load(fnames[1], allow_pickle=True).item()
        param3 = np.load(fnames[2], allow_pickle=True).item()
        return param1, param2, param3
    
    elif all and merge:
        param1, param2, param3 = load_params(all=True, merge=False)
        tags = base(fnames, [])
        return {tags[0]: param1, tags[1]: param2, tags[2]: param3}
    
    elif not all and not merge:
        return np.load(base2filename(path, fname), allow_pickle=True).item()
    
def get_tab_nest_values(tab_nest):
    """
    Extract values from the `tab_nest` widget and return them in a dictionary.

    Parameters:
        tab_nest: The top-level Tab widget containing nested widgets.

    Returns:
        dict: A dictionary with values extracted from the widgets.
    """
    values = {}

    # Iterate over tab children
    for i in range(len(tab_nest.children)):
        tab_name = tab_nest.get_title(i)
        tab_content = tab_nest.children[i]

        if isinstance(tab_content, widgets.Accordion):
            accordion_values = {}

            # Iterate over Accordion children
            for j in range(len(tab_content.children)):
                section_name = tab_content.get_title(j)
                section_content = tab_content.children[j]

                # Handle different widget types
                if isinstance(section_content, widgets.IntText):
                    accordion_values[section_name] = section_content.value
                elif isinstance(section_content, widgets.Dropdown):
                    accordion_values[section_name] = section_content.value
                elif isinstance(section_content, widgets.VBox):
                    vbox_values = {}
                    for child_widget in section_content.children:
                        if isinstance(child_widget, widgets.IntRangeSlider):
                            vbox_values['IntRangeSlider'] = child_widget.value
                        elif isinstance(child_widget, widgets.IntText):
                            vbox_values['IntText'] = child_widget.value
                        elif isinstance(child_widget, widgets.Checkbox):
                            vbox_values['Checkbox'] = child_widget.value
                    accordion_values[section_name] = vbox_values

            values[tab_name] = accordion_values

        elif isinstance(tab_content, widgets.VBox):
            vbox_values = {}
            for child_widget in tab_content.children:
                if isinstance(child_widget, widgets.IntText):
                    vbox_values['IntText'] = child_widget.value
                elif isinstance(child_widget, widgets.Dropdown):
                    vbox_values['Dropdown'] = child_widget.value
            values[tab_name] = vbox_values

        elif isinstance(tab_content, widgets.IntText):
            values[tab_name] = tab_content.value

        elif isinstance(tab_content, widgets.Dropdown):
            values[tab_name] = tab_content.value

    return values

def extract_params_from_widget(widget):
    _params = get_tab_nest_values(widget)
    
    low = _params['Cognitive Parameters']['Task']['IntRangeSlider'][0]
    high = _params['Cognitive Parameters']['Task']['IntRangeSlider'][0]
    copy_task = _params['Cognitive Parameters']['Task']['Checkbox']
    n_questions = _params['Experiment Parameters']['N Questions']

    if copy_task:
        _task = make_tasks(low, high, n_questions)
        task = [_task, _task]
    else:
        _task_word = make_tasks(low, high, n_questions)
        _task_image = make_tasks(low, high, n_questions)
        task = [_task_word, _task_image]

    params = {
        'word.perceptual': _params['Cognitive Parameters']['Word -> Perceptual'],
        'image.perceptual': _params['Cognitive Parameters']['Image -> Perceptual'],
        'word.concept': _params['Cognitive Parameters']['Word -> Conceptual'],
        'image.concept': _params['Cognitive Parameters']['Image -> Conceptual'],
        'word.task': task[0],
        'image.task':task[1],
        'var.image': _params['Variance parameters']['Image'],
        'var.word': _params['Variance parameters']['Word'],
        'var.question': _params['Variance parameters']['Question'],
        'var.participant': _params['Variance parameters']['Participant'],
        'n.participant': _params['Experiment Parameters']['N Participants'],
        'n.question': _params['Experiment Parameters']['N Questions'],
        'n.trial': _params['Experiment Parameters']['N Items'],
        'design': {'items': _params['Experiment Parameters']['Design']}
    }

    return params

def fmt_script(df:pd.DataFrame, shared_re:Formula, separate_re:Formula=None, shared_fixed:str="rt ~ modality + question", 
               separate_fixed:str=" rt ~ modality * question", add:list[str]=None, VarCorr_only:bool=False, optimizer:str="bobyqa",
               maxfun:int=10000) -> str:
    
    if separate_re is None:
        separate_re = shared_re

    """Format R script for mixed-effects model analysis.
    
    Parameters
    ----------
    shared_f: str
        Shared fixed effects formula.
    separate_f: str
        Separate fixed effects formula. 
    df: pd.DataFrame
        Dataframe containing the data.
    add: list[str]  
        Additional lines to add to the script.
    """
    _add = "\n".join(add) if add else ""
    optimizer_control = f', control = lmerControl(optimizer = "{optimizer}", optCtrl = list(maxfun = {maxfun}))' if optimizer else ""
    return(rf"""
    # imports
    suppressMessages(library(lme4))
    suppressMessages(library(psych))
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

    # add lines
    {_add}


    # model
    shared <- lmer({shared_fixed + " + " + str(shared_re)}, data = df, REML = FALSE, {optimizer_control}) # nolint
    separate <- lmer({separate_fixed + " + " + str(separate_re)}, data = df, REML = FALSE, {optimizer_control}) # nolint

    if ({to_r(VarCorr_only)}) {{

        cat("\n\033[1m Variance components (Shared Model)\033[0m\n")
        print(VarCorr(shared))
        cat("\n\033[1m Variance components (Separate Model)\033[0m\n")
        print(VarCorr(separate))
    }} else {{
        # full output
        cat("\n\033[1m SHARED model summary\033[0m\n")
        print(summary(shared))
        cat("\n\033[1m SEPARATE model summary\033[0m\n")
        print(summary(separate))

        cat("\n\033[1m ANOVA\033[0m\n")

        # compare
        print(anova(shared, separate))

        # VarCorr
        cat("\n\033[1m Variance components\033[0m\n")
        print(VarCorr(shared))
    }}
    """)