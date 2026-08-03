import pytest
import asyncio
from core.models.automation_models import WorkflowStep
from engines.automation_engine.core.pipeline_coordinator import PipelineCoordinator

class MockEngineManager:
    def get_engine(self, name):
        class Engine:
            async def custom_action(self):
                return "custom_result"
        return Engine()

@pytest.mark.asyncio
async def test_pipeline_coordinator():
    manager = MockEngineManager()
    coordinator = PipelineCoordinator(manager)
    
    # Test mapped action
    step1 = WorkflowStep(step_id="1", engine_name="video_engine", action="extract_audio")
    res1 = await coordinator.execute_step(step1, {})
    assert res1["audio_path"] == "simulated_audio.wav"
    
    # Test fallback action
    step2 = WorkflowStep(step_id="2", engine_name="some_engine", action="custom_action")
    res2 = await coordinator.execute_step(step2, {})
    assert res2 == "custom_result"
