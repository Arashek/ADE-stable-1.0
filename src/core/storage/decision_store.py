from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
import json
import aiosqlite
from pathlib import Path

from ..orchestrator.decision_engine import DecisionPoint, DecisionOption, DecisionStatus, ImpactLevel

class DecisionStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure the database and tables exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create decision points table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decision_points (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    deadline TIMESTAMP,
                    rationale TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')
            
            # Create decision options table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decision_options (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    pros TEXT NOT NULL,
                    cons TEXT NOT NULL,
                    impact_analysis TEXT NOT NULL,
                    votes TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (decision_id) REFERENCES decision_points(id)
                )
            ''')
            
            conn.commit()

    async def save_decision_point(self, decision: DecisionPoint) -> bool:
        """Save a decision point to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            # Convert options to JSON for storage
            options_json = json.dumps([
                {
                    'id': opt.id,
                    'title': opt.title,
                    'description': opt.description,
                    'pros': opt.pros,
                    'cons': opt.cons,
                    'impact_analysis': opt.impact_analysis,
                    'votes': opt.votes,
                    'created_at': opt.created_at.isoformat(),
                    'updated_at': opt.updated_at.isoformat()
                }
                for opt in decision.options
            ])
            
            # Insert or update decision point
            await cursor.execute('''
                INSERT OR REPLACE INTO decision_points 
                (id, project_id, title, description, category, status, impact_level, 
                 created_at, updated_at, deadline, rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.id,
                decision.project_id,
                decision.title,
                decision.description,
                decision.category,
                decision.status.value,
                decision.impact_level.value,
                decision.created_at.isoformat(),
                decision.updated_at.isoformat(),
                decision.deadline.isoformat() if decision.deadline else None,
                decision.rationale
            ))
            
            # Delete existing options
            await cursor.execute('DELETE FROM decision_options WHERE decision_id = ?', (decision.id,))
            
            # Insert new options
            for option in decision.options:
                await cursor.execute('''
                    INSERT INTO decision_options 
                    (id, decision_id, title, description, pros, cons, impact_analysis, 
                     votes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    option.id,
                    decision.id,
                    option.title,
                    option.description,
                    json.dumps(option.pros),
                    json.dumps(option.cons),
                    json.dumps(option.impact_analysis),
                    json.dumps(option.votes),
                    option.created_at.isoformat(),
                    option.updated_at.isoformat()
                ))
            
            await db.commit()
            return True

    async def get_decision_point(self, decision_id: str) -> Optional[DecisionPoint]:
        """Retrieve a decision point by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            # Get decision point
            await cursor.execute('''
                SELECT * FROM decision_points WHERE id = ?
            ''', (decision_id,))
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Get options
            await cursor.execute('''
                SELECT * FROM decision_options WHERE decision_id = ?
            ''', (decision_id,))
            
            options_rows = await cursor.fetchall()
            options = []
            
            for opt_row in options_rows:
                option = DecisionOption(
                    id=opt_row[0],
                    title=opt_row[2],
                    description=opt_row[3],
                    pros=json.loads(opt_row[4]),
                    cons=json.loads(opt_row[5]),
                    impact_analysis=json.loads(opt_row[6]),
                    votes=json.loads(opt_row[7]),
                    created_at=datetime.fromisoformat(opt_row[8]),
                    updated_at=datetime.fromisoformat(opt_row[9])
                )
                options.append(option)
            
            return DecisionPoint(
                id=row[0],
                project_id=row[1],
                title=row[2],
                description=row[3],
                category=row[4],
                status=DecisionStatus(row[5]),
                impact_level=ImpactLevel(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                updated_at=datetime.fromisoformat(row[8]),
                deadline=datetime.fromisoformat(row[9]) if row[9] else None,
                rationale=row[10],
                options=options
            )

    async def get_project_decisions(self, project_id: str) -> List[DecisionPoint]:
        """Get all decisions for a project."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            # Get decision points
            await cursor.execute('''
                SELECT * FROM decision_points WHERE project_id = ?
                ORDER BY created_at DESC
            ''', (project_id,))
            
            rows = await cursor.fetchall()
            decisions = []
            
            for row in rows:
                decision_id = row[0]
                
                # Get options for this decision
                await cursor.execute('''
                    SELECT * FROM decision_options WHERE decision_id = ?
                ''', (decision_id,))
                
                options_rows = await cursor.fetchall()
                options = []
                
                for opt_row in options_rows:
                    option = DecisionOption(
                        id=opt_row[0],
                        title=opt_row[2],
                        description=opt_row[3],
                        pros=json.loads(opt_row[4]),
                        cons=json.loads(opt_row[5]),
                        impact_analysis=json.loads(opt_row[6]),
                        votes=json.loads(opt_row[7]),
                        created_at=datetime.fromisoformat(opt_row[8]),
                        updated_at=datetime.fromisoformat(opt_row[9])
                    )
                    options.append(option)
                
                decision = DecisionPoint(
                    id=row[0],
                    project_id=row[1],
                    title=row[2],
                    description=row[3],
                    category=row[4],
                    status=DecisionStatus(row[5]),
                    impact_level=ImpactLevel(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    deadline=datetime.fromisoformat(row[9]) if row[9] else None,
                    rationale=row[10],
                    options=options
                )
                decisions.append(decision)
            
            return decisions

    async def delete_decision_point(self, decision_id: str) -> bool:
        """Delete a decision point and its options."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            # Delete options first
            await cursor.execute('DELETE FROM decision_options WHERE decision_id = ?', (decision_id,))
            
            # Delete decision point
            await cursor.execute('DELETE FROM decision_points WHERE id = ?', (decision_id,))
            
            await db.commit()
            return True

    async def get_decisions_by_status(self, project_id: str, status: DecisionStatus) -> List[DecisionPoint]:
        """Get all decisions with a specific status for a project."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            await cursor.execute('''
                SELECT * FROM decision_points 
                WHERE project_id = ? AND status = ?
                ORDER BY created_at DESC
            ''', (project_id, status.value))
            
            rows = await cursor.fetchall()
            decisions = []
            
            for row in rows:
                decision_id = row[0]
                
                # Get options for this decision
                await cursor.execute('''
                    SELECT * FROM decision_options WHERE decision_id = ?
                ''', (decision_id,))
                
                options_rows = await cursor.fetchall()
                options = []
                
                for opt_row in options_rows:
                    option = DecisionOption(
                        id=opt_row[0],
                        title=opt_row[2],
                        description=opt_row[3],
                        pros=json.loads(opt_row[4]),
                        cons=json.loads(opt_row[5]),
                        impact_analysis=json.loads(opt_row[6]),
                        votes=json.loads(opt_row[7]),
                        created_at=datetime.fromisoformat(opt_row[8]),
                        updated_at=datetime.fromisoformat(opt_row[9])
                    )
                    options.append(option)
                
                decision = DecisionPoint(
                    id=row[0],
                    project_id=row[1],
                    title=row[2],
                    description=row[3],
                    category=row[4],
                    status=DecisionStatus(row[5]),
                    impact_level=ImpactLevel(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    deadline=datetime.fromisoformat(row[9]) if row[9] else None,
                    rationale=row[10],
                    options=options
                )
                decisions.append(decision)
            
            return decisions

    async def get_decisions_by_category(self, project_id: str, category: str) -> List[DecisionPoint]:
        """Get all decisions in a specific category for a project."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            
            await cursor.execute('''
                SELECT * FROM decision_points 
                WHERE project_id = ? AND category = ?
                ORDER BY created_at DESC
            ''', (project_id, category))
            
            rows = await cursor.fetchall()
            decisions = []
            
            for row in rows:
                decision_id = row[0]
                
                # Get options for this decision
                await cursor.execute('''
                    SELECT * FROM decision_options WHERE decision_id = ?
                ''', (decision_id,))
                
                options_rows = await cursor.fetchall()
                options = []
                
                for opt_row in options_rows:
                    option = DecisionOption(
                        id=opt_row[0],
                        title=opt_row[2],
                        description=opt_row[3],
                        pros=json.loads(opt_row[4]),
                        cons=json.loads(opt_row[5]),
                        impact_analysis=json.loads(opt_row[6]),
                        votes=json.loads(opt_row[7]),
                        created_at=datetime.fromisoformat(opt_row[8]),
                        updated_at=datetime.fromisoformat(opt_row[9])
                    )
                    options.append(option)
                
                decision = DecisionPoint(
                    id=row[0],
                    project_id=row[1],
                    title=row[2],
                    description=row[3],
                    category=row[4],
                    status=DecisionStatus(row[5]),
                    impact_level=ImpactLevel(row[6]),
                    created_at=datetime.fromisoformat(row[7]),
                    updated_at=datetime.fromisoformat(row[8]),
                    deadline=datetime.fromisoformat(row[9]) if row[9] else None,
                    rationale=row[10],
                    options=options
                )
                decisions.append(decision)
            
            return decisions

    async def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the decision database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False

    async def restore_database(self, backup_path: str) -> bool:
        """Restore the decision database from a backup."""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False 