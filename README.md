# AioDNS-test
## Home assistant aiodns test Python code  
Copy code to HA /config directory
Run python3 test_aiodns.py  
Explanation of the code:  
The test_aiodns.py script tests the aiodns library for asynchronous DNS resolution in a Home Assistant Docker container.   
It performs:  
	* A record queries for registry.hub.docker.com (single-domain test)  
	* Multiple domains (registry.hub.docker.com, google.com, nonexistent.domain) concurrently, with a 2-second timeout.   
	* The script logs the system's default DNS servers (from /etc/resolv.conf), measures and logs query durations   
	* It handles errors like timeouts and NXDOMAIN.   
	* It ensures proper resolver cleanup to avoid cancellation errors, making it suitable for testing DNS functionality in a Docker environment with --	network=host.  
