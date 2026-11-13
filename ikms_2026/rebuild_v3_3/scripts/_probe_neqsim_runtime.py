import os
import sys

os.environ["JAVA_HOME"] = r"C:\Users\khari\AppData\Local\openLCA\jre"
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(os.path.join(BASE, "MR_OPTIMIZATION_REBUILD", "src"))

print("--- bare neqsim import with JAVA_HOME set ---")
try:
    import neqsim
    print("neqsim OK", getattr(neqsim, "__version__", ""))
except Exception as e:
    print("neqsim FAILED:", type(e).__name__, e)

print("--- engine import ---")
try:
    from thermodynamics.neqsim_engine import evaluate_mche_pinch_5comp
    print("engine OK")
    res = evaluate_mche_pinch_5comp(
        mcr_flow_th=518.33,
        mcr_comp=[0.0367, 0.5126, 0.4262, 0.0044, 0.0201],
        feed_flow_th=134.49,
        t_suct_c=-41.0,
        p_shell_bara=3.09,
        n_slices=50,
    )
    for k, v in res.items():
        if isinstance(v, float):
            print("  %-20s %.4f" % (k, v))
except Exception as e:
    print("engine FAILED:", type(e).__name__, e)
