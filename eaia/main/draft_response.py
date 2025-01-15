"""Core agent responsible for impact analysis and translation between teams."""

from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.store.base import BaseStore

from schemas import (
    State,
    EngineeringImpactAnalysis,
    BusinessImpactAnalysis,
    ClarificationQuestion,
    CoordinationAction,
    CreateJiraTicket,
    Escalate,
    change_template,
)
from config import get_config

IMPACT_ANALYSIS_INSTRUCTIONS = """You are a Change Impact Coordinator responsible for analyzing changes and coordinating between Engineering and Business teams.

Your role is to:
1. Analyze incoming changes
2. Determine the primary impact domain (Engineering or Business)
3. Route to appropriate team
4. Translate implications for the other team
5. Coordinate necessary actions

{coordination_background}

# Using the `ClarificationQuestion` tool
If you need more information to properly assess the impact, use this tool to ask specific questions.
Never make assumptions about technical implications or business impact - get clarification!

# Using the `EngineeringImpactAnalysis` tool
For changes that primarily affect the engineering domain:
- Analyze technical implications
- Identify affected systems
- Estimate implementation complexity
- Determine testing requirements
- Assess deployment risks

# Using the `BusinessImpactAnalysis` tool
For changes that primarily affect the business domain:
- Analyze requirement changes
- Identify affected stakeholders
- Estimate resource needs
- Determine timeline impacts
- Assess business risks

# Using the `CoordinationAction` tool
When coordination between teams is needed:
- Schedule necessary sync meetings
- Create communication channels
- Set up collaborative workspaces
- Define handoff points

# Using the `CreateJiraTicket` tool
Create appropriate Jira tickets for:
- Impact analysis findings
- Required actions
- Team coordination needs
- Follow-up tasks

# Using the `Escalate` tool
Escalate when:
- High-risk changes detected
- Cross-team conflicts arise
- Immediate attention needed
- Critical dependencies identified

{workflow_preferences}

{response_preferences}

{jira_preferences}"""

impact_prompt = """{instructions}

Remember to use the correct tool calls and pass all required arguments.

Here is the change request. Pay special attention to the source and type of change.

{change}"""


async def analyze_impact(state: State, config: RunnableConfig, store: BaseStore):
    """Analyze and coordinate change impact."""
    model = config["configurable"].get("model", "gpt-4")
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        parallel_tool_calls=False,
        tool_choice="required",
    )
    tools = [
        EngineeringImpactAnalysis,
        BusinessImpactAnalysis,
        ClarificationQuestion,
        CoordinationAction,
        CreateJiraTicket,
    ]
    messages = state.get("messages") or []
    if len(messages) > 0:
        tools.append(Escalate)

    prompt_config = get_config(config)
    namespace = (config["configurable"].get("coordinator_id", "default"),)

    # Get stored preferences
    preferences = {}
    for key in ["workflow_preferences", "response_preferences", "jira_preferences", "coordination_background"]:
        result = await store.aget(namespace, key)
        if result and "data" in result.value:
            preferences[key] = result.value["data"]
        else:
            await store.aput(namespace, key, {"data": prompt_config[key]})
            preferences[key] = prompt_config[key]

    _prompt = IMPACT_ANALYSIS_INSTRUCTIONS.format(**preferences)

    input_message = impact_prompt.format(
        instructions=_prompt,
        change=change_template.format(
            change_description=state["change"]["description"],
            source_team=state["change"]["source_team"],
            change_type=state["change"]["type"],
            priority=state["change"].get("priority", "Medium"),
        ),
    )

    model = llm.bind_tools(tools)
    messages = [{"role": "user", "content": input_message}] + messages

    # Attempt to get valid tool call
    max_retries = 5
    for i in range(max_retries):
        response = await model.ainvoke(messages)
        if len(response.tool_calls) == 1:
            break
        messages += [{"role": "user", "content": "Please make a single valid tool call."}]

    # Track in LangSmith
    config["configurable"].get("langsmith_client").log_trace(
        run_id=config["configurable"].get("run_id"),
        tool_calls=response.tool_calls,
        messages=messages
    )

    return {
        "impact_analysis": response,
        "messages": [response],
        "source_team": state["change"]["source_team"]
    }