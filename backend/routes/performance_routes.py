from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_db
from ..auth.auth import get_current_user
from ..config.logging_config import logger
from ..performance.monitoring.performance_monitor import PerformanceMonitor
from ..performance.analysis.language_analyzer import LanguageAnalyzer

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/metrics")
async def get_performance_metrics(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Get performance metrics"""
    try:
        monitor = PerformanceMonitor()
        return await monitor.get_performance_report(days)
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_performance_trends(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Get performance trends"""
    try:
        monitor = PerformanceMonitor()
        return await monitor.get_performance_trends(days)
    except Exception as e:
        logger.error(f"Error getting performance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_performance_alerts(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Get performance alerts"""
    try:
        monitor = PerformanceMonitor()
        key = f"performance_alerts:{datetime.utcnow().strftime('%Y%m%d')}"
        alerts = await redis_client.get(key)
        return alerts or []
    except Exception as e:
        logger.error(f"Error getting performance alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/code")
async def analyze_code(
    code: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """Analyze code for performance optimizations"""
    try:
        analyzer = LanguageAnalyzer()
        report = analyzer.generate_optimization_report(language, code)
        await analyzer.store_optimizations(language, report["optimizations"])
        return report
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_optimization_recommendations(
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """Get optimization recommendations for a language"""
    try:
        analyzer = LanguageAnalyzer()
        return analyzer.get_optimization_recommendations(language)
    except Exception as e:
        logger.error(f"Error getting optimization recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memory/analysis")
async def get_memory_analysis(
    current_user: dict = Depends(get_current_user)
):
    """Get memory analysis report"""
    try:
        monitor = PerformanceMonitor()
        return monitor.memory_analyzer.generate_memory_report()
    except Exception as e:
        logger.error(f"Error getting memory analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/metrics")
async def get_api_metrics(
    route: Optional[str] = None,
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Get API endpoint metrics"""
    try:
        monitor = PerformanceMonitor()
        if route:
            return await monitor.api_profiler.get_route_statistics(route, days)
        return await monitor.api_profiler.get_request_metrics()
    except Exception as e:
        logger.error(f"Error getting API metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/anomalies")
async def get_api_anomalies(
    route: str,
    current_user: dict = Depends(get_current_user)
):
    """Get API endpoint anomalies"""
    try:
        monitor = PerformanceMonitor()
        return await monitor.api_profiler.detect_anomalies(route)
    except Exception as e:
        logger.error(f"Error getting API anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 