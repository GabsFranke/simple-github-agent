"""GitHub webhook receiver."""
import os
import hmac
import hashlib
import logging
import sys
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Response
from pydantic import BaseModel

# Add shared to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.queue import get_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SimpleGitHubAgent Webhook Service")

# Initialize queue
queue = get_queue()


class WebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    action: str
    issue: Dict[str, Any] = None
    comment: Dict[str, Any] = None
    repository: Dict[str, Any]
    installation: Dict[str, Any] = None


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False
    
    expected_signature = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def parse_command(comment_body: str) -> str:
    """Extract agent command from comment."""
    lines = comment_body.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('/agent'):
            return line
    return ""


@app.get("/")
async def root():
    """Root endpoint."""
    return {"status": "SimpleGitHubAgent webhook service is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/webhook")
async def webhook(request: Request):
    """Handle GitHub webhook events."""
    try:
        # Get payload
        payload = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "")
        
        # Verify signature (optional for testing)
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        if webhook_secret and not verify_signature(payload, signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        data = await request.json()
        
        logger.info(f"Received {event_type} event")
        
        # Handle issue_comment events
        if event_type == "issue_comment" and data.get("action") == "created":
            comment_body = data["comment"]["body"]
            command = parse_command(comment_body)
            
            if command:
                # Extract context
                request_data = {
                    "repository": data["repository"]["full_name"],
                    "issue_number": data["issue"]["number"],
                    "command": command,
                    "user": data["comment"]["user"]["login"],
                    "installation_id": data.get("installation", {}).get("id"),
                }
                
                logger.info(f"Agent command detected: {command}")
                logger.info(f"Processing request for {request_data['repository']} issue #{request_data['issue_number']}")
                
                # Publish to queue (async processing)
                import asyncio
                asyncio.create_task(queue.publish(request_data))
                
                return {"status": "accepted", "message": "Agent is processing your request"}
        
        return {"status": "ignored", "message": "Not an agent command"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
