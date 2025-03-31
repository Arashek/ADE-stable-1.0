from typing import Dict, List
from datetime import datetime, timedelta
from ..storage.waitlist_store import waitlist_store
from ..db.models.early_access import WaitlistStatus, UseCase

class WaitlistAnalytics:
    def __init__(self):
        self.store = waitlist_store

    async def get_conversion_metrics(self) -> Dict:
        """Calculate conversion metrics for the waitlist"""
        total = await self.store.get_waitlist_stats()
        
        # Calculate conversion rates
        conversion_rates = {
            "pending_to_approved": round(
                (total["approved"] / total["pending"]) * 100
                if total["pending"] > 0 else 0,
                2
            ),
            "approved_to_registered": round(
                (total["registered"] / total["approved"]) * 100
                if total["approved"] > 0 else 0,
                2
            ),
            "overall_conversion": round(
                (total["registered"] / total["total"]) * 100
                if total["total"] > 0 else 0,
                2
            )
        }

        return {
            "total_requests": total["total"],
            "conversion_rates": conversion_rates,
            "current_status": total
        }

    async def get_trend_analysis(self, days: int = 30) -> Dict:
        """Analyze waitlist trends over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily signups
        daily_signups = await self.store.get_daily_signups(start_date, end_date)
        
        # Calculate growth rate
        if len(daily_signups) > 1:
            growth_rate = round(
                ((daily_signups[-1]["count"] - daily_signups[0]["count"]) 
                / daily_signups[0]["count"]) * 100,
                2
            )
        else:
            growth_rate = 0

        return {
            "daily_signups": daily_signups,
            "growth_rate": growth_rate,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    async def get_use_case_analysis(self) -> Dict:
        """Analyze use case distribution and conversion rates"""
        use_cases = await self.store.get_use_case_distribution()
        conversion_by_use_case = {}
        
        for use_case in UseCase:
            stats = await self.store.get_use_case_stats(use_case)
            conversion_by_use_case[use_case] = {
                "total": stats["total"],
                "approved": stats["approved"],
                "registered": stats["registered"],
                "conversion_rate": round(
                    (stats["registered"] / stats["total"]) * 100
                    if stats["total"] > 0 else 0,
                    2
                )
            }

        return {
            "distribution": use_cases,
            "conversion_by_use_case": conversion_by_use_case
        }

    async def get_wait_time_analysis(self) -> Dict:
        """Analyze average wait times and processing speed"""
        stats = await self.store.get_wait_time_stats()
        
        return {
            "average_wait_time": stats["average_wait_time"],
            "median_wait_time": stats["median_wait_time"],
            "processing_speed": stats["processing_speed"],
            "current_backlog": stats["current_backlog"]
        }

    async def get_engagement_metrics(self) -> Dict:
        """Track user engagement with the waitlist"""
        metrics = await self.store.get_engagement_metrics()
        
        return {
            "email_open_rate": metrics["email_open_rate"],
            "click_through_rate": metrics["click_through_rate"],
            "response_rate": metrics["response_rate"],
            "social_shares": metrics["social_shares"]
        }

# Create a global instance
waitlist_analytics = WaitlistAnalytics() 