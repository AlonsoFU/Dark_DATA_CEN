#!/usr/bin/env python3
"""
Session Management System for Claude Code Development Continuity
Tracks progress, manages session handoffs, and maintains development history.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class SessionTracker:
    """Manages development session tracking and continuity."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.profiles_dir = self.project_root / "data" / "profiles"
        
    def start_session(self, profile: str, goals: List[str], estimated_hours: float = 2.0) -> str:
        """Start a new development session."""
        profile_dir = self.profiles_dir / profile
        session_dir = profile_dir / "session_history"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate session ID
        existing_sessions = list(session_dir.glob("session_*.json"))
        session_num = len(existing_sessions) + 1
        session_id = f"session_{session_num:03d}"
        
        session_data = {
            "session_info": {
                "session_id": session_id,
                "profile": profile,
                "start_time": datetime.now().isoformat(),
                "goals": goals,
                "estimated_duration_hours": estimated_hours,
                "status": "active"
            },
            "baseline_metrics": self._get_current_metrics(profile),
            "focus_areas": [],
            "progress_log": []
        }
        
        session_file = session_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
        # Update current session pointer
        current_file = session_dir / "current_session.json"
        with open(current_file, 'w') as f:
            json.dump({"current_session": session_id, "profile": profile}, f)
            
        print(f"✅ Started session {session_id} for profile '{profile}'")
        print(f"📋 Goals: {', '.join(goals)}")
        return session_id
    
    def log_progress(self, profile: str, achievements: List[str], issues: List[str] = None, metrics: Dict = None):
        """Log progress during active session."""
        current_session = self._get_current_session(profile)
        if not current_session:
            print("⚠️ No active session found. Start a session first.")
            return
            
        session_file = self._get_session_file(profile, current_session)
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            
        progress_entry = {
            "timestamp": datetime.now().isoformat(),
            "achievements": achievements,
            "issues_discovered": issues or [],
            "metrics": metrics or {}
        }
        
        session_data["progress_log"].append(progress_entry)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
        print(f"📝 Progress logged for session {current_session}")
    
    def end_session(self, profile: str, handoff_notes: str, next_priorities: List[str]):
        """End current session with handoff information."""
        current_session = self._get_current_session(profile)
        if not current_session:
            print("⚠️ No active session found.")
            return
            
        session_file = self._get_session_file(profile, current_session)
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            
        # Update session with end information
        session_data["session_info"]["end_time"] = datetime.now().isoformat()
        session_data["session_info"]["status"] = "completed"
        
        # Calculate actual duration
        start_time = datetime.fromisoformat(session_data["session_info"]["start_time"])
        end_time = datetime.fromisoformat(session_data["session_info"]["end_time"])
        actual_duration = (end_time - start_time).total_seconds() / 3600
        session_data["session_info"]["actual_duration_hours"] = round(actual_duration, 2)
        
        # Add handoff information
        session_data["handoff_info"] = {
            "handoff_notes": handoff_notes,
            "next_priorities": next_priorities,
            "final_metrics": self._get_current_metrics(profile),
            "recommended_next_focus": self._suggest_next_focus(session_data)
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
            
        # Clear current session pointer
        current_file = self.profiles_dir / profile / "session_history" / "current_session.json"
        if current_file.exists():
            current_file.unlink()
            
        print(f"✅ Session {current_session} ended successfully")
        print(f"⏱️ Duration: {actual_duration:.1f} hours")
        print(f"📋 Next priorities: {', '.join(next_priorities)}")
        
    def load_session_context(self, profile: str, show_history: bool = False) -> Dict:
        """Load context for starting a new session."""
        profile_dir = self.profiles_dir / profile
        if not profile_dir.exists():
            print(f"❌ Profile '{profile}' not found")
            return {}
            
        # Get latest session
        session_dir = profile_dir / "session_history"
        if not session_dir.exists():
            print(f"📝 No previous sessions found for '{profile}'")
            return {}
            
        session_files = sorted(session_dir.glob("session_*.json"))
        if not session_files:
            print(f"📝 No previous sessions found for '{profile}'")
            return {}
            
        latest_session = session_files[-1]
        with open(latest_session, 'r') as f:
            latest_data = json.load(f)
            
        context = {
            "profile": profile,
            "last_session": latest_data["session_info"],
            "final_metrics": latest_data.get("handoff_info", {}).get("final_metrics", {}),
            "next_priorities": latest_data.get("handoff_info", {}).get("next_priorities", []),
            "recommended_focus": latest_data.get("handoff_info", {}).get("recommended_next_focus", ""),
            "session_count": len(session_files)
        }
        
        # Display context
        print(f"📊 {profile} Development Context")
        print(f"Last Session: {latest_data['session_info']['session_id']} ({self._format_time_ago(latest_data['session_info']['end_time'])})")
        
        if context["final_metrics"]:
            print(f"Quality: {context['final_metrics'].get('overall_quality', 'N/A')}")
            
        if context["next_priorities"]:
            print("📋 Next Priorities:")
            for i, priority in enumerate(context["next_priorities"], 1):
                print(f"  {i}. {priority}")
                
        if show_history:
            self._show_session_history(profile, session_files)
            
        return context
        
    def generate_status_report(self, profile: str, format: str = "markdown") -> str:
        """Generate comprehensive status report."""
        profile_dir = self.profiles_dir / profile
        session_dir = profile_dir / "session_history"
        
        if not session_dir.exists():
            return f"No session history found for profile '{profile}'"
            
        session_files = sorted(session_dir.glob("session_*.json"))
        if not session_files:
            return f"No sessions found for profile '{profile}'"
            
        # Analyze all sessions
        total_hours = 0
        session_count = len(session_files)
        achievements = []
        current_metrics = {}
        
        for session_file in session_files:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                
            if "actual_duration_hours" in session_data["session_info"]:
                total_hours += session_data["session_info"]["actual_duration_hours"]
                
            # Collect achievements
            for progress in session_data.get("progress_log", []):
                achievements.extend(progress.get("achievements", []))
                
            # Get latest metrics
            if "handoff_info" in session_data and "final_metrics" in session_data["handoff_info"]:
                current_metrics = session_data["handoff_info"]["final_metrics"]
                
        # Get next priorities from latest session
        with open(session_files[-1], 'r') as f:
            latest_session = json.load(f)
        next_priorities = latest_session.get("handoff_info", {}).get("next_priorities", [])
        
        if format == "markdown":
            return self._generate_markdown_report(
                profile, session_count, total_hours, current_metrics, 
                achievements, next_priorities
            )
        else:
            return self._generate_json_report(
                profile, session_count, total_hours, current_metrics,
                achievements, next_priorities
            )
    
    def _get_current_session(self, profile: str) -> Optional[str]:
        """Get current active session ID."""
        current_file = self.profiles_dir / profile / "session_history" / "current_session.json"
        if not current_file.exists():
            return None
            
        with open(current_file, 'r') as f:
            data = json.load(f)
        return data.get("current_session")
    
    def _get_session_file(self, profile: str, session_id: str) -> Path:
        """Get session file path."""
        return self.profiles_dir / profile / "session_history" / f"{session_id}.json"
    
    def _get_current_metrics(self, profile: str) -> Dict:
        """Get current quality metrics for profile."""
        # This would integrate with actual quality measurement system
        return {
            "overall_quality": 0.85,
            "processing_speed_minutes": 4.2,
            "critical_issues_count": 3
        }
    
    def _suggest_next_focus(self, session_data: Dict) -> str:
        """Suggest next focus area based on session progress."""
        progress_log = session_data.get("progress_log", [])
        if not progress_log:
            return "Continue with initial development"
            
        # Analyze recent issues to suggest focus
        recent_issues = []
        for entry in progress_log[-3:]:  # Last 3 entries
            recent_issues.extend(entry.get("issues_discovered", []))
            
        if recent_issues:
            return f"Address critical issues: {', '.join(recent_issues[:2])}"
        else:
            return "Continue quality improvements and validation"
    
    def _format_time_ago(self, timestamp: str) -> str:
        """Format timestamp as time ago."""
        try:
            time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - time
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            else:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
        except:
            return timestamp
    
    def _show_session_history(self, profile: str, session_files: List[Path]):
        """Show session history summary."""
        print("\n📈 Session History:")
        for session_file in session_files[-5:]:  # Show last 5 sessions
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                
            session_id = session_data["session_info"]["session_id"]
            duration = session_data["session_info"].get("actual_duration_hours", "N/A")
            status = session_data["session_info"].get("status", "unknown")
            
            print(f"  {session_id}: {duration}h ({status})")
    
    def _generate_markdown_report(self, profile: str, session_count: int, total_hours: float, 
                                 current_metrics: Dict, achievements: List[str], 
                                 next_priorities: List[str]) -> str:
        """Generate markdown status report."""
        report = f"""# {profile.title()} Development Status Report

**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Sessions:** {session_count} sessions  
**Time Invested:** {total_hours:.1f} hours

## 📊 Current Metrics:
- **Overall Quality:** {current_metrics.get('overall_quality', 'N/A')}
- **Processing Speed:** {current_metrics.get('processing_speed_minutes', 'N/A')} min/document
- **Critical Issues:** {current_metrics.get('critical_issues_count', 'N/A')} remaining

## ✅ Recent Achievements:
"""
        
        for achievement in achievements[-10:]:  # Last 10 achievements
            report += f"- {achievement}\n"
            
        report += "\n## 🎯 Next Session Priorities:\n"
        for i, priority in enumerate(next_priorities, 1):
            report += f"{i}. {priority}\n"
            
        return report
    
    def _generate_json_report(self, profile: str, session_count: int, total_hours: float,
                             current_metrics: Dict, achievements: List[str],
                             next_priorities: List[str]) -> str:
        """Generate JSON status report."""
        report_data = {
            "profile": profile,
            "report_date": datetime.now().isoformat(),
            "development_summary": {
                "session_count": session_count,
                "total_hours": total_hours,
                "current_metrics": current_metrics
            },
            "recent_achievements": achievements[-10:],
            "next_priorities": next_priorities
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Session tracking for Claude Code development")
    parser.add_argument("action", choices=["start", "progress", "end", "context", "report"])
    parser.add_argument("--profile", required=True, help="Profile name")
    parser.add_argument("--goals", nargs="+", help="Session goals (for start)")
    parser.add_argument("--hours", type=float, default=2.0, help="Estimated hours (for start)")
    parser.add_argument("--achievements", nargs="+", help="Achievements to log (for progress)")
    parser.add_argument("--issues", nargs="+", help="Issues discovered (for progress)")
    parser.add_argument("--handoff-notes", help="Handoff notes (for end)")
    parser.add_argument("--next-priorities", nargs="+", help="Next priorities (for end)")
    parser.add_argument("--show-history", action="store_true", help="Show history (for context)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Report format")
    
    args = parser.parse_args()
    
    tracker = SessionTracker()
    
    if args.action == "start":
        if not args.goals:
            print("❌ Goals required for starting session")
            return
        tracker.start_session(args.profile, args.goals, args.hours)
        
    elif args.action == "progress":
        if not args.achievements:
            print("❌ Achievements required for logging progress")
            return
        tracker.log_progress(args.profile, args.achievements, args.issues)
        
    elif args.action == "end":
        if not args.handoff_notes or not args.next_priorities:
            print("❌ Handoff notes and next priorities required for ending session")
            return
        tracker.end_session(args.profile, args.handoff_notes, args.next_priorities)
        
    elif args.action == "context":
        tracker.load_session_context(args.profile, args.show_history)
        
    elif args.action == "report":
        report = tracker.generate_status_report(args.profile, args.format)
        print(report)


if __name__ == "__main__":
    main()