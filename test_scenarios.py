#!/usr/bin/env python3
"""
ESR Orchestrator Test Scenarios
Run various test cases to validate your solution with different data scenarios.
"""

import asyncio
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8010"

# Test scenarios based on your sample data and real-world ESR cases
TEST_SCENARIOS = [
    {
        "name": "Battery Leak Incident",
        "task": "Leak detected in container C-456 containing Lead-acid batteries at Site-A. Assess environmental impact, compliance status, and prepare insurance claim documentation.",
        "expected_components": ["waste_data", "compliance_check", "risk_assessment", "insurance_claim"]
    },
    {
        "name": "Lithium Battery Storage Assessment",
        "task": "Review storage conditions for lithium batteries in container C-222. Check compliance with fire safety regulations and assess insurance coverage adequacy.",
        "expected_components": ["storage_compliance", "fire_risk", "coverage_analysis"]
    },
    {
        "name": "Multi-Container Audit",
        "task": "Conduct comprehensive audit of all waste containers. Generate compliance report and identify potential insurance gaps.",
        "expected_components": ["full_audit", "compliance_gaps", "insurance_recommendations"]
    },
    {
        "name": "Regulatory Update Impact",
        "task": "New ISO 14001 requirements published. Assess impact on current waste management practices and update compliance protocols.",
        "expected_components": ["regulatory_analysis", "gap_assessment", "protocol_updates"]
    }
]

async def test_scenario(client: httpx.AsyncClient, scenario: dict) -> dict:
    """Test a single scenario against the ESR orchestrator."""
    print(f"\n🧪 Testing: {scenario['name']}")
    print(f"📝 Task: {scenario['task'][:100]}...")
    
    try:
        response = await client.post(
            f"{BASE_URL}/run",
            json={"task": scenario["task"]},
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Status: Success")
        print(f"📊 Response keys: {list(result.keys())}")
        
        if "report" in result:
            report = result["report"]
            print(f"📋 Report sections: {list(report.keys()) if isinstance(report, dict) else 'N/A'}")
        
        return {
            "scenario": scenario["name"],
            "status": "success",
            "result": result
        }
        
    except httpx.TimeoutException:
        print(f"⏰ Timeout: Request took longer than 60 seconds")
        return {"scenario": scenario["name"], "status": "timeout"}
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        return {"scenario": scenario["name"], "status": "http_error", "error": str(e)}
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return {"scenario": scenario["name"], "status": "error", "error": str(e)}

async def check_server_health():
    """Verify the server is running and healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            response.raise_for_status()
            print("✅ Server is healthy and ready for testing")
            return True
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        print(f"💡 Make sure to start the server first:")
        print(f"   uvicorn src.app:app --reload --port 8010")
        return False

async def run_all_tests():
    """Run all test scenarios."""
    print("🚀 ESR Orchestrator Test Suite")
    print("=" * 50)
    
    if not await check_server_health():
        return
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for scenario in TEST_SCENARIOS:
            result = await test_scenario(client, scenario)
            results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
    
    # Summary
    print("\n📈 Test Summary")
    print("=" * 30)
    success_count = sum(1 for r in results if r["status"] == "success")
    total_count = len(results)
    print(f"✅ Successful: {success_count}/{total_count}")
    
    if success_count < total_count:
        print("\n❌ Failed tests:")
        for result in results:
            if result["status"] != "success":
                print(f"  - {result['scenario']}: {result['status']}")
    
    # Save detailed results
    results_file = Path("test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Detailed results saved to: {results_file}")

def run_single_test(scenario_name: str = None):
    """Run a specific test scenario."""
    if scenario_name:
        scenario = next((s for s in TEST_SCENARIOS if s["name"] == scenario_name), None)
        if not scenario:
            print(f"❌ Scenario '{scenario_name}' not found")
            print("Available scenarios:")
            for s in TEST_SCENARIOS:
                print(f"  - {s['name']}")
            return
        scenarios = [scenario]
    else:
        scenarios = TEST_SCENARIOS
    
    async def run_tests():
        if not await check_server_health():
            return
        
        async with httpx.AsyncClient() as client:
            for scenario in scenarios:
                result = await test_scenario(client, scenario)
                print(f"\nResult: {json.dumps(result, indent=2, default=str)}")
    
    asyncio.run(run_tests())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        scenario_name = sys.argv[1]
        run_single_test(scenario_name)
    else:
        asyncio.run(run_all_tests())
