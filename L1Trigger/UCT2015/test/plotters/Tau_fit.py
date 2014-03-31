'''
Determines the functional relation between L1pT and pT95 (pTx)
Authors: T.M.Perry, M.Cepeda, E.K.Friis
'''
#!/usr/bin/env python
import ROOT
import random
from ROOT import *
from array import array
#eff_file = ROOT.TFile("/scratch/efriis/uct_tau_efficiency.root")
file_string='../data/Evan/uct_tau_efficiency.root'
eff_file = ROOT.TFile(file_string)

tau_eff_ntuple = eff_file.Get("rlxTauEfficiency/Ntuple")
tau_eff_ntuple_cur = eff_file.Get("isoTauEfficiency/Ntuple")

FixPlat = False #fix plateau value to that of first L1pT Cut
VarBins = False #use variable bin sizing (5 upto pt95, 10 above)
AbsEff = True #instead of pt95, use absolute efficiency threshold
rangeMax=100
thresh=0.90
absThresh=0.6

if AbsEff: saveWhere='../plots/Tau%i_'%(100*absThresh)
else: saveWhere='../plots/Tau%i_'%(100*thresh)
if FixPlat:
 saveWhere+='FixPlat_'
if VarBins:
 saveWhere+='BinVar_'
if AbsEff:
 saveWhere+='AbsEff_'
extraName=''

log = open(saveWhere+extraName+'fit.log','w')
log.write('File: %s\n'%file_string)
log.write('Fixed Plateau: %s\n'%FixPlat)
log.write('Variable Bins: %s\n\n'%VarBins)

canvas = ROOT.TCanvas("asdf", "adsf", 600, 600)
def get_pt95(formula): #not actually pT95, but pT(thresh)
 for i in range(rangeMax):
  if not AbsEff and formula.Eval(i) / formula.GetParameter(0) > thresh:
   return i
  if AbsEff and formula.Eval(i) > absThresh:
   return i 
 return -1

def make_turnon(ntuple,l1_cut, color, name, fix_plateau=None,save=False,binning=array('d',range(0,rangeMax,2)),extraName='',logg=log,pt=-1):
    num = ROOT.TH1F("num", "numerator", len(binning)-1, binning)
    denom = ROOT.TH1F("denom", "denominator", len(binning)-1, binning)
    ntuple.Draw("recoPt>>+num", l1_cut, "goff")
    ntuple.Draw("recoPt>>+denom", "", "goff")
    denom = ROOT.gDirectory.Get("denom")
    num = ROOT.gDirectory.Get("num")
    graph = ROOT.TGraphAsymmErrors(num, denom)
    graph.SetMarkerColor(color)
    graph.SetMarkerStyle(20)
    formula = ROOT.TF1('fitter' + str(random.randint(0, 1000)),
                       "[0]*(0.5*(tanh([1]*(x-[2]))+1))", 0, rangeMax)
    formula.SetParName(0, 'plateau')
    formula.SetParName(1, 'width')
    formula.SetParName(2, 'threshold')
    formula.SetParameter(0, 0.95)
    formula.SetParLimits(0, 0.1, 1.01)
    if fix_plateau is not None:
        print 'fix plat'
        formula.FixParameter(0, fix_plateau)
    formula.SetParameter(1, 1. / 10)
    formula.SetParameter(2, 30)
    formula.SetLineColor(color)
    graph.Fit(formula)
    # refit, not using the inefficient junk at start of curve
    formula.SetRange(formula.GetParameter(2), rangeMax)
    graph.Fit(formula, "R")
    graph.Draw("ape")
    graph.GetHistogram().SetMaximum(1.1)
    graph.GetHistogram().SetMinimum(0)
    pt95 = get_pt95(formula)
    plat=formula.GetParameter(0)
    if AbsEff: graph.GetHistogram().GetXaxis().SetTitle('abs pt%i = %i' % (100*absThresh,pt95))
    graph.GetHistogram().GetXaxis().SetTitle('pt%i = %i' % (100*thresh,pt95))
    if save==True:
     canvas.SaveAs(saveWhere+name+extraName+".png")
    return graph, formula, pt95, plat

ISOTHRESHOLD=0.20

tex = ROOT.TLatex()
tex.SetNDC(True)
tex.SetTextAlign(11)
tex.SetTextSize(0.03)

isoCut='((l1gJetPt-max(l1gRegionEt,l1gPt))/max(l1gRegionEt,l1gPt) <%s)'%(ISOTHRESHOLD)
log.write('Isolation Threshold: %s\n'%ISOTHRESHOLD)
log.write('Iso Cut: %s\n\n'%isoCut)

l1ptVal=array('d',[20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50])
#l1ptValCur=array('d',[26,28,30,32,34,36,38,40,42,44,46])
colors=[
ROOT.EColor.kRed,
ROOT.EColor.kOrange,
ROOT.EColor.kYellow,
ROOT.EColor.kGreen,
ROOT.EColor.kBlue,
ROOT.EColor.kViolet,
ROOT.EColor.kRed,
ROOT.EColor.kOrange,
ROOT.EColor.kYellow,
ROOT.EColor.kGreen,
ROOT.EColor.kBlue,
ROOT.EColor.kViolet,
ROOT.EColor.kRed,
ROOT.EColor.kOrange,
ROOT.EColor.kYellow,
ROOT.EColor.kGreen
]
evenBins=[]
arry=array('d',range(0,rangeMax,5))
for x in l1ptVal:
 evenBins.append(arry)

def find_pt95(isoPlateau=None,nonPlateau=None,curPlateau=None,isoBin=evenBins,nonBin=evenBins,curBin=evenBins,extraName=''):
 iso95=array('d',[])
 non95=array('d',[])
 cur95=array('d',[])
 platIso=array('d',[])
 platNon=array('d',[])
 platCur=array('d',[])
 #loop through l1ptVal and make effi plots, find pT95
 for pt,color,ibin,nbin,cbin in zip(l1ptVal,colors,isoBin,nonBin,curBin):
  l1gPtCut = '(max(l1gPt,l1gRegionEt) > %i )' %pt
  l1PtCut = 'l1Pt>%i' %pt
  #cuts
  cutI=isoCut +'&&'+l1gPtCut+'&&l1gMatch'
  cutN=l1gPtCut+'&&l1gMatch'
  cutC=l1PtCut+'&&l1Match'
  #make turnons, find pT95  
  resultIso = make_turnon(tau_eff_ntuple,cutI,color,
   'pt%i_Iso'%pt,save=True,fix_plateau=isoPlateau,
   binning=ibin,extraName=extraName,pt=pt)
  resultNon = make_turnon(tau_eff_ntuple,cutN,color,
   'pt%i_Non'%pt,save=True,fix_plateau=nonPlateau,
   binning=nbin,extraName=extraName,pt=pt)
  resultCur = make_turnon(tau_eff_ntuple_cur,cutC,color,
   'pt%i_Cur'%pt,save=True,fix_plateau=curPlateau,
   binning=cbin,extraName=extraName,pt=pt)
  #array of pT95s
  iso95.append(resultIso[2])
  non95.append(resultNon[2])
  cur95.append(resultCur[2])
  platIso.append(resultIso[3])
  platNon.append(resultNon[3])
  platCur.append(resultCur[3])
  if FixPlat is True:
   if isoPlateau is None:
    isoPlateau=resultIso[1].GetParameter(0)
   if nonPlateau is None:
    nonPlateau=resultNon[1].GetParameter(0)
 return iso95,non95,cur95,platIso,platNon,platCur

def makeMod(m=3,arr=array('d',[5])):
 ar=array('d',[])
 for i in arr:
  x=i + (m - i%m)
  ar.append(x)
 return ar

def makeBins(bmin=0,bmax=rangeMax,lowStep=5,hiStep=10,arr=array('d',[5])):
 binArr=[]
 for x in arr:
  theMax=int(bmax+(hiStep-(bmax-x)%hiStep))
  bins = array('d',range(bmin,int(x)-1,lowStep)+range(int(x),theMax,hiStep))
  binArr.append(bins)
 return binArr
#
if VarBins:
 #1st iteration with even bin size
 iso95a,non95a,cur95a,platIsoA,platNonA,platCurA=find_pt95()
 #intermediate step to make sure bins stay integer when floating
 iso95aMod=makeMod(5,iso95a)
 non95aMod=makeMod(5,non95a)
 cur95aMod=makeMod(5,cur95a)
 #make steps=5 upto pt95, steps=10 above
 binIso=makeBins(arr=iso95a)
 binNon=makeBins(arr=non95a)
 binCur=makeBins(arr=cur95a)
 #use new binning to find pt95 (current uses fixed bins)
 iso95,non95,cur95,platIso,platNon,platCur=find_pt95(isoBin=binIso,nonBin=binNon,extraName='2')
 log.write('L1 pT|iso pT%i 1|iso pT%i 2|non pT%i 1|non pT%i 2|cur pT%i 1|cur pT%i 2|\n'%(100*thresh,100*thresh,100*thresh,100*thresh,100*thresh,100*thresh))
 for l1pt,i95a,i95b,n95a,n95b,c95a,c95b in zip(l1ptVal,iso95a,iso95,non95a,non95,cur95a,cur95):
  log.write('%i   |%i        |%i        |%i        |%i        |%i        |%i        |\n'%(l1pt,i95a,i95b,n95a,n95b,c95a,c95b))
#
if not VarBins:
 iso95,non95,cur95,platIso,platNon,platCur=find_pt95()
 log.write('L1 pT|iso pT%i|non pT%i|cur pT%i|\n'%(100*thresh,100*thresh,100*thresh))
 for l1pt,i95a,n95a,c95a in zip(l1ptVal,iso95,non95,cur95):
  log.write('%i   |%i      |%i      |%i      |\n'%(l1pt,i95a,n95a,c95a))

def goodBins(ptvals,pt95s):
 listPt=array('d',[])
 list95=array('d',[])
 for l1pt,pt95 in zip(ptvals,pt95s):
  if pt95 > 0:
   listPt.append(l1pt)
   list95.append(pt95)
 return listPt,list95

isoPts,iso95s=goodBins(l1ptVal,iso95)
nonPts,non95s=goodBins(l1ptVal,non95)
curPts,cur95s=goodBins(l1ptVal,cur95)

avgPlatIso=0
avgPlatNon=0
avgPlatCur=0
for p in platIso:
 avgPlatIso+=p
avgPIso=avgPlatIso/float(len(platIso))
print('Iso:')
print(avgPIso)
for q in platNon:
 avgPlatNon+=q
avgPNon=avgPlatNon/float(len(platNon))
print('Non:')
print(avgPNon)
for r in platCur:
 avgPlatCur+=r
avgPCur=avgPlatCur/float(len(platCur))
print('Cur:')
print(avgPCur)

# Drawing Final fits.png
nrIsoPts=len(isoPts)
nrNonPts=len(nonPts)
nrCurPts=len(curPts)
xmin=min(min(isoPts),min(nonPts),min(curPts))-5
xmax=max(max(isoPts),max(nonPts),max(curPts))+10
ymin=min(min(iso95s),min(non95s),min(cur95s))-5
ymax=max(max(iso95s),max(non95s),max(cur95s))+5
uIColor=ROOT.EColor.kBlue
uNColor=ROOT.EColor.kGreen+3
cColor=ROOT.EColor.kRed
uIMarker=21
uNMarker=20
cMarker=22
uISize=1.5
uNSize=1.5
cSize=1.5

lineFit = ROOT.TF1('lineFit'+str(random.randint(0, 1000)),
   "[0]*x+[1]", 0, rangeMax)
lineFit.SetParName(0,'m')
lineFit.SetParName(1,'b')

can = ROOT.TCanvas('can','can',800,800)
can.SetLogy(False)
frame = TH1F('frame','',1,xmin,xmax)
frame.SetMinimum(ymin)
frame.SetMaximum(ymax)
frame.SetStats(False)
frame.GetXaxis().SetTitle('L1 Cut')
if AbsEff: frame.GetYaxis().SetTitle('Abs Reco pT%i'%(100*absThresh))
else: frame.GetYaxis().SetTitle('(RECO) pT%i'%(100*thresh))
frame.SetTitle('')
frame.Draw()

log.write('\n\nResult of Fits:\n\n')
uIgraph=ROOT.TGraph(nrIsoPts,isoPts,iso95s)
uIgraph.SetMarkerColor(uIColor)
uIgraph.SetMarkerStyle(uIMarker)
uIgraph.SetMarkerSize(uISize)
lineFit.SetLineColor(uIColor)
uIgraph.Fit(lineFit)
uIgraph.Draw('P')
if AbsEff:
 #tex.DrawLatex(0.5,0.3,'UCT Iso: Abs pT%i = %0.01f L1 + %0.1f'
 #  %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.5,'UCT Iso: Abs pT%i = %0.01f L1 + %0.1f'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('UCT Iso: Abs pT%i = %0.01f L1 + %0.1f\n'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
else:
 #tex.DrawLatex(0.5,0.3,'UCT Iso: pT%i = %0.01f L1 + %0.1f'
 #  %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.5,'UCT Iso: pT%i = %0.01f L1 + %0.1f'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('UCT Iso: pT%i = %0.01f L1 + %0.1f\n'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))

uNgraph=ROOT.TGraph(nrNonPts,nonPts,non95s)
uNgraph.SetMarkerColor(uNColor)
uNgraph.SetMarkerStyle(uNMarker)
uNgraph.SetMarkerSize(uNSize)
lineFit.SetLineColor(uNColor)
uNgraph.Fit(lineFit)
uNgraph.Draw('P')
if AbsEff:
 #tex.DrawLatex(0.5,0.25,'UCT NonIso: Abs pT%i = %0.01f L1 + %0.1f'
 #  %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.45,'UCT NonIso: Abs pT%i = %0.01f L1 + %0.1f'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('UCT NonIso: Abs pT%i = %0.01f L1 + %0.1f\n'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
else:
 #tex.DrawLatex(0.5,0.25,'UCT NonIso: pT%i = %0.01f L1 + %0.1f'
 #  %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.45,'UCT NonIso: pT%i = %0.01f L1 + %0.1f'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('UCT NonIso: pT%i = %0.01f L1 + %0.1f\n'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 uNgraph.Draw('P')
 uNgraph.Draw('P')

cgraph=ROOT.TGraph(nrCurPts,curPts,cur95s)
cgraph.SetMarkerColor(cColor)
cgraph.SetMarkerStyle(cMarker)
cgraph.SetMarkerSize(cSize)
lineFit.SetLineColor(cColor)
cgraph.Fit(lineFit)
cgraph.Draw('P')
if AbsEff:
 #tex.DrawLatex(0.5,0.2,'Current: Abs pT%i = %0.01f L1 + %0.1f'
 #  %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.4,'Current: Abs pT%i = %0.01f L1 + %0.1f'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('Current: Abs pT%i = %0.01f L1 + %0.1f'
   %(100*absThresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
else:
 #tex.DrawLatex(0.5,0.2,'Current: pT%i = %0.01f L1 + %0.1f'
 #  %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 tex.DrawLatex(0.5,0.4,'Current: pT%i = %0.01f L1 + %0.1f'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
 log.write('Current: pT%i = %0.01f L1 + %0.1f'
   %(100*thresh,lineFit.GetParameter(0),lineFit.GetParameter(1)))
cgraph.Draw('P')

legend = ROOT.TLegend(0.11,0.5,0.4,0.89,'','brNDC')
legend.SetFillColor(ROOT.EColor.kWhite)
legend.SetBorderSize(0)
legend.AddEntry(uIgraph,'UCT Iso','P')
legend.AddEntry(uNgraph,'UCT NonIso','P')
legend.AddEntry(cgraph,'Current','P')
legend.Draw()

save=raw_input('press enter to finish, type save to save\n')
if save=='save':
 can.SaveAs(saveWhere+'fits.png')
