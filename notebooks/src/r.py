import rpy2.robjects as robjects # type: ignore
import subprocess
import re, os

class RInterface(object):

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
        global rpy2
        global robjects
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
        import rpy2.robjects as robjects # type: ignore
        robjects.r(code)
    
    @staticmethod
    def script(code:str, save:bool=False,fname:str=None,capture:bool=False, grab:bool=False):
        """
        Run R code in the terminal using Rscript, with support for grabbing variable values.

        Parameters
        ----------
        code : str
            The R code to be executed.
        save : bool, optional
            Whether to save the R code to a file. Default is False.
        fname : str, optional
            The filename to save the R code if save is True. Default is None.
        capture : bool, optional
            Whether to capture the output of the R script. Default is False.
        grab : bool, optional
            Whether to extract specific variable values using the @grab annotation. Default is False.

        Returns
        -------
        Any or tuple
            If `grab` is True, returns the extracted variable(s). Otherwise, returns captured output or None.
        """
        temp_file = ".temp.R"
        temp_output = ".grab_output.txt"
        try:
            grab_vars = []
            if grab:
                annotated_lines = re.findall(r"# @grab\{(\w+)\}\n(.+)", code)
                for var_type, var_def in annotated_lines:
                    grab_vars.append((var_type, var_def.strip()))
                capture_code = "\n".join(
                    f'cat("{var_def}=", {var_def}, "\\n", file="{temp_output}", append=TRUE)' for _, var_def in grab_vars
                )
                code += f"\n# Grabbed Variables\n{capture_code}\n"

            with open(temp_file, "w") as f:
                f.write(code)
            
            if save:
                if not fname:
                    raise ValueError("If 'save' is True, 'fname' cannot be None.")
                with open(fname, "w") as f:
                    f.write(code)
            
            # Run the R script
            subprocess.run(["Rscript", temp_file], check=True, text=True)

            # Process the grabbed variables
            if grab:
                with open(temp_output, "r") as f:
                    output = f.readlines()
                
                # Extract and process the variable values based on their type
                results = []
                for (var_type, var_def), line in zip(grab_vars, output):
                    var_name, value = line.strip().split("=", 1)
                    value = value.strip()
                    if var_type == "float":
                        results.append(float(value))
                    elif var_type == "int":
                        results.append(int(value))
                    elif var_type == "str":
                        results.append(value)
                    else:
                        raise ValueError(f"Unsupported type '{var_type}' in @grab annotation.")
                
                return tuple(results) if len(results) > 1 else results[0]

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"R script execution failed: {e.stderr or e}")
        
        finally:
            # Ensure temporary files are deleted
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_output):
                os.remove(temp_output)