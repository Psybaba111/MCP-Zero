"""
MCP-Zero Dynamic Tool Discovery Service
Provides intelligent tool discovery for Rube automation workflows
"""

import asyncio
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os

# Import MCP-Zero components
import sys
sys.path.append('/workspace/MCP-zero')
from matcher import ToolMatcher
from sampler import ToolSampler
from reformatter import ToolReformatter

app = FastAPI(title="MCP-Zero Discovery Service", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class ToolDiscoveryRequest(BaseModel):
    query: str
    required_capabilities: List[str]
    context: Optional[Dict[str, Any]] = None
    max_tools: int = 5

class ToolDiscoveryResponse(BaseModel):
    tools: List[Dict[str, Any]]
    confidence_scores: List[float]
    fallback_tools: List[str]
    processing_time: float

class MCPZeroService:
    """MCP-Zero service for dynamic tool discovery"""
    
    def __init__(self):
        self.matcher = ToolMatcher()
        self.sampler = ToolSampler()
        self.reformatter = ToolReformatter()
        self.tool_database = self._load_tool_database()
        
    def _load_tool_database(self) -> Dict[str, Any]:
        """Load MCP tools database with embeddings"""
        try:
            with open('/workspace/MCP-tools/mcp_tools_with_embedding.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("MCP tools database not found, using minimal fallback")
            return self._create_fallback_database()
    
    def _create_fallback_database(self) -> Dict[str, Any]:
        """Create minimal tool database for development"""
        return {
            "servers": [
                {
                    "server_name": "payment_processor",
                    "server_summary": "Payment processing and refund handling",
                    "tools": [
                        {
                            "name": "create_payment_intent",
                            "description": "Create payment intent for transactions",
                            "parameters": {
                                "amount": "(float) Payment amount",
                                "currency": "(string) Currency code"
                            }
                        },
                        {
                            "name": "process_refund",
                            "description": "Process refund for completed payments",
                            "parameters": {
                                "payment_id": "(string) Original payment ID",
                                "amount": "(optional, float) Refund amount"
                            }
                        }
                    ]
                },
                {
                    "server_name": "document_processor",
                    "server_summary": "Document analysis and data extraction",
                    "tools": [
                        {
                            "name": "extract_document_data",
                            "description": "Extract structured data from documents using OCR",
                            "parameters": {
                                "document_url": "(string) URL of document to process",
                                "document_type": "(string) Type of document"
                            }
                        }
                    ]
                },
                {
                    "server_name": "notification_service",
                    "server_summary": "Multi-channel notification sending",
                    "tools": [
                        {
                            "name": "send_notification",
                            "description": "Send notifications via push, SMS, or email",
                            "parameters": {
                                "user_id": "(string) Target user ID",
                                "type": "(string) Notification type",
                                "message": "(string) Notification content"
                            }
                        }
                    ]
                }
            ]
        }
    
    async def discover_tools(self, request: ToolDiscoveryRequest) -> ToolDiscoveryResponse:
        """Discover relevant tools for a given query and capabilities"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Use MCP-Zero matcher to find relevant tools
            relevant_tools = await self._find_relevant_tools(
                request.query, 
                request.required_capabilities,
                request.max_tools
            )
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_confidence_scores(
                request.query,
                relevant_tools
            )
            
            # Define fallback tools
            fallback_tools = self._get_fallback_tools(request.required_capabilities)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ToolDiscoveryResponse(
                tools=relevant_tools,
                confidence_scores=confidence_scores,
                fallback_tools=fallback_tools,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            # Return fallback response
            fallback_tools = self._get_fallback_tools(request.required_capabilities)
            return ToolDiscoveryResponse(
                tools=[],
                confidence_scores=[],
                fallback_tools=fallback_tools,
                processing_time=asyncio.get_event_loop().time() - start_time
            )
    
    async def _find_relevant_tools(self, query: str, capabilities: List[str], max_tools: int) -> List[Dict[str, Any]]:
        """Find tools using MCP-Zero matching algorithm"""
        # Get query embedding
        query_embedding = await self._get_embedding(query)
        
        # Find matching tools from database
        tool_matches = []
        
        for server in self.tool_database.get("servers", []):
            for tool in server.get("tools", []):
                # Calculate similarity with query
                if "description_embedding" in tool:
                    tool_embedding = np.array(tool["description_embedding"])
                    similarity = cosine_similarity([query_embedding], [tool_embedding])[0][0]
                    
                    # Check if tool matches required capabilities
                    capability_match = any(
                        cap.lower() in tool["description"].lower() 
                        for cap in capabilities
                    )
                    
                    if similarity > 0.7 or capability_match:
                        tool_matches.append({
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool.get("parameters", {}),
                            "server": server["server_name"],
                            "similarity": float(similarity)
                        })
        
        # Sort by similarity and return top matches
        tool_matches.sort(key=lambda x: x["similarity"], reverse=True)
        return tool_matches[:max_tools]
    
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get text embedding using OpenAI API"""
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-3-large",
                input=text
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(3072)
    
    async def _calculate_confidence_scores(self, query: str, tools: List[Dict[str, Any]]) -> List[float]:
        """Calculate confidence scores for discovered tools"""
        return [tool.get("similarity", 0.0) for tool in tools]
    
    def _get_fallback_tools(self, capabilities: List[str]) -> List[str]:
        """Get static fallback tools for required capabilities"""
        capability_mapping = {
            "payment_processing": ["backend_api", "payment_gateway"],
            "notification_sending": ["slack_notify", "notification_sender"],
            "document_extraction": ["document_processor", "ocr_service"],
            "database_updates": ["backend_api", "database_connector"],
            "calendar_event_creation": ["calendar_manager", "google_calendar"],
            "email_sending": ["email_service", "gmail_api"],
            "sms_sending": ["twilio_sms", "notification_sender"]
        }
        
        fallback_tools = []
        for capability in capabilities:
            fallback_tools.extend(capability_mapping.get(capability, ["backend_api"]))
        
        return list(set(fallback_tools))  # Remove duplicates

# Initialize service
mcp_zero_service = MCPZeroService()

@app.post("/discover", response_model=ToolDiscoveryResponse)
async def discover_tools(request: ToolDiscoveryRequest):
    """Discover tools for automation workflow"""
    return await mcp_zero_service.discover_tools(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mcp-zero-discovery",
        "tools_loaded": len(mcp_zero_service.tool_database.get("servers", [])),
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/tools/list")
async def list_available_tools():
    """List all available tools in the database"""
    tools = []
    for server in mcp_zero_service.tool_database.get("servers", []):
        for tool in server.get("tools", []):
            tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "server": server["server_name"],
                "parameters": tool.get("parameters", {})
            })
    
    return {"tools": tools, "total_count": len(tools)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)