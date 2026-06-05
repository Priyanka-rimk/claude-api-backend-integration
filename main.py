import os
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from dotenv import load_dotenv
import anthropic
from contextlib import asynccontextmanager

from database import init_db, get_db, TestRun
from possibilities import POSSIBILITIES

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    yield

app = FastAPI(
    title="StrokeCare Tester API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── Pydantic models ──────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    possibility_code: str
    inputs: dict


# ── Helpers ──────────────────────────────────────────────────────────────────

def build_user_prompt(template: str, inputs: dict) -> str:
    try:
        return template.format(**inputs)
    except KeyError as e:
        return template


def run_safety_checks(text: str, config: dict) -> dict:
    checks = []
    passed = True

    # Check starts_with
    if "starts_with" in config:
        ok = text.strip().upper().startswith(config["starts_with"].upper())
        checks.append({"label": f"Starts with '{config['starts_with']}'", "pass": ok})
        if not ok:
            passed = False

    # Check max_chars
    if "max_chars" in config:
        ok = len(text) <= config["max_chars"]
        checks.append({"label": f"Under {config['max_chars']} characters ({len(text)} found)", "pass": ok})
        if not ok:
            passed = False

    # Check max_words
    if "max_words" in config:
        word_count = len(text.split())
        ok = word_count <= config["max_words"]
        checks.append({"label": f"Under {config['max_words']} words ({word_count} found)", "pass": ok})
        if not ok:
            passed = False

    # Check question marks
    if "question_marks" in config:
        qm = text.count("?")
        ok = qm == config["question_marks"]
        checks.append({"label": f"Exactly {config['question_marks']} question mark(s) ({qm} found)", "pass": ok})
        if not ok:
            passed = False

    # Check prohibited phrases
    prohibited = config.get("prohibited", []) + config.get("prohibited_in_output", [])
    for phrase in prohibited:
        found = phrase.lower() in text.lower()
        checks.append({"label": f"No '{phrase}'", "pass": not found})
        if found:
            passed = False

    return {"passed": passed, "checks": checks}

from typing import Dict, Any


def run_preflight(config: Dict[str, Any], inputs: Dict[str, Any]):
    """
    Returns:
        None -> passed

        {
            "blocked": True,
            "message": "..."
        }
    """

    preflight = config.get("preflight")

    if not preflight:
        return None

    rules = preflight.get("block_if", [])

    for rule in rules:

        # Rule type 1
        if "field" in rule:
            value = inputs.get(rule["field"])

            if value == rule["equals"]:
                return {
                    "blocked": True,
                    "message": rule["message"],
                }

        # Rule type 2
        elif "fields_empty" in rule:

            missing = [
                field
                for field in rule["fields_empty"]
                if not inputs.get(field)
            ]

            if missing:
                return {
                    "blocked": True,
                    "message": rule["message"],
                    "missing_fields": missing,
                }

    return None

def get_fallback(config: dict, inputs: dict) -> str:
    try:
        return config["fallback"].format(**inputs)
    except Exception:
        return "Unable to generate response. Please try again."


def call_claude(system_prompt: str, user_prompt: str,
                model: str, max_tokens: int) -> tuple[str, int, int]:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": user_prompt}]
    )
    text = response.content[0].text.strip()
    tokens_in = response.usage.input_tokens
    tokens_out = response.usage.output_tokens
    return text, tokens_in, tokens_out


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/possibilities")
async def get_possibilities():
    result = []
    for code, config in POSSIBILITIES.items():
        result.append({
            "code": code,
            "name": config["name"],
            "section": config["section"],
            "model": config["model"],
            "max_tokens": config["max_tokens"],
            "safety": config["safety"],
            "fields": config["fields"],
        })
    return result


@app.get("/api/possibilities/{code}")
async def get_possibility(code: str):
    if code not in POSSIBILITIES:
        raise HTTPException(status_code=404, detail="Possibility not found")
    config = POSSIBILITIES[code]
    return {
        "code": code,
        "name": config["name"],
        "section": config["section"],
        "model": config["model"],
        "max_tokens": config["max_tokens"],
        "safety": config["safety"],
        "fields": config["fields"],
        "system_prompt": config["system_prompt"],
    }


@app.post("/api/run")
async def run_possibility(req: RunRequest, db: AsyncSession = Depends(get_db)):
    """
    Returns:
        {"blocked": True,  "message": "..."}   — preflight blocked, no API call made
        {"blocked": False, "output": "..."}     — API called, output returned
        {"blocked": False, "output": "...", "fallback": True}  — API failed, fallback used
    """

    code = req.possibility_code.upper()
    if code not in POSSIBILITIES:
        raise HTTPException(status_code=404, detail="Possibility not found")

    config = POSSIBILITIES[code]
    preflight_result = run_preflight(
    config=config,
    inputs=req.inputs)
    if preflight_result:
        return preflight_result
    system_prompt = config["system_prompt"]
    user_prompt = build_user_prompt(config["user_prompt_template"], req.inputs)
    model = config["model"]
    max_tokens = config["max_tokens"]
    validation_config = config.get("validation", {})

    output = None
    status = "pass"
    tokens_in = 0
    tokens_out = 0
    safety_result = {}
    regen_count = 0

    try:
        # First Claude call
        output, tokens_in, tokens_out = call_claude(
            system_prompt, user_prompt, model, max_tokens
        )
        print(output)

        # Run validation
        safety_result = run_safety_checks(output, validation_config)

        if not safety_result["passed"]:
            # Regenerate once
            regen_count = 1
            output, ti2, to2 = call_claude(
                system_prompt, user_prompt, model, max_tokens
            )
            tokens_in += ti2
            tokens_out += to2
            safety_result = run_safety_checks(output, validation_config)

            if not safety_result["passed"]:
                # Use fallback
                output = get_fallback(config, req.inputs)
                status = "fallback"
            else:
                status = "pass_regen"

    except anthropic.APIError as e:
        output = get_fallback(config, req.inputs)
        status = "error"
        safety_result = {"passed": False, "checks": [], "error": str(e)}

    # Fix starts_with if needed
    if "starts_with" in validation_config and status == "pass":
        prefix = validation_config["starts_with"]
        if not output.strip().upper().startswith(prefix.upper()):
            output = f"{prefix} — {output}"

    # Save to DB
    run = TestRun(
        possibility=code,
        input_data=json.dumps(req.inputs),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output=output,
        status=status,
        model_used=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        safety_result=json.dumps(safety_result),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    return {
        "id": run.id,
        "output": output,
        "status": status,
        "regen_count": regen_count,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "safety": safety_result,
        "model": model,
        "user_prompt": user_prompt,
        "system_prompt": system_prompt,
        "created_at": run.created_at.isoformat(),
    }


@app.get("/api/history/{code}")
async def get_history(code: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    code = code.upper()
    result = await db.execute(
        select(TestRun)
        .where(TestRun.possibility == code)
        .order_by(desc(TestRun.created_at))
        .limit(limit)
    )
    runs = result.scalars().all()
    return [
        {
            "id": r.id,
            "output": r.output,
            "status": r.status,
            "tokens_in": r.tokens_in,
            "tokens_out": r.tokens_out,
            "model_used": r.model_used,
            "safety_result": json.loads(r.safety_result) if r.safety_result else {},
            "input_data": json.loads(r.input_data) if r.input_data else {},
            "created_at": r.created_at.isoformat(),
        }
        for r in runs
    ]


@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestRun).order_by(desc(TestRun.created_at)).limit(500))
    runs = result.scalars().all()
    total = len(runs)
    if total == 0:
        return {"total": 0, "pass_rate": 0, "fallbacks": 0, "errors": 0}
    passed = sum(1 for r in runs if r.status in ("pass", "pass_regen"))
    fallbacks = sum(1 for r in runs if r.status == "fallback")
    errors = sum(1 for r in runs if r.status == "error")
    return {
        "total": total,
        "pass_rate": round((passed / total) * 100, 1),
        "fallbacks": fallbacks,
        "errors": errors,
    }


@app.delete("/api/history/{code}")
async def clear_history(code: str, db: AsyncSession = Depends(get_db)):
    code = code.upper()
    result = await db.execute(select(TestRun).where(TestRun.possibility == code))
    runs = result.scalars().all()
    for r in runs:
        await db.delete(r)
    await db.commit()
    return {"deleted": len(runs)}
