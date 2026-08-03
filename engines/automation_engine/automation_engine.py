"""
The Automation Engine Facade.
"""
import logging
import asyncio
from engines.base_engine import BaseEngine
from core.models.shared_types import EngineStatus
from core.exceptions.exceptions import EngineInitError

from app.services.engine_manager import EngineManager
from app.scheduler.task_manager import TaskManager

from engines.automation_engine.core.workflow_validator import WorkflowValidator
from engines.automation_engine.core.task_scheduler import TaskScheduler
from engines.automation_engine.core.pipeline_coordinator import PipelineCoordinator
from engines.automation_engine.core.workflow_executor import WorkflowExecutor
from engines.automation_engine.core.automation_logger import AutomationLogger

from engines.automation_engine.managers.workflow_manager import WorkflowManager
from engines.automation_engine.managers.progress_manager import ProgressManager
from engines.automation_engine.managers.error_recovery_manager import ErrorRecoveryManager
from engines.automation_engine.managers.workflow_template_manager import WorkflowTemplateManager
from core.models.automation_models import Workflow

class AutomationEngine(BaseEngine):
    """Orchestrates workflows across all other engines."""
    def __init__(self, engine_manager: EngineManager, task_manager: TaskManager) -> None:
        super().__init__("automation_engine")
        
        self.workflow_manager = WorkflowManager()
        self.progress_manager = ProgressManager()
        self.recovery_manager = ErrorRecoveryManager()
        self.template_manager = WorkflowTemplateManager()
        
        self.validator = WorkflowValidator(engine_manager)
        self.scheduler = TaskScheduler(task_manager)
        self.coordinator = PipelineCoordinator(engine_manager)
        self.logger_util = AutomationLogger()
        
        self.executor = WorkflowExecutor(
            self.coordinator, 
            self.scheduler, 
            self.progress_manager, 
            self.recovery_manager
        )

    def initialize(self) -> None:
        self._status = EngineStatus.INITIALIZING
        self.logger.info("Initializing Automation Engine...")
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = True
        self.logger.info("Automation Engine initialized successfully.")

    def start(self) -> None:
        if not self.is_initialized:
            raise EngineInitError("Cannot start uninitialized AutomationEngine")
        self._status = EngineStatus.RUNNING
        self.is_running = True
        self.logger.info("Automation Engine started.")

    def stop(self) -> None:
        self._status = EngineStatus.STOPPED
        self.is_running = False
        self.logger.info("Automation Engine stopped.")

    def shutdown(self) -> None:
        self.stop()
        self._status = EngineStatus.UNINITIALIZED
        self.is_initialized = False
        self.logger.info("Automation Engine shutdown.")

    def health_check(self) -> bool:
        return self._status == EngineStatus.RUNNING
        
    async def run_workflow(self, workflow: Workflow) -> None:
        self.logger_util.log_start(workflow)
        self.workflow_manager.register_workflow(workflow)
        self.validator.validate(workflow)
        await self.executor.execute(workflow)
        self.logger_util.log_end(workflow)
