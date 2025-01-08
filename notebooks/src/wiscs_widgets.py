import ipywidgets as widgets # type: ignore

task = widgets.VBox([widgets.IntRangeSlider(
    value=[100, 500],
    min=0,
    max=1000,
    step=1,
    description='Task:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d',
), 
widgets.IntText(
    value=0,
    description='N tasks',
    disabled=False),
widgets.Checkbox(
    value=False,
    description='Copy?',
    disabled=False
)])

# cognitive parameters
cog_params = widgets.Accordion(children=[widgets.IntText(
    value=0,
    disabled=False
), widgets.IntText(
    value=0,
    disabled=False
), 
widgets.IntText(
    value=0,
    disabled=False
), widgets.IntText(
    value=0,
    disabled=False
), 
task])
cog_params.set_title(0, 'Word -> Perceptual')
cog_params.set_title(1, 'Image -> Perceptual')
cog_params.set_title(2, 'Word -> Conceptual')
cog_params.set_title(3, 'Image -> Conceptual')
cog_params.set_title(4, 'Task')

# variance parameters
var_params = widgets.Accordion(children=[widgets.IntText(
    value=0,
    disabled=False
), widgets.IntText(
    value=0,
    disabled=False
),
widgets.IntText(
    value=0,
    disabled=False
),
widgets.IntText(
    value=0,
    disabled=False
)])
var_params.set_title(0, 'Word')
var_params.set_title(1, 'Image')
var_params.set_title(2, 'Question')
var_params.set_title(3, 'Participant')

experiment_params = widgets.Accordion(children=[widgets.IntText(
    value=0,
    disabled=False
), widgets.IntText(
    value=0,
    disabled=False
),
widgets.IntText(
    value=0,
    disabled=False
),
widgets.Dropdown(
    options=['between', 'within'],
    value='within',
    description='Design:',
    disabled=False,
)])
experiment_params.set_title(0, 'N Participants')
experiment_params.set_title(1, 'N Items')
experiment_params.set_title(2, 'N Questions')
experiment_params.set_title(3, 'Design')

wiscs_widget = widgets.Tab()
wiscs_widget.children = [cog_params, var_params, experiment_params]
wiscs_widget.set_title(0, 'Cognitive Parameters')
wiscs_widget.set_title(1, 'Variance parameters')
wiscs_widget.set_title(2, 'Experiment Parameters')