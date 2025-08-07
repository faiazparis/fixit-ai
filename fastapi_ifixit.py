"""
FastAPI-specific iFixit repair guide system
Without Streamlit dependencies to avoid conflicts
"""

import requests
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from langchain_community.document_loaders import IFixitLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result data class."""
    page_content: str
    metadata: Dict[str, Any]

class IFixitRepairGuide:
    """FastAPI version of iFixit repair guide system without Streamlit."""
    
    def __init__(self):
        """Initialize the iFixit repair guide system."""
        self.base_url = "https://www.ifixit.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'iFixit-Repair-Guide-API/1.0.0'
        })
        
        # Common model number mappings (deduplicated)
        self.model_mappings = {
            # Samsung Galaxy models
            'G973': 'Samsung Galaxy S10',
            'G973F': 'Samsung Galaxy S10',
            'G973U': 'Samsung Galaxy S10',
            'G973W': 'Samsung Galaxy S10',
            'G970': 'Samsung Galaxy S10e',
            'G970F': 'Samsung Galaxy S10e',
            'G970U': 'Samsung Galaxy S10e',
            'G975': 'Samsung Galaxy S10+',
            'G975F': 'Samsung Galaxy S10+',
            'G975U': 'Samsung Galaxy S10+',
            'G998': 'Samsung Galaxy S21 Ultra',
            'G991': 'Samsung Galaxy S21',
            'G996': 'Samsung Galaxy S21+',
            'G998B': 'Samsung Galaxy S21 Ultra',
            'G991B': 'Samsung Galaxy S21',
            'G996B': 'Samsung Galaxy S21+',
            
            # iPhone models
            'A1505': 'iPhone 6',
            'A1507': 'iPhone 6',
            'A1508': 'iPhone 6',
            'A1516': 'iPhone 6',
            'A1522': 'iPhone 6 Plus',
            'A1524': 'iPhone 6 Plus',
            'A1526': 'iPhone 6 Plus',
            'A1529': 'iPhone 6 Plus',
            'A1549': 'iPhone 6 Plus',
            'A1586': 'iPhone 6',
            'A1589': 'iPhone 6',
            'A1593': 'iPhone 6 Plus',
            'A1633': 'iPhone 6s',
            'A1634': 'iPhone 6s Plus',
            'A1688': 'iPhone 6s',
            'A1687': 'iPhone 6s Plus',
            'A1700': 'iPhone 6s',
            'A1699': 'iPhone 6s Plus',
            'A1778': 'iPhone 7',
            'A1784': 'iPhone 7 Plus',
            'A1660': 'iPhone 7',
            'A1661': 'iPhone 7 Plus',
            'A1779': 'iPhone 7',
            'A1785': 'iPhone 7 Plus',
            'A1863': 'iPhone 8',
            'A1864': 'iPhone 8 Plus',
            'A1905': 'iPhone 8',
            'A1897': 'iPhone 8 Plus',
            'A1906': 'iPhone 8',
            'A1898': 'iPhone 8 Plus',
            'A1920': 'iPhone XS',
            'A1921': 'iPhone XS Max',
            'A2097': 'iPhone XS',
            'A2101': 'iPhone XS Max',
            'A2098': 'iPhone XS',
            'A2102': 'iPhone XS Max',
            'A2111': 'iPhone XR',
            'A2105': 'iPhone XR',
            'A2106': 'iPhone XR',
            'A2108': 'iPhone XR',
            'A2215': 'iPhone 11',
            'A2221': 'iPhone 11 Pro',
            'A2223': 'iPhone 11 Pro Max',
            'A2220': 'iPhone 11',
            'A2218': 'iPhone 11 Pro',
            
            # MacBook models
            'A1502': 'MacBook Pro 13-inch',
            'A1398': 'MacBook Pro 15-inch',
            'A1466': 'MacBook Air 13-inch',
            'A1465': 'MacBook Air 11-inch',
            'A1534': 'MacBook 12-inch',
            'A1706': 'MacBook Pro 13-inch',
        }
    
    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with model number mappings.
        
        Args:
            query: Original search query
            
        Returns:
            List of expanded queries including model mappings
        """
        expanded = [query]
        
        # Add model number mappings
        if query in self.model_mappings:
            expanded.append(self.model_mappings[query])
        
        # Add variations
        query_lower = query.lower()
        for model, name in self.model_mappings.items():
            if model.lower() in query_lower or name.lower() in query_lower:
                expanded.extend([model, name])
        
        return list(set(expanded))
    
    def search_device(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search for devices using the real iFixit API.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            logger.info(f"Searching for devices with query: '{query}' (max_results: {max_results})")
            
            # Expand query with model number mappings
            expanded_queries = self.expand_query(query)
            all_documents = []
            
            for search_query in expanded_queries:
                try:
                    documents = IFixitLoader.load_suggestions(search_query)
                    all_documents.extend(documents)
                except Exception as e:
                    logger.warning(f"Search failed for '{search_query}': {str(e)}")
                    continue
            
            # Remove duplicates based on source URL
            seen_urls = set()
            unique_documents = []
            for doc in all_documents:
                url = doc.metadata.get('source', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_documents.append(doc)
            
            # Filter and rank results to prioritize exact matches
            filtered_documents = self._filter_and_rank_results(unique_documents, query)
            
            # Convert to SearchResult format and limit results
            results = []
            for doc in filtered_documents[:max_results]:
                results.append(SearchResult(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                ))
            
            logger.info(f"Found {len(results)} devices for query '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error searching for device {query}: {e}")
            return []
    
    def _filter_and_rank_results(self, documents: List[Document], query: str) -> List[Document]:
        """
        Filter and rank search results based on relevance.
        
        Args:
            documents: List of documents to filter
            query: Original search query
            
        Returns:
            Filtered and ranked list of documents
        """
        filtered_documents = []
        query_lower = query.lower()
        
        for doc in documents:
            title = doc.metadata.get('title', '').lower()
            content = doc.page_content.lower()
            
            # Check for exact matches first
            if query_lower in title or query_lower in content:
                # Prioritize exact matches
                doc.metadata['relevance_score'] = 100
                filtered_documents.append(doc)
            # Check for partial matches
            elif any(word in title or word in content for word in query_lower.split()):
                # Lower score for partial matches
                doc.metadata['relevance_score'] = 50
                filtered_documents.append(doc)
            # Check for model number patterns (like G973, A1505, etc.)
            elif any(char.isdigit() for char in query) and any(char.isdigit() for char in title):
                # Check if model numbers are similar
                query_digits = ''.join(filter(str.isdigit, query))
                title_digits = ''.join(filter(str.isdigit, title))
                if query_digits in title_digits or title_digits in query_digits:
                    doc.metadata['relevance_score'] = 75
                    filtered_documents.append(doc)
        
        # Sort by relevance score (highest first)
        filtered_documents.sort(key=lambda x: x.metadata.get('relevance_score', 0), reverse=True)
        
        # If no filtered results, return original results
        if not filtered_documents:
            filtered_documents = documents
        
        return filtered_documents
    
    def get_repair_guides(self, device_url: str) -> List[SearchResult]:
        """
        Get repair guides for a specific device.
        
        Args:
            device_url: URL of the device page
            
        Returns:
            List of SearchResult objects containing repair guides
        """
        try:
            logger.info(f"Loading repair guides for device: {device_url}")
            
            # Create loader with the device URL as web_path
            loader = IFixitLoader(device_url)
            documents = loader.load()
            
            # Convert to SearchResult format
            results = []
            for doc in documents:
                results.append(SearchResult(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                ))
            
            logger.info(f"Loaded {len(results)} repair guides for device")
            return results
            
        except Exception as e:
            logger.error(f"Error loading repair guides: {str(e)}")
            return []
    
    def get_teardowns(self, device_url: str) -> List[SearchResult]:
        """
        Get teardowns for a specific device.
        
        Args:
            device_url: URL of the device page
            
        Returns:
            List of SearchResult objects containing teardowns
        """
        # TODO: Implement teardown retrieval
        logger.info(f"Teardown retrieval not yet implemented for: {device_url}")
        return []
    
    def get_answers(self, device_url: str) -> List[SearchResult]:
        """
        Get community answers for a specific device.
        
        Args:
            device_url: URL of the device page
            
        Returns:
            List of SearchResult objects containing community answers
        """
        # TODO: Implement community answers retrieval
        logger.info(f"Community answers retrieval not yet implemented for: {device_url}")
        return [] 