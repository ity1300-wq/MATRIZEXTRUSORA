# -*- coding: utf-8 -*-
"""Confere, re-medindo os STEP, todo numero escrito em RESFRIAMENTO_MATRIZ_COPO e no bloco da 9a."""
import math, re
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_SurfaceType
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

RHO_ACO=7.85e-6; CP_ACO=486.0; CP_MAST=2.0; RHO_MAST=1.25e-3
Q=15000.0; K=18500.0; N=0.32; GRAD=2.187; KA=45.0; KB=0.25; KAIR=0.026
ok=[]; fail=[]
def chk(nome, med, aleg, tol=0.006, un=''):
    d=abs(med-aleg)/max(abs(aleg),1e-9)
    (ok if d<=tol else fail).append('%-52s medido %12s  no doc %12s  %.3f%%%s'%(nome,f'{med:,.3f}',f'{aleg:,.3f}',100*d,un))

A='06_CAD_Cabecote_EX-030/STEP/Cabecote_EX-030_com_Matriz_Copo.step'
S=list(cq.importers.importStep(A).solids().vals())
head=[s for s in S if s.Volume()>1e6][0]; die=[s for s in S if s.Volume()<1e6][0]
V=die.Volume(); chk('volume da copo (mm3)',V,224289.0,1e-6)
chk('massa (kg)',V*RHO_ACO,1.761,0.001)
chk('capacidade termica (J/K)',V*RHO_ACO*CP_ACO,855.7,0.001)
bb=die.BoundingBox(); chk('face de saida da matriz Z',bb.zmax,80.70,1e-4)
chk('boca enterrada (mm)',head.BoundingBox().zmax-bb.zmax,14.30,1e-3)
areas={}; dist={}
for f in die.Faces():
    ad=BRepAdaptor_Surface(f.wrapped); t=ad.GetType(); fb=f.BoundingBox()
    key=None
    if t==GeomAbs_SurfaceType.GeomAbs_Cylinder:
        r=ad.Cylinder().Radius()
        key={93.0:'banda',75.6:'furo_copo',89.5:'estagio_89-5'}.get(round(2*r,2))
        if round(2*r,2)==1.5 and key is None: key='land_arco'
    elif t==GeomAbs_SurfaceType.GeomAbs_Plane and abs(ad.Plane().Axis().Direction().Z())>0.99:
        key={0.0:'face_traseira',69.9:'ombro',70.7:'fundo_copo',80.7:'face_frontal'}.get(round(fb.zmin,2))
    if key:
        areas[key]=areas.get(key,0.0)+f.Area()
        dist[key]=min(dist.get(key,9e9),BRepExtrema_DistShapeShape(f.wrapped,head.wrapped).Value())
for nm,v in [('banda',20422.6),('furo_copo',16791.6),('estagio_89-5',3036.7),('face_frontal',6179.2),
             ('face_traseira',2304.1),('ombro',501.7),('land_arco',47.12)]:
    chk('area '+nm+' (mm2)',areas[nm],v,2e-4)
tot=sum(areas.values())+2*735.0-areas['fundo_copo']+areas['fundo_copo']
chk('casca total (mm2)',tot,55129.7,1e-4)
chk('molhado de massa (mm2)',areas['furo_copo']+areas['fundo_copo']+areas['face_frontal']+areas['land_arco']+2*735.0,28864.7,1e-4)
for nm,pct in [('furo_copo+fundo',38.4)]:
    chk('%% massa dentro do copo',100*(areas['furo_copo']+areas['fundo_copo'])/tot,pct,0.01)
for nm,pct in [('banda',37.0),('furo_copo',30.5),('face_frontal',11.2),('estagio_89-5',5.5),
               ('face_traseira',4.2),('ombro',0.9),('fundo_copo',7.9)]:
    chk('%% '+nm,100*areas[nm]/tot,pct,0.02)
chk('folga face frontal (mm)',dist['face_frontal'],0.25,1e-3)
chk('folga ombro (mm)',dist['ombro'],0.10,1e-3)
chk('folga banda (axial no canto, mm)',dist['banda'],0.10,1e-3)
chk('folga estagio (mm)',dist['estagio_89-5'],0.25,1e-3)
# degrau axial
chk('face frontal ate o plano do degrau (mm)',81.00-80.70,0.30,1e-9)
# contato real do anel
a_int=math.pi*(46.5**2-45.0**2); chk('contato real no degrau (mm2)',a_int,431.2,1e-3)
# tunel
tun=math.pi/4*80.0**2*14.0; chk('vao livre do tunel (mm3)',tun,70371.7,1e-4)
# canal
Cc=list(cq.importers.importStep('07_CAD_Matrizes/Matriz_Copo_HISTORICA/Matriz1_Original_Copo_Canal_Fluxo.step').solids().vals())[0]
Vc=Cc.Volume(); chk('volume do canal (mm3)',Vc,318480.7,1e-5)
chk('massa de massa no copo (g)',Vc*RHO_MAST,398.1,1e-3)
chk('residencia (s)',Vc/Q,21.2,0.005)
chk('capacidade da massa (J/K)',Vc*RHO_MAST/1000*1000*CP_MAST,796.2,0.002)
# land e calor
land=80.70-70.70; chk('land (mm)',land,10.00,1e-9)
dp=GRAD*land; chk('DeltaP do land (bar)',dp,21.87,1e-3)
W=dp*1e5*Q*1e-9; chk('calor do land (W)',W,32.8,2e-3)
C=V*RHO_ACO*CP_ACO
chk('tempo p/ +20C com 33 W (min)',20*C/W/60,8.7,0.01)
chk('tempo p/ +20C com 300 W (min)',20*C/300/60,0.95,0.01)
# resistencias
def R(L,A_,k): return (L*1e-3)/(k*A_*1e-6)
chk('R filme 0,30 massa (K/W)',R(0.30,areas['face_frontal'],KB),0.194,2e-3)
chk('R filme 0,30 ar (K/W)',R(0.30,areas['face_frontal'],KAIR),1.867,2e-3)
chk('R filme 0,25 estagio (K/W)',R(0.25,areas['estagio_89-5'],KB),0.329,2e-3)
chk('R filme 1,00 banda (K/W)',R(1.00,areas['banda'],KAIR),1.883,2e-3)
band=[f for f in head.Faces() if BRepAdaptor_Surface(f.wrapped).GetType()==GeomAbs_SurfaceType.GeomAbs_Cylinder
      and abs(round(BRepAdaptor_Surface(f.wrapped).Cylinder().Radius(),2)-65.0)<0.01][0]
Ab=band.Area(); chk('area da banda Ø130 (mm2)',Ab,17153.1,1e-4)
d_band=BRepExtrema_DistShapeShape(band.wrapped,die.wrapped).Value(); chk('nariz ate a matriz (mm)',d_band,18.50,1e-3)
hb=band.BoundingBox(); chk('comprimento da banda (mm)',hb.zmax-hb.zmin,42.00,1e-6)
Ac=math.pi*130.0*28.0; chk('area do colar de 28 mm (mm2)',Ac,11435.4,1e-4)
chk('R colar agua h=2000 (K/W)',1/(2000*Ac*1e-6),0.044,0.02)
chk('puxada com 40C (W)',40/R(0.30,areas['face_frontal'],KB)+40/R(0.25,areas['estagio_89-5'],KB),330,0.02)
chk('agua 1 L/min elevacao p/ 300W (C)',300/(1/60*1000*4.186),4.3,0.01)
chk('W por 1C de mastiche',Q*RHO_MAST*CP_MAST,37.5,1e-3)
chk('vazao massica (g/s)',Q*RHO_MAST,18.75,1e-3)
# furo de agua: faixa de centro
cmin=37.80+4.00+2.00; cmax=46.50-4.00-2.00
chk('centro minimo do furo d agua (mm raio)',cmin,43.80,1e-6); chk('centro maximo (mm raio)',cmax,40.50,1e-6)
print('faixa vazia (impossivel)?', cmin>cmax)
print('protruir: banda Ø93 passa do degrau Ø90?  falta mm de raio =',46.50-45.00)
# boca das outras matrizes
for tag,aleg in [('Cabecote_EX-030_com_Matriz_Jonatha_v30',0.00),('Cabecote_EX-030_com_Matriz_Jonatha_v29',14.00)]:
    T=list(cq.importers.importStep('06_CAD_Cabecote_EX-030/STEP/%s.step'%tag).solids().vals())
    d2=[s for s in T if s.Volume()<1e6][0]; h2=[s for s in T if s.Volume()>1e6][0]
    chk('protrusao da boca, '+tag[-3:],d2.BoundingBox().zmax-h2.BoundingBox().zmax,aleg,1e-3 if aleg else 1e-9) if aleg else print('%-52s medido %.3f  no doc %.3f  (rasa)'%('protrusao da boca, '+tag[-3:],d2.BoundingBox().zmax-h2.BoundingBox().zmax,aleg))
print('== PASS (%d)'%len(ok)); [print('  ok ',x.strip()) for x in ok]
print('== DIVERGE (%d)'%len(fail)); [print('  XX ',x.strip()) for x in fail]
