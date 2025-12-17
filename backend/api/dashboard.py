"""
Dashboard API endpoints.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from ..auth import get_current_user
from ..models.user import User
from ..services import ReportStatsService
from .schemas import DashboardStats, ReportDetail, ReportSummary, RiskDistribution

# Import from existing codebase
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import get_settings

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

settings = get_settings()
# Initialize report statistics service
report_stats = ReportStatsService(csv_path=settings.csv_path)


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    _current_user: User = Depends(get_current_user),
):
    """
    Get dashboard statistics from real CSV data.

    Returns counts and trends for reports, risks, and OKR completion.
    """
    try:
        # Get real statistics from CSV data
        stats = report_stats.get_dashboard_stats()
        return DashboardStats(**stats)
    except Exception:
        # Fallback to zero stats if CSV read fails
        return DashboardStats(
            weekly_reports=0,
            monthly_reports=0,
            high_risk_items=0,
            okr_completion=0.0,
            weekly_trend=0.0,
            monthly_trend=0.0,
            risk_trend=0.0,
            okr_trend=0.0,
        )


@router.get("/recent-reports", response_model=List[ReportSummary])
async def get_recent_reports(
    limit: int = 10,
    _current_user: User = Depends(get_current_user),
):
    """
    Get recent reports from CSV data for dashboard display.

    Args:
        limit: Maximum number of reports to return (default 10)
    """
    try:
        # Get real recent reports from CSV data
        reports_data = report_stats.get_recent_reports(limit=limit)
        return [ReportSummary(**report) for report in reports_data]
    except Exception:
        # Return empty list if CSV read fails
        return []


@router.get("/risk-distribution", response_model=RiskDistribution)
async def get_risk_distribution(
    _current_user: User = Depends(get_current_user),
):
    """
    Get risk level distribution from CSV data for pie chart.

    Returns counts of reports by risk level (low, medium, high).
    """
    try:
        # Get real risk distribution from CSV data
        distribution = report_stats.get_risk_distribution()
        return RiskDistribution(**distribution)
    except Exception:
        # Return zeros if CSV read fails
        return RiskDistribution(low=0, medium=0, high=0)


@router.get("/reports/{report_id}", response_model=ReportDetail)
async def get_report_detail(
    report_id: int,
    _current_user: User = Depends(get_current_user),
):
    """
    Get full details of a specific report.

    Args:
        report_id: The report ID

    Returns:
        Full report details including raw text, AI summary, risks, OKR info, etc.
    """
    report = report_stats.get_report_by_id(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Map CSV fields to API schema
    return ReportDetail(
        id=report["id"],
        user_id=report.get("user_id", ""),
        user_name=report.get("user_name", "Unknown"),
        period_type=report.get("period_type", "daily"),
        period_start=report.get("period_start", ""),
        period_end=report.get("period_end", ""),
        created_at=report.get("message_ts", ""),
        raw_text=report.get("raw_text", ""),
        hr_summary=report.get("hr_summary", ""),
        risk_level=report.get("risk_level", "low"),
        risks=report.get("risks"),
        needs=report.get("needs"),
        hit_objectives=report.get("hit_objectives"),
        hit_krs=report.get("hit_krs"),
        okr_gaps=report.get("okr_gaps"),
        okr_confidence=report.get("okr_confidence"),
        next_actions=report.get("next_actions"),
        okr_brief=report.get("okr_brief"),
    )


@router.get("/okr-trend")
async def get_okr_trend(
    days: int = 30,
    _current_user: User = Depends(get_current_user),
):
    """
    Get OKR completion trend data for charts.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        List of daily OKR completion data points
    """
    try:
        trend_data = report_stats.get_okr_trend_data(days=days)
        return trend_data
    except Exception:
        return []


@router.get("/report-timeline")
async def get_report_timeline(
    days: int = 30,
    _current_user: User = Depends(get_current_user),
):
    """
    Get report submission timeline data for charts.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        List of daily report submission counts
    """
    try:
        timeline_data = report_stats.get_report_timeline_data(days=days)
        return timeline_data
    except Exception:
        return []


@router.get("/reports")
async def get_reports_list(
    page: int = 1,
    page_size: int = 20,
    risk_level: str = None,
    period_type: str = None,
    user_name: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    _current_user: User = Depends(get_current_user),
):
    """
    Get paginated and filtered list of reports.

    Args:
        page: Page number (default 1)
        page_size: Items per page (default 20)
        risk_level: Filter by risk level (low, medium, high)
        period_type: Filter by period type (daily, weekly, monthly)
        user_name: Filter by user name
        search: Search keyword
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Paginated list of reports with total count
    """
    try:
        result = report_stats.get_reports_list(
            page=page,
            page_size=page_size,
            risk_level=risk_level,
            period_type=period_type,
            user_name=user_name,
            search=search,
            start_date=start_date,
            end_date=end_date,
        )
        return result
    except Exception as e:
        return {"total": 0, "page": page, "page_size": page_size, "total_pages": 0, "items": []}


@router.get("/reports/export")
async def export_reports(
    risk_level: str = None,
    period_type: str = None,
    user_name: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    _current_user: User = Depends(get_current_user),
):
    """
    Export reports as CSV file.

    Args:
        risk_level: Filter by risk level
        period_type: Filter by period type
        user_name: Filter by user name
        search: Search keyword
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        CSV file download
    """
    import io
    import csv
    from datetime import datetime

    try:
        # Get all filtered reports (no pagination)
        result = report_stats.get_reports_list(
            page=1,
            page_size=10000,  # Get all results
            risk_level=risk_level,
            period_type=period_type,
            user_name=user_name,
            search=search,
            start_date=start_date,
            end_date=end_date,
        )

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'ID',
            '提交人',
            '报告周期',
            '开始日期',
            '结束日期',
            '创建时间',
            '风险等级',
            'HR总结',
        ])

        # Write data rows
        for item in result['items']:
            risk_level_map = {'low': '低', 'medium': '中', 'high': '高'}
            period_type_map = {'daily': '日报', 'weekly': '周报', 'monthly': '月报'}

            writer.writerow([
                item['id'],
                item['user_name'],
                period_type_map.get(item['period_type'], item['period_type']),
                item.get('period_start', ''),
                item.get('period_end', ''),
                item['created_at'],
                risk_level_map.get(item['risk_level'], item['risk_level']),
                item['hr_summary'],
            ])

        # Get CSV content
        csv_content = output.getvalue()
        output.close()

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports_export_{timestamp}.csv"

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8-sig')),  # Add BOM for Excel
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/reports/{report_id}/export")
async def export_report_detail(
    report_id: int,
    _current_user: User = Depends(get_current_user),
):
    """
    Export a single report detail as CSV file.

    Args:
        report_id: The report ID

    Returns:
        CSV file download with detailed report information
    """
    import io
    import csv
    from datetime import datetime

    report = report_stats.get_report_by_id(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Map field names to Chinese
    risk_level_map = {'low': '低', 'medium': '中', 'high': '高'}
    period_type_map = {'daily': '日报', 'weekly': '周报', 'monthly': '月报'}

    # Write report details as key-value pairs
    writer.writerow(['字段', '内容'])
    writer.writerow(['报告ID', report['id']])
    writer.writerow(['提交人', report.get('user_name', 'Unknown')])
    writer.writerow(['报告周期', period_type_map.get(report.get('period_type', 'daily'), report.get('period_type', 'daily'))])
    writer.writerow(['开始日期', report.get('period_start', '')])
    writer.writerow(['结束日期', report.get('period_end', '')])
    writer.writerow(['创建时间', report.get('message_ts', '')])
    writer.writerow(['风险等级', risk_level_map.get(report.get('risk_level', 'low'), report.get('risk_level', 'low'))])
    writer.writerow([])
    writer.writerow(['HR总结', report.get('hr_summary', '')])
    writer.writerow([])
    writer.writerow(['原始内容', report.get('raw_text', '')])

    # Add risks if available
    if report.get('risks'):
        writer.writerow([])
        writer.writerow(['风险项'])
        for risk in report.get('risks', []):
            writer.writerow(['', risk])

    # Add needs if available
    if report.get('needs'):
        writer.writerow([])
        writer.writerow(['需求和帮助'])
        for need in report.get('needs', []):
            writer.writerow(['', need])

    # Add OKR information if available
    if report.get('hit_objectives'):
        writer.writerow([])
        writer.writerow(['命中的目标'])
        for obj in report.get('hit_objectives', []):
            writer.writerow(['', obj])

    if report.get('hit_krs'):
        writer.writerow([])
        writer.writerow(['命中的关键结果'])
        for kr in report.get('hit_krs', []):
            writer.writerow(['', kr])

    if report.get('okr_gaps'):
        writer.writerow([])
        writer.writerow(['OKR差距'])
        for gap in report.get('okr_gaps', []):
            writer.writerow(['', gap])

    if report.get('next_actions'):
        writer.writerow([])
        writer.writerow(['下一步行动'])
        for action in report.get('next_actions', []):
            writer.writerow(['', action])

    # Get CSV content
    csv_content = output.getvalue()
    output.close()

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{report_id}_{timestamp}.csv"

    # Return as streaming response
    return StreamingResponse(
        io.BytesIO(csv_content.encode('utf-8-sig')),  # Add BOM for Excel
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/analytics/user-submissions")
async def get_user_submission_analytics(
    days: int = 30,
    _current_user: User = Depends(get_current_user),
):
    """
    Get user submission statistics for analytics.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        List of users with their submission statistics
    """
    try:
        stats = report_stats.get_user_submission_stats(days=days)
        return stats
    except Exception as e:
        return []


@router.get("/analytics/risk-trend")
async def get_risk_trend_analytics(
    days: int = 30,
    _current_user: User = Depends(get_current_user),
):
    """
    Get risk trend data for analytics.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        Daily risk level distribution data
    """
    try:
        trend_data = report_stats.get_risk_trend_data(days=days)
        return trend_data
    except Exception as e:
        return []


@router.get("/analytics/okr-ranking")
async def get_okr_ranking_analytics(
    days: int = 30,
    _current_user: User = Depends(get_current_user),
):
    """
    Get OKR achievement ranking for analytics.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        List of users sorted by OKR confidence
    """
    try:
        ranking = report_stats.get_okr_achievement_ranking(days=days)
        return ranking
    except Exception as e:
        return []


@router.get("/analytics/team-stats")
async def get_team_statistics(
    _current_user: User = Depends(get_current_user),
):
    """
    Get overall team statistics for analytics.

    Returns:
        Aggregated team metrics
    """
    try:
        stats = report_stats.get_team_statistics()
        return stats
    except Exception as e:
        return {
            "total_users": 0,
            "total_reports": 0,
            "avg_reports_per_user": 0,
            "risk_distribution": {"low": 0, "medium": 0, "high": 0},
            "period_distribution": {"daily": 0, "weekly": 0, "monthly": 0},
            "avg_okr_confidence": 0,
            "high_risk_rate": 0,
        }
