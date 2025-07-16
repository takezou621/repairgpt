"""
Database initialization script for RepairGPT
Creates tables and optionally loads sample data
"""

import sys
import logging
import argparse
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent.parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from database.database import (
    create_tables, get_db_session, check_database_health,
    get_database_info
)
from database.models import (
    User, Device, Issue, DeviceIssue, RepairGuide, RepairStep,
    ChatSession, ExternalDataSource
)
from database.crud import UserCRUD, DeviceCRUD, RepairGuideCRUD, ChatSessionCRUD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_devices(db):
    """Create sample devices"""
    devices = [
        {
            "id": "nintendo_switch",
            "name": "Nintendo Switch",
            "category": "Gaming Console",
            "manufacturer": "Nintendo",
            "model_variants": ["OLED", "Lite", "V1", "V2"],
            "release_year": 2017,
            "description": "Hybrid gaming console"
        },
        {
            "id": "iphone_14",
            "name": "iPhone 14",
            "category": "Smartphone", 
            "manufacturer": "Apple",
            "model_variants": ["iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max"],
            "release_year": 2022,
            "description": "Apple smartphone"
        },
        {
            "id": "ps5",
            "name": "PlayStation 5",
            "category": "Gaming Console",
            "manufacturer": "Sony",
            "model_variants": ["Standard", "Digital Edition"],
            "release_year": 2020,
            "description": "Sony gaming console"
        },
        {
            "id": "macbook_pro",
            "name": "MacBook Pro",
            "category": "Laptop",
            "manufacturer": "Apple",
            "model_variants": ["13-inch", "14-inch", "16-inch"],
            "release_year": 2023,
            "description": "Apple laptop computer"
        }
    ]
    
    for device_data in devices:
        existing = DeviceCRUD.get_device_by_id(db, device_data["id"])
        if not existing:
            device = DeviceCRUD.create_device(db, **device_data)
            logger.info(f"Created device: {device.name}")


def create_sample_issues(db):
    """Create sample issues"""
    issues = [
        {
            "id": "joy_con_drift",
            "name": "Joy-Con Analog Stick Drift",
            "description": "Joy-Con analog sticks registering movement when not touched",
            "category": "Controller Issues",
            "severity": "high"
        },
        {
            "id": "screen_cracked",
            "name": "Cracked Screen",
            "description": "Physical damage to device screen",
            "category": "Display Issues",
            "severity": "medium"
        },
        {
            "id": "overheating",
            "name": "Device Overheating",
            "description": "Device running hot and shutting down",
            "category": "Thermal Issues",
            "severity": "high"
        },
        {
            "id": "boot_failure",
            "name": "Won't Boot/Turn On",
            "description": "Device fails to start or turn on",
            "category": "Power Issues",
            "severity": "critical"
        },
        {
            "id": "audio_problems",
            "name": "Audio Issues",
            "description": "Sound not working or distorted",
            "category": "Audio Issues", 
            "severity": "medium"
        }
    ]
    
    for issue_data in issues:
        existing = db.query(Issue).filter(Issue.id == issue_data["id"]).first()
        if not existing:
            issue = Issue(**issue_data)
            db.add(issue)
            logger.info(f"Created issue: {issue.name}")
    
    db.commit()


def create_device_issue_relationships(db):
    """Create device-issue relationships"""
    relationships = [
        ("nintendo_switch", "joy_con_drift", 0.85, "intermediate"),
        ("nintendo_switch", "overheating", 0.30, "advanced"),
        ("iphone_14", "screen_cracked", 0.60, "advanced"),
        ("iphone_14", "audio_problems", 0.25, "intermediate"),
        ("ps5", "overheating", 0.45, "intermediate"),
        ("ps5", "boot_failure", 0.20, "advanced"),
        ("macbook_pro", "overheating", 0.35, "intermediate"),
        ("macbook_pro", "boot_failure", 0.15, "advanced")
    ]
    
    for device_id, issue_id, frequency, difficulty in relationships:
        existing = db.query(DeviceIssue).filter(
            DeviceIssue.device_id == device_id,
            DeviceIssue.issue_id == issue_id
        ).first()
        
        if not existing:
            device_issue = DeviceIssue(
                device_id=device_id,
                issue_id=issue_id,
                frequency=frequency,
                difficulty=difficulty
            )
            db.add(device_issue)
            logger.info(f"Created device-issue relationship: {device_id} - {issue_id}")
    
    db.commit()


def create_sample_repair_guides(db):
    """Create sample repair guides with steps"""
    guides = [
        {
            "title": "Nintendo Switch Joy-Con Analog Stick Drift Repair",
            "device_id": "nintendo_switch",
            "issue_id": "joy_con_drift",
            "difficulty": "intermediate",
            "estimated_time": 45,
            "success_rate": 0.85,
            "tools_required": ["Y00 Tripoint screwdriver", "Phillips PH000 screwdriver", "Plastic prying tools"],
            "parts_required": ["Replacement analog stick module"],
            "safety_warnings": ["Warranty will be voided", "Handle ribbon cables carefully"],
            "description": "Complete guide to fixing Joy-Con analog stick drift",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Power Off and Prepare",
                    "description": "Power off Switch completely. Remove Joy-Con from console.",
                    "estimated_time": 5
                },
                {
                    "step_number": 2,
                    "title": "Remove Back Cover",
                    "description": "Use Y00 screwdriver to remove 4 tripoint screws from Joy-Con back.",
                    "estimated_time": 10
                },
                {
                    "step_number": 3,
                    "title": "Replace Analog Stick",
                    "description": "Disconnect old module and install replacement stick.",
                    "estimated_time": 20
                },
                {
                    "step_number": 4,
                    "title": "Reassemble and Test",
                    "description": "Reassemble Joy-Con and test functionality.",
                    "estimated_time": 10
                }
            ]
        }
    ]
    
    for guide_data in guides:
        steps_data = guide_data.pop("steps")
        
        existing = db.query(RepairGuide).filter(
            RepairGuide.title == guide_data["title"]
        ).first()
        
        if not existing:
            guide = RepairGuide(**guide_data)
            db.add(guide)
            db.commit()
            db.refresh(guide)
            
            # Create steps
            for step_data in steps_data:
                step = RepairStep(
                    repair_guide_id=guide.id,
                    **step_data
                )
                db.add(step)
            
            db.commit()
            logger.info(f"Created repair guide: {guide.title}")


def create_sample_external_sources(db):
    """Create sample external data sources"""
    sources = [
        {
            "name": "iFixit API",
            "source_type": "ifixit",
            "base_url": "https://www.ifixit.com/api/2.0",
            "api_key_name": "IFIXIT_API_KEY",
            "config": {"rate_limit": 100, "timeout": 30}
        },
        {
            "name": "Reddit RepairGPT",
            "source_type": "reddit",
            "base_url": "https://www.reddit.com/r/repair",
            "config": {"subreddits": ["repair", "fixit", "diyrepair"]}
        }
    ]
    
    for source_data in sources:
        existing = db.query(ExternalDataSource).filter(
            ExternalDataSource.name == source_data["name"]
        ).first()
        
        if not existing:
            source = ExternalDataSource(**source_data)
            db.add(source)
            logger.info(f"Created external source: {source.name}")
    
    db.commit()


def load_sample_data():
    """Load comprehensive sample data"""
    logger.info("Loading sample data...")
    
    with get_db_session() as db:
        create_sample_devices(db)
        create_sample_issues(db)
        create_device_issue_relationships(db)
        create_sample_repair_guides(db)
        create_sample_external_sources(db)
    
    logger.info("Sample data loaded successfully")


def initialize_database(load_samples: bool = False):
    """Initialize the database with tables and optionally sample data"""
    logger.info("Initializing RepairGPT database...")
    
    try:
        # Create tables
        logger.info("Creating database tables...")
        create_tables()
        
        # Check database health
        if check_database_health():
            logger.info("Database health check passed")
        else:
            logger.error("Database health check failed")
            return False
        
        # Load sample data if requested
        if load_samples:
            load_sample_data()
        
        # Show database info
        info = get_database_info()
        logger.info(f"Database initialized successfully")
        logger.info(f"Database type: {info['database_type']}")
        logger.info(f"Tables created: {len(info['tables'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Initialize RepairGPT database")
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Load sample data (devices, issues, repair guides)"
    )
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Only check database health"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show database information"
    )
    
    args = parser.parse_args()
    
    if args.check_health:
        if check_database_health():
            print("✅ Database is healthy")
            return 0
        else:
            print("❌ Database health check failed")
            return 1
    
    if args.info:
        info = get_database_info()
        print(f"Database Type: {info['database_type']}")
        print(f"Environment: {info['environment']}")
        print(f"Health: {info['health_status']}")
        print(f"Tables: {len(info['tables'])}")
        if info['tables']:
            print("  - " + "\n  - ".join(info['tables']))
        return 0
    
    # Initialize database
    success = initialize_database(load_samples=args.sample_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())