"""
DeepSeek API Integration for Repair Guide Summarization
Provides beginner-friendly summaries of repair guides using DeepSeek's AI models.
"""

import os
import logging
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_RETRIES = 3
MAX_CONTENT_LENGTH = 4000
VALID_SUMMARY_TYPES = ["beginner", "intermediate", "expert"]

class DeepSeekSummarizer:
    """DeepSeek-powered summarizer for repair guides."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek summarizer.
        
        Args:
            api_key: DeepSeek API key. If not provided, will look for DEEPSEEK_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("No DeepSeek API key found. Summarization will be disabled.")
            self.llm = None
            return
            
        try:
            self.llm = ChatDeepSeek(
                model="deepseek-chat",
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
                timeout=DEFAULT_TIMEOUT,
                max_retries=DEFAULT_MAX_RETRIES
            )
            logger.info("DeepSeek summarizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek: {e}")
            self.llm = None
    
    def is_available(self) -> bool:
        """
        Check if DeepSeek summarization is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.llm is not None
    
    def create_summary_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for repair guide summarization.
        
        Returns:
            ChatPromptTemplate for summarization
        """
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert repair technician who specializes in creating comprehensive yet beginner-friendly summaries of repair guides. Your goal is to provide maximum useful information while keeping it accessible.

When summarizing a repair guide, provide:

1. **Safety Warnings**: All critical safety precautions (battery risks, glass hazards, etc.)
2. **Difficulty Assessment**: Realistic difficulty level with explanation
3. **Complete Tools List**: All essential tools with their purposes
4. **Parts Required**: All necessary replacement parts and optional items
5. **Detailed Step-by-Step**: Comprehensive but simplified steps (10-15 key steps)
6. **Time Estimates**: Realistic time expectations for different skill levels
7. **Common Mistakes**: Specific pitfalls and how to avoid them
8. **Pro Tips**: Expert advice for success
9. **Post-Repair Notes**: Calibration, testing, and warranty considerations
10. **Success Rate**: Honest assessment of beginner success likelihood

Structure your response with clear sections, emojis for visual appeal, and encouraging but realistic language. Include specific details from the guide but present them in a digestible format."""),
            ("human", """Please create a comprehensive beginner-friendly summary of this repair guide:

**Device**: {device_name}
**Repair Type**: {repair_type}
**Guide Content**: {guide_content}

Provide maximum useful details while keeping it accessible for beginners. Include specific steps, tools, and warnings from the guide.""")
        ])
    
    def summarize_repair_guide(
        self, 
        device_name: str, 
        repair_type: str, 
        guide_content: str
    ) -> Dict[str, Any]:
        """
        Summarize a repair guide for beginners.
        
        Args:
            device_name: Name of the device being repaired
            repair_type: Type of repair (e.g., "battery replacement", "screen replacement")
            guide_content: The full repair guide content
            
        Returns:
            Dictionary containing the summary and metadata
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if not device_name or not device_name.strip():
            raise ValueError("Device name cannot be empty")
        if not repair_type or not repair_type.strip():
            raise ValueError("Repair type cannot be empty")
        if not guide_content or not guide_content.strip():
            raise ValueError("Guide content cannot be empty")
        
        device_name = device_name.strip()
        repair_type = repair_type.strip()
        
        if not self.is_available():
            logger.warning("DeepSeek API not available, using fallback summary")
            return self._generate_fallback_summary(device_name, repair_type, guide_content)
        
        try:
            logger.info(f"Generating AI summary for {device_name} {repair_type}")
            
            # Create the prompt
            prompt = self.create_summary_prompt()
            
            # Create the chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Truncate content if too long
            truncated_content = guide_content[:MAX_CONTENT_LENGTH] if len(guide_content) > MAX_CONTENT_LENGTH else guide_content
            
            # Generate summary
            summary = chain.invoke({
                "device_name": device_name,
                "repair_type": repair_type,
                "guide_content": truncated_content
            })
            
            logger.info("AI summary generated successfully")
            
            # Extract key information from summary
            difficulty = self._extract_difficulty(summary)
            time_estimate = self._extract_time_estimate(summary)
            success_rate = self._extract_success_rate(summary)
            
            return {
                "summary": summary,
                "difficulty": difficulty,
                "time_estimate": time_estimate,
                "success_rate": success_rate,
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            logger.info("Using fallback summary due to API error")
            return self._generate_fallback_summary(device_name, repair_type, guide_content)
    
    def _generate_fallback_summary(self, device_name: str, repair_type: str, guide_content: str) -> Dict[str, Any]:
        """
        Generate a fallback summary when DeepSeek API is unavailable.
        
        Args:
            device_name: Name of the device
            repair_type: Type of repair
            guide_content: Guide content
            
        Returns:
            Dictionary containing fallback summary and metadata
        """
        try:
            logger.info(f"Generating fallback summary for {device_name} {repair_type}")
            
            # Extract basic information from guide content
            content_lower = guide_content.lower()
            
            # Determine difficulty based on content analysis
            difficulty = self._analyze_difficulty_from_content(content_lower)
            
            # Estimate time based on content length and complexity
            time_estimate = self._estimate_time_from_content(guide_content)
            
            # Determine success rate
            success_rate = self._estimate_success_rate(difficulty)
            
            # Generate a comprehensive fallback summary
            summary = self._create_fallback_summary(device_name, repair_type, difficulty, time_estimate, success_rate)
            
            logger.info("Fallback summary generated successfully")
            
            return {
                "summary": summary,
                "difficulty": difficulty,
                "time_estimate": time_estimate,
                "success_rate": success_rate,
                "available": True
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback summary: {e}")
            return {
                "summary": f"Unable to generate summary for {device_name} {repair_type}. Please try again later or contact support.",
                "difficulty": "Unknown",
                "time_estimate": "Unknown",
                "success_rate": "Unknown",
                "available": False
            }
    
    def _analyze_difficulty_from_content(self, content_lower: str) -> str:
        """
        Analyze difficulty from content keywords.
        
        Args:
            content_lower: Lowercase content
            
        Returns:
            Difficulty level
        """
        if any(word in content_lower for word in ["easy", "simple", "straightforward", "basic", "beginner"]):
            return "Easy"
        elif any(word in content_lower for word in ["difficult", "challenging", "complex", "advanced", "expert", "professional"]):
            return "Difficult"
        else:
            return "Moderate"
    
    def _estimate_time_from_content(self, content: str) -> str:
        """
        Estimate time from content length and complexity.
        
        Args:
            content: Guide content
            
        Returns:
            Time estimate
        """
        content_length = len(content)
        if content_length < 1000:
            return "30-60 minutes"
        elif content_length < 3000:
            return "1-2 hours"
        else:
            return "2-4 hours"
    
    def _estimate_success_rate(self, difficulty: str) -> str:
        """
        Estimate success rate based on difficulty.
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            Success rate estimate
        """
        if difficulty == "Easy":
            return "High"
        elif difficulty == "Difficult":
            return "Low"
        else:
            return "Moderate"
    
    def _create_fallback_summary(self, device_name: str, repair_type: str, difficulty: str, time_estimate: str, success_rate: str) -> str:
        """
        Create a comprehensive fallback summary.
        
        Args:
            device_name: Device name
            repair_type: Repair type
            difficulty: Difficulty level
            time_estimate: Time estimate
            success_rate: Success rate
            
        Returns:
            Formatted summary string
        """
        return f"""🔧 **{device_name} {repair_type} - Quick Summary**

⚠️ **Safety First**: Always disconnect power and remove batteries before starting any repair.

🛠️ **Tools Needed**: Basic repair toolkit (screwdrivers, pry tools, spudger)
📦 **Parts Required**: Replacement {repair_type.split()[0]} (check compatibility)

⏱️ **Time Estimate**: {time_estimate}
📊 **Difficulty Level**: {difficulty}
🎯 **Success Rate**: {success_rate}

📋 **Key Steps**:
1. Power down device completely
2. Remove all screws and open device carefully
3. Disconnect cables and remove old component
4. Install new component and reconnect cables
5. Test functionality before reassembly
6. Reassemble device and test again

💡 **Pro Tips**:
- Take photos during disassembly for reference
- Keep screws organized by location
- Work on a clean, well-lit surface
- Be patient and don't force anything

🔍 **What to Watch For**:
- Fragile cables and connectors
- Hidden screws under labels or rubber feet
- Proper cable routing during reassembly

This repair guide provides step-by-step instructions for {repair_type.lower()} on the {device_name}. Follow all safety precautions and take your time for best results."""
    
    def _extract_difficulty(self, summary: str) -> str:
        """
        Extract difficulty level from summary.
        
        Args:
            summary: Generated summary
            
        Returns:
            Difficulty level
        """
        summary_lower = summary.lower()
        if any(word in summary_lower for word in ["easy", "simple", "straightforward", "beginner"]):
            return "Easy"
        elif any(word in summary_lower for word in ["moderate", "medium", "intermediate"]):
            return "Moderate"
        elif any(word in summary_lower for word in ["difficult", "challenging", "complex", "advanced"]):
            return "Difficult"
        else:
            return "Moderate"
    
    def _extract_time_estimate(self, summary: str) -> str:
        """
        Extract time estimate from summary.
        
        Args:
            summary: Generated summary
            
        Returns:
            Time estimate
        """
        time_patterns = [
            r"(\d+)\s*-\s*(\d+)\s*(?:hours?|hrs?)",
            r"(\d+)\s*(?:hours?|hrs?)",
            r"(\d+)\s*-\s*(\d+)\s*(?:minutes?|mins?)",
            r"(\d+)\s*(?:minutes?|mins?)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return f"{match.group(1)}-{match.group(2)} hours"
                else:
                    return f"{match.group(1)} hours"
        
        return "1-2 hours"  # Default estimate
    
    def _extract_success_rate(self, summary: str) -> str:
        """
        Extract success rate from summary.
        
        Args:
            summary: Generated summary
            
        Returns:
            Success rate
        """
        summary_lower = summary.lower()
        if any(word in summary_lower for word in ["high success", "likely to succeed", "good chance", "excellent"]):
            return "High"
        elif any(word in summary_lower for word in ["moderate success", "decent chance", "reasonable", "fair"]):
            return "Moderate"
        elif any(word in summary_lower for word in ["low success", "challenging", "difficult", "risky"]):
            return "Low"
        else:
            return "Moderate" 