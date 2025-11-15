# Voice Agent Context Integration

## How It Works

The VoiceAssistant component now receives real-time context about what the user is viewing in the dashboard and sends this information to the ElevenLabs agent.

## Context Data Sent to Agent

When you click the orb to start a conversation, the agent receives:

### For Issues View:
- View Mode: "issues"
- Selected Category (e.g., "Credit Risk")
- Selected Sub-Category (e.g., "1.1 Credit Assessment & Underwriting Standards")
- Currently Viewing Issue:
  - Issue ID
  - Type (overlap/contradiction)
  - Regulations involved
  - Description
  - Severity (if applicable)
- Total number of issues in current filter

### For Requirements View:
- View Mode: "requirements"
- Selected Category
- Selected Sub-Category
- Currently Viewing Requirement:
  - Regulation name
  - Requirement text
  - Sub-Category
- Total number of requirements in current filter

## Dynamic Updates

The context is automatically updated when:
- User switches between Issues and Requirements view
- User selects a different category or sub-category
- User clicks on a different issue or requirement

The agent receives these updates in real-time via `sendContextualUpdate()`.

## How to Use in ElevenLabs Agent Prompt

In your ElevenLabs agent configuration, you can reference this context using the variable you created. The context is sent as:

1. **Initial Context**: Sent when starting the conversation via the `overrides.agent.prompt.prompt` parameter
2. **Dynamic Updates**: Sent during the conversation via `sendContextualUpdate()`

### Example Agent Prompt Variable Usage

If you created a variable called `{{dashboard_context}}` in your ElevenLabs agent, it will be populated with:

```
Current Dashboard Context:
- View Mode: issues
- Selected Category: Credit Risk
- Selected Sub-Category: 1.1 Credit Assessment & Underwriting Standards
- Currently Viewing Issue:
  * ID: contradiction-1-1
  * Type: contradiction
  * Regulations: CRR Article 124 × Local Banking Act §45
  * Description: Conflicting thresholds for residential mortgage risk weights.
  * Severity: Medium
- Total Issues: 23
```

## Customizing Context

To add more context data, edit `frontend/src/components/VoiceAssistant.tsx`:

1. Add new fields to the `VoiceAssistantProps.context` interface
2. Update the `buildContextString()` function to include the new data
3. Pass the new data from `App.tsx` when rendering `<VoiceAssistant />`

## Example Questions Users Can Ask

With this context, users can ask questions like:
- "What is this issue about?"
- "Explain the contradiction I'm looking at"
- "What are the conflicting requirements?"
- "Show me more details about this regulation"
- "What category am I in?"
- "How many issues are there in this category?"
