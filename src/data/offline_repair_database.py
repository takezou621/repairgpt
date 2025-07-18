"""
Offline Repair Database for RepairGPT
Provides repair guides when online services are unavailable
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class OfflineGuide:
    """Offline repair guide structure"""

    id: str
    title: str
    device: str
    category: str
    difficulty: str
    time_estimate: str
    cost_estimate: str
    tools_required: List[str]
    parts_required: List[str]
    steps: List[Dict[str, str]]
    warnings: List[str]
    tips: List[str]
    success_rate: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class OfflineRepairDatabase:
    """Offline repair database with common repair guides"""

    def __init__(self):
        self.guides = self._load_repair_guides()

    def _load_repair_guides(self) -> List[OfflineGuide]:
        """Load comprehensive repair guides database"""

        guides_data = [
            # Nintendo Switch Joy-Con Drift
            {
                "id": "switch_joycon_drift",
                "title": "Nintendo Switch Joy-Con Analog Stick Drift Repair",
                "device": "Nintendo Switch",
                "category": "Controller Repair",
                "difficulty": "Medium",
                "time_estimate": "30-60 minutes",
                "cost_estimate": "$5-25",
                "tools_required": [
                    "Y00 Tripoint screwdriver",
                    "Phillips PH000 screwdriver",
                    "Plastic prying tools",
                    "Tweezers",
                    "Compressed air",
                    "Electrical contact cleaner (optional)",
                ],
                "parts_required": [
                    "Replacement analog stick module (if replacing)",
                    "Ribbon cable (if damaged)",
                ],
                "steps": [
                    {
                        "step": "1",
                        "title": "Power Off and Prepare",
                        "description": "Power off Switch completely. Remove Joy-Con from console. Gather tools and work in well-lit, static-free area.",
                    },
                    {
                        "step": "2",
                        "title": "Remove Back Cover",
                        "description": "Use Y00 screwdriver to remove 4 tripoint screws from Joy-Con back. Carefully lift back cover.",
                    },
                    {
                        "step": "3",
                        "title": "Disconnect Battery",
                        "description": "Locate small battery connector. Carefully disconnect by pulling connector straight up with tweezers.",
                    },
                    {
                        "step": "4",
                        "title": "Access Analog Stick",
                        "description": "Remove additional screws to access analog stick module. Note cable routing for reassembly.",
                    },
                    {
                        "step": "5",
                        "title": "Clean or Replace",
                        "description": "For cleaning: Use compressed air and contact cleaner around mechanism. For replacement: Disconnect ribbon cable and remove old module.",
                    },
                    {
                        "step": "6",
                        "title": "Reassemble",
                        "description": "Install new module or reassemble cleaned components. Reconnect all cables. Replace screws in reverse order.",
                    },
                    {
                        "step": "7",
                        "title": "Test",
                        "description": "Power on and test analog stick in System Settings > Controllers and Sensors > Calibrate Control Sticks.",
                    },
                ],
                "warnings": [
                    "Warranty will be voided",
                    "Ribbon cables are fragile - handle carefully",
                    "Keep track of small screws",
                    "Static electricity can damage components",
                ],
                "tips": [
                    "Try recalibration and cleaning before disassembly",
                    "Take photos during disassembly for reference",
                    "Work over a clean, organized surface",
                    "Contact cleaner may provide temporary fix",
                ],
                "success_rate": "85% with replacement, 60% with cleaning",
            },
            # iPhone Screen Replacement
            {
                "id": "iphone_screen_replacement",
                "title": "iPhone Screen Replacement Guide",
                "device": "iPhone",
                "category": "Screen Repair",
                "difficulty": "Hard",
                "time_estimate": "1-2 hours",
                "cost_estimate": "$50-200",
                "tools_required": [
                    "Pentalobe P2 screwdriver",
                    "Phillips PH000 screwdriver",
                    "Suction cup",
                    "Plastic picks",
                    "Spudger tools",
                    "Heat gun or hair dryer",
                    "iOpener or heat pads",
                ],
                "parts_required": [
                    "Replacement screen assembly",
                    "Adhesive strips",
                    "Screen protector (optional)",
                ],
                "steps": [
                    {
                        "step": "1",
                        "title": "Power Down and Prepare",
                        "description": "Power off iPhone completely. Discharge battery below 25% to reduce fire risk. Remove SIM card tray.",
                    },
                    {
                        "step": "2",
                        "title": "Remove Pentalobe Screws",
                        "description": "Remove two pentalobe screws next to Lightning port using P2 screwdriver.",
                    },
                    {
                        "step": "3",
                        "title": "Heat and Separate",
                        "description": "Apply heat around edges to soften adhesive. Use suction cup and picks to carefully separate screen.",
                    },
                    {
                        "step": "4",
                        "title": "Disconnect Cables",
                        "description": "Remove bracket screws and carefully disconnect display, digitizer, and front camera cables.",
                    },
                    {
                        "step": "5",
                        "title": "Transfer Components",
                        "description": "Transfer home button, front camera, speaker, and other components to new screen assembly.",
                    },
                    {
                        "step": "6",
                        "title": "Install New Screen",
                        "description": "Connect all cables to new screen. Apply new adhesive strips and carefully position screen.",
                    },
                    {
                        "step": "7",
                        "title": "Test and Seal",
                        "description": "Test all functions before final assembly. Press firmly to seat adhesive. Replace pentalobe screws.",
                    },
                ],
                "warnings": [
                    "Extremely delicate repair - high risk of damage",
                    "Warranty will be voided",
                    "Risk of cutting fingers on broken glass",
                    "Battery must be discharged to prevent fire",
                    "Water resistance will be compromised",
                ],
                "tips": [
                    "Consider professional repair for valuable devices",
                    "Practice on old device first",
                    "Take detailed photos during disassembly",
                    "Use proper lighting and magnification",
                    "Have backup device ready in case of failure",
                ],
                "success_rate": "70% for experienced repairers, 40% for beginners",
            },
            # Laptop Won't Boot
            {
                "id": "laptop_boot_troubleshooting",
                "title": "Laptop Won't Boot - Comprehensive Troubleshooting",
                "device": "Laptop",
                "category": "Boot Issues",
                "difficulty": "Easy to Medium",
                "time_estimate": "30 minutes - 2 hours",
                "cost_estimate": "$0-150",
                "tools_required": [
                    "Phillips screwdrivers",
                    "Anti-static wrist strap",
                    "External monitor",
                    "USB keyboard/mouse",
                    "Bootable USB drive",
                    "Multimeter (advanced)",
                ],
                "parts_required": [
                    "Replacement RAM (if testing)",
                    "New power adapter (if needed)",
                    "Replacement hard drive/SSD (if failed)",
                ],
                "steps": [
                    {
                        "step": "1",
                        "title": "Power Supply Check",
                        "description": "Verify power adapter is working. Try different outlet. Remove battery and run on adapter only.",
                    },
                    {
                        "step": "2",
                        "title": "Hard Reset",
                        "description": "Disconnect all power sources. Hold power button for 30 seconds. Reconnect power and attempt boot.",
                    },
                    {
                        "step": "3",
                        "title": "External Display Test",
                        "description": "Connect external monitor. If external display works, issue is with laptop screen or connection.",
                    },
                    {
                        "step": "4",
                        "title": "Memory Test",
                        "description": "Remove and reseat RAM modules. Test with one stick at a time. Try RAM in different slots.",
                    },
                    {
                        "step": "5",
                        "title": "Boot Diagnostics",
                        "description": "Access BIOS/UEFI. Run built-in hardware diagnostics. Check boot order and settings.",
                    },
                    {
                        "step": "6",
                        "title": "Storage Test",
                        "description": "Boot from USB drive to test if hard drive has failed. Run disk check utilities.",
                    },
                    {
                        "step": "7",
                        "title": "Professional Diagnosis",
                        "description": "If previous steps fail, likely motherboard issue. Consider professional repair service.",
                    },
                ],
                "warnings": [
                    "Remove battery before working inside laptop",
                    "Use anti-static protection",
                    "Don't force components",
                    "Some laptops void warranty when opened",
                ],
                "tips": [
                    "Document cable positions before disconnecting",
                    "Clean dust from vents during repair",
                    "Check for loose connections",
                    "Some issues resolve with time and retrying",
                ],
                "success_rate": "Power issues: 85%, RAM issues: 90%, Storage: 80%, Motherboard: 25%",
            },
            # PlayStation 5 Overheating
            {
                "id": "ps5_overheating_fix",
                "title": "PlayStation 5 Overheating and Thermal Issues",
                "device": "PlayStation 5",
                "category": "Cooling System",
                "difficulty": "Medium",
                "time_estimate": "45-90 minutes",
                "cost_estimate": "$10-50",
                "tools_required": [
                    "Phillips screwdrivers",
                    "Torx T8 screwdriver",
                    "Compressed air",
                    "Thermal paste",
                    "Plastic prying tools",
                    "Cotton swabs",
                    "Isopropyl alcohol",
                ],
                "parts_required": [
                    "Thermal paste (Arctic MX-4 or similar)",
                    "Thermal pads (if replacing)",
                ],
                "steps": [
                    {
                        "step": "1",
                        "title": "Initial Assessment",
                        "description": "Verify overheating symptoms: loud fan, hot exhaust, thermal shutdowns. Ensure proper ventilation around console.",
                    },
                    {
                        "step": "2",
                        "title": "External Cleaning",
                        "description": "Power off completely. Clean intake and exhaust vents with compressed air. Remove visible dust buildup.",
                    },
                    {
                        "step": "3",
                        "title": "Disassembly",
                        "description": "Remove base, back panel, and side covers. Disconnect fan connector. Remove screws securing heat sink.",
                    },
                    {
                        "step": "4",
                        "title": "Clean Heat Sink",
                        "description": "Remove heat sink assembly. Clean old thermal paste from CPU and heat sink with isopropyl alcohol.",
                    },
                    {
                        "step": "5",
                        "title": "Apply New Thermal Paste",
                        "description": "Apply thin, even layer of new thermal paste to CPU. Use rice grain size amount.",
                    },
                    {
                        "step": "6",
                        "title": "Reassemble",
                        "description": "Reinstall heat sink with proper screw torque sequence. Reconnect fan. Replace panels in reverse order.",
                    },
                    {
                        "step": "7",
                        "title": "Test",
                        "description": "Power on and run demanding game. Monitor temperatures and fan noise for improvement.",
                    },
                ],
                "warnings": [
                    "Warranty will be voided",
                    "Console must be completely powered off",
                    "Don't overtighten screws on heat sink",
                    "Thermal paste is messy - protect workspace",
                ],
                "tips": [
                    "Clean console every 6-12 months",
                    "Ensure 6+ inches clearance around vents",
                    "Consider vertical stand for better airflow",
                    "Monitor system storage - full drives generate more heat",
                ],
                "success_rate": "90% for dust-related issues, 70% for thermal paste issues",
            },
        ]

        # Convert to OfflineGuide objects
        guides = []
        for guide_data in guides_data:
            try:
                guide = OfflineGuide(**guide_data)
                guides.append(guide)
            except Exception as e:
                logger.error(
                    f"Error loading guide {guide_data.get('id', 'unknown')}: {e}"
                )

        logger.info(f"Loaded {len(guides)} offline repair guides")
        return guides

    def search_guides(
        self, query: str, device_type: str = "", limit: int = 10
    ) -> List[OfflineGuide]:
        """Search offline repair guides"""
        query_lower = query.lower()
        device_lower = device_type.lower()

        matching_guides = []

        for guide in self.guides:
            # Check if query matches guide content
            searchable_text = f"{guide.title} {guide.device} {guide.category}".lower()

            # Add device context if provided
            if device_lower and device_lower not in searchable_text:
                continue

            # Check for query matches
            if any(term in searchable_text for term in query_lower.split()):
                matching_guides.append(guide)

        # Sort by relevance (exact device matches first)
        if device_lower:
            matching_guides.sort(
                key=lambda g: device_lower in g.device.lower(), reverse=True
            )

        return matching_guides[:limit]

    def get_guide_by_id(self, guide_id: str) -> Optional[OfflineGuide]:
        """Get specific guide by ID"""
        for guide in self.guides:
            if guide.id == guide_id:
                return guide
        return None

    def get_guides_by_device(
        self, device_type: str, limit: int = 10
    ) -> List[OfflineGuide]:
        """Get guides for specific device type"""
        device_lower = device_type.lower()

        matching_guides = [
            guide for guide in self.guides if device_lower in guide.device.lower()
        ]

        return matching_guides[:limit]

    def get_all_devices(self) -> List[str]:
        """Get list of all devices with guides"""
        devices = set()
        for guide in self.guides:
            devices.add(guide.device)
        return sorted(list(devices))

    def get_all_categories(self) -> List[str]:
        """Get list of all repair categories"""
        categories = set()
        for guide in self.guides:
            categories.add(guide.category)
        return sorted(list(categories))

    def export_guides(self, filepath: str):
        """Export guides to JSON file"""
        guides_dict = [guide.to_dict() for guide in self.guides]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(guides_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self.guides)} guides to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    print("Testing Offline Repair Database...")

    # Initialize database
    db = OfflineRepairDatabase()

    print(f"\nLoaded {len(db.guides)} repair guides")
    print(f"Available devices: {db.get_all_devices()}")
    print(f"Available categories: {db.get_all_categories()}")

    # Test searches
    print("\n1. Searching for 'joy-con drift':")
    results = db.search_guides("joy-con drift")
    for guide in results:
        print(f"   - {guide.title} ({guide.difficulty})")

    print("\n2. Searching for iPhone guides:")
    results = db.search_guides("screen", "iPhone")
    for guide in results:
        print(f"   - {guide.title} ({guide.difficulty})")

    print("\n3. Getting specific guide details:")
    guide = db.get_guide_by_id("switch_joycon_drift")
    if guide:
        print(f"   Title: {guide.title}")
        print(f"   Steps: {len(guide.steps)} steps")
        print(f"   Success Rate: {guide.success_rate}")

    print("\nOffline repair database test completed!")
