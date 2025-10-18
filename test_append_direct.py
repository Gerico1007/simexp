import asyncio
import sys
from simexp.playwright_writer import SimplenoteWriter

async def test():
    async with SimplenoteWriter(
        note_url='https://app.simplenote.com/',
        cdp_url='http://localhost:9222'
    ) as writer:
        await writer.page.goto('https://app.simplenote.com/')
        await writer.page.wait_for_load_state('networkidle')
        
        # Direct test of append_content
        print("\n🔬 CALLING append_content() DIRECTLY:\n")
        try:
            await writer.append_content("Direct test content\n")
            print("\n✅ append_content() completed\n")
        except Exception as e:
            print(f"\n❌ append_content() failed: {e}\n")
            import traceback
            traceback.print_exc()

asyncio.run(test())
