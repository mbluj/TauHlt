'''

Script to make some quick rate plots

Author: Nate Woods, adapted from Evan K. Friis, UW Madison

'''

import ROOT

# So things don't look like crap.
ROOT.gROOT.SetStyle("Plain")
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
#ntuple_file = ROOT.TFile("../submission/PU/uct_rates_eic7.root")
#ntuple_file = ROOT.TFile("../data/LSB50/uct_rates_eic7.root")
#ntuple_file = ROOT.TFile("../data/LSB50/uct_rates_eic3.root")
ntuple_file = ROOT.TFile("../data/March_22_MC/uct_rates_eic3.root")
ntuplemc_file = ROOT.TFile("../data/March_22_MC/mc_rates.root")
#ntuple_file = ROOT.TFile("marias/RATES_TUESDAYMORNING_MIP3_h0p5_e2.root")
#ntuple_file = ROOT.TFile("/scratch/efriis/uct_rates_eic3.root")

#sums_l1_ntuple = ntuple_file.Get("sumsL1Rates/Ntuple")
#sums_uct_ntuple = ntuple_file.Get("sumsUCTRates/Ntuple")
sums_uct_ntuple = ntuple_file.Get("corrjetUCTRate/Ntuple")
sums_l1_ntuple = ntuple_file.Get("jetL1Rate/Ntuple")
sums_mc_ntuple = ntuplemc_file.Get("corrjetUCTRate/Ntuple")

canvas = ROOT.TCanvas("asdf", "adsf", 800, 800)
ZEROBIAS_RATE=15000000.00

def make_plot(tree, variable, selection, binning, xaxis='', title='', calFactor=1):
    ''' Plot a variable using draw and return the histogram '''
    #draw_string = "MaxIf$(%s * %0.2f, %s)>>htemp(%s)" % (variable, calFactor, selection, ", ".join(str(x) for x in binning))
    draw_string = "%s * %0.2f>>htemp(%s)" % (variable, calFactor, ", ".join(str(x) for x in binning))
    print draw_string
    print tree
    #tree.Draw(draw_string, "", "goff")
    tree.Draw(draw_string, selection, "goff")
    output_histo = ROOT.gDirectory.Get("htemp").Clone()
    output_histo.GetXaxis().SetTitle(xaxis)
    output_histo.SetTitle(title)
    return output_histo

def make_l1_rate(pt):
    ''' Make a rate plot out of L1Extra Pts '''
    numBins = pt.GetNbinsX()
    rate = pt.Clone()

    for i in range(numBins):
        rate.SetBinContent(i+1, pt.Integral(i+1, numBins))

    rate.SetLineColor(ROOT.EColor.kRed)
    rate.SetMarkerStyle(25)
    rate.SetMarkerColor(ROOT.EColor.kRed)

    return rate

def make_l1g_rate(pt):
    ''' Return a rate plot out of L1Extra Pts '''
    numBins = pt.GetNbinsX()
    rate = pt.Clone()

    for i in range(1,numBins+1):
        rate.SetBinContent(i, pt.Integral(i, numBins))

    rate.SetLineColor(ROOT.EColor.kBlue)
    rate.SetMarkerStyle(22)
    rate.SetMarkerColor(ROOT.EColor.kBlue)

    return rate



def plotRates(l1Ntuple, l1gNtuple, l1gMCNtuple, binning,
              l1Variable='', l1gVariable='',
              filename='', title='', xaxis='',
              l1Cut = '', l1gCut = '',
              showL1=True, showMC=True, l1gLabel='UCT', l1gColor=ROOT.EColor.kBlack,
              l1gStyle = 22
             ):
    ''' Save a rate Plot '''
#    scale = ZEROBIAS_RATE/l1Ntuple.GetEntries()
#    scaleg = ZEROBIAS_RATE/l1gNtuple.GetEntries()
#    scaleMC = ZEROBIAS_RATE/l1gMCNtuple.GetEntries()
	
    l1_pt = make_plot(
        l1Ntuple, l1Variable,
        l1Cut,
        binning,
        '','', # Don't bother with titles
        )
    l1g_pt = make_plot(
        l1gNtuple, l1gVariable,
        l1gCut,
        binning,
        '','', # Don't bother with titles
        )
    l1g_MC = make_plot(
	l1gMCNtuple, l1gVariable,
	l1gCut,
	binning,
	'','',
	)
    l1Rate = make_l1_rate(l1_pt)
    l1gRate = make_l1g_rate(l1g_pt)
    l1gMCRate = make_l1g_rate(l1g_MC)
 #   l1Rate.Scale(scale)
 #   l1gRate.Scale(scaleg)
 #   l1gMCRate.Scale(scaleMC)
    l1gRate.SetLineColor(l1gColor)
    l1gRate.SetMarkerStyle(l1gStyle)
    l1gRate.SetMarkerColor(l1gColor)

  #  l1gRate.SetMaximum(l1Rate.GetMaximum()*20)
  #  l1gRate.SetMinimum(
#            l1Rate.GetBinContent(l1Rate.FindBin(200))
#	10
#    )

    canvas.SetLogy()
    l1gRate.SetTitle(title)
    l1gRate.GetXaxis().SetTitle(xaxis)
    l1gRate.GetYaxis().SetTitle("Rate Events")
    l1gRate.GetYaxis().SetTitleOffset(1.29)
    l1gRate.Draw('ph')
    if showL1:
        l1Rate.Draw('phsame')
    if showMC:
  	l1gMCRate.SetLineColor(ROOT.EColor.kRed)
	l1gMCRate.Draw('phsame')
    legend = ROOT.TLegend(0.3, 0.89, 0.89, 0.7, "", "brNDC")
    legend.SetFillColor(ROOT.EColor.kWhite)
    legend.SetBorderSize(1)
    legend.AddEntry(l1gRate, l1gLabel, "p")
    if showL1:
        legend.AddEntry(l1Rate, "Current", "p")
    if showMC:
	legend.AddEntry(l1gMCRate, "MC","p")
    legend.Draw()
    print 'rate at 72:'
    binn = l1gRate.GetXaxis().FindBin(72)
    rateVal = l1gRate.GetBinContent(binn)
    print rateVal
    print 'MC rate at 72:'
    binn = l1gMCRate.GetXaxis().FindBin(72)
    rateVal = l1gMCRate.GetBinContent(binn)
    print rateVal
    print 'rate at 84:'
    binn = l1gRate.GetXaxis().FindBin(84)
    rateVal = l1gRate.GetBinContent(binn)
    print rateVal
    print 'MC rate at 84:'
    binn = l1gMCRate.GetXaxis().FindBin(84)
    rateVal = l1gMCRate.GetBinContent(binn)
    print rateVal
    canvas.SaveAs(filename+".png")

###############################################################################
# Draw Rates                                                                  #
###############################################################################

#plotRates(sums_l1_ntuple, sums_uct_ntuple,
#          [39, 5, 200],
#          '2*l1MET',
#          'l1MET',
#          'met_rate_cmp',
#          "MET Rate", " ME_{T} Threshold (GeV)",
#          l1gLabel="",
#          l1gColor = ROOT.EColor.kBlue,
#          l1gStyle = 20,
#          l1gCut = "",
#          l1Cut = "",
#          showL1 = True,
#         )

#plotRates(sums_l1_ntuple, sums_uct_ntuple,
#          [39, 5, 200],
#          'l1MHT',
#          'l1MHT',
#          #'0.5*l1MHT', # fixed
#          'mht_rate_cmp',
#          "MHT Rate", " MH_{T} Threshold (GeV)",
#          l1gLabel="",
#          l1gColor = ROOT.EColor.kBlue,
#          l1gStyle = 20,
#          l1gCut = "",
#          l1Cut = "",
#          showL1 = True,
#         )
plotRates(sums_l1_ntuple, sums_uct_ntuple, sums_mc_ntuple,
          [39, 5, 200],
          'pt',
          'pt',
          #'0.5*l1MHT', # fixed
          'Jet_Rate',
          "Jet Rate", " P_{t} Threshold (GeV)",
          l1gLabel="",
          l1gColor = ROOT.EColor.kBlue,
          l1gStyle = 20,
          l1gCut = "",
          l1Cut = "",
          showL1 = False,
          showMC = True
         )

