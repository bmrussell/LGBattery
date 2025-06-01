import asyncio
import threading


async def listen_for_messages(wait_task_holder):
    # Simulating websocket.recv() with asyncio.sleep()
    wait_task = asyncio.create_task(asyncio.sleep(10))
    wait_task_holder['task'] = wait_task  # Expose the task to the other thread

    try:
        print("Waiting for message...")
        response = await asyncio.gather(wait_task)
        print(f"Response: {response}")
    except asyncio.CancelledError:
        print("wait_task was cancelled")

def cancel_wait_task(loop, wait_task_holder):
    # Called from another thread
    print("Cancelling the wait_task...")
    loop.call_soon_threadsafe(wait_task_holder['task'].cancel)

async def main():
    wait_task_holder = {}
    # Start the listener coroutine
    listener = asyncio.create_task(listen_for_messages(wait_task_holder))

    # Start the thread that will cancel the task after 2 seconds
    cancel_thread = threading.Thread(
        target=lambda: (
            asyncio.run(asyncio.sleep(2)),  # Sleep in thread for demonstration
            cancel_wait_task(asyncio.get_running_loop(), wait_task_holder)
        )
    )
    cancel_thread.start()

    # Wait for the listener to complete
    await listener

if __name__ == "__main__":
    asyncio.run(main())
