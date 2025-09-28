"""PubMed integration service for fetching latest neurosurgical research."""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

import requests
from Bio import Entrez
import aiohttp

from ..core.config import settings
from ..models.content import ContentSource, ContentType

logger = logging.getLogger(__name__)


class PubMedService:
    """Service for interacting with PubMed API and fetching research papers."""
    
    def __init__(self):
        if settings.pubmed_email:
            Entrez.email = settings.pubmed_email
        if settings.pubmed_api_key:
            Entrez.api_key = settings.pubmed_api_key
        
        # Base URLs for PubMed API
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.search_url = f"{self.base_url}/esearch.fcgi"
        self.fetch_url = f"{self.base_url}/efetch.fcgi"
        self.summary_url = f"{self.base_url}/esummary.fcgi"
        
        # Neurosurgical search terms and concepts
        self.neurosurgical_terms = [
            "neurosurgery", "neurosurgical", "brain surgery", "craniotomy",
            "brain tumor", "glioma", "meningioma", "acoustic neuroma",
            "aneurysm", "arteriovenous malformation", "AVM",
            "deep brain stimulation", "DBS", "epilepsy surgery",
            "spinal fusion", "discectomy", "laminectomy",
            "hydrocephalus", "shunt", "cerebrospinal fluid",
            "traumatic brain injury", "TBI", "intracranial pressure",
            "stereotactic", "gamma knife", "radiosurgery",
            "pituitary adenoma", "transsphenoidal",
            "spine surgery", "spinal cord", "vertebroplasty"
        ]
    
    async def search_recent_papers(
        self, 
        query_terms: Optional[List[str]] = None,
        days_back: int = 30,
        max_results: int = 100
    ) -> List[Dict]:
        """Search for recent neurosurgical papers."""
        if not query_terms:
            query_terms = self.neurosurgical_terms[:10]  # Use first 10 terms
        
        # Build search query
        search_query = " OR ".join([f'"{term}"[Title/Abstract]' for term in query_terms])
        
        # Add date filter
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_filter = f"({start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[pdat])"
        
        full_query = f"({search_query}) AND {date_filter}"
        
        try:
            # Search for papers
            async with aiohttp.ClientSession() as session:
                search_params = {
                    "db": "pubmed",
                    "term": full_query,
                    "retmax": max_results,
                    "retmode": "xml",
                    "sort": "pub+date"
                }
                
                if settings.pubmed_api_key:
                    search_params["api_key"] = settings.pubmed_api_key
                
                async with session.get(self.search_url, params=search_params) as response:
                    search_results = await response.text()
                
                # Parse search results to get PMIDs
                pmids = self._parse_search_results(search_results)
                
                if not pmids:
                    logger.warning("No papers found in search")
                    return []
                
                # Fetch detailed information for each paper
                papers = await self._fetch_paper_details(pmids, session)
                return papers
                
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []
    
    def _parse_search_results(self, xml_content: str) -> List[str]:
        """Parse search results XML to extract PMIDs."""
        try:
            root = ET.fromstring(xml_content)
            pmids = []
            
            for id_elem in root.findall(".//Id"):
                pmids.append(id_elem.text)
            
            return pmids
        except Exception as e:
            logger.error(f"Failed to parse search results: {e}")
            return []
    
    async def _fetch_paper_details(
        self, 
        pmids: List[str], 
        session: aiohttp.ClientSession
    ) -> List[Dict]:
        """Fetch detailed information for papers by PMID."""
        if not pmids:
            return []
        
        try:
            # Batch fetch paper details
            pmid_str = ",".join(pmids)
            fetch_params = {
                "db": "pubmed",
                "id": pmid_str,
                "retmode": "xml",
                "rettype": "abstract"
            }
            
            if settings.pubmed_api_key:
                fetch_params["api_key"] = settings.pubmed_api_key
            
            async with session.get(self.fetch_url, params=fetch_params) as response:
                details_xml = await response.text()
            
            return self._parse_paper_details(details_xml)
            
        except Exception as e:
            logger.error(f"Failed to fetch paper details: {e}")
            return []
    
    def _parse_paper_details(self, xml_content: str) -> List[Dict]:
        """Parse paper details XML into structured data."""
        try:
            root = ET.fromstring(xml_content)
            papers = []
            
            for article in root.findall(".//PubmedArticle"):
                paper_data = self._extract_paper_data(article)
                if paper_data:
                    papers.append(paper_data)
            
            return papers
            
        except Exception as e:
            logger.error(f"Failed to parse paper details: {e}")
            return []
    
    def _extract_paper_data(self, article_elem) -> Optional[Dict]:
        """Extract paper data from XML element."""
        try:
            # Get PMID
            pmid_elem = article_elem.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else None
            
            # Get basic article info
            article_info = article_elem.find(".//Article")
            if article_info is None:
                return None
            
            # Extract title
            title_elem = article_info.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "No title"
            
            # Extract abstract
            abstract_elem = article_info.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else ""
            
            # Extract authors
            authors = []
            for author in article_info.findall(".//Author"):
                last_name = author.find("LastName")
                first_name = author.find("ForeName")
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
            
            # Extract journal info
            journal_elem = article_info.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "Unknown journal"
            
            # Extract publication date
            pub_date = self._extract_publication_date(article_info)
            
            # Extract DOI
            doi = None
            for article_id in article_elem.findall(".//ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi = article_id.text
                    break
            
            # Calculate confidence score based on various factors
            confidence_score = self._calculate_paper_confidence(
                title, abstract, journal, authors, pub_date
            )
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
                "doi": doi,
                "confidence_score": confidence_score,
                "source_type": ContentSource.PUBMED,
                "content_type": ContentType.CONCEPT,  # Default type
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None
            }
            
        except Exception as e:
            logger.error(f"Failed to extract paper data: {e}")
            return None
    
    def _extract_publication_date(self, article_info) -> Optional[datetime]:
        """Extract publication date from article info."""
        try:
            # Try different date fields
            date_fields = [
                ".//PubDate",
                ".//ArticleDate[@DateType='Electronic']",
                ".//PubMedPubDate[@PubStatus='pubmed']"
            ]
            
            for field in date_fields:
                date_elem = article_info.find(field)
                if date_elem is not None:
                    year = date_elem.find("Year")
                    month = date_elem.find("Month")
                    day = date_elem.find("Day")
                    
                    if year is not None:
                        try:
                            year_val = int(year.text)
                            month_val = int(month.text) if month is not None else 1
                            day_val = int(day.text) if day is not None else 1
                            
                            return datetime(year_val, month_val, day_val)
                        except (ValueError, TypeError):
                            continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract publication date: {e}")
            return None
    
    def _calculate_paper_confidence(
        self, 
        title: str, 
        abstract: str, 
        journal: str, 
        authors: List[str], 
        pub_date: Optional[datetime]
    ) -> float:
        """Calculate confidence score for a paper based on various factors."""
        confidence = 0.5  # Base confidence
        
        # Title relevance (check for key neurosurgical terms)
        title_lower = title.lower()
        for term in self.neurosurgical_terms:
            if term.lower() in title_lower:
                confidence += 0.1
                break
        
        # Abstract quality
        if abstract and len(abstract) > 200:
            confidence += 0.1
        
        # Journal reputation (simplified check)
        high_impact_journals = [
            "journal of neurosurgery", "neurosurgery", "brain",
            "neurosurgical focus", "journal of neurotrauma",
            "stroke", "acta neurochirurgica", "world neurosurgery"
        ]
        
        journal_lower = journal.lower()
        for high_journal in high_impact_journals:
            if high_journal in journal_lower:
                confidence += 0.2
                break
        
        # Recency (more recent papers get higher confidence)
        if pub_date:
            days_old = (datetime.now() - pub_date).days
            if days_old <= 365:  # Within last year
                confidence += 0.1
            elif days_old <= 365 * 3:  # Within last 3 years
                confidence += 0.05
        
        # Author count (papers with multiple authors often more reliable)
        if len(authors) >= 3:
            confidence += 0.05
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    async def get_paper_by_pmid(self, pmid: str) -> Optional[Dict]:
        """Get detailed information for a specific paper by PMID."""
        try:
            async with aiohttp.ClientSession() as session:
                papers = await self._fetch_paper_details([pmid], session)
                return papers[0] if papers else None
        except Exception as e:
            logger.error(f"Failed to fetch paper {pmid}: {e}")
            return None
    
    async def search_concept_papers(
        self, 
        concept: str, 
        max_results: int = 20
    ) -> List[Dict]:
        """Search for papers related to a specific neurosurgical concept."""
        try:
            # Build concept-specific query
            query = f'"{concept}"[Title/Abstract] AND neurosurg*[Title/Abstract]'
            
            async with aiohttp.ClientSession() as session:
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "xml",
                    "sort": "relevance"
                }
                
                if settings.pubmed_api_key:
                    search_params["api_key"] = settings.pubmed_api_key
                
                async with session.get(self.search_url, params=search_params) as response:
                    search_results = await response.text()
                
                pmids = self._parse_search_results(search_results)
                papers = await self._fetch_paper_details(pmids, session)
                
                return papers
                
        except Exception as e:
            logger.error(f"Concept search failed for '{concept}': {e}")
            return []


# Global PubMed service instance
pubmed_service = PubMedService()