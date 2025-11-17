# 🔐 Secure API Key Setup Guide

## ⚠️ IMPORTANT SECURITY NOTICE

**NEVER commit API keys to Git!** This guide shows you how to securely configure your API keys locally.

---

## 🔑 Required API Keys

You need **TWO** API keys to run the system:

1. **LLM API Key** (Groq, OpenAI, or compatible provider)
2. **Daytona API Key** (for sandbox execution)

---

## 📋 Step-by-Step Secure Setup

### Step 1: Get Your API Keys

#### Option A: Groq (FREE, Recommended)

1. Visit: https://console.groq.com/
2. Sign up for a free account
3. Go to: https://console.groq.com/keys
4. Click "Create API Key"
5. Copy your key (starts with `gsk_`)

**Benefits**: Free, fast, good for agentic tasks

#### Option B: OpenAI (Paid)

1. Visit: https://platform.openai.com/
2. Sign up or log in
3. Go to: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy your key (starts with `sk-`)

**Cost**: ~$0.03-0.06 per 1K tokens

#### Option C: Anthropic Claude (Paid)

1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Generate API key
4. Copy your key (starts with `sk-ant-`)

**Cost**: ~$0.015-0.075 per 1K tokens

#### Daytona API Key (Required)

1. Visit: https://app.daytona.io
2. Sign up for free account
3. Go to: https://app.daytona.io/dashboard/keys
4. Click "Create New Key"
5. Copy your key (starts with `dtn_`)

**Benefits**: Free tier with compute credits

---

### Step 2: Create Local .env File

**IMPORTANT**: The `.env` file should ONLY exist on your local machine, never in git!

```bash
# In the project root directory
cp .env.example .env
```

Then edit the `.env` file:

```bash
nano .env
# or
vim .env
# or use your favorite editor
```

---

### Step 3: Configure API Keys Securely

Edit your **local** `.env` file and add your API keys:

#### For Groq (Free, Recommended):

```env
# ============================================
# LLM Configuration (Groq - Free)
# ============================================
LLM_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8000

# ============================================
# Daytona Configuration
# ============================================
DAYTONA_API_KEY=dtn_YOUR_ACTUAL_DAYTONA_KEY_HERE
DAYTONA_API_URL=https://app.daytona.io/api
DAYTONA_TARGET=default

# ============================================
# Code-Server Configuration
# ============================================
CODE_SERVER_PASSWORD=YourSecurePassword123!
```

#### For OpenAI:

```env
LLM_API_KEY=sk-YOUR_ACTUAL_OPENAI_KEY_HERE
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

#### For Anthropic Claude:

```env
LLM_API_KEY=sk-ant-YOUR_ACTUAL_ANTHROPIC_KEY_HERE
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL=claude-3-opus-20240229
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

---

### Step 4: Verify .env is Not Tracked

Check that `.env` is ignored by git:

```bash
# This should show .env in .gitignore
cat .gitignore | grep "^\.env$"

# This should return nothing (file not tracked)
git ls-files | grep "^\.env$"

# This should show .env is not staged
git status
```

✅ **Expected**: `.env` should NOT appear in git status

---

### Step 5: Set Secure Permissions (Linux/Mac)

Protect your `.env` file from other users:

```bash
chmod 600 .env
```

This ensures only you can read/write the file.

---

## 🛡️ Security Best Practices

### DO ✅

1. ✅ **Keep .env local only** - Never commit to git
2. ✅ **Use .env.example** - Commit this template WITHOUT real keys
3. ✅ **Set file permissions** - `chmod 600 .env` on Linux/Mac
4. ✅ **Use environment variables** - Load keys from .env at runtime
5. ✅ **Rotate keys regularly** - Change keys every few months
6. ✅ **Use different keys** - Different keys for dev/staging/prod
7. ✅ **Add .env to .gitignore** - Already done in this project

### DON'T ❌

1. ❌ **Never commit .env** - Git will expose your keys
2. ❌ **Never hardcode keys** - Don't put keys directly in code
3. ❌ **Never share keys** - Each developer should have their own
4. ❌ **Never email keys** - Use secure methods to share if needed
5. ❌ **Never put in screenshots** - Keys visible in screenshots
6. ❌ **Never log keys** - Don't print keys in console/logs
7. ❌ **Never push to public repos** - Even in private, avoid it

---

## 🔍 Verification Steps

After setting up your `.env` file:

### 1. Check File Exists

```bash
ls -la .env
```

✅ Should show the file exists

### 2. Check Content (Securely)

```bash
head -5 .env
```

✅ Should show your configuration (don't share this output!)

### 3. Check Git Status

```bash
git status
```

✅ `.env` should NOT appear here

### 4. Test Configuration

```bash
# Load env vars
source .env

# Check they're set (without printing values)
[ -z "$LLM_API_KEY" ] && echo "❌ LLM_API_KEY not set" || echo "✅ LLM_API_KEY is set"
[ -z "$DAYTONA_API_KEY" ] && echo "❌ DAYTONA_API_KEY not set" || echo "✅ DAYTONA_API_KEY is set"
```

---

## 🚀 Start the System

Once your `.env` is configured:

```bash
# Start the system
docker-compose up -d

# Check health
curl http://localhost/api/health

# View logs
docker-compose logs -f backend
```

---

## 🆘 Troubleshooting

### Problem: "LLM_API_KEY not set"

**Solution**:
1. Verify `.env` file exists: `ls -la .env`
2. Check content: `cat .env | grep LLM_API_KEY`
3. Restart containers: `docker-compose restart`

### Problem: "Invalid API key"

**Solution**:
1. Verify key is correct (no extra spaces)
2. Check key is active on provider's dashboard
3. Ensure you have credits/quota available

### Problem: "Daytona connection failed"

**Solution**:
1. Check Daytona key: `cat .env | grep DAYTONA_API_KEY`
2. Verify key at: https://app.daytona.io/dashboard/keys
3. Check internet connectivity

### Problem: ".env accidentally committed"

**Solution**:
```bash
# Remove from git cache
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from git"

# Push
git push

# Regenerate all exposed API keys immediately!
```

⚠️ **IMPORTANT**: If you accidentally committed keys, **regenerate them immediately** on the provider's dashboard!

---

## 🔄 Key Rotation

Rotate your API keys every 3-6 months:

### Groq

1. Go to: https://console.groq.com/keys
2. Create new key
3. Update `.env` with new key
4. Delete old key from Groq

### Daytona

1. Go to: https://app.daytona.io/dashboard/keys
2. Create new key
3. Update `.env` with new key
4. Delete old key from Daytona

### After Rotation

```bash
# Restart services with new keys
docker-compose restart
```

---

## 📝 Team Setup

If multiple people will use the system:

### For Each Team Member:

1. **Each gets their own API keys** - Never share
2. **Each creates their own .env** - From .env.example
3. **Each configures locally** - Following this guide
4. **Never commit .env** - Check before pushing

### Team Best Practices:

- Use a password manager for team key storage (1Password, LastPass)
- Set up CI/CD with secrets management (GitHub Secrets, AWS Secrets Manager)
- Use different keys for different environments
- Document who has which keys

---

## 🏢 Production Deployment

For production, use proper secrets management:

### Options:

1. **Docker Secrets**
   ```bash
   docker secret create llm_api_key ./llm_key.txt
   ```

2. **Kubernetes Secrets**
   ```bash
   kubectl create secret generic api-keys \
     --from-literal=llm-api-key=xxx \
     --from-literal=daytona-api-key=xxx
   ```

3. **Cloud Secrets Manager**
   - AWS Secrets Manager
   - Google Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

4. **Environment Variables (Heroku, Vercel, etc.)**
   - Set via platform UI
   - Never in code or config files

---

## 📖 Summary Checklist

Before starting:

- [ ] Created `.env` from `.env.example`
- [ ] Added actual API keys to `.env`
- [ ] Verified `.env` is in `.gitignore`
- [ ] Confirmed `.env` is not tracked by git
- [ ] Set file permissions: `chmod 600 .env`
- [ ] Tested configuration works
- [ ] Never committed `.env` to git

✅ **You're ready to start the system securely!**

---

## 🔗 Useful Links

- **Groq Console**: https://console.groq.com/
- **Groq API Keys**: https://console.groq.com/keys
- **Daytona Dashboard**: https://app.daytona.io/dashboard
- **Daytona API Keys**: https://app.daytona.io/dashboard/keys
- **OpenAI Keys**: https://platform.openai.com/api-keys
- **Anthropic Console**: https://console.anthropic.com/

---

## 🆘 Need Help?

If you have security concerns or questions:

1. Review this guide carefully
2. Check the `.gitignore` file
3. Run `git status` to verify nothing is tracked
4. Never share your `.env` file or API keys
5. Regenerate keys immediately if exposed

---

**Remember**: Security is not optional! Follow these practices to keep your API keys safe. 🔐
