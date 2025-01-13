# wiscs-stats
Statistical pipeline for WISCS

## Data generation
Although data have already been generated, a detailed walkthough of the process and the option to do it yourself has been put together into a single jupyter notebook.

The data generation process can be found in [$\texttt{/notebooks/generate\_data.ipynb}$](/notebooks/generate_data.ipynb). This notebook **cannot** be run in Colab due to incompatible environments: the custom module built for data generation, [`wiscs`](https://github.com/w-decker/wiscs) makes use of `numpy==2.2.1`, which is not functional in Colab at this time. 

To run the notebook, clone the repository and open the notebook. Then activate the associated conda environment. This can be done by copying and pasting the following code into your terminal.

```bash
git clone https://github.com/w-decker/wiscs-stats.git
cd wiscs-stats
conda env create -f environment.yml
```

It is recommended to view and run the notebook in VS Code. 

>[!NOTE]
>There are specific and detailed instructions _inside_ the document too.

## Statistical analysis
A skeleton for statistical analysis is located in [$\texttt{/notebooks/stats\_pipeline.ipynb}$](notebooks/stats_pipeline.ipynb). This can be run in [Google Colab](https://colab.research.google.com/). Simply click <a href="/notebooks/stats_pipeline.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=15 alt="Open In Colab"/></a> at the top of the document.

>[!NOTE]
>There are specific and detailed instructions _inside_ the document too.

## Power
A notebook for computing power and minimum $n\_\{variable\}$ using a simulation approach and by numerically solving for $n\_\{variable\}$. This notebook makes use of [`mixedpower`](https://github.com/w-decker/mixedpower) a custom Python library not installable when activating the conda environment (see inside the notebook for installation).

>[!NOTE]
>There are specific and detailed instructions _inside_ the document too.
