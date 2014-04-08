// -*- C++ -*-
//
// Package:    RecoPixelVertexing/PixelVertexFinding
// Class:      PixelVertexCollectionTrimmer
// 
/**\class PixelVertexCollectionTrimmer PixelVertexCollectionTrimmer.cc RecoPixelVertexing/PixelVertexFinding/src/PixelVertexCollectionTrimmer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Riccardo Manzoni
//         Created:  Tue, 01 Apr 2014 10:11:16 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "RecoPixelVertexing/PixelVertexFinding/interface/PVClusterComparer.h"

class PixelVertexCollectionTrimmer : public edm::EDProducer {
   public:
      explicit PixelVertexCollectionTrimmer(const edm::ParameterSet&);
      ~PixelVertexCollectionTrimmer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() override;
      virtual void produce(edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      edm::InputTag src_            ;            
      int           maxVtx_         ;         
      double        fractionSumPt2_ ;
      double        minSumPt2_      ;

};

PixelVertexCollectionTrimmer::PixelVertexCollectionTrimmer(const edm::ParameterSet& iConfig)
{
  src_            = iConfig.getParameter<edm::InputTag>("src"            );
  maxVtx_         = iConfig.getParameter<int>          ("maxVtx"         );
  fractionSumPt2_ = iConfig.getParameter<double>       ("fractionSumPt2" );
  minSumPt2_      = iConfig.getParameter<double>       ("minSumPt2"      );

  produces<reco::VertexCollection>(); 
}

PixelVertexCollectionTrimmer::~PixelVertexCollectionTrimmer()
{
}

// ------------ method called to produce the data  ------------
void
PixelVertexCollectionTrimmer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   
   Handle<reco::VertexCollection> vtxs;
   iEvent.getByLabel(src_,vtxs);

   std::auto_ptr<reco::VertexCollection> vtxs_trim(new reco::VertexCollection);

   double sumpt2                ;
   //double sumpt2previous = -99. ;
   int    counter        = 0    ;
   PVClusterComparer PVCluster  ;  

// this is not the logic we want, at least for now
// if requires the sumpt2 for vtx_n to be > threshold * sumpt2 vtx_n-1
//    for (reco::VertexCollection::const_iterator vtx = vtxs->begin(); vtx != vtxs->end(); ++vtx, ++counter){
//      if (counter > maxVtx_) break ;
//      sumpt2 = PVCluster.pTSquaredSum(*vtx) ;
//      if (sumpt2 > sumpt2previous*fractionSumPt2_ && sumpt2 > minSumPt2_ ) vtxs_trim->push_back(*vtx) ; 
//      else if (counter == 0 )                                              vtxs_trim->push_back(*vtx) ;
//      sumpt2previous = sumpt2 ;
//    }

   double sumpt2first = PVCluster.pTSquaredSum(*(vtxs->begin())) ;

   for (reco::VertexCollection::const_iterator vtx = vtxs->begin(); vtx != vtxs->end(); ++vtx, ++counter){
     if (counter > maxVtx_) break ;
     sumpt2 = PVCluster.pTSquaredSum(*vtx) ;
     if (sumpt2 >= sumpt2first*fractionSumPt2_ && sumpt2 > minSumPt2_ ) vtxs_trim->push_back(*vtx) ; 
   }
      
   iEvent.put(vtxs_trim);
    
}

// ------------ method called once each job just before starting event loop  ------------
void 
PixelVertexCollectionTrimmer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PixelVertexCollectionTrimmer::endJob() {
}
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PixelVertexCollectionTrimmer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PixelVertexCollectionTrimmer);
