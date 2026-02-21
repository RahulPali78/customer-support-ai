# n8n Credentials Setup Guide

## Required Credentials

### 1. OpenAI API
- Go to https://platform.openai.com/api-keys
- Create new secret key
- Save it securely (you'll only see it once)
- In n8n: Settings → Credentials → Add → OpenAI API

### 2. Supabase
- Go to your Supabase project → Settings → API
- Copy "anon public" key
- Note your Project URL
- In n8n: Settings → Credentials → Add → Supabase API

### 3. Gmail OAuth2
- Go to Google Cloud Console → APIs → Credentials
- Create OAuth 2.0 credentials
- Add Gmail API scope
- Download credentials JSON
- In n8n: Create OAuth2 credential + enable Gmail OAuth

### 4. Slack
- Go to api.slack.com/apps → Create New App
- Add scopes: chat:write, chat:write.public, app_mentions:read
- Install to workspace
- Copy Bot User OAuth Token
- In n8n: Add Slack API credential

## Workflow Configuration

After importing workflows, update:
1. Credential IDs in each node (replace YOUR_* placeholders)
2. Database/URL references
3. Channel names for Slack notifications
4. Adjust confidence thresholds as needed

Run test: Test first workflow manually with sample data.