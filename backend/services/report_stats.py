"""
Report statistics service for dashboard.

Reads data from CSV storage and calculates statistics.
"""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter


class ReportStatsService:
    """Service for calculating report statistics from CSV storage."""

    def __init__(self, csv_path: str):
        """
        Initialize report stats service.

        Args:
            csv_path: Path to CSV file containing report data
        """
        self.csv_path = Path(csv_path)

    def _read_all_reports(self) -> List[Dict[str, Any]]:
        """
        Read all reports from CSV file.

        Returns:
            List of report dictionaries
        """
        if not self.csv_path.exists():
            return []

        reports = []
        with self.csv_path.open("r", encoding="utf-8") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                try:
                    # Parse timestamp
                    row["parsed_ts"] = datetime.fromisoformat(row["message_ts"])
                    reports.append(row)
                except (ValueError, KeyError):
                    # Skip rows with invalid timestamps
                    continue

        return reports

    def _filter_by_date_range(
        self, reports: List[Dict[str, Any]], start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Filter reports by date range.

        Args:
            reports: List of report dictionaries
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Filtered list of reports
        """
        return [
            r
            for r in reports
            if start_date <= r["parsed_ts"] <= end_date
        ]

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Calculate dashboard statistics from all available reports.

        Returns:
            Dictionary with statistics:
            - weekly_reports: Total number of weekly reports
            - monthly_reports: Total number of reports
            - high_risk_items: Number of high-risk reports
            - okr_completion: Average OKR completion percentage
            - weekly_trend: Simulated trend (0 for now)
            - monthly_trend: Simulated trend (0 for now)
            - risk_trend: Simulated trend (0 for now)
            - okr_trend: Simulated trend (0 for now)
        """
        all_reports = self._read_all_reports()

        if not all_reports:
            # Return zeros if no data
            return {
                "weekly_reports": 0,
                "monthly_reports": 0,
                "high_risk_items": 0,
                "okr_completion": 0.0,
                "weekly_trend": 0.0,
                "monthly_trend": 0.0,
                "risk_trend": 0.0,
                "okr_trend": 0.0,
            }

        # Count reports by type
        weekly_reports_count = sum(
            1 for r in all_reports if r.get("period_type") == "weekly"
        )

        # Count high-risk items
        high_risk_items = sum(
            1 for r in all_reports if r.get("risk_level") == "high"
        )

        # Calculate OKR completion average from all reports
        okr_scores = []
        for r in all_reports:
            try:
                confidence = float(r.get("okr_confidence", 0))
                okr_scores.append(confidence * 100)  # Convert to percentage
            except (ValueError, TypeError):
                pass

        okr_completion = sum(okr_scores) / len(okr_scores) if okr_scores else 0.0

        return {
            "weekly_reports": weekly_reports_count,
            "monthly_reports": len(all_reports),
            "high_risk_items": high_risk_items,
            "okr_completion": round(okr_completion, 1),
            "weekly_trend": 0.0,  # TODO: Calculate real trend when we have time-series data
            "monthly_trend": 0.0,
            "risk_trend": 0.0,
            "okr_trend": 0.0,
        }

    def _calculate_trend(self, current: float, previous: float) -> float:
        """
        Calculate percentage change between current and previous values.

        Args:
            current: Current value
            previous: Previous value

        Returns:
            Percentage change (can be negative)
        """
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    def get_recent_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of report summaries with fields:
            - id: Auto-generated ID (based on index)
            - user_name: User's name
            - period_type: Report period (daily/weekly/monthly)
            - created_at: Timestamp in ISO format
            - risk_level: Risk level (low/medium/high)
            - hr_summary: HR-friendly summary
        """
        all_reports = self._read_all_reports()

        # Sort by timestamp descending (newest first)
        all_reports.sort(key=lambda r: r["parsed_ts"], reverse=True)

        # Take top N and format
        recent = []
        for idx, report in enumerate(all_reports[:limit]):
            recent.append(
                {
                    "id": 10000 + idx,  # Generate unique ID
                    "user_name": report.get("user_name", "Unknown"),
                    "period_type": report.get("period_type", "daily"),
                    "created_at": report["message_ts"],
                    "risk_level": report.get("risk_level", "low"),
                    "hr_summary": report.get("hr_summary", "")[:100] + "...",  # Truncate
                }
            )

        return recent

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single report by its ID.

        Args:
            report_id: The report ID (offset from 10000)

        Returns:
            Full report dictionary with all fields, or None if not found
        """
        all_reports = self._read_all_reports()

        # Sort by timestamp descending (to match the ID generation logic)
        all_reports.sort(key=lambda r: r["parsed_ts"], reverse=True)

        # Calculate the index from the ID
        index = report_id - 10000
        if 0 <= index < len(all_reports):
            report = all_reports[index]
            # Return full report with generated ID
            return {
                "id": report_id,
                **report,  # Include all CSV fields
            }

        return None

    def get_risk_distribution(self) -> Dict[str, int]:
        """
        Get distribution of reports by risk level.

        Returns:
            Dictionary with counts for each risk level:
            - low: Count of low-risk reports
            - medium: Count of medium-risk reports
            - high: Count of high-risk reports
        """
        all_reports = self._read_all_reports()

        # Count by risk level
        risk_counts = Counter(r.get("risk_level", "low") for r in all_reports)

        return {
            "low": risk_counts.get("low", 0),
            "medium": risk_counts.get("medium", 0),
            "high": risk_counts.get("high", 0),
        }

    def get_okr_trend_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get OKR completion trend data for the last N days.

        Args:
            days: Number of days to look back (default 30)

        Returns:
            List of daily OKR completion data points
        """
        all_reports = self._read_all_reports()

        # Group reports by date
        from datetime import datetime, timedelta

        today = datetime.now()
        date_data = {}

        for report in all_reports:
            try:
                report_date = report["parsed_ts"].date()
                days_ago = (today.date() - report_date).days

                if days_ago <= days:
                    date_str = report_date.strftime("%Y-%m-%d")

                    if date_str not in date_data:
                        date_data[date_str] = {"scores": [], "count": 0}

                    # Add OKR confidence score
                    confidence = float(report.get("okr_confidence", 0))
                    if confidence > 0:
                        date_data[date_str]["scores"].append(confidence * 100)
                        date_data[date_str]["count"] += 1
            except (ValueError, TypeError, AttributeError):
                continue

        # Calculate daily averages
        trend_data = []
        for i in range(days, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            if date_str in date_data and date_data[date_str]["scores"]:
                avg_score = sum(date_data[date_str]["scores"]) / len(
                    date_data[date_str]["scores"]
                )
                trend_data.append(
                    {
                        "date": date_str,
                        "okr_completion": round(avg_score, 1),
                        "report_count": date_data[date_str]["count"],
                    }
                )
            else:
                # Include zero data points for continuity
                trend_data.append(
                    {"date": date_str, "okr_completion": 0, "report_count": 0}
                )

        return trend_data

    def get_report_timeline_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get report submission timeline for the last N days.

        Args:
            days: Number of days to look back (default 30)

        Returns:
            List of daily report submission counts
        """
        all_reports = self._read_all_reports()

        from datetime import datetime, timedelta

        today = datetime.now()
        date_counts = {}

        # Initialize all dates with zero
        for i in range(days, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_counts[date_str] = {"total": 0, "daily": 0, "weekly": 0, "monthly": 0}

        # Count reports by date and type
        for report in all_reports:
            try:
                report_date = report["parsed_ts"].date()
                days_ago = (today.date() - report_date).days

                if days_ago <= days:
                    date_str = report_date.strftime("%Y-%m-%d")
                    date_counts[date_str]["total"] += 1

                    period_type = report.get("period_type", "daily")
                    if period_type == "daily":
                        date_counts[date_str]["daily"] += 1
                    elif period_type == "weekly":
                        date_counts[date_str]["weekly"] += 1
                    elif period_type == "monthly":
                        date_counts[date_str]["monthly"] += 1
            except (ValueError, TypeError, AttributeError):
                continue

        # Convert to list
        timeline_data = []
        for i in range(days, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            data = date_counts[date_str]
            timeline_data.append(
                {
                    "date": date_str,
                    "total": data["total"],
                    "daily": data["daily"],
                    "weekly": data["weekly"],
                    "monthly": data["monthly"],
                }
            )

        return timeline_data

    def get_reports_list(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_level: Optional[str] = None,
        period_type: Optional[str] = None,
        user_name: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get paginated and filtered list of reports.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            risk_level: Filter by risk level (low, medium, high)
            period_type: Filter by period type (daily, weekly, monthly)
            user_name: Filter by user name (partial match)
            search: Search keyword in hr_summary and raw_text
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)

        Returns:
            Dictionary with total count and paginated results
        """
        all_reports = self._read_all_reports()

        # Sort by timestamp descending
        all_reports.sort(key=lambda r: r["parsed_ts"], reverse=True)

        # Apply filters
        filtered_reports = []
        for idx, report in enumerate(all_reports):
            # Generate ID
            report_id = 10000 + idx

            # Filter by risk level
            if risk_level and report.get("risk_level") != risk_level:
                continue

            # Filter by period type
            if period_type and report.get("period_type") != period_type:
                continue

            # Filter by user name (partial match, case-insensitive)
            if user_name and user_name.lower() not in report.get("user_name", "").lower():
                continue

            # Filter by date range
            if start_date or end_date:
                try:
                    from datetime import datetime

                    report_date = report["parsed_ts"].date()
                    if start_date:
                        filter_start = datetime.strptime(start_date, "%Y-%m-%d").date()
                        if report_date < filter_start:
                            continue
                    if end_date:
                        filter_end = datetime.strptime(end_date, "%Y-%m-%d").date()
                        if report_date > filter_end:
                            continue
                except (ValueError, AttributeError):
                    continue

            # Filter by search keyword
            if search:
                search_lower = search.lower()
                hr_summary = report.get("hr_summary", "").lower()
                raw_text = report.get("raw_text", "").lower()
                if search_lower not in hr_summary and search_lower not in raw_text:
                    continue

            filtered_reports.append(
                {
                    "id": report_id,
                    "user_id": report.get("user_id", ""),
                    "user_name": report.get("user_name", "Unknown"),
                    "period_type": report.get("period_type", "daily"),
                    "period_start": report.get("period_start", ""),
                    "period_end": report.get("period_end", ""),
                    "created_at": report["message_ts"],
                    "risk_level": report.get("risk_level", "low"),
                    "hr_summary": report.get("hr_summary", ""),
                }
            )

        # Calculate pagination
        total = len(filtered_reports)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_reports = filtered_reports[start_idx:end_idx]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "items": paginated_reports,
        }

    def get_user_submission_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get user submission statistics for ranking.

        Returns list of users with their submission counts and rates.
        """
        all_reports = self._read_all_reports()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Group by user
        user_stats: Dict[str, Dict] = {}
        for report in all_reports:
            if report["parsed_ts"] < cutoff_date:
                continue

            user_name = report.get("user_name", "Unknown")
            if user_name not in user_stats:
                user_stats[user_name] = {
                    "user_name": user_name,
                    "total_reports": 0,
                    "weekly_reports": 0,
                    "monthly_reports": 0,
                    "high_risk_count": 0,
                    "avg_okr_confidence": 0.0,
                    "okr_confidence_sum": 0.0,
                    "okr_confidence_count": 0,
                }

            stats = user_stats[user_name]
            stats["total_reports"] += 1

            period_type = report.get("period_type", "")
            if period_type == "weekly":
                stats["weekly_reports"] += 1
            elif period_type == "monthly":
                stats["monthly_reports"] += 1

            if report.get("risk_level") == "high":
                stats["high_risk_count"] += 1

            okr_confidence = report.get("okr_confidence")
            if okr_confidence is not None:
                try:
                    confidence_value = float(okr_confidence)
                    stats["okr_confidence_sum"] += confidence_value
                    stats["okr_confidence_count"] += 1
                except (ValueError, TypeError):
                    pass

        # Calculate averages and sort
        result = []
        for user_name, stats in user_stats.items():
            if stats["okr_confidence_count"] > 0:
                stats["avg_okr_confidence"] = stats["okr_confidence_sum"] / stats["okr_confidence_count"]

            # Remove temporary fields
            del stats["okr_confidence_sum"]
            del stats["okr_confidence_count"]

            result.append(stats)

        # Sort by total reports desc
        result.sort(key=lambda x: x["total_reports"], reverse=True)
        return result

    def get_risk_trend_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get risk trend data over time.

        Returns daily counts of reports by risk level.
        """
        all_reports = self._read_all_reports()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Group by date and risk level
        daily_risks: Dict[str, Dict[str, int]] = {}
        for report in all_reports:
            if report["parsed_ts"] < cutoff_date:
                continue

            date_str = report["parsed_ts"].strftime("%Y-%m-%d")
            if date_str not in daily_risks:
                daily_risks[date_str] = {"low": 0, "medium": 0, "high": 0}

            risk_level = report.get("risk_level", "low")
            if risk_level in daily_risks[date_str]:
                daily_risks[date_str][risk_level] += 1

        # Convert to list and sort by date
        result = []
        for date_str in sorted(daily_risks.keys()):
            result.append({
                "date": date_str,
                "low": daily_risks[date_str]["low"],
                "medium": daily_risks[date_str]["medium"],
                "high": daily_risks[date_str]["high"],
                "total": sum(daily_risks[date_str].values()),
            })

        return result

    def get_okr_achievement_ranking(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get OKR achievement ranking by user.

        Returns list of users sorted by OKR confidence.
        """
        all_reports = self._read_all_reports()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Group by user
        user_okr: Dict[str, Dict] = {}
        for report in all_reports:
            if report["parsed_ts"] < cutoff_date:
                continue

            user_name = report.get("user_name", "Unknown")
            okr_confidence = report.get("okr_confidence")

            if okr_confidence is None:
                continue

            try:
                confidence_value = float(okr_confidence)
            except (ValueError, TypeError):
                continue

            if user_name not in user_okr:
                user_okr[user_name] = {
                    "user_name": user_name,
                    "confidence_sum": 0.0,
                    "confidence_count": 0,
                    "avg_confidence": 0.0,
                    "report_count": 0,
                    "hit_objectives_count": 0,
                    "hit_krs_count": 0,
                }

            stats = user_okr[user_name]
            stats["confidence_sum"] += confidence_value
            stats["confidence_count"] += 1
            stats["report_count"] += 1

            if report.get("hit_objectives"):
                stats["hit_objectives_count"] += len(report["hit_objectives"])
            if report.get("hit_krs"):
                stats["hit_krs_count"] += len(report["hit_krs"])

        # Calculate averages
        result = []
        for user_name, stats in user_okr.items():
            if stats["confidence_count"] > 0:
                stats["avg_confidence"] = stats["confidence_sum"] / stats["confidence_count"]

            # Remove temporary fields
            del stats["confidence_sum"]
            del stats["confidence_count"]

            result.append(stats)

        # Sort by average confidence desc
        result.sort(key=lambda x: x["avg_confidence"], reverse=True)
        return result

    def get_team_statistics(self) -> Dict[str, Any]:
        """
        Get overall team statistics.

        Returns aggregated team metrics.
        """
        all_reports = self._read_all_reports()

        total_users = len(set(r.get("user_name", "Unknown") for r in all_reports))
        total_reports = len(all_reports)

        # Count by risk level
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for report in all_reports:
            risk_level = report.get("risk_level", "low")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1

        # Count by period type
        period_counts = {"daily": 0, "weekly": 0, "monthly": 0}
        for report in all_reports:
            period_type = report.get("period_type", "")
            if period_type in period_counts:
                period_counts[period_type] += 1

        # Calculate average OKR confidence
        okr_confidences = []
        for report in all_reports:
            okr_confidence = report.get("okr_confidence")
            if okr_confidence is not None:
                try:
                    okr_confidences.append(float(okr_confidence))
                except (ValueError, TypeError):
                    pass

        avg_okr_confidence = sum(okr_confidences) / len(okr_confidences) if okr_confidences else 0.0

        return {
            "total_users": total_users,
            "total_reports": total_reports,
            "avg_reports_per_user": total_reports / total_users if total_users > 0 else 0,
            "risk_distribution": risk_counts,
            "period_distribution": period_counts,
            "avg_okr_confidence": avg_okr_confidence,
            "high_risk_rate": risk_counts["high"] / total_reports if total_reports > 0 else 0,
        }
