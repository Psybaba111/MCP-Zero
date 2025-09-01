"""
MCP-Zero Discovery Module for EV Platform Automation
Provides dynamic tool discovery with intelligent fallback mechanisms
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class DiscoveryStatus(Enum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    FALLBACK = "fallback"

@dataclass
class ToolInfo:
    name: str
    description: str
    parameters: Dict[str, Any]
    server_name: str
    confidence_score: float

@dataclass
class DiscoveryResult:
    status: DiscoveryStatus
    tools: List[ToolInfo]
    discovery_time: float
    fallback_used: bool
    error_message: Optional[str] = None

class MCPZeroDiscovery:
    def __init__(self, config: Dict[str, Any]):
        self.endpoint = config.get("endpoint", "http://localhost:8001")
        self.timeout = config.get("timeout", 5000)
        self.fallback_enabled = config.get("fallback_enabled", True)
        self.max_retries = config.get("max_retries", 3)
        
        # Static fallback tools for common operations
        self.static_fallbacks = {
            "kyc_verification": [
                ToolInfo(
                    name="manual_kyc_review",
                    description="Manual KYC document review by compliance team",
                    parameters={
                        "user_id": "int",
                        "document_type": "str",
                        "review_notes": "str"
                    },
                    server_name="compliance_service",
                    confidence_score=0.8
                )
            ],
            "document_analysis": [
                ToolInfo(
                    name="ocr_document_extraction",
                    description="OCR-based document text extraction",
                    parameters={
                        "document_url": "str",
                        "document_type": "str"
                    },
                    server_name="document_service",
                    confidence_score=0.7
                )
            ],
            "police_verification": [
                ToolInfo(
                    name="police_api_verification",
                    description="Police database verification API",
                    parameters={
                        "license_number": "str",
                        "user_details": "dict"
                    },
                    server_name="police_service",
                    confidence_score=0.9
                )
            ]
        }
    
    async def discover_tools(self, tool_pattern: str, context: Dict[str, Any] = None) -> DiscoveryResult:
        """
        Discover relevant tools using MCP-Zero with intelligent fallback
        """
        start_time = time.time()
        
        try:
            # Attempt MCP-Zero discovery
            tools = await self._mcp_zero_discovery(tool_pattern, context)
            
            if tools:
                return DiscoveryResult(
                    status=DiscoveryStatus.SUCCESS,
                    tools=tools,
                    discovery_time=time.time() - start_time,
                    fallback_used=False
                )
            
            # Fallback to static tools if MCP-Zero fails
            if self.fallback_enabled:
                fallback_tools = self._get_static_fallbacks(tool_pattern)
                if fallback_tools:
                    logger.info(f"Using static fallback tools for pattern: {tool_pattern}")
                    return DiscoveryResult(
                        status=DiscoveryStatus.FALLBACK,
                        tools=fallback_tools,
                        discovery_time=time.time() - start_time,
                        fallback_used=True
                    )
            
            return DiscoveryResult(
                status=DiscoveryStatus.ERROR,
                tools=[],
                discovery_time=time.time() - start_time,
                fallback_used=False,
                error_message="No tools found and fallback disabled"
            )
            
        except asyncio.TimeoutError:
            logger.warning(f"MCP-Zero discovery timed out for pattern: {tool_pattern}")
            return await self._handle_timeout_fallback(tool_pattern, start_time)
            
        except Exception as e:
            logger.error(f"MCP-Zero discovery error: {str(e)}")
            return await self._handle_error_fallback(tool_pattern, start_time, str(e))
    
    async def _mcp_zero_discovery(self, tool_pattern: str, context: Dict[str, Any] = None) -> List[ToolInfo]:
        """
        Perform MCP-Zero tool discovery
        """
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout/1000)) as session:
            payload = {
                "pattern": tool_pattern,
                "context": context or {},
                "max_results": 10,
                "min_confidence": 0.6
            }
            
            async with session.post(
                f"{self.endpoint}/discover",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_discovery_response(data)
                else:
                    logger.error(f"MCP-Zero discovery failed with status {response.status}")
                    return []
    
    def _parse_discovery_response(self, response_data: Dict[str, Any]) -> List[ToolInfo]:
        """
        Parse MCP-Zero discovery response
        """
        tools = []
        
        for tool_data in response_data.get("tools", []):
            tool = ToolInfo(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                parameters=tool_data.get("parameters", {}),
                server_name=tool_data.get("server_name", ""),
                confidence_score=tool_data.get("confidence_score", 0.0)
            )
            tools.append(tool)
        
        # Sort by confidence score
        tools.sort(key=lambda x: x.confidence_score, reverse=True)
        return tools
    
    def _get_static_fallbacks(self, tool_pattern: str) -> List[ToolInfo]:
        """
        Get static fallback tools for a given pattern
        """
        fallback_tools = []
        
        for pattern, tools in self.static_fallbacks.items():
            if pattern in tool_pattern.lower():
                fallback_tools.extend(tools)
        
        return fallback_tools
    
    async def _handle_timeout_fallback(self, tool_pattern: str, start_time: float) -> DiscoveryResult:
        """
        Handle timeout by using static fallbacks
        """
        if self.fallback_enabled:
            fallback_tools = self._get_static_fallbacks(tool_pattern)
            if fallback_tools:
                logger.info(f"Timeout fallback: Using static tools for {tool_pattern}")
                return DiscoveryResult(
                    status=DiscoveryStatus.FALLBACK,
                    tools=fallback_tools,
                    discovery_time=time.time() - start_time,
                    fallback_used=True
                )
        
        return DiscoveryResult(
            status=DiscoveryStatus.TIMEOUT,
            tools=[],
            discovery_time=time.time() - start_time,
            fallback_used=False,
            error_message="Discovery timed out"
        )
    
    async def _handle_error_fallback(self, tool_pattern: str, start_time: float, error_msg: str) -> DiscoveryResult:
        """
        Handle errors by using static fallbacks
        """
        if self.fallback_enabled:
            fallback_tools = self._get_static_fallbacks(tool_pattern)
            if fallback_tools:
                logger.info(f"Error fallback: Using static tools for {tool_pattern}")
                return DiscoveryResult(
                    status=DiscoveryStatus.FALLBACK,
                    tools=fallback_tools,
                    discovery_time=time.time() - start_time,
                    fallback_used=True
                )
        
        return DiscoveryResult(
            status=DiscoveryStatus.ERROR,
            tools=[],
            discovery_time=time.time() - start_time,
            fallback_used=False,
            error_message=error_msg
        )
    
    def get_tool_usage_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about tool discovery usage
        """
        return {
            "total_discoveries": getattr(self, '_total_discoveries', 0),
            "successful_discoveries": getattr(self, '_successful_discoveries', 0),
            "fallback_usage": getattr(self, '_fallback_usage', 0),
            "average_discovery_time": getattr(self, '_avg_discovery_time', 0.0)
        }

# Factory function to create discovery instance
def create_discovery(config: Dict[str, Any]) -> MCPZeroDiscovery:
    return MCPZeroDiscovery(config)