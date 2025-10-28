"""
ROS2 Network Discovery - Detect robots and their topics on local network
Uses ROS2 DDS discovery to find all ROS2 entities on the same domain
"""

import subprocess
import re
import os
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ROS2Robot:
    """Represents a discovered ROS2 robot on the network"""
    hostname: str
    domain_id: int
    nodes: List[str]
    topics: List[str]
    services: List[str]
    last_seen: datetime
    
    def __hash__(self):
        return hash(self.hostname)


class NetworkRobotDiscovery:
    """Discovers ROS2 robots on the local network"""
    
    def __init__(self):
        self.discovered_robots: Dict[str, ROS2Robot] = {}
        self.current_domain = self._get_current_domain()
        
    def _get_current_domain(self) -> int:
        """Get current ROS2 domain ID"""
        domain = os.environ.get('ROS_DOMAIN_ID', '0')
        try:
            return int(domain)
        except:
            return 0
    
    def set_domain(self, domain_id: int):
        """Change ROS2 domain for discovery"""
        self.current_domain = domain_id
        os.environ['ROS_DOMAIN_ID'] = str(domain_id)
        
    def discover_network_robots(self) -> Dict[str, ROS2Robot]:
        """
        Discover all ROS2 robots on the network
        Returns dict of hostname -> ROS2Robot
        """
        try:
            # Get all nodes with their hostnames
            nodes_by_host = self._get_nodes_by_hostname()
            
            # For each unique host, gather all ROS2 info
            for hostname, nodes in nodes_by_host.items():
                topics = self._get_topics_for_nodes(nodes)
                services = self._get_services_for_nodes(nodes)
                
                robot = ROS2Robot(
                    hostname=hostname,
                    domain_id=self.current_domain,
                    nodes=nodes,
                    topics=topics,
                    services=services,
                    last_seen=datetime.now()
                )
                
                self.discovered_robots[hostname] = robot
                
            return self.discovered_robots
            
        except Exception as e:
            print(f"Network discovery error: {e}")
            return {}
    
    def _get_nodes_by_hostname(self) -> Dict[str, List[str]]:
        """Get all ROS2 nodes grouped by hostname"""
        nodes_by_host = {}
        
        try:
            # Get node list
            result = subprocess.run(
                ['ros2', 'node', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return nodes_by_host
            
            nodes = [n.strip() for n in result.stdout.split('\n') if n.strip()]
            
            # For each node, try to get its hostname via node info
            for node in nodes:
                hostname = self._get_node_hostname(node)
                if hostname not in nodes_by_host:
                    nodes_by_host[hostname] = []
                nodes_by_host[hostname].append(node)
                
        except subprocess.TimeoutExpired:
            print("Node discovery timeout")
        except Exception as e:
            print(f"Error getting nodes: {e}")
            
        return nodes_by_host
    
    def _get_node_hostname(self, node_name: str) -> str:
        """
        Try to determine hostname for a node
        ROS2 doesn't directly provide hostname, so we use heuristics
        """
        try:
            # Try to get node info
            result = subprocess.run(
                ['ros2', 'node', 'info', node_name],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parse for any hostname hints in the output
            # This is a heuristic - actual implementation may vary
            output = result.stdout.lower()
            
            # Check for common hostname patterns
            hostname_match = re.search(r'(?:host|name):\s*(\S+)', output)
            if hostname_match:
                return hostname_match.group(1)
            
            # If no hostname found, check if node is local or remote
            # by checking if we can reach it quickly
            if result.returncode == 0:
                # Node is reachable, assume local for now
                return self._get_local_hostname()
            
        except:
            pass
        
        # Default to local hostname
        return self._get_local_hostname()
    
    def _get_local_hostname(self) -> str:
        """Get local machine hostname"""
        try:
            result = subprocess.run(
                ['hostname'],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.stdout.strip()
        except:
            return "localhost"
    
    def _get_topics_for_nodes(self, nodes: List[str]) -> List[str]:
        """Get all topics published/subscribed by given nodes"""
        topics = set()
        
        for node in nodes:
            try:
                result = subprocess.run(
                    ['ros2', 'node', 'info', node],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                # Parse topics from node info
                lines = result.stdout.split('\n')
                in_topics_section = False
                
                for line in lines:
                    if 'Subscribers:' in line or 'Publishers:' in line:
                        in_topics_section = True
                        continue
                    elif 'Service Servers:' in line or 'Service Clients:' in line:
                        in_topics_section = False
                        continue
                    
                    if in_topics_section and line.strip():
                        # Extract topic name (format: "  /topic_name: msg_type")
                        match = re.match(r'\s+(/\S+):', line)
                        if match:
                            topics.add(match.group(1))
                            
            except:
                continue
                
        return sorted(list(topics))
    
    def _get_services_for_nodes(self, nodes: List[str]) -> List[str]:
        """Get all services provided by given nodes"""
        services = set()
        
        for node in nodes:
            try:
                result = subprocess.run(
                    ['ros2', 'node', 'info', node],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                # Parse services from node info
                lines = result.stdout.split('\n')
                in_services_section = False
                
                for line in lines:
                    if 'Service Servers:' in line:
                        in_services_section = True
                        continue
                    elif 'Service Clients:' in line or 'Action Servers:' in line:
                        in_services_section = False
                        continue
                    
                    if in_services_section and line.strip():
                        # Extract service name
                        match = re.match(r'\s+(/\S+):', line)
                        if match:
                            services.add(match.group(1))
                            
            except:
                continue
                
        return sorted(list(services))
    
    def get_all_network_topics(self) -> List[Dict]:
        """Get all unique topics from all robots on network"""
        all_topics = set()
        
        for robot in self.discovered_robots.values():
            all_topics.update(robot.topics)
        
        # Get additional info for each topic
        topics_info = []
        for topic in sorted(all_topics):
            try:
                # Get topic type
                result = subprocess.run(
                    ['ros2', 'topic', 'info', topic],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                topic_type = "Unknown"
                publisher_count = 0
                subscriber_count = 0
                
                for line in result.stdout.split('\n'):
                    if 'Type:' in line:
                        topic_type = line.split('Type:')[1].strip()
                    elif 'Publisher count:' in line:
                        publisher_count = int(re.search(r'\d+', line).group())
                    elif 'Subscription count:' in line:
                        subscriber_count = int(re.search(r'\d+', line).group())
                
                topics_info.append({
                    'name': topic,
                    'type': topic_type,
                    'publishers': publisher_count,
                    'subscribers': subscriber_count
                })
                
            except:
                topics_info.append({
                    'name': topic,
                    'type': 'Unknown',
                    'publishers': 0,
                    'subscribers': 0
                })
        
        return topics_info
    
    def get_robot_sensors(self, hostname: str) -> Dict[str, List[str]]:
        """
        Identify sensors on a robot by topic patterns
        Returns categorized sensor topics
        """
        if hostname not in self.discovered_robots:
            return {}
        
        robot = self.discovered_robots[hostname]
        sensors = {
            'cameras': [],
            'lidars': [],
            'imu': [],
            'gps': [],
            'odometry': [],
            'joint_states': [],
            'tf': [],
            'other': []
        }
        
        for topic in robot.topics:
            topic_lower = topic.lower()
            
            if 'camera' in topic_lower or 'image' in topic_lower or '/rgb' in topic_lower:
                sensors['cameras'].append(topic)
            elif 'lidar' in topic_lower or 'scan' in topic_lower or 'pointcloud' in topic_lower or 'laser' in topic_lower:
                sensors['lidars'].append(topic)
            elif 'imu' in topic_lower:
                sensors['imu'].append(topic)
            elif 'gps' in topic_lower or 'navsat' in topic_lower:
                sensors['gps'].append(topic)
            elif 'odom' in topic_lower:
                sensors['odometry'].append(topic)
            elif 'joint_state' in topic_lower:
                sensors['joint_states'].append(topic)
            elif '/tf' in topic or 'transform' in topic_lower:
                sensors['tf'].append(topic)
            else:
                sensors['other'].append(topic)
        
        # Remove empty categories
        return {k: v for k, v in sensors.items() if v}
    
    def scan_domains(self, start_domain: int = 0, end_domain: int = 10) -> Dict[int, int]:
        """
        Scan multiple ROS2 domains for active robots
        Returns dict of domain_id -> number of nodes found
        """
        original_domain = self.current_domain
        domain_results = {}
        
        for domain_id in range(start_domain, end_domain + 1):
            try:
                self.set_domain(domain_id)
                
                # Quick check for nodes
                result = subprocess.run(
                    ['ros2', 'node', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                node_count = len([n for n in result.stdout.split('\n') if n.strip()])
                domain_results[domain_id] = node_count
                
            except:
                domain_results[domain_id] = 0
        
        # Restore original domain
        self.set_domain(original_domain)
        
        return domain_results
    
    def get_summary(self) -> str:
        """Get human-readable summary of discovered robots"""
        if not self.discovered_robots:
            return "No robots discovered on the network."
        
        summary = f"Discovered {len(self.discovered_robots)} robot(s) on ROS_DOMAIN_ID={self.current_domain}:\n\n"
        
        for hostname, robot in self.discovered_robots.items():
            summary += f"🤖 Robot: {hostname}\n"
            summary += f"   Nodes: {len(robot.nodes)}\n"
            summary += f"   Topics: {len(robot.topics)}\n"
            summary += f"   Services: {len(robot.services)}\n"
            summary += f"   Last seen: {robot.last_seen.strftime('%H:%M:%S')}\n"
            
            # Show sensors if any
            sensors = self.get_robot_sensors(hostname)
            if sensors:
                summary += "   Sensors:\n"
                for sensor_type, topics in sensors.items():
                    summary += f"      {sensor_type}: {len(topics)}\n"
            
            summary += "\n"
        
        return summary
