from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.dependencies import get_current_user, rate_limit
from app.models.user import User
from app.schemas.schemas import AgentRunRequest, AgentRunResponse
from app.services.llm import llm_service
from app.core.cache import cache
from typing import Dict, Any, List
import uuid
import json

router = APIRouter(prefix="/agent", tags=["AI Agent"])

class SimpleAgent:
    """
    Simple ReAct style agent
    
    Agent loop:
    1. Thought - কি করতে হবে চিন্তা করবে
    2. Action - Action take করবে (tool call)
    3. Observation - Result observe করবে
    4. Repeat until done
    
    Tools available:
    - search: Information খুঁজবে (simulated)
    - calculate: Math calculation করবে
    - final_answer: Final answer দেবে
    """
    
    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self.tools = {
            "search": self._search_tool,
            "calculate": self._calculate_tool,
            "final_answer": self._final_answer_tool
        }
    
    def _search_tool(self, query: str) -> str:
        """Search simulation - Real implementation এ web search বা DB query হবে"""
        # This is a placeholder - আসলে web search বা knowledge base query করবে
        return f"Search results for '{query}': [Simulated search - implement real search here]"
    
    def _calculate_tool(self, expression: str) -> str:
        """Math calculation করবে"""
        try:
            # Safe eval (limited scope)
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    def _final_answer_tool(self, answer: str) -> str:
        """Final answer - এটা call হলে agent থেমে যাবে"""
        return answer
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Agent task execute করবে
        
        Returns:
            {
                "status": "completed",
                "result": "...",
                "steps": [...],
                "iterations": 3
            }
        """
        steps = []
        context = context or {}
        
        # System prompt for agent
        system_prompt = """You are an AI agent that can use tools to solve tasks.

Available tools:
1. search(query) - Search for information
2. calculate(expression) - Perform math calculations
3. final_answer(answer) - Provide final answer

You must follow this format for each step:

Thought: [What you need to do next]
Action: [tool_name]
Action Input: [input for the tool]

After seeing the observation, continue thinking until you can provide the final answer.

When you have the final answer, use:
Action: final_answer
Action Input: [your final answer]
"""
        
        messages = [
            {"role": "user", "content": f"Task: {task}\n\nContext: {json.dumps(context)}"}
        ]
        
        for iteration in range(self.max_iterations):
            # LLM call করবে
            response = await llm_service.chat_completion_async(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more focused reasoning
            )
            
            # Parse response
            thought, action, action_input = self._parse_response(response)
            
            step = {
                "iteration": iteration + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input
            }
            
            # Execute action
            if action in self.tools:
                observation = self.tools[action](action_input)
                step["observation"] = observation
                
                # Check if final answer
                if action == "final_answer":
                    steps.append(step)
                    return {
                        "status": "completed",
                        "result": observation,
                        "steps": steps,
                        "iterations": iteration + 1
                    }
                
                # Add observation to messages
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"Observation: {observation}\n\nContinue thinking."})
            else:
                step["observation"] = f"Unknown action: {action}"
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": "Invalid action. Try again with a valid tool."})
            
            steps.append(step)
        
        # Max iterations reached
        return {
            "status": "max_iterations_reached",
            "result": "Could not complete task within iteration limit",
            "steps": steps,
            "iterations": self.max_iterations
        }
    
    def _parse_response(self, response: str) -> tuple:
        """Parse LLM response to extract thought, action, and input"""
        thought = ""
        action = ""
        action_input = ""
        
        lines = response.split("\n")
        for line in lines:
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                action_input = line.replace("Action Input:", "").strip()
        
        return thought, action, action_input

# Background task runner
async def run_agent_background(task_id: str, task: str, context: Dict, max_iterations: int):
    """Background এ agent run করবে"""
    agent = SimpleAgent(max_iterations=max_iterations)
    
    try:
        # Update status
        cache.set(f"agent_task:{task_id}", {
            "status": "running",
            "task": task
        }, ttl=3600)
        
        # Run agent
        result = await agent.run(task, context)
        
        # Save result
        cache.set(f"agent_task:{task_id}", {
            "status": result["status"],
            "task": task,
            "result": result
        }, ttl=3600)
        
    except Exception as e:
        cache.set(f"agent_task:{task_id}", {
            "status": "failed",
            "task": task,
            "error": str(e)
        }, ttl=3600)

@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(rate_limit(10))  # Lower limit for expensive operations
):
    """
    AI Agent task run করবে (background)
    
    Returns task_id - status check করতে পারবে
    """
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Schedule background task
    background_tasks.add_task(
        run_agent_background,
        task_id,
        request.task,
        request.context,
        request.max_iterations
    )
    
    # Return task ID
    return {
        "task_id": task_id,
        "status": "queued",
        "result": None,
        "steps": []
    }

@router.get("/status/{task_id}", response_model=AgentRunResponse)
async def get_agent_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Agent task এর status check করবে"""
    
    task_data = cache.get(f"agent_task:{task_id}")
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": task_data.get("status", "unknown"),
        "result": task_data.get("result", {}).get("result"),
        "steps": task_data.get("result", {}).get("steps", [])
    }

@router.post("/run-sync", response_model=AgentRunResponse)
async def run_agent_sync(
    request: AgentRunRequest,
    current_user: User = Depends(get_current_user),
    _: bool = Depends(rate_limit(5))
):
    """
    Synchronous agent execution - Immediately result return করবে
    Small tasks এর জন্য
    """
    
    agent = SimpleAgent(max_iterations=request.max_iterations)
    
    try:
        result = await agent.run(request.task, request.context)
        
        return {
            "task_id": "sync",
            "status": result["status"],
            "result": result.get("result"),
            "steps": result.get("steps", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        }