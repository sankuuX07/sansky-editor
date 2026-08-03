import pytest
import asyncio
from pathlib import Path
from engines.shorts_generator_engine.managers.workflow_launcher import WorkflowLauncher
from core.models.shorts_models import ProcessingRequest
from core.models.automation_models import WorkflowStatus

class MockTemplateManager:
    def get_gaming_shorts_template(self):
        from core.models.automation_models import Workflow, WorkflowStep
        return Workflow("Test", steps=[WorkflowStep(step_id="extract_audio", engine_name="v", action="a")])

class MockAutomationEngine:
    def __init__(self):
        self.template_manager = MockTemplateManager()
        
    async def run_workflow(self, workflow):
        workflow.status = WorkflowStatus.COMPLETED
        workflow.steps[0].result = "success"

@pytest.mark.asyncio
async def test_workflow_launcher():
    engine = MockAutomationEngine()
    launcher = WorkflowLauncher(engine)
    req = ProcessingRequest([])
    
    res = await launcher.launch_for_video(req, Path("test.mp4"))
    assert res["extract_audio"] == "success"
