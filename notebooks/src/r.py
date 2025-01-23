import rpy2.robjects as robjects # type: ignore

class RInterface(object):

    def __init__(self):
        pass

    @staticmethod
    def init_rpy2():
        """
        Initialize rpy2 for use in Jupyter notebooks. Imports rpy2 into the workspace.
        """
        from IPython import get_ipython
        import importlib

        ipython = get_ipython()
        if not ipython:
            raise RuntimeError("This method must be called from a Jupyter notebook or IPython environment.")
        ipython.run_line_magic("load_ext", "rpy2.ipython")
        global rpy2, robjects
        rpy2 = importlib.import_module("rpy2")
        robjects = importlib.import_module("rpy2.robjects")
        ipython.run_line_magic("reload_ext", "rpy2.ipython")

        return print("""
        import rpy2
        import rpy2.robjects as robjects
        import rpy2.ipython.html
        rpy2.ipython.html.init_printing()
        %load_ext rpy2.ipython
                     """)
    
    @staticmethod
    def r(code:str):
        """Run R code using rpy2.robjects.r
        
        Parameters
        ----------
        code : str
            The R code to be executed
        """
        robjects.r(code)
    
    @staticmethod
    def script(code:str):
        """
        Run R code in the terminal using Rscript.

        Descriotion
        -----------
        This code writes R code to a hidden .R file, runs the file in the terminal, and then deletes the file afterwards.

        Parameters
        ----------
        code : str
            The R code to be executed
        """
        import subprocess
        with open('.temp.R', 'w') as f:
            f.write(code)
        subprocess.run(['Rscript', '.temp.R'])
        subprocess.run(['rm', '.temp.R'])