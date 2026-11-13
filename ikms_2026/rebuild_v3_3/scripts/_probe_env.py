import os
import sys

# Ensure JAVA_HOME is set
if "JAVA_HOME" not in os.environ:
    os.environ["JAVA_HOME"] = r"C:\Users\khari\AppData\Local\openLCA\jre"

print("Python:", sys.version.split()[0])
for m in ["CoolProp", "neqsim", "win32com.client", "pandas", "numpy",
          "sklearn", "scipy", "joblib", "lightgbm", "openpyxl"]:
    try:
        mod = __import__(m)
        ver = getattr(mod, "__version__", "LOADED_OK")
        print("%-22s OK    %s" % (m, ver))
    except Exception as e:
        print("%-22s MISSING (%s)" % (m, type(e).__name__))
