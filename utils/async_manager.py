"""
Async task management module for the Simple Chat Agency.
Provides improved async task management with tracking and lifecycle handling.
"""
import asyncio
import threading
import time
from . import logger

# Get a logger instance
log = logger.get_logger(__name__)

class AsyncTaskManager:
    """
    Manager for async tasks that provides tracking and lifecycle management.
    """
    def __init__(self):
        self.loop = None
        self.pending_tasks = set()
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()
        self._started = False
    
    def start(self):
        """Start the event loop in a new thread if not already running"""
        with self._lock:
            if self._started:
                log.warning("AsyncTaskManager already started")
                return
                
            self._started = True
            self.loop = asyncio.new_event_loop()
            
            # Start the loop in a separate thread
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            
            log.info("AsyncTaskManager started")
    
    def _run_loop(self):
        """Run the event loop forever (in a separate thread)"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
        # Clean up pending tasks on loop stop
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        
        # Allow tasks to handle cancellation
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            
        log.info("AsyncTaskManager event loop stopped")
    
    def submit_task(self, coroutine, name=None):
        """
        Submit an async task to the event loop
        
        Args:
            coroutine: The coroutine to run
            name: Optional name for the task
            
        Returns:
            asyncio.Future: The future representing the task
        """
        with self._lock:
            if self._shutdown_event.is_set():
                raise RuntimeError("AsyncTaskManager is shutting down")
                
            if not self._started:
                self.start()
                
            task_name = name or f"Task-{len(self.pending_tasks)}"
            log.info(f"Submitting task: {task_name}")
            
            # Create a future for the coroutine
            future = asyncio.run_coroutine_threadsafe(coroutine, self.loop)
            
            # Add metadata
            future.task_name = task_name
            future.submit_time = time.time()
            
            # Track the future
            self.pending_tasks.add(future)
            future.add_done_callback(self._task_done_callback)
            
            return future
    
    def _task_done_callback(self, future):
        """Callback when a task is done"""
        # Remove from pending tasks
        self.pending_tasks.remove(future)
        
        # Get metadata
        task_name = getattr(future, 'task_name', 'Unknown')
        duration = time.time() - getattr(future, 'submit_time', time.time())
        
        # Check for exceptions
        if future.cancelled():
            log.warning(f"Task {task_name} was cancelled after {duration:.2f}s")
        elif future.exception() is not None:
            log.error(
                f"Task {task_name} failed after {duration:.2f}s: {future.exception()}",
                exc_info=future.exception()
            )
        else:
            log.info(f"Task {task_name} completed successfully in {duration:.2f}s")
    
    def shutdown(self, timeout=5.0):
        """
        Shutdown the AsyncTaskManager gracefully
        
        Args:
            timeout: Time to wait for pending tasks to complete
        """
        if not self._started:
            return
            
        log.info("Shutting down AsyncTaskManager")
        self._shutdown_event.set()
        
        # Wait for pending tasks to complete
        if self.pending_tasks:
            log.info(f"Waiting for {len(self.pending_tasks)} pending tasks to complete")
            wait_until = time.time() + timeout
            while self.pending_tasks and time.time() < wait_until:
                time.sleep(0.1)
                
        # Cancel any remaining tasks
        remaining = len(self.pending_tasks)
        if remaining > 0:
            log.warning(f"Cancelling {remaining} incomplete tasks")
            for task in list(self.pending_tasks):
                task.cancel()
                
        # Stop the loop
        with self._lock:
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
                
        # Wait for the thread to exit
        self._thread.join(timeout=1.0)
        log.info("AsyncTaskManager shutdown complete")

# Global task manager instance
task_manager = AsyncTaskManager()

def submit_async_task(coroutine, task_name=None):
    """
    Submit an async task to the global task manager
    
    Args:
        coroutine: The coroutine to run
        task_name: Optional name for the task
        
    Returns:
        asyncio.Future: The future representing the task
    """
    return task_manager.submit_task(coroutine, task_name)

def start_async_manager():
    """Start the global async task manager"""
    task_manager.start()

def shutdown_async_manager(timeout=5.0):
    """Shutdown the global async task manager"""
    task_manager.shutdown(timeout)
