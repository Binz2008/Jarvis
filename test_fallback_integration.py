import asyncio
from jarvis.ai import fallback_manager

async def test_task(model_name, prompt):
    if 'fail' in prompt:
        raise ValueError('Simulated failure')
    return f'Response from {model_name} for: {prompt}'

async def test_fallback():
    print('=== Fallback Test: Success ===')
    result, attempt = await fallback_manager.execute_with_fallback(test_task, 'text', 'This should succeed.')
    print(f'Result: {result}')
    print(f'Attempt: {attempt}')
    print('\n=== Fallback Test: Forced Failure ===')
    result, attempt = await fallback_manager.execute_with_fallback(test_task, 'text', 'This should fail. fail')
    print(f'Result: {result}')
    print(f'Attempt: {attempt}')

if __name__ == "__main__":
    asyncio.run(test_fallback())
