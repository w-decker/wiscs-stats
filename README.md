# wiscs-stats
Statistical pipeline for WISCS

## Data generation
The data generation process can be found in [$\texttt{/notebooks/generate\_data.ipynb}$](/notebooks/generate_data.ipynb). This notebook cannot be run in Colab, unfortunately due to incompatible environments. The custom module built for data generation, `wiscs` makes use of `numpy==2.2.1`, which is not functional in Colab at this time. 

To run the notebook, clone the repository and open the notebook. Then activate the associate conda environment. This can be done by copying and pasting the following code into your terminal.

```bash
git clone https://github.com/w-decker/wiscs-stats.git
conda env create -f environment.yml
```

It is recommended to view and run the notebook in VS Code. 
