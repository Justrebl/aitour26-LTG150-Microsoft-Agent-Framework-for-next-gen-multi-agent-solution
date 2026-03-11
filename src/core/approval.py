"""
Human approval workflow components for Zava clothing concept evaluation.

This module handles the human-in-the-loop approval process where Zava team members
review and make final decisions on clothing concept submissions.
"""

from typing import Any
from dataclasses import dataclass

from agent_framework import (
    Executor,
    WorkflowContext,
    handler,
    response_handler,
    executor,
)

# Module-level cache for passing analysis content through the approval flow
_approval_cache: dict[str, str] = {}


@dataclass
class ClothingConceptApprovalRequest:
    """
    Data structure for requesting human approval of clothing concepts.

    This class extends RequestInfoMessage to provide structured approval
    requests for Zava's clothing concept evaluation workflow.
    """

    question: str = "Do you approve this clothing concept? (yes/no)"
    context: str = ""
    analysis_content: str = ""  # Store the analysis content in the request

    def __str__(self) -> str:
        """Return a formatted string representation of the approval request."""
        return f"""
ZAVA CLOTHING CONCEPT APPROVAL REQUEST

{self.question}

CONCEPT ANALYSIS CONTEXT:
{self.context}

Please review the above analysis and decide whether to approve this clothing
concept for development or reject it for reconsideration.

Response Options:
- Type 'yes' to APPROVE the concept for development
- Type 'no' to REJECT the concept

Your decision will determine the next steps in our evaluation process.
        """.strip()


@dataclass
class ZavaApprovalDecision:
    """
    Data structure to represent approval decisions for clothing concepts.

    This class encapsulates the decision outcome and associated metadata
    for tracking approval workflow results.
    """

    approved: bool
    feedback: str = ""
    analysis_content: str = ""  # Store the analysis content for saving

    def __str__(self) -> str:
        """Return a formatted string representation of the decision."""
        status = "APPROVED" if self.approved else "REJECTED"
        return f"Decision: {status}" + (f" - {self.feedback}" if self.feedback else "")


class ZavaConceptApprovalManager(Executor):
    """
    Manages the human approval workflow for clothing concept evaluation.

    This executor handles the routing of approval requests and processes
    the human decisions to determine next steps in the workflow.
    """

    def __init__(self, id: str = "zava_approval_manager"):
        super().__init__(id=id)

    @handler
    async def start_approval(self, analysis_results: Any, ctx: WorkflowContext[str]) -> None:
        """Initiates approval request to human."""
        print("=" * 80)
        print("APPROVAL MANAGER: start_approval handler called")
        print("=" * 80)
        print(f"APPROVAL MANAGER: Received analysis_results type: {type(analysis_results)}")
        print(f"APPROVAL MANAGER: Analysis results length: {len(str(analysis_results))} chars")
        print("Starting Zava concept approval process...")

        # Extract key information from analysis results
        analysis_text = str(analysis_results) if analysis_results else "No analysis provided"

        # Store analysis content in cache for later retrieval by route_decision
        _approval_cache["analysis_content"] = analysis_text

        print("=" * 60)
        print("FASHION ANALYSIS RESULTS:")
        print("=" * 60)
        print(analysis_text[:1000] + ('...' if len(analysis_text) > 1000 else ''))
        print("=" * 60)

        # Build a plain-string approval request (JSON-serializable for DevUI)
        approval_text = f"""ZAVA CLOTHING CONCEPT APPROVAL REQUEST

Based on the comprehensive fashion analysis above, should Zava approve this clothing concept for development?

COMPREHENSIVE CLOTHING CONCEPT ANALYSIS SUMMARY

{analysis_text}

KEY DECISION FACTORS:
• Market alignment with current fashion trends
• Design innovation and brand fit with Zava
• Production feasibility and cost considerations
• Competitive differentiation potential
• Strategic alignment with company goals

Please type 'yes' to APPROVE or 'no' to REJECT."""

        print("APPROVAL MANAGER: Sending approval request to Zava design team...")
        await ctx.send_message(approval_text)
        print("APPROVAL MANAGER: Approval request sent successfully to human approver")
        print("=" * 80)

    @response_handler
    async def route_decision(
        self,
        request: str,
        response: str,
        ctx: WorkflowContext[str]
    ) -> None:
        """Processes human response and prepares routing decision."""
        print("=" * 80)
        print("APPROVAL MANAGER: route_decision handler called")
        print("=" * 80)
        print(f"APPROVAL MANAGER: Received response type: {type(response)}")
        print(f"APPROVAL MANAGER: Response data: {response}")

        print("Processing human approval response...")
        human_input = (response or "").strip().lower()
        print(f"APPROVAL MANAGER: Human input normalized: '{human_input}'")

        # Parse human input into routing decision
        approved = human_input in ["yes", "y", "approve", "approved"]
        print(f"APPROVAL MANAGER: Approval status: {approved}")

        # Retrieve analysis content from cache
        analysis_content = _approval_cache.get("analysis_content", "")
        print(f"APPROVAL MANAGER: Analysis content length: {len(analysis_content)} chars")

        # Send a plain-string decision (JSON-serializable for DevUI)
        decision_str = f"APPROVED|{response or ''}|{analysis_content}" if approved else f"REJECTED|{response or ''}|{analysis_content}"
        print(f"Zava team decision - {'APPROVED' if approved else 'REJECTED'}")
        print("APPROVAL MANAGER: Sending decision to trigger conditional routing...")
        await ctx.send_message(decision_str)
        print("APPROVAL MANAGER: Decision sent successfully")
        print("=" * 80)


def concept_approval_condition(decision: Any) -> bool:
    """
    Condition function to check if a clothing concept was approved.

    Decision is a string starting with 'APPROVED|' or 'REJECTED|'.
    """
    decision_str = str(decision).strip()
    print(f"CONDITION: concept_approval_condition - decision starts with: {decision_str[:20]}")
    return decision_str.startswith("APPROVED|")


def concept_rejection_condition(decision: Any) -> bool:
    """
    Condition function to check if a clothing concept was rejected.

    Decision is a string starting with 'APPROVED|' or 'REJECTED|'.
    """
    decision_str = str(decision).strip()
    print(f"CONDITION: concept_rejection_condition - decision starts with: {decision_str[:20]}")
    return decision_str.startswith("REJECTED|")


def create_auto_approver():
    """Create an executor that auto-approves concepts (for DevUI mode).

    DevUI does not support human-in-the-loop for workflows.
    This executor automatically sends a 'no' response so the workflow completes
    end-to-end in DevUI for demonstration and tracing purposes.
    """

    @executor(id="zava_human_approver")
    async def auto_approve_executor(request: str, ctx: WorkflowContext) -> None:
        print("AUTO-APPROVE: Automatically rejecting concept (DevUI mode)")
        await ctx.send_message("no")

    return auto_approve_executor


def create_zava_human_approver():
    """
    Create a human approver executor for Zava clothing concept decisions.

    Uses ctx.request_info() to pause the workflow and request human input.

    Returns:
        Executor configured for human approval workflow
    """

    @executor(id="zava_human_approver")
    async def human_approver_executor(request: str, ctx: WorkflowContext) -> None:
        print("HUMAN APPROVER: Requesting human approval via request_info...")
        await ctx.request_info(request, str)
        print("HUMAN APPROVER: request_info sent, workflow will pause for response.")

    return human_approver_executor


# Convenience aliases for backward compatibility and clarity
yes_condition = concept_approval_condition
no_condition = concept_rejection_condition