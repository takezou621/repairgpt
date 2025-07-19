"""Integration functionality test for RepairGPT"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))


class TestRepairGPTIntegration:
    """Integration tests for RepairGPT components"""
    
    def test_chatbot_initialization(self):
        """Test chatbot can be initialized"""
        from chat.llm_chatbot import RepairChatbot
        
        chatbot = RepairChatbot(preferred_model='enhanced_fallback')
        assert chatbot is not None
        assert hasattr(chatbot, 'chat')
        assert hasattr(chatbot, 'active_client')
    
    def test_chatbot_basic_functionality(self):
        """Test chatbot basic chat functionality"""
        from chat.llm_chatbot import RepairChatbot
        
        chatbot = RepairChatbot(preferred_model='enhanced_fallback')
        
        # Set context
        chatbot.update_context(
            device_type='smartphone',
            issue_description='screen crack',
            user_skill_level='beginner'
        )
        
        # Test chat
        response = chatbot.chat("My phone screen is cracked")
        assert isinstance(response, str)
        assert len(response) > 0
        assert 'RepairGPT' in response or 'repair' in response.lower()
    
    def test_ifixit_client_initialization(self):
        """Test iFixit client initialization"""
        from clients.ifixit_client import IFixitClient
        
        client = IFixitClient()
        assert client is not None
        assert hasattr(client, 'search_guides')
        assert hasattr(client, 'get_guide')
    
    def test_image_analysis_service_initialization(self):
        """Test image analysis service initialization"""
        from services.image_analysis import ImageAnalysisService
        
        service = ImageAnalysisService(provider='local')
        assert service is not None
        assert service.provider == 'local'
        assert hasattr(service, 'analyze_device_image')
    
    def test_image_analysis_mock_result(self):
        """Test mock image analysis result creation"""
        from services.image_analysis import create_mock_analysis_result, DeviceType
        
        result = create_mock_analysis_result(
            device_type='smartphone',
            condition='fair',
            language='en'
        )
        
        assert result is not None
        assert result.device_info.device_type == DeviceType.SMARTPHONE
        assert result.overall_condition == 'fair'
        assert result.language == 'en'
        assert len(result.damage_detected) > 0
    
    def test_repair_guide_service_initialization(self):
        """Test repair guide service initialization"""
        from services.repair_guide_service import RepairGuideService
        
        service = RepairGuideService(enable_offline_fallback=False)
        assert service is not None
        assert hasattr(service, 'search_guides')
        assert hasattr(service, 'get_guide_details')
    
    def test_streamlit_app_import(self):
        """Test that Streamlit app can be imported"""
        from ui.repair_app import main
        assert callable(main)
    
    def test_settings_configuration(self):
        """Test settings configuration"""
        from config.settings import get_settings
        
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'api_timeout_seconds')
        assert hasattr(settings, 'default_language')
    
    def test_logger_functionality(self):
        """Test logger functionality"""
        from utils.logger import get_logger
        
        logger = get_logger('test')
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_workflow_files_exist(self):
        """Test that CI/CD workflow files exist"""
        workflows_dir = Path(__file__).parent.parent / '.github' / 'workflows'
        
        assert workflows_dir.exists()
        
        expected_workflows = [
            'test.yml',
            'code-quality.yml', 
            'security-scan.yml',
            'release.yml'
        ]
        
        for workflow in expected_workflows:
            workflow_file = workflows_dir / workflow
            assert workflow_file.exists(), f"Workflow {workflow} not found"
    
    def test_documentation_exists(self):
        """Test that documentation files exist"""
        root_dir = Path(__file__).parent.parent
        docs_dir = root_dir / 'docs'
        
        assert (root_dir / 'README.md').exists()
        assert (root_dir / 'CLAUDE.md').exists()
        assert docs_dir.exists()
        assert (docs_dir / 'README.md').exists()


class TestRepairGPTFunctionalFlow:
    """Test complete functional flow"""
    
    def test_repair_consultation_flow(self):
        """Test complete repair consultation flow"""
        from chat.llm_chatbot import RepairChatbot
        from services.image_analysis import create_mock_analysis_result
        
        # 1. Initialize chatbot
        chatbot = RepairChatbot(preferred_model='enhanced_fallback')
        
        # 2. Set device context
        chatbot.update_context(
            device_type='Nintendo Switch',
            device_model='OLED',
            issue_description='Joy-Con drift',
            user_skill_level='beginner'
        )
        
        # 3. Get initial diagnosis
        initial_response = chatbot.chat("My Joy-Con is drifting, what should I do?")
        assert isinstance(initial_response, str)
        assert len(initial_response) > 0
        
        # 4. Mock image analysis
        image_result = create_mock_analysis_result(
            device_type='gaming_console',
            condition='fair',
            language='en'
        )
        
        # 5. Follow-up question
        followup_response = chatbot.chat("I've tried calibration, what's next?")
        assert isinstance(followup_response, str)
        assert len(followup_response) > 0
        
        # 6. Verify conversation history
        assert len(chatbot.conversation_history) >= 4  # 2 user + 2 assistant
        
        # 7. Get conversation summary
        summary = chatbot.get_conversation_summary()
        assert isinstance(summary, dict)
        assert 'session_id' in summary
        assert 'message_count' in summary
        assert summary['message_count'] >= 4
    
    def test_multilingual_support(self):
        """Test multilingual support"""
        from chat.llm_chatbot import RepairChatbot
        from services.image_analysis import create_mock_analysis_result
        
        # English test
        en_result = create_mock_analysis_result(language='en')
        assert en_result.language == 'en'
        assert any('repair' in action.lower() for action in en_result.recommended_actions)
        
        # Japanese test  
        ja_result = create_mock_analysis_result(language='ja')
        assert ja_result.language == 'ja'
        assert any('修理' in action for action in ja_result.recommended_actions)
    
    def test_service_integration(self):
        """Test services can work together"""
        from services.image_analysis import ImageAnalysisService
        from services.repair_guide_service import RepairGuideService
        
        # Initialize services
        image_service = ImageAnalysisService(provider='local')
        guide_service = RepairGuideService(enable_offline_fallback=False)
        
        # Get service stats
        image_stats = image_service.get_analysis_stats()
        guide_stats = guide_service.get_cache_stats()
        
        assert isinstance(image_stats, dict)
        assert isinstance(guide_stats, dict)
        
        assert 'provider' in image_stats
        assert 'redis_available' in guide_stats


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])
