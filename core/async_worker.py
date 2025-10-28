"""
Async Worker for Non-Blocking ROS2 Operations

This module provides a high-performance, non-blocking worker system for ROS2 operations.
Uses Qt's QThreadPool + concurrent.futures for efficient thread management and prevents UI freezing.
OPTIMIZED: Multiple async tasks in parallel with priority management
"""

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool, QTimer  # type: ignore
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading


class WorkerSignals(QObject):
    """
    Defines signals available from a running worker thread.
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class ROS2Worker(QRunnable):
    """
    Worker thread for executing ROS2 operations without blocking the UI.
    
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    """

    def __init__(self, fn, *args, **kwargs):
        super(ROS2Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Don't add progress_callback to kwargs - ROS2 functions don't need it

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            import sys
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class AsyncROS2Manager:
    """
    Async wrapper for ROS2Manager with AGGRESSIVE caching.
    
    Uses QThreadPool for GUI integration + ThreadPoolExecutor for pure async work.
    OPTIMIZED: Maximum cache reuse to minimize subprocess calls.
    """
    
    def __init__(self, ros2_manager, max_threads=2, cache_timeout=5.0):
        self.ros2_manager = ros2_manager
        self.threadpool = QThreadPool()
        
        # AGGRESSIVE thread management - fewer threads
        self.max_threads = max_threads
        self.cache_timeout = cache_timeout
        self.threadpool.setMaxThreadCount(max_threads)
        
        # Additional ThreadPoolExecutor for pure async operations
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        
        # AGGRESSIVE result cache - 5+ seconds
        self._cache = {}
        self._cache_timeout = cache_timeout
        self._cache_timestamps = {}
        self._lock = threading.Lock()
        
    def get_topics_async(self, callback):
        """Get topics info asynchronously with AGGRESSIVE caching"""
        if self._is_cached('topics'):
            with self._lock:
                callback(self._cache.get('topics', []))
            return
        
        def _wrapper(**kwargs):
            result = self.ros2_manager.get_topics_info()
            with self._lock:
                self._cache['topics'] = result
                self._cache_timestamps['topics'] = __import__('time').time()
            return result
        
        worker = ROS2Worker(_wrapper)
        worker.signals.result.connect(callback)
        worker.signals.error.connect(self._handle_error)
        self.threadpool.start(worker)
        
    def get_nodes_async(self, callback):
        """Get nodes info asynchronously with AGGRESSIVE caching"""
        if self._is_cached('nodes'):
            with self._lock:
                callback(self._cache.get('nodes', []))
            return
        
        def _wrapper(**kwargs):
            result = self.ros2_manager.get_nodes_info()
            with self._lock:
                self._cache['nodes'] = result
                self._cache_timestamps['nodes'] = __import__('time').time()
            return result
        
        worker = ROS2Worker(_wrapper)
        worker.signals.result.connect(callback)
        worker.signals.error.connect(self._handle_error)
        self.threadpool.start(worker)
        
    def get_services_async(self, callback):
        """Get services info asynchronously with AGGRESSIVE caching"""
        if self._is_cached('services'):
            with self._lock:
                callback(self._cache.get('services', []))
            return
        
        def _wrapper(**kwargs):
            result = self.ros2_manager.get_services_info()
            with self._lock:
                self._cache['services'] = result
                self._cache_timestamps['services'] = __import__('time').time()
            return result
        
        worker = ROS2Worker(_wrapper)
        worker.signals.result.connect(callback)
        worker.signals.error.connect(self._handle_error)
        self.threadpool.start(worker)
        
    def get_bag_info_async(self, bag_path, callback):
        """Get bag info asynchronously"""
        def _wrapper(**kwargs):
            return self.ros2_manager.get_bag_info(bag_path)
        
        worker = ROS2Worker(_wrapper)
        worker.signals.result.connect(callback)
        worker.signals.error.connect(self._handle_error)
        self.threadpool.start(worker)
    
    def _is_cached(self, key):
        """Check if cache is still valid"""
        import time
        with self._lock:
            if key not in self._cache:
                return False
            
            cache_age = time.time() - self._cache_timestamps.get(key, 0)
            return cache_age < self._cache_timeout
    
    def _handle_error(self, error_tuple):
        """Handle worker errors"""
        exctype, value, format_exc = error_tuple
        print(f"Async worker error: {value}")
        print(format_exc)
    
    def active_thread_count(self):
        """Get number of active threads"""
        return self.threadpool.activeThreadCount()
    
    def wait_for_done(self, timeout_ms=5000):
        """Wait for all threads to complete"""
        return self.threadpool.waitForDone(timeout_ms)
    
    def shutdown(self):
        """Shutdown all thread pools gracefully"""
        self.threadpool.waitForDone()
        self.executor.shutdown(wait=True)
