"""Small, dependency-light Peng--Robinson thermodynamics engine.
Units: pressure bar(a), temperature K, molar enthalpy J/mol, density kg/m3.
It reports supplied-composition PR results and never calibrates to a target.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq
R=8.31446261815324; BAR=1e5
NAMES=("N2","C1","C2","C2H4","C3")
TC=np.array([126.20,190.56,305.32,282.34,369.83])
PC=np.array([33.90,45.99,48.72,50.41,42.48])*BAR
OMEGA=np.array([.037,.011,.099,.087,.152]); MW=np.array([28.013,16.042,30.070,28.054,44.096])/1000
KIJ=np.zeros((5,5)); KIJ[0,1]=KIJ[1,0]=.038; KIJ[1,2]=KIJ[2,1]=.008; KIJ[1,4]=KIJ[4,1]=.015
CP=np.array([29.1,35.7,52.5,43.6,73.6])

def _x(x):
 x=np.asarray(x,dtype=float).ravel()
 if x.size!=5 or np.any(x<0) or not np.isfinite(x).all() or x.sum()<=0: raise ValueError("x_mole_frac must contain five finite non-negative values")
 return x/x.sum()

def _params(T,x):
 x=_x(x); m=.37464+1.54226*OMEGA-.26992*OMEGA**2; alpha=(1+m*(1-np.sqrt(T/TC)))**2
 ai=.45724*R**2*TC**2/PC*alpha; bi=.07780*R*TC/PC
 aij=np.sqrt(ai[:,None]*ai[None,:])*(1-KIJ); a=float(x@aij@x); b=float(x@bi)
 dalpha=-(m*(1+m*(1-np.sqrt(T/TC))))/np.sqrt(T*TC); dai=.45724*R**2*TC**2/PC*dalpha
 daij=.5*aij*(dai[:,None]/ai[:,None]+dai[None,:]/ai[None,:]); da=float(x@daij@x)
 return a,b,da,ai,bi,aij

def _roots(P_bar,T_K,x):
 if P_bar<=0 or T_K<=0: raise ValueError("P_bar and T_K must be positive")
 a,b,*_= _params(T_K,x); P=P_bar*BAR; A=a*P/(R*T_K)**2; B=b*P/(R*T_K)
 c=[1,-(1-B),A-3*B**2-2*B,-(A*B-B**2-B**3)]
 roots=np.roots(c); real=np.sort(roots.real[np.abs(roots.imag)<1e-7]); real=real[real>B-1e-10]
 if not len(real): raise ValueError("PR cubic has no physical real root")
 return real,A,B

def pr_compressibility(P_bar,T_K,x_mole_frac):
 r,_,_=_roots(P_bar,T_K,x_mole_frac); return float(r[-1]),float(r[0])

def pr_density(P_bar,T_K,x_mole_frac,phase="vapor"):
 x=_x(x_mole_frac); zv,zl=pr_compressibility(P_bar,T_K,x); z=zl if phase.lower().startswith("l") else zv
 return float(P_bar*BAR*(x@MW)/(z*R*T_K))

def _lnphi(P_bar,T,x,phase):
 x=_x(x); P=P_bar*BAR; a,b,_,ai,bi,aij=_params(T,x); zv,zl=pr_compressibility(P_bar,T,x); Z=zl if phase.startswith("l") else zv
 A=a*P/(R*T)**2; B=b*P/(R*T); S=aij@x; q=np.log((Z+(1+np.sqrt(2))*B)/(Z+(1-np.sqrt(2))*B))
 return bi/b*(Z-1)-np.log(Z-B)-A/(2*np.sqrt(2)*B)*(2*S/a-bi/b)*q

def _equilibrate(P,T,z,beta0=.5):
 z=_x(z)
 r,A,B=_roots(P,T,z)
 if len(r)==1:
  # A single cubic root does not identify the phase by its numerical Z value.
  # Wilson K is a screening estimate, not a stability calculation: ambiguous
  # states must not silently be labelled vapor or liquid.
  K=(PC/(P*BAR))*np.exp(5.373*(1+OMEGA)*(1-TC/T))
  if np.sum(z/K)<1.0: return z,z,1.0
  if np.sum(z*K)<1.0: return z,z,0.0
  raise ValueError("Single-root phase ambiguous; stability analysis required")
 ln_phi_l=_lnphi(P,T,z,"l"); ln_phi_v=_lnphi(P,T,z,"v")
 K=np.exp(np.clip(ln_phi_l-ln_phi_v,-20,20))
 if np.all(np.abs(K-1.0)<1e-5):
  zv,zl=pr_compressibility(P,T,z)
  return (z,z,1.0) if zv>0.5 else (z,z,0.0)
 beta=beta0
 for _ in range(100):
  def rr(b): return float(np.sum(z*(K-1)/(1+b*(K-1))))
  f0=rr(0.0); f1=rr(1.0)
  if f0<=0: return z,z,0.0
  if f1>=0: return z,z,1.0
  beta=brentq(rr,0.0,1.0)
  xl=z/(1+beta*(K-1)); yv=K*xl; xl/=xl.sum(); yv/=yv.sum()
  knew=np.exp(np.clip(_lnphi(P,T,xl,"l")-_lnphi(P,T,yv,"v"),-20,20))
  if np.max(np.abs(np.log(knew/K)))<1e-7: return xl,yv,beta
  K=.5*K+.5*knew
 return xl,yv,beta

def pr_dew_bubble_temperatures(P_bar,x_mole_frac):
 z=_x(x_mole_frac)
 def k_w(T): return (PC/(P_bar*BAR))*np.exp(5.373*(1+OMEGA)*(1-TC/T))
 def f_b(T): return float(np.sum(z*k_w(T))-1.0)
 def f_d(T): return float(np.sum(z/k_w(T))-1.0)
 grid=np.linspace(80,450,200)
 def solve_bracket(fn):
  vals=[fn(t) for t in grid]
  for a,b,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
   if np.isfinite(fa) and np.isfinite(fb) and fa*fb<=0: return float(brentq(fn,a,b))
  return float("nan")
 tb_w=solve_bracket(f_b); td_w=solve_bracket(f_d)
 tb=tb_w
 if np.isfinite(tb_w):
  for _ in range(25):
   K=k_w(tb); yv=z*K; yv/=yv.sum()
   try:
    phil=_lnphi(P_bar,tb,z,"l"); phiv=_lnphi(P_bar,tb,yv,"v")
    K_pr=np.exp(np.clip(phil-phiv,-20,20)); err=np.sum(z*K_pr)-1.0
    if abs(err)<1e-5: break
    tb=tb*(1.0-0.05*err)
   except Exception: break
 td=td_w
 if np.isfinite(td_w):
  for _ in range(25):
   K=k_w(td); xl=z/K; xl/=xl.sum()
   try:
    phil=_lnphi(P_bar,td,xl,"l"); phiv=_lnphi(P_bar,td,z,"v")
    K_pr=np.exp(np.clip(phil-phiv,-20,20)); err=float(np.sum(z/K_pr)-1.0)
    if abs(err)<1e-5: break
    td=td*(1.0+0.05*err)
   except Exception: break
 return (tb if np.isfinite(tb) else tb_w),(td if np.isfinite(td) else td_w)

def pr_dew_temperature(P_bar,x_mole_frac):
 z=_x(x_mole_frac)
 def k_w(T): return (PC/(P_bar*BAR))*np.exp(5.373*(1+OMEGA)*(1-TC/T))
 def f_d(T): return float(np.sum(z/k_w(T))-1.0)
 try:
  td_w=float(brentq(f_d,120.0,350.0))
 except Exception:
  grid=np.linspace(80,450,100); vals=[f_d(t) for t in grid]; td_w=float("nan")
  for a,b,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
   if np.isfinite(fa) and np.isfinite(fb) and fa*fb<=0:
    td_w=float(brentq(f_d,a,b)); break
 td=td_w
 if np.isfinite(td_w):
  for _ in range(25):
   K=k_w(td); xl=z/K; xl/=xl.sum()
   try:
    phil=_lnphi(P_bar,td,xl,"l"); phiv=_lnphi(P_bar,td,z,"v")
    K_pr=np.exp(np.clip(phil-phiv,-20,20)); err=float(np.sum(z/K_pr)-1.0)
    if abs(err)<1e-5: break
    td=td*(1.0+0.05*err)
   except Exception: break
 return td if np.isfinite(td) else td_w

def _h(T,P,x,phase):
 x=_x(x); a,b,da,*_=_params(T,x); z=pr_compressibility(P,T,x)[0 if phase=="vapor" else 1]
 B=b*P*BAR/(R*T); q=np.log((z+(1+np.sqrt(2))*B)/(z+(1-np.sqrt(2))*B))
 return float((x@CP)*(T-273.15)+R*T*(z-1)+(T*da-a)/(2*np.sqrt(2)*b)*q)

def pr_isenthalpic_flash(P_in,T_in,P_out,x_mole_frac):
 x=_x(x_mole_frac); hin=_h(T_in,P_in,x,"vapor")
 def residual(T):
  xl,yv,beta=_equilibrate(P_out,T,x)
  return beta*_h(T,P_out,yv,"vapor")+(1-beta)*_h(T,P_out,xl,"liquid")-hin
 grid=np.linspace(max(90,T_in-120),min(400,T_in+80),160); vals=[residual(t) for t in grid]
 for a,b,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
  if np.isfinite(fa) and fa*fb<=0:
   Tout=float(brentq(residual,a,b)); xl,yv,beta=_equilibrate(P_out,Tout,x)
   return {"T_out_K":Tout,"T_out_C":Tout-273.15,"vapor_fraction":float(beta),"x_liquid":xl,"y_vapor":yv,"h_in_J_mol":hin}
 raise ValueError("No isenthalpic outlet root in bounded temperature range")

def mche_pinch_check(feed_cooling_curve,mcr_warming_curve):
 hot=np.asarray(feed_cooling_curve,float); cold=np.asarray(mcr_warming_curve,float)
 if hot.ndim!=2 or cold.ndim!=2 or hot.shape[1]!=2 or cold.shape[1]!=2: raise ValueError("curves must be Nx2 (temperature_C, duty_fraction)")
 if len(hot)<2 or len(cold)<2 or not np.isfinite(hot).all() or not np.isfinite(cold).all():
  raise ValueError("curves need at least two finite points")
 hot=hot[np.argsort(hot[:,1])]; cold=cold[np.argsort(cold[:,1])]
 for curve in (hot,cold):
  qv=curve[:,1]
  if np.any(np.diff(qv)<=0) or qv[0]!=0 or qv[-1]!=1:
   raise ValueError("duty_fraction must be unique and span 0 to 1")
 # Piecewise-linear difference reaches its minimum at an endpoint or knot.
 q_profile=np.linspace(0,1,20)
 q_eval=np.unique(np.concatenate((q_profile,hot[:,1],cold[:,1])))
 d_eval=np.interp(q_eval,hot[:,1],hot[:,0])-np.interp(q_eval,cold[:,1],cold[:,0]); i=int(np.argmin(d_eval))
 return {"pinch_delta_T_C":float(d_eval[i]),"pinch_index":i,"q_fraction":float(q_eval[i]),"delta_T_profile_C":np.interp(q_profile,q_eval,d_eval)}

