"""
Standalone workflow builder for Zava Clothing Concept Analysis.

Builds the complete workflow graph without UI-specific callbacks or progress tracking,
suitable for use with DevUI or any other runner.
"""

import os
from typing import List, Any

from agent_framework import WorkflowBuilder, WorkflowExecutor

from core.executors import (
    process_clothing_concept_pitch,
    log_fashion_analysis_outputs,
    adapt_concept_for_analysis,
    extract_analysis_prompt,
    convert_report_to_approval_request,
    save_approved_concept_report,
    draft_concept_rejection_email,
    handle_approved_concept,
    handle_rejected_concept,
)
from core.agents import (
    create_concurrent_fashion_analysis_workflow,
    create_concept_report_writer_agent,
)
from core.approval import (
    ZavaConceptApprovalManager,
    create_auto_approver,
    create_zava_human_approver,
    concept_approval_condition,
    concept_rejection_condition,
)


def create_chat_clients() -> List[Any]:
    """Create Azure AI Agent chat clients from environment variables."""
    from agent_framework_azure_ai import AzureAIAgentClient
    from azure.identity.aio import AzureCliCredential

    project_endpoint = (
        os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        or os.getenv("FOUNDRY_PROJECT_ENDPOINT")
        or os.getenv("PROJECT_ENDPOINT")
    )
    if not project_endpoint:
        raise ValueError(
            "AZURE_AI_PROJECT_ENDPOINT, FOUNDRY_PROJECT_ENDPOINT, or PROJECT_ENDPOINT "
            "environment variable is required."
        )

    model_deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    if not model_deployment_name:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME environment variable is required.")

    credential = AzureCliCredential()

    # Three separate clients to avoid agent instruction caching
    return [
        AzureAIAgentClient(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            async_credential=credential,
        )
        for _ in range(3)
    ]


async def build_workflow(chat_clients: List[Any], auto_approve: bool = False):
    """
    Build the complete Zava clothing concept evaluation workflow.

    Args:
        chat_clients: List of Azure AI Agent chat clients.
        auto_approve: If True, skip human approval (auto-approve). Used for DevUI mode.

    Returns:
        A built Workflow ready to be served by DevUI or executed programmatically.
    """
    concept_report_writer = create_concept_report_writer_agent(chat_clients)
    concurrent_analysis_workflow = await create_concurrent_fashion_analysis_workflow(chat_clients)
    concurrent_analysis_subworkflow = WorkflowExecutor(
        concurrent_analysis_workflow, id="concurrent_fashion_analysis"
    )

    human_approver = create_auto_approver() if auto_approve else create_zava_human_approver()
    approval_manager = ZavaConceptApprovalManager()

    workflow = (
        WorkflowBuilder()
        .set_start_executor(process_clothing_concept_pitch)
        .add_edge(process_clothing_concept_pitch, adapt_concept_for_analysis)
        .add_edge(adapt_concept_for_analysis, extract_analysis_prompt)
        .add_edge(extract_analysis_prompt, concurrent_analysis_subworkflow)
        .add_edge(concurrent_analysis_subworkflow, log_fashion_analysis_outputs)
        .add_edge(log_fashion_analysis_outputs, concept_report_writer)
        .add_edge(concept_report_writer, convert_report_to_approval_request)
        .add_edge(convert_report_to_approval_request, approval_manager)
        .add_edge(approval_manager, human_approver)
        .add_edge(human_approver, approval_manager)
        .add_edge(approval_manager, save_approved_concept_report, condition=concept_approval_condition)
        .add_edge(approval_manager, draft_concept_rejection_email, condition=concept_rejection_condition)
        .add_edge(save_approved_concept_report, handle_approved_concept)
        .add_edge(draft_concept_rejection_email, handle_rejected_concept)
        .build()
    )

    return workflow
