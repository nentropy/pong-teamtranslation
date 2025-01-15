# Pong - Team Translation Agent

Pong is an AI-powered coordination system that bridges the communication gap between Engineering and Business teams. It analyzes changes, translates their impact across domains, and ensures effective cross-team collaboration.

For a hosted version of Pong, see documentation [here].

## Table of Contents

- [General Setup](#general-setup)
  - [Environment](#environment)
  - [Credentials](#credentials)
  - [Configuration](#configuration)
- [Run Locally](#run-locally)
  - [Setup Pong](#setup-pong)
  - [Process Changes](#process-changes)
  - [Connect to Agent Inbox](#connect-to-agent-inbox)
- [Run in Production](#run-in-production)
  - [Setup on LangGraph Cloud](#setup-on-langgraph-cloud)
  - [Configure Automated Analysis](#configure-automated-analysis)
  - [Set up Monitoring](#set-up-monitoring)
- [Agent Configuration](#agent-configuration)
  - [Engineering Agent](#engineering-agent)
  - [Business Agent](#business-agent)
  - [Coordination Agent](#coordination-agent)

## General Setup

### Environment

1. Fork and clone this repo
2. Create a Python virtualenv and activate it (e.g. `pyenv virtualenv 3.11.1 pong`, `pyenv activate pong`)
3. Run `pip install -e .` to install dependencies

### Credentials

1. Export OpenAI API key (`export OPENAI_API_KEY=...`)
2. Export Anthropic API key (`export ANTHROPIC_API_KEY=...`)
3. Configure Jira Access:
   - Create API token in Jira
   - Set environment variables:
     ```bash
     export JIRA_EMAIL=...
     export JIRA_API_TOKEN=...
     export JIRA_URL=...
     ```
4. Export LangSmith API key (`export LANGSMITH_API_KEY=...`)

### Configuration

Configuration files for Pong can be found in `configs/`:

- `engineering_agent_config.yaml`: Technical impact analysis settings
- `business_agent_config.yaml`: Business impact analysis settings
- `coordination_agent_config.yaml`: Cross-team coordination settings

Required configuration for each agent includes:
- Team composition
- Impact analysis preferences
- Response protocols
- Jira integration settings
- LangSmith monitoring preferences

## Run Locally

You can run Pong locally for testing before deploying to production.

### Setup Pong

1. Install development server: `pip install -U "langgraph-cli[inmem]"`
2. Run development server: `langgraph dev`

### Process Changes

To analyze changes locally:

```bash
python scripts/process_changes.py \
  --source [engineering|business] \
  --type [code|requirement] \
  --description "Change description" \
  --priority [High|Medium|Low]
```

### Connect to Agent Inbox

1. Go to Agent Inbox
2. Configure local connection:
   - Click Settings
   - Input LangSmith API key
   - Add new inbox
   - Set Assistant/Graph ID to "pong"
   - Set URL to `http://127.0.0.1:2024`
   - Name it "Local Pong"

## Run in Production

### Setup on LangGraph Cloud

1. Access LangSmith Plus account
2. Navigate to deployments
3. Create new deployment:
   - Connect to GitHub repo
   - Name it "Pong-Team-Translation"
   - Add environment variables:
     - OPENAI_API_KEY
     - ANTHROPIC_API_KEY
     - JIRA_EMAIL
     - JIRA_API_TOKEN
     - JIRA_URL
4. Deploy and monitor status

### Configure Automated Analysis

Set up automated change detection:

```bash
python scripts/setup_monitoring.py --url ${LANGGRAPH_CLOUD_URL}
```

### Set up Monitoring

1. Configure LangSmith monitoring
2. Set up Jira integration
3. Enable alerting for critical changes

## Agent Configuration

### Engineering Agent

Controls technical impact analysis:
- System architecture assessment
- Implementation complexity
- Testing requirements
- Security implications
- Performance impact

### Business Agent

Manages business impact analysis:
- Resource requirements
- Timeline implications
- Stakeholder impact
- Cost assessment
- Operational changes

### Coordination Agent

Orchestrates cross-team activities:
- Change routing
- Impact translation
- Meeting coordination
- Documentation tracking
- Escalation management

## Advanced Options

To customize Pong's behavior beyond configuration:

- Impact Analysis Logic: Edit `pong/analysis_graphs.py`
- Coordination Logic: Edit `pong/coordination_agent.py`
- Translation Logic: Edit `pong/translation_engine.py`
- Integration Logic: Edit `pong/jira_integration.py`
- Monitoring Logic: Edit `pong/langsmith_monitoring.py`