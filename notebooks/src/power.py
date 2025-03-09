import numpy as np
import warnings
warnings.filterwarnings("ignore")

def grid(**kwargs):
    """Generate all possible combinations of elements in K arrays
    
    **kwargs
    -------
    list, np.ndarray
        K arrays of elements to combine
    """
    return np.array(np.meshgrid(*list(kwargs.values()))).T.reshape(-1, len(kwargs))