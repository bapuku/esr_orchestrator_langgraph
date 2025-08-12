import httpx
from src.utils.config import settings

async def insurer_call(query: str) -> dict:
    # mock GET for demo; replace with real endpoints
    url = f"{settings.insurer_api_base}/v1/clauses"
    headers = {"Authorization": f"Bearer {settings.insurer_api_key}"} if settings.insurer_api_key else {}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # mock reply if base is not real
            if "mockinsurer" in settings.insurer_api_base:
                return {"clause": "Spills of toxic materials must be reported in 24h; form INS-24."}
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"error": str(e)}
