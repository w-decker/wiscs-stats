import numpy as np
from glob import glob
import os
import ipywidgets as widgets # type: ignore

from wiscs.utils import make_tasks # type: ignore

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