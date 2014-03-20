#flake8: noqa
'''

Emulate the L1 and UCT upgrade primitives, and put them in the event.

Authors: Isobel Ojalvo, Sridhara Dasu (kludger)

'''

import FWCore.ParameterSet.Config as cms


from Configuration.StandardSequences.RawToDigi_Data_cff import *
from L1Trigger.UCT2015.Lut import *
from L1Trigger.UCT2015.regionSF_cfi import *


# Modify the HCAL TPGs according to the proposed HTR modification.  If the HCAL
# is above a given energy threshold, set the MIP bit.
hackHCALMIPs = cms.EDProducer(
    "HcalTpgMipEmbedder",
    src = cms.InputTag("hcalDigis"),
    threshold = cms.double(3), # In GeV
    rawThreshold = cms.uint32(3), # In TPG rank
    cutOnRawBits = cms.bool(False), # What to cut on
)

uctDigis = cms.EDProducer(
    "L1RCTProducer",
    #hcalDigis = cms.VInputTag(cms.InputTag("hcalDigis")),
    hcalDigis = cms.VInputTag(cms.InputTag("hackHCALMIPs")),
    useEcal = cms.bool(True),
    useHcal = cms.bool(True),
    ecalDigis = cms.VInputTag(cms.InputTag("ecalDigis:EcalTriggerPrimitives")),
    BunchCrossings = cms.vint32(0),
    getFedsFromOmds = cms.bool(False),
    queryDelayInLS = cms.uint32(10),
    queryIntervalInLS = cms.uint32(100)#,
)

CorrectedDigis = cms.EDProducer(
    "RegionCorrection",
    puMultCorrect = cms.bool(True),
    regionLSB = RCTConfigProducers.jetMETLSB,
    egammaLSB = cms.double(1.0), # This has to correspond with the value from L1CaloEmThresholds
    regionSF = regionSF,
    regionSubtraction = regionSubtraction
)


UCT2015Producer = cms.EDProducer(
    "UCT2015Producer",
    puCorrect = cms.bool(False), #regions corrected instead
    puMultCorrect = cms.bool(True), #Change this one for producer
    puCorrectSums = cms.bool(False), # regions corrected instead
    useUICrho = cms.bool(True),
    useHI = cms.bool(False),
    # All of these uint32 thresholds are in GeV.
    puETMax = cms.uint32(7),
    regionETCutForHT = cms.uint32(7),
    regionETCutForMET = cms.uint32(0),
    minGctEtaForSums = cms.uint32(4),
    maxGctEtaForSums = cms.uint32(17),
    jetSeed = cms.uint32(10),
    tauSeed = cms.uint32(7),
    egtSeed = cms.uint32(2),
    relativeTauIsolationCut = cms.double(1.),
    relativeJetIsolationCut = cms.double(1.),
    switchOffTauIso= cms.double(60),
    egammaLSB = cms.double(1.0), # This has to correspond with the value from L1CaloEmThresholds
    regionLSB = RCTConfigProducers.jetMETLSB,
)

uctDigiStep = cms.Sequence(
    # Only do the digitization of objects that we care about
    #RawToDigi
    gctDigis
    * gtDigis
    * ecalDigis
    * hcalDigis
)

uctEmulatorStep = cms.Sequence(
    hackHCALMIPs
    # Now make UCT and L1 objects
    * uctDigis
    * CorrectedDigis 
)

emulationSequence = cms.Sequence(uctDigiStep * uctEmulatorStep)
