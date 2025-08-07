"""
FastAPI utilities for iFixit repair guide system
Separate from Streamlit dependencies to avoid conflicts
"""

import re
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def clean_content(content: str) -> str:
    """
    Clean and format content for API responses.
    
    Args:
        content: Raw content to clean
        
    Returns:
        Cleaned content string
    """
    if not content:
        return ""
    
    try:
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up special characters
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&amp;', '&')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        content = content.replace('&quot;', '"')
        content = content.replace('&#39;', "'")
        
        return content.strip()
    except Exception as e:
        logger.warning(f"Error cleaning content: {e}")
        return content.strip() if content else ""

def extract_tools_and_parts(content: str) -> Tuple[List[str], List[str]]:
    """
    Extract tools and parts from repair guide content.
    
    Args:
        content: Repair guide content
        
    Returns:
        Tuple of (tools_list, parts_list)
    """
    tools = []
    parts = []
    
    if not content:
        return tools, parts
    
    try:
        # Look for common tool patterns
        tool_patterns = [
            r'Tools?[:\s]*([^.\n]+)',
            r'Required[:\s]*([^.\n]+)',
            r'Equipment[:\s]*([^.\n]+)',
            r'Supplies[:\s]*([^.\n]+)',
            r'Tools? needed[:\s]*([^.\n]+)',
            r'Required tools?[:\s]*([^.\n]+)'
        ]
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                items = [item.strip() for item in match.split(',')]
                tools.extend([item for item in items if item and len(item) > 1])
        
        # Look for common part patterns
        part_patterns = [
            r'Parts?[:\s]*([^.\n]+)',
            r'Replacement[:\s]*([^.\n]+)',
            r'Components?[:\s]*([^.\n]+)',
            r'Parts? needed[:\s]*([^.\n]+)',
            r'Required parts?[:\s]*([^.\n]+)'
        ]
        
        for pattern in part_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                items = [item.strip() for item in match.split(',')]
                parts.extend([item for item in items if item and len(item) > 1])
        
        # Remove duplicates and clean up
        tools = list(set([tool.strip() for tool in tools if tool.strip()]))
        parts = list(set([part.strip() for part in parts if part.strip()]))
        
        return tools, parts
        
    except Exception as e:
        logger.warning(f"Error extracting tools and parts: {e}")
        return [], []

def extract_steps(content: str) -> List[Tuple[str, str]]:
    """
    Extract repair steps from content.
    
    Args:
        content: Repair guide content
        
    Returns:
        List of (step_title, step_content) tuples
    """
    steps = []
    
    if not content:
        return steps
    
    try:
        # Look for numbered steps with various patterns
        step_patterns = [
            r'(\d+)[\.\)]\s*([^.\n]+)',
            r'Step\s*(\d+)[:\s]*([^.\n]+)',
            r'(\d+)[\.\)]\s*([^.\n]+)',
            r'Step\s*(\d+)[:\s]*([^.\n]+)',
            r'(\d+)[\.\)]\s*([^.\n]+)',
            r'Step\s*(\d+)[:\s]*([^.\n]+)'
        ]
        
        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                step_num = match[0]
                step_desc = match[1].strip()
                if step_desc and len(step_desc) > 3:  # Minimum meaningful step length
                    steps.append((f"Step {step_num}", step_desc))
        
        # Remove duplicates based on step number
        seen_steps = set()
        unique_steps = []
        for step in steps:
            if step[0] not in seen_steps:
                seen_steps.add(step[0])
                unique_steps.append(step)
        
        return unique_steps
        
    except Exception as e:
        logger.warning(f"Error extracting steps: {e}")
        return []

def extract_difficulty(content: str) -> str:
    """
    Extract difficulty level from content.
    
    Args:
        content: Repair guide content
        
    Returns:
        Difficulty level string
    """
    if not content:
        return "Unknown"
    
    try:
        content_lower = content.lower()
        
        # Look for difficulty indicators
        if any(word in content_lower for word in ["easy", "simple", "straightforward", "basic", "beginner"]):
            return "Easy"
        elif any(word in content_lower for word in ["moderate", "medium", "intermediate", "average"]):
            return "Moderate"
        elif any(word in content_lower for word in ["difficult", "challenging", "complex", "advanced", "expert", "hard"]):
            return "Difficult"
        else:
            return "Moderate"  # Default assumption
            
    except Exception as e:
        logger.warning(f"Error extracting difficulty: {e}")
        return "Unknown"

def extract_time_estimate(content: str) -> str:
    """
    Extract time estimate from content.
    
    Args:
        content: Repair guide content
        
    Returns:
        Time estimate string
    """
    if not content:
        return "Unknown"
    
    try:
        # Look for time patterns
        time_patterns = [
            r'(\d+)\s*-\s*(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*-\s*(\d+)\s*(?:days?)',
            r'(\d+)\s*(?:days?)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} hours"
                else:
                    return f"{match.group(1)} hours"
        
        # Estimate based on content length
        content_length = len(content)
        if content_length < 1000:
            return "30-60 minutes"
        elif content_length < 3000:
            return "1-2 hours"
        else:
            return "2-4 hours"
            
    except Exception as e:
        logger.warning(f"Error extracting time estimate: {e}")
        return "1-2 hours"  # Default estimate

def validate_url(url: str) -> bool:
    """
    Validate if a URL is a valid iFixit URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    try:
        # Basic iFixit URL validation
        if not url.startswith("https://www.ifixit.com/"):
            return False
        
        # Check for basic URL structure
        if len(url) < 25:  # Minimum reasonable length
            return False
        
        return True
        
    except Exception:
        return False

def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text for safe API responses.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    try:
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized.strip()
        
    except Exception as e:
        logger.warning(f"Error sanitizing text: {e}")
        return text[:max_length] if max_length else text 