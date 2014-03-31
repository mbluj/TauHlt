/*
 * =====================================================================================
 *
 *       Filename:  PFSumET.cc
 *
 *    Description:  Compute total SumET and SumHt from PF objects
 *
 *         Author:  Evan Friis, evan.friis@cern.ch
 *        Company:  UW Madison
 *
 * =====================================================================================
 */

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "DataFormats/Candidate/interface/LeafCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"

class PFSumET : public edm::EDProducer {
  public:
    typedef std::vector<reco::LeafCandidate> LeafCandidateCollection;
    PFSumET(const edm::ParameterSet& pset);
    virtual ~PFSumET(){}
    void produce(edm::Event& evt, const edm::EventSetup& es);
  private:
    edm::InputTag src_;
    double maxEta_;
    double minForHt_;
    bool excludeMuons_;
};

PFSumET::PFSumET(const edm::ParameterSet& pset) {
  src_ = pset.getParameter<edm::InputTag>("src");
  maxEta_ = pset.getParameter<double>("maxEta");
  minForHt_ = pset.getParameter<double>("minForHt");
  excludeMuons_ = pset.getParameter<bool>("excludeMuons");

  produces<LeafCandidateCollection>("set");
  produces<LeafCandidateCollection>("sht");
  produces<LeafCandidateCollection>("mht");

}
void PFSumET::produce(edm::Event& evt, const edm::EventSetup& es) {

  edm::Handle<reco::PFCandidateCollection> pfcands;
  evt.getByLabel(src_, pfcands);

  double sumET = 0;
  double sumHT = 0;

  double sumET_x = 0;
  double sumHT_x = 0;

  double sumET_y = 0;
  double sumHT_y = 0;

  for (size_t i = 0; i < pfcands->size(); ++i) {
    const reco::PFCandidate& pfcand = pfcands->at(i);
    if (std::abs(pfcand.eta()) > maxEta_)
      continue;
    if (std::abs(pfcand.pdgId() == 13) && excludeMuons_)
      continue;
    sumET_x += pfcand.px();
    sumET_y += pfcand.py();
    sumET += pfcand.pt();

    if (pfcand.et() > minForHt_){
      sumHT_x += pfcand.px();
      sumHT_y += pfcand.py();
      sumHT += pfcand.pt();
      }   
  }

  double mHT=sqrt(sumHT_x*sumHT_x+sumHT_y*sumHT_y);

  std::auto_ptr<LeafCandidateCollection> set(new LeafCandidateCollection);
  set->push_back(reco::LeafCandidate(0, reco::Candidate::PolarLorentzVector(sumET,0,0,0)));
  evt.put(set, "set");

  std::auto_ptr<LeafCandidateCollection> sht(new LeafCandidateCollection);
  sht->push_back(reco::LeafCandidate(0, reco::Candidate::PolarLorentzVector(sumHT,0,0,0)));
  evt.put(sht, "sht");

  std::auto_ptr<LeafCandidateCollection> mht(new LeafCandidateCollection);
  mht->push_back(reco::LeafCandidate(0, reco::Candidate::PolarLorentzVector(mHT,0,0,0)));   // we could also add phi
  evt.put(mht, "mht");



}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(PFSumET);
