from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from langchain.schema import HumanMessage, SystemMessage
from prompts import get_system_prompt  # merged + contextual prompt
import re
SUBMIT_MARKER = re.compile(r"<idea\s+submit>", re.I)

# ------------------------------------------------------------
@dataclass
class SessionState:
    turn_id: int = 0
    messages: List[dict[str, str]] = field(default_factory=list)

    # ---- locked-in answers ----
    idea: str = ""
    implemented: str = ""
    classification: str = ""
    values: str = ""
    submitted: bool = False   # NEW

# ------------------------------------------------------------
sessions: Dict[str, SessionState] = {}

# ------------------------------------------------------------

import httpx

async def _submit_idea(session_id: str):
    """Fire-and-forget POST to /call_api."""
    url = "http://localhost:8000/call_api"
    payload = {"session_id": session_id, "user_id": session_id}  # use same id
    async with httpx.AsyncClient() as c:
        await c.post(url, json=payload, timeout=5)
        
        
async def next_turn(session_id: str, user_text: str, azure_chat) -> str:
    print("\n========== [START TURN] ==========")
    print(f"[SESSION ID] {session_id}")
    print(f"[USER INPUT] {user_text}")

    # 0. Get or create session state
    state = sessions.setdefault(session_id, SessionState())
    print(f"[TURN ID] {state.turn_id}")

    # 1. Store user turn
    state.messages.append({"role": "user", "content": user_text})
    print("[HISTORY] Appended user input to messages.")

    # 2. Build the full system prompt
    prompt = get_system_prompt(
        idea=state.idea,
        implemented=state.implemented,
        classification=state.classification,
        values=state.values,
    )
    print("[SYSTEM PROMPT]\n" + prompt)

    # 3. Build full message history
    lc_msgs = [SystemMessage(content=prompt)]
    print("\n[CHAT HISTORY]")
    for m in state.messages:
        role = m["role"]
        content = m["content"]
        msg = HumanMessage(content=content) if role == "user" else SystemMessage(content=content)
        lc_msgs.append(msg)
        print(f"  {role.upper()}: {content}")

    # 4. Call LLM
    print("\n[SENDING TO LLM] Calling Azure OpenAI...")
    response = await azure_chat.ainvoke(lc_msgs)
    reply = response.content
    
    # --- NEW LOGIC ---
    if not state.submitted and SUBMIT_MARKER.search(reply):
        await _submit_idea(session_id)
        state.submitted = True
        # Remove marker for frontend
        reply = SUBMIT_MARKER.sub("", reply).strip()
    
    print("[LLM REPLY RECEIVED]")
    print(reply)

    # 5. Extract slot values from reply
    print("\n[EXTRACTING SLOTS]")
    for line in reply.splitlines():
        if line.startswith("[IDEA]"):
            state.idea = line[6:].strip()
            print(f"  Extracted IDEA: {state.idea}")
        elif line.startswith("[IMPLEMENTED]"):
            state.implemented = line[13:].strip()
            print(f"  Extracted IMPLEMENTED: {state.implemented}")
        elif line.startswith("[CLASSIFICATION]"):
            state.classification = line[16:].strip()
            print(f"  Extracted CLASSIFICATION: {state.classification}")
        elif line.startswith("[VALUES]"):
            state.values = line[8:].strip()
            print(f"  Extracted VALUES: {state.values}")

    # 6. Store assistant turn and return
    state.messages.append({"role": "assistant", "content": reply})
    state.turn_id += 1
    print(f"\n[TURN COMPLETE] New Turn ID: {state.turn_id}")
    print("[SESSION STATE]")
    print(f"  IDEA         : {state.idea}")
    print(f"  IMPLEMENTED  : {state.implemented}")
    print(f"  CLASSIFICATION: {state.classification}")
    print(f"  VALUES       : {state.values}")
    print("========== [END TURN] ==========\n")

    return reply
