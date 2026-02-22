# Push to GitHub

The project is committed locally. To push to https://github.com/RahulPali78/customer-support-ai:

## Method 1: From Your Local Machine

```bash
# Clone fresh
git clone https://github.com/RahulPali78/customer-support-ai.git
cd customer-support-ai

# OR if repo already exists, just force push the new content
git remote add vps ssh://your-vps:/data/.openclaw/workspace/customer-support-ai
git pull vps master --force
git push origin master
```

## Method 2: Using GitHub Token (on this VPS)

```bash
cd /data/.openclaw/workspace/customer-support-ai
export GITHUB_TOKEN=ghp_your_token_here

git remote set-url origin https://${GITHUB_TOKEN}@github.com/RahulPali78/customer-support-ai.git
git push -u origin master
```

## Method 3: Download and Manual Upload

```bash
# Zip the project
cd /tmp
tar -czf customer-support-ai.tar.gz \
  -C /data/.openclaw/workspace customer-support-ai

# Now download /tmp/customer-support-ai.tar.gz from this VPS
# Extract locally and push to GitHub
```

## Files Committed
- 12 files, 1211 lines
- All n8n workflows
- Database schema
- Dashboard code
- Docker setup
- Documentation

Commit: `68a7db2`