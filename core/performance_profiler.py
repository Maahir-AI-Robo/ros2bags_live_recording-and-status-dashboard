"""
Performance Profiler - Advanced ROS2 performance analysis
Tracks message latency, per-topic resource usage, QoS mismatches
"""

import subprocess
import json
import time
from datetime import datetime
from collections import defaultdict, deque
import psutil


class PerformanceProfiler:
    """
    Advanced performance profiling for ROS2 systems
    """
    
    def __init__(self, ros2_manager):
        self.ros2_manager = ros2_manager
        
        # Performance data storage
        self.topic_stats = defaultdict(lambda: {
            'message_count': 0,
            'total_size_bytes': 0,
            'message_rates': deque(maxlen=60),  # Last 60 samples
            'bandwidth': deque(maxlen=60),
            'last_update': None
        })
        
        # Latency tracking
        self.latency_data = defaultdict(lambda: deque(maxlen=100))
        
        # QoS analysis results
        self.qos_issues = []
        
        # Node resource usage
        self.node_resources = defaultdict(lambda: {
            'cpu_percent': 0,
            'memory_mb': 0,
            'thread_count': 0
        })
        
    def profile_topics(self):
        """
        Profile all active topics for performance metrics
        
        Returns:
            dict: Topic-level performance data
        """
        topics = self.ros2_manager.get_topics_info()
        current_time = time.time()
        
        profiling_results = []
        
        for topic_info in topics:
            topic_name = topic_info['name']
            
            # Get topic bandwidth using ros2 topic bw
            bandwidth = self._measure_topic_bandwidth(topic_name)
            
            # Get message rate using ros2 topic hz
            msg_rate = self._measure_topic_rate(topic_name)
            
            # Update stats
            stats = self.topic_stats[topic_name]
            stats['message_rates'].append(msg_rate)
            stats['bandwidth'].append(bandwidth)
            stats['last_update'] = current_time
            
            # Calculate averages
            avg_rate = sum(stats['message_rates']) / len(stats['message_rates']) if stats['message_rates'] else 0
            avg_bandwidth = sum(stats['bandwidth']) / len(stats['bandwidth']) if stats['bandwidth'] else 0
            
            profiling_results.append({
                'topic': topic_name,
                'type': topic_info['type'],
                'publishers': topic_info.get('publishers', 0),
                'current_rate_hz': msg_rate,
                'avg_rate_hz': avg_rate,
                'current_bandwidth_kbs': bandwidth,
                'avg_bandwidth_kbs': avg_bandwidth,
                'efficiency_score': self._calculate_efficiency_score(msg_rate, bandwidth)
            })
            
        return profiling_results
        
    def _measure_topic_bandwidth(self, topic_name, duration=2.0):
        """
        Measure topic bandwidth in KB/s
        
        Args:
            topic_name: Topic to measure
            duration: Measurement duration in seconds
            
        Returns:
            float: Bandwidth in KB/s
        """
        try:
            cmd = f"timeout {duration}s ros2 topic bw {topic_name} 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=duration + 1
            )
            
            # Parse output: "average: X.XX KB/s"
            output = result.stdout.strip()
            if "average:" in output:
                parts = output.split("average:")[1].strip().split()
                if len(parts) >= 1:
                    return float(parts[0])
                    
        except (subprocess.TimeoutExpired, ValueError, IndexError):
            pass
            
        return 0.0
        
    def _measure_topic_rate(self, topic_name, duration=2.0):
        """
        Measure topic message rate in Hz
        
        Args:
            topic_name: Topic to measure
            duration: Measurement duration in seconds
            
        Returns:
            float: Message rate in Hz
        """
        try:
            cmd = f"timeout {duration}s ros2 topic hz {topic_name} 2>/dev/null"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=duration + 1
            )
            
            # Parse output: "average rate: X.XXX"
            output = result.stdout.strip()
            if "average rate:" in output:
                parts = output.split("average rate:")[1].strip().split()
                if len(parts) >= 1:
                    return float(parts[0])
                    
        except (subprocess.TimeoutExpired, ValueError, IndexError):
            pass
            
        return 0.0
        
    def analyze_qos_compatibility(self):
        """
        Analyze QoS compatibility between publishers and subscribers
        
        Returns:
            list: QoS issues found
        """
        issues = []
        topics = self.ros2_manager.get_topics_info()
        
        for topic_info in topics:
            topic_name = topic_info['name']
            
            # Get QoS info (would need ros2 topic info --verbose)
            qos_data = self._get_topic_qos(topic_name)
            
            # Check for common QoS mismatches
            if qos_data:
                # Reliability mismatch
                if 'reliability_mismatch' in qos_data:
                    issues.append({
                        'topic': topic_name,
                        'severity': 'high',
                        'issue': 'Reliability mismatch',
                        'description': 'Publisher/subscriber reliability settings incompatible',
                        'recommendation': 'Align reliability policies (RELIABLE or BEST_EFFORT)'
                    })
                    
                # Durability mismatch
                if 'durability_mismatch' in qos_data:
                    issues.append({
                        'topic': topic_name,
                        'severity': 'medium',
                        'issue': 'Durability mismatch',
                        'description': 'Incompatible durability settings',
                        'recommendation': 'Use consistent durability (VOLATILE or TRANSIENT_LOCAL)'
                    })
                    
                # Deadline missed
                if qos_data.get('deadline_missed', False):
                    issues.append({
                        'topic': topic_name,
                        'severity': 'high',
                        'issue': 'Deadline violations',
                        'description': 'Messages not meeting deadline requirements',
                        'recommendation': 'Increase deadline period or optimize publisher'
                    })
        
        self.qos_issues = issues
        return issues
        
    def _get_topic_qos(self, topic_name):
        """
        Get QoS information for a topic
        
        Args:
            topic_name: Topic name
            
        Returns:
            dict: QoS data
        """
        try:
            cmd = f"ros2 topic info {topic_name} --verbose"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=3
            )
            
            # Parse QoS info from output
            # This is simplified - real implementation would parse full QoS details
            qos_data = {}
            
            output = result.stdout.lower()
            if 'reliability' in output:
                qos_data['has_reliability'] = True
            if 'durability' in output:
                qos_data['has_durability'] = True
                
            return qos_data
            
        except (subprocess.TimeoutExpired, Exception):
            return {}
            
    def profile_nodes(self):
        """
        Profile resource usage per ROS2 node
        
        Returns:
            dict: Node resource usage data
        """
        nodes = self.ros2_manager.get_nodes_info()
        profiling_results = []
        
        # Get all ROS2-related processes
        ros2_processes = self._get_ros2_processes()
        
        for node_info in nodes:
            node_name = node_info['name']
            
            # Try to find matching process
            process = self._find_node_process(node_name, ros2_processes)
            
            if process:
                try:
                    cpu = process.cpu_percent(interval=0.1)
                    memory = process.memory_info().rss / (1024 * 1024)  # MB
                    threads = process.num_threads()
                    
                    self.node_resources[node_name].update({
                        'cpu_percent': cpu,
                        'memory_mb': memory,
                        'thread_count': threads
                    })
                    
                    profiling_results.append({
                        'node': node_name,
                        'cpu_percent': cpu,
                        'memory_mb': memory,
                        'thread_count': threads,
                        'publishers': node_info.get('publishers', 0),
                        'subscribers': node_info.get('subscribers', 0),
                        'efficiency_score': self._calculate_node_efficiency(cpu, memory, 
                                                node_info.get('publishers', 0) + node_info.get('subscribers', 0))
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        return profiling_results
        
    def _get_ros2_processes(self):
        """Get all ROS2-related processes"""
        ros2_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('ros2' in str(cmd).lower() for cmd in cmdline):
                    ros2_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return ros2_processes
        
    def _find_node_process(self, node_name, processes):
        """Find process matching node name"""
        # Simplified - in real implementation, would use more sophisticated matching
        for proc in processes:
            try:
                cmdline = ' '.join(proc.cmdline())
                if node_name in cmdline:
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return None
        
    def _calculate_efficiency_score(self, msg_rate, bandwidth):
        """
        Calculate efficiency score for a topic
        
        Args:
            msg_rate: Messages per second
            bandwidth: Bandwidth in KB/s
            
        Returns:
            float: Efficiency score (0-100)
        """
        if msg_rate == 0 or bandwidth == 0:
            return 100.0
            
        # Calculate average message size
        avg_msg_size = (bandwidth * 1024) / msg_rate if msg_rate > 0 else 0
        
        # Score based on message size (smaller is better for efficiency)
        # Typical message sizes: 100 bytes - 10KB
        if avg_msg_size < 1024:  # < 1KB
            return 95.0
        elif avg_msg_size < 10240:  # < 10KB
            return 80.0
        elif avg_msg_size < 102400:  # < 100KB
            return 60.0
        else:
            return 40.0
            
    def _calculate_node_efficiency(self, cpu_percent, memory_mb, topic_count):
        """
        Calculate efficiency score for a node
        
        Args:
            cpu_percent: CPU usage
            memory_mb: Memory usage in MB
            topic_count: Number of topics handled
            
        Returns:
            float: Efficiency score (0-100)
        """
        if topic_count == 0:
            return 50.0
            
        # Calculate resource per topic
        cpu_per_topic = cpu_percent / topic_count
        memory_per_topic = memory_mb / topic_count
        
        # Score based on resource efficiency
        score = 100.0
        
        # Penalize high CPU per topic
        if cpu_per_topic > 10:
            score -= 30
        elif cpu_per_topic > 5:
            score -= 15
            
        # Penalize high memory per topic
        if memory_per_topic > 100:
            score -= 30
        elif memory_per_topic > 50:
            score -= 15
            
        return max(0, score)
        
    def generate_performance_report(self):
        """
        Generate comprehensive performance report
        
        Returns:
            dict: Complete performance report
        """
        topic_profiles = self.profile_topics()
        node_profiles = self.profile_nodes()
        qos_issues = self.analyze_qos_compatibility()
        
        # Calculate overall system health
        topic_scores = [t['efficiency_score'] for t in topic_profiles if 'efficiency_score' in t]
        node_scores = [n['efficiency_score'] for n in node_profiles if 'efficiency_score' in n]
        
        avg_topic_score = sum(topic_scores) / len(topic_scores) if topic_scores else 100
        avg_node_score = sum(node_scores) / len(node_scores) if node_scores else 100
        
        overall_health = (avg_topic_score + avg_node_score) / 2
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            topic_profiles, node_profiles, qos_issues
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health_score': overall_health,
            'topic_performance': topic_profiles,
            'node_performance': node_profiles,
            'qos_issues': qos_issues,
            'recommendations': recommendations,
            'summary': {
                'total_topics': len(topic_profiles),
                'total_nodes': len(node_profiles),
                'critical_issues': len([i for i in qos_issues if i['severity'] == 'high']),
                'warnings': len([i for i in qos_issues if i['severity'] == 'medium'])
            }
        }
        
    def _generate_recommendations(self, topics, nodes, qos_issues):
        """Generate performance recommendations"""
        recommendations = []
        
        # Check for high bandwidth topics
        high_bw_topics = [t for t in topics if t.get('avg_bandwidth_kbs', 0) > 1000]
        if high_bw_topics:
            recommendations.append({
                'priority': 'high',
                'category': 'bandwidth',
                'message': f'High bandwidth detected on {len(high_bw_topics)} topic(s)',
                'action': 'Consider reducing message rate or size, or use compression'
            })
            
        # Check for inefficient nodes
        inefficient_nodes = [n for n in nodes if n.get('efficiency_score', 100) < 60]
        if inefficient_nodes:
            recommendations.append({
                'priority': 'medium',
                'category': 'resource_usage',
                'message': f'{len(inefficient_nodes)} node(s) using excessive resources',
                'action': 'Profile and optimize node code, reduce unnecessary processing'
            })
            
        # Check for QoS issues
        if qos_issues:
            recommendations.append({
                'priority': 'high',
                'category': 'qos',
                'message': f'Found {len(qos_issues)} QoS compatibility issue(s)',
                'action': 'Review and align QoS policies between publishers and subscribers'
            })
            
        return recommendations
        
    def export_report(self, filepath):
        """Export performance report to JSON file"""
        report = self.generate_performance_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
            
        return filepath
