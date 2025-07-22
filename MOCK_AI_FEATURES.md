# Mock AI Features for RepairGPT

This document describes the mock AI functionality added to RepairGPT for testing and development without requiring API keys.

## Overview

RepairGPT now includes comprehensive mock AI functionality that allows you to test and demonstrate the application without configuring real API keys for OpenAI, Claude, or other AI services.

## Features

### 1. Mock Chat Responses
- Context-aware responses based on user input
- Device-specific repair guidance for Joy-Con drift, iPhone screen issues, battery problems
- Safety warnings and tool recommendations
- Generic repair advice for unrecognized issues

### 2. Mock Device Diagnosis
- Detailed diagnosis based on device type and issue description
- Confidence scores and severity assessments
- Repair recommendations with cost estimates
- Required tools and safety warnings
- Difficulty levels and time estimates

### 3. Mock Image Analysis
- Simulated damage detection based on image properties
- Various damage types: screen cracks, scratches, physical damage
- Repair recommendations with cost estimates
- Safety notes and required tools

## Configuration

### Automatic Mock Mode (Default)
By default, RepairGPT automatically enables mock mode when no API keys are configured:

```bash
# No API keys needed - mock mode will be used automatically
python run_app.py
```

### Manual Configuration
You can explicitly control mock mode using environment variables:

```bash
# Force mock mode on (even if API keys are available)
export REPAIRGPT_USE_MOCK_AI=true

# Force mock mode off (require real API keys)
export REPAIRGPT_USE_MOCK_AI=false

# Auto mode (default) - use mock only if no API keys available
export REPAIRGPT_USE_MOCK_AI=auto
```

## Mock Response Examples

### Chat Response Example
```
🤖 **Mock AI Response** (API keys not configured)

I understand you're experiencing Joy-Con drift issues. This is a common problem with Nintendo Switch controllers.

**Common Solutions:**
1. **Recalibration**: Go to System Settings > Controllers and Sensors > Calibrate Control Sticks
2. **Cleaning**: Use compressed air around the analog stick base
3. **Contact Cleaner**: Apply electrical contact cleaner under the rubber cap (advanced users)
4. **Replacement**: The analog stick mechanism can be replaced with proper tools

**Tools Needed:**
- Compressed air
- Electrical contact cleaner (optional)
- Y00 Tripoint screwdriver (for replacement)
- Plastic prying tools

⚠️ **Safety Note**: Always power off your device before attempting repairs.

*This is a mock response for testing. Configure API keys for real AI assistance.*
```

### Diagnosis Response Example
```json
{
  "diagnosis": "Joy-Con analog stick drift detected",
  "confidence": 0.85,
  "possible_causes": [
    "Worn analog stick mechanism",
    "Dust or debris buildup under the stick",
    "Electrical contact degradation"
  ],
  "recommended_actions": [
    "Try recalibrating the Joy-Con in System Settings",
    "Clean around the analog stick with compressed air",
    "Replace the analog stick module"
  ],
  "safety_warnings": [
    "Power off the device before any physical repairs",
    "Use proper tools to avoid damage"
  ],
  "estimated_difficulty": "Easy to Moderate",
  "estimated_time": "10-45 minutes",
  "success_rate": "70-95%"
}
```

## API Endpoints with Mock Support

### Chat Endpoint
- **URL**: `POST /api/v1/chat`
- **Mock Features**: Context-aware responses, device-specific guidance
- **Mock Indicator**: Responses include "Mock AI Response" header

### Diagnose Endpoint
- **URL**: `POST /api/v1/diagnose`
- **Mock Features**: Device-specific diagnosis, repair recommendations
- **Mock Data**: Realistic confidence scores, cost estimates, tool requirements

### Image Analysis (Future)
- **URL**: `POST /api/v1/image/analyze`
- **Mock Features**: Simulated damage detection, repair suggestions
- **Mock Logic**: Based on image dimensions and properties

## Development Benefits

1. **No Setup Required**: Test the application immediately without API key configuration
2. **Consistent Results**: Predictable responses for testing and demonstrations
3. **Cost-Free Testing**: No API charges during development
4. **Feature Coverage**: All major AI features have mock implementations
5. **Educational Content**: Realistic repair guidance for learning purposes

## Switching to Real AI

To use real AI services, simply configure the appropriate API keys:

```bash
# For OpenAI (GPT-4, Vision)
export REPAIRGPT_OPENAI_API_KEY="sk-..."

# For Anthropic Claude
export REPAIRGPT_ANTHROPIC_API_KEY="sk-ant-..."

# For iFixit integration
export REPAIRGPT_IFIXIT_API_KEY="your-ifixit-key"
```

Once API keys are configured, the application will automatically switch from mock mode to real AI services.

## Technical Implementation

### Mock Response Generation
- **Keyword Detection**: Responses are tailored based on device type and issue keywords
- **Contextual Information**: Device context is included in responses when available
- **Processing Simulation**: Artificial delays simulate real API response times
- **Realistic Data**: Mock responses include realistic repair data and safety information

### Integration Points
- **Chat Service**: `RepairChatbot` class with `use_mock` parameter
- **Diagnosis Service**: Mock diagnosis generation in API routes
- **Image Analysis**: Mock damage detection in `ImageAnalysisService`
- **Configuration**: Automatic mock detection via `settings.should_use_mock_ai()`

## Testing

You can test the mock functionality by:

1. **Starting the application without API keys**:
   ```bash
   python run_app.py
   ```

2. **Using the web interface** at http://localhost:8501

3. **Testing API endpoints directly**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "My Joy-Con is drifting", "device_type": "nintendo_switch"}'
   ```

4. **Verifying mock responses** contain the "Mock AI Response" indicator

## Future Enhancements

- Enhanced mock responses with more device-specific knowledge
- Mock image analysis with simulated computer vision results
- Mock integration with external repair databases
- Advanced context awareness in mock responses