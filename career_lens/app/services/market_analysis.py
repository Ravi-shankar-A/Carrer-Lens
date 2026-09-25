"""
Market Analysis Service

Provides functions for analyzing job market data, career demand, and salary trends.
"""

from typing import List, Dict, Optional
from app.database.db import CAREER_DATA


class MarketAnalysisService:
    """Service for job market analysis and insights."""
    
    def get_career_market_insight(self, career: str) -> Dict:
        """
        Get market insights for a specific career.
        
        Args:
            career: Career name
            
        Returns:
            Dictionary with market data
        """
        career_data = CAREER_DATA.get(career)
        
        if not career_data:
            # Try to find partial match
            for key in CAREER_DATA.keys():
                if career.lower() in key.lower() or key.lower() in career.lower():
                    career_data = CAREER_DATA[key]
                    career = key
                    break
        
        if not career_data:
            return {
                "career": career,
                "demand": "Unknown",
                "average_salary": "N/A",
                "growth_rate": "N/A",
                "top_companies": [],
                "top_skills": [],
                "error": "Career not found in database"
            }
        
        market = career_data.get("market", {})
        
        return {
            "career": career,
            "demand": market.get("demand", "Moderate"),
            "average_salary": market.get("average_salary", "$80,000"),
            "growth_rate": market.get("growth_rate", "10%"),
            "top_companies": market.get("top_companies", []),
            "top_skills": market.get("top_skills", career_data.get("skills", [])[:5])
        }
    
    def get_market_skills(self, career: str) -> Dict:
        """
        Get the most in-demand skills for a career.
        
        Args:
            career: Career name
            
        Returns:
            Dictionary with top skills and demand data
        """
        career_data = CAREER_DATA.get(career)
        
        if not career_data:
            # Try partial match
            for key in CAREER_DATA.keys():
                if career.lower() in key.lower() or key.lower() in career.lower():
                    career_data = CAREER_DATA[key]
                    career = key
                    break
        
        if not career_data:
            return {
                "career": career,
                "top_skills": [],
                "skill_demand": {}
            }
        
        # Get top skills from market data or general skills
        top_skills = career_data.get("market", {}).get(
            "top_skills", 
            career_data.get("skills", [])[:5]
        )
        
        # Generate skill demand levels
        skill_demand = {}
        demand_levels = ["Very High", "High", "High", "Moderate", "Moderate"]
        for i, skill in enumerate(top_skills):
            skill_demand[skill] = demand_levels[i] if i < len(demand_levels) else "Moderate"
        
        return {
            "career": career,
            "top_skills": top_skills,
            "skill_demand": skill_demand
        }
    
    def get_all_careers_market(self) -> List[Dict]:
        """
        Get market overview for all careers.
        
        Returns:
            List of market data for all careers
        """
        results = []
        for career in CAREER_DATA.keys():
            results.append(self.get_career_market_insight(career))
        
        # Sort by demand
        demand_order = {"Very High": 4, "High": 3, "Moderate": 2, "Low": 1, "Unknown": 0}
        results.sort(
            key=lambda x: demand_order.get(x["demand"], 0), 
            reverse=True
        )
        
        return results
    
    def compare_careers(self, careers: List[str]) -> Dict:
        """
        Compare multiple careers side by side.
        
        Args:
            careers: List of career names
            
        Returns:
            Comparison data
        """
        comparison = {
            "careers": careers,
            "data": []
        }
        
        for career in careers:
            market_data = self.get_career_market_insight(career)
            comparison["data"].append(market_data)
        
        return comparison
    
    def get_trending_skills(self, limit: int = 10) -> List[Dict]:
        """
        Get the most trending skills across all careers.
        
        Args:
            limit: Maximum number of skills to return
            
        Returns:
            List of skills with their occurrence and demand
        """
        skill_count = {}
        skill_careers = {}
        
        for career, data in CAREER_DATA.items():
            market_skills = data.get("market", {}).get("top_skills", [])
            for i, skill in enumerate(market_skills):
                if skill not in skill_count:
                    skill_count[skill] = 0
                    skill_careers[skill] = []
                skill_count[skill] += (5 - min(i, 4))  # Weight by position
                skill_careers[skill].append(career)
        
        # Sort by count
        sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for skill, count in sorted_skills[:limit]:
            results.append({
                "skill": skill,
                "demand_score": count,
                "careers": skill_careers[skill][:3]
            })
        
        return results
    
    def get_salary_comparison(self) -> List[Dict]:
        """
        Get salary comparison across careers.
        
        Returns:
            List of careers with salary data
        """
        results = []
        
        for career, data in CAREER_DATA.items():
            market = data.get("market", {})
            salary_str = market.get("average_salary", "$0")
            
            # Parse salary string to numeric for sorting
            salary_num = int(salary_str.replace("$", "").replace(",", "").replace("k", "000"))
            
            results.append({
                "career": career,
                "average_salary": salary_str,
                "salary_numeric": salary_num,
                "demand": market.get("demand", "Moderate")
            })
        
        # Sort by salary
        results.sort(key=lambda x: x["salary_numeric"], reverse=True)
        
        return results


# Singleton instance
_service_instance = None


def get_market_analysis_service() -> MarketAnalysisService:
    """Get or create the market analysis service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MarketAnalysisService()
    return _service_instance
