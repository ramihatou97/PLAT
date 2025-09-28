#!/usr/bin/env python3
"""
Initialize the PLAT system with sample neurosurgical concepts.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime
import asyncio
import logging

from plat.models.base import Base, engine, SessionLocal
from plat.models.content import Concept, ContentType, Tag, concept_tags
from plat.services.search_service import search_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample neurosurgical concepts
SAMPLE_CONCEPTS = [
    {
        "title": "Craniotomy",
        "description": "Surgical procedure involving the temporary removal of a bone flap from the skull to access the brain",
        "content": """A craniotomy is a surgical procedure in which a portion of the skull is removed to access the brain. This procedure is commonly used for:

1. **Brain tumor removal**: Accessing and resecting primary or metastatic brain tumors
2. **Aneurysm clipping**: Treating cerebral aneurysms by placing clips across the neck
3. **AVM resection**: Removing arteriovenous malformations
4. **Hematoma evacuation**: Draining intracranial hematomas
5. **Biopsy procedures**: Obtaining tissue samples for diagnosis

**Surgical Technique:**
- Patient positioning depends on the target location
- Scalp incision and reflection
- Bone flap creation using craniotome or drill
- Dural opening to expose brain tissue
- Specific procedure performance
- Dural closure and bone flap replacement

**Complications:**
- Infection
- Bleeding
- Neurological deficits
- Seizures
- CSF leak

**Post-operative care** includes neurological monitoring, pain management, and gradual mobilization.""",
        "content_type": ContentType.SURGICAL_TECHNIQUE,
        "category": "General Neurosurgery",
        "subcategory": "Access Procedures",
        "confidence_score": 0.95,
        "evidence_level": "I",
        "peer_reviewed": True
    },
    {
        "title": "Deep Brain Stimulation (DBS)",
        "description": "Neurosurgical procedure involving implantation of electrodes for therapeutic electrical stimulation",
        "content": """Deep Brain Stimulation (DBS) is a neurosurgical treatment involving the implantation of a neurostimulator that sends electrical impulses to specific brain regions.

**Indications:**
- Parkinson's disease (refractory to medical therapy)
- Essential tremor
- Dystonia
- Obsessive-compulsive disorder (OCD)
- Epilepsy (under investigation)

**Target Locations:**
- **Subthalamic nucleus (STN)**: Primary target for Parkinson's disease
- **Globus pallidus internus (GPi)**: Alternative target for PD, primary for dystonia
- **Ventral intermediate nucleus (VIM)**: Primary target for essential tremor
- **Anterior limb of internal capsule**: Target for OCD

**Surgical Procedure:**
1. Pre-operative imaging (MRI, DTI)
2. Stereotactic frame placement
3. Target localization using coordinates
4. Microelectrode recording (optional)
5. Test stimulation
6. Permanent electrode implantation
7. IPG (Internal Pulse Generator) implantation

**Programming and Follow-up:**
- Initial programming 2-4 weeks post-surgery
- Regular adjustments of parameters
- Battery replacement every 3-7 years

**Complications:**
- Hardware-related: lead fracture, IPG malfunction
- Surgical: hemorrhage, infection
- Stimulation-related: speech/balance issues, mood changes""",
        "content_type": ContentType.SURGICAL_TECHNIQUE,
        "category": "Functional Neurosurgery",
        "subcategory": "Movement Disorders",
        "confidence_score": 0.92,
        "evidence_level": "I",
        "peer_reviewed": True
    },
    {
        "title": "Glioblastoma Multiforme (GBM)",
        "description": "Most aggressive primary brain tumor with poor prognosis",
        "content": """Glioblastoma Multiforme (GBM) is the most common and aggressive primary brain tumor in adults, classified as WHO Grade IV.

**Epidemiology:**
- Peak incidence: 45-70 years
- Male predominance (1.6:1)
- Incidence: 3-5 per 100,000 population
- Median survival: 12-15 months

**Pathophysiology:**
- Originates from astrocytes
- Highly infiltrative growth pattern
- Significant neovascularization
- Central necrosis with pseudopalisading
- Blood-brain barrier disruption

**Clinical Presentation:**
- Progressive neurological deficits
- Seizures (30-50% of patients)
- Headaches
- Cognitive changes
- Increased intracranial pressure symptoms

**Diagnostic Workup:**
- MRI with gadolinium (gold standard)
- Perfusion and diffusion studies
- PET scan (optional)
- Biopsy or resection for tissue diagnosis

**Treatment Protocol (Stupp Protocol):**
1. **Maximal safe resection**
   - Gross total resection when feasible
   - Use of intraoperative navigation
   - Awake craniotomy for eloquent areas
   
2. **Adjuvant therapy**
   - Concurrent chemoradiation (temozolomide + RT)
   - 6 cycles of adjuvant temozolomide

**Molecular Markers:**
- MGMT promoter methylation (favorable prognostic factor)
- IDH mutations (rare in primary GBM)
- EGFR amplification
- p53 mutations

**Prognosis:**
- Extent of resection impacts survival
- Age is strongest prognostic factor
- MGMT methylation status affects treatment response
- 5-year survival: <10%""",
        "content_type": ContentType.CONCEPT,
        "category": "Brain Tumors",
        "subcategory": "Primary Malignant",
        "confidence_score": 0.97,
        "evidence_level": "I",
        "peer_reviewed": True
    },
    {
        "title": "Anterior Cervical Discectomy and Fusion (ACDF)",
        "description": "Surgical procedure for cervical disc disease involving disc removal and spinal fusion",
        "content": """Anterior Cervical Discectomy and Fusion (ACDF) is a surgical procedure used to treat cervical disc disease, stenosis, and instability.

**Indications:**
- Cervical radiculopathy refractory to conservative treatment
- Cervical myelopathy
- Traumatic disc herniation
- Degenerative disc disease with instability

**Surgical Technique:**
1. **Patient positioning**: Supine with neck extension
2. **Approach**: Right-sided anterior cervical approach
3. **Exposure**: 
   - Skin incision along natural skin crease
   - Dissection between carotid sheath and trachea
   - Longus colli muscle elevation
4. **Discectomy**:
   - Disc removal with rongeurs and curettes
   - Posterior longitudinal ligament removal
   - Neural decompression
5. **Fusion**:
   - Endplate preparation
   - Graft insertion (cage, allograft, or autograft)
   - Plate fixation (optional)

**Graft Options:**
- **Autograft**: Iliac crest (gold standard, higher morbidity)
- **Allograft**: Cadaveric bone (lower morbidity, slower fusion)
- **Cages**: PEEK or titanium with bone graft
- **Artificial discs**: Motion-preserving alternative

**Post-operative Care:**
- Cervical collar (optional, varies by surgeon)
- Early mobilization
- Fusion assessment at 3, 6, 12 months
- Return to work: 6-12 weeks

**Complications:**
- Dysphagia (temporary in 10-15%)
- Recurrent laryngeal nerve injury (<1%)
- Esophageal perforation (<1%)
- Pseudoarthrosis (5-10%)
- Adjacent segment disease (long-term)

**Outcomes:**
- Success rate: 90-95% for radiculopathy
- Fusion rate: >95% for single level
- Patient satisfaction: High for appropriately selected cases""",
        "content_type": ContentType.SURGICAL_TECHNIQUE,
        "category": "Spinal Surgery",
        "subcategory": "Cervical Spine",
        "confidence_score": 0.94,
        "evidence_level": "I",
        "peer_reviewed": True
    },
    {
        "title": "Intracranial Pressure (ICP) Monitoring",
        "description": "Clinical protocol for monitoring and managing elevated intracranial pressure",
        "content": """Intracranial Pressure (ICP) monitoring is crucial for managing patients with various neurological conditions that may cause increased ICP.

**Normal Values:**
- Adults: 5-15 mmHg
- Children: 3-7 mmHg
- Infants: 1.5-6 mmHg

**Indications for ICP Monitoring:**
- Severe traumatic brain injury (GCS ≤8)
- Intracerebral hemorrhage with mass effect
- Large cerebral infarctions
- Post-operative neurosurgical patients
- Hydrocephalus management

**Monitoring Methods:**
1. **Intraventricular catheter** (gold standard)
   - Most accurate
   - Allows CSF drainage
   - Higher infection risk
   
2. **Intraparenchymal monitors**
   - Fiber-optic or strain gauge
   - Lower infection risk
   - Cannot drain CSF
   
3. **Subdural/epidural monitors**
   - Less accurate
   - Rarely used

**ICP Management Protocol:**
**Tier 1 (ICP >20 mmHg):**
- Head of bed elevation (30 degrees)
- Adequate sedation and analgesia
- Maintain normothermia
- Optimize ventilation (avoid hypercapnia)
- Maintain euvolemia
- Avoid hypotension (SBP >90 mmHg)

**Tier 2 (Refractory ICP):**
- Hyperosmolar therapy:
  - Mannitol 0.25-1 g/kg IV
  - Hypertonic saline (3% or 23.4%)
- Mild hyperventilation (PaCO2 30-35 mmHg)
- CSF drainage (if ventriculostomy present)

**Tier 3 (Last resort):**
- Barbiturate coma
- Decompressive craniectomy
- Hypothermia

**Cerebral Perfusion Pressure (CPP):**
- CPP = MAP - ICP
- Target CPP: 60-70 mmHg (adults)
- Maintain with vasopressors if needed

**Complications of Monitoring:**
- Infection (1-5%)
- Hemorrhage (<1%)
- Malposition
- Technical failures

**Weaning ICP Monitoring:**
- When ICP consistently <20 mmHg
- Neurological improvement
- Reduced need for interventions""",
        "content_type": ContentType.PROTOCOL,
        "category": "Trauma",
        "subcategory": "Critical Care",
        "confidence_score": 0.96,
        "evidence_level": "I",
        "peer_reviewed": True
    }
]

SAMPLE_TAGS = [
    {"name": "Brain Tumor", "description": "Related to brain neoplasms", "color": "#FF6B6B"},
    {"name": "Spinal Surgery", "description": "Spine-related procedures", "color": "#4ECDC4"},
    {"name": "Trauma", "description": "Traumatic brain and spinal injuries", "color": "#45B7D1"},
    {"name": "Functional", "description": "Functional neurosurgery procedures", "color": "#96CEB4"},
    {"name": "Critical Care", "description": "Neurocritical care protocols", "color": "#FFEAA7"},
    {"name": "Vascular", "description": "Cerebrovascular conditions", "color": "#DDA0DD"},
    {"name": "Pediatric", "description": "Pediatric neurosurgery", "color": "#98D8C8"},
    {"name": "Oncology", "description": "Neurosurgical oncology", "color": "#F7DC6F"},
]

async def create_database():
    """Create database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

async def create_sample_concepts():
    """Create sample neurosurgical concepts."""
    logger.info("Creating sample concepts...")
    
    db = SessionLocal()
    try:
        # Create tags first
        tags = []
        for tag_data in SAMPLE_TAGS:
            tag = Tag(**tag_data)
            db.add(tag)
            tags.append(tag)
        
        db.commit()
        logger.info(f"Created {len(tags)} tags")
        
        # Create concepts
        concepts = []
        for concept_data in SAMPLE_CONCEPTS:
            concept = Concept(**concept_data)
            db.add(concept)
            concepts.append(concept)
        
        db.commit()
        logger.info(f"Created {len(concepts)} concepts")
        
        # Add concepts to search index
        for concept in concepts:
            await search_service.add_concept(concept)
        
        logger.info("Added concepts to search index")
        
        return concepts
        
    except Exception as e:
        logger.error(f"Error creating sample concepts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def main():
    """Main initialization function."""
    logger.info("Initializing PLAT system...")
    
    try:
        # Create database
        await create_database()
        
        # Create sample data
        concepts = await create_sample_concepts()
        
        # Get search statistics
        stats = await search_service.get_search_statistics()
        logger.info(f"Search index statistics: {stats}")
        
        logger.info("PLAT system initialization completed successfully!")
        logger.info(f"Created {len(concepts)} neurosurgical concepts")
        logger.info("The system is ready to use.")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())