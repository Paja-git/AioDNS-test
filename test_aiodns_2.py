import asyncio
import aiodns
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log DNS servers used by aiodns
def log_dns_servers():
    resolver = aiodns.DNSResolver()
    nameservers = resolver.nameservers or ["system default (from /etc/resolv.conf)"]
    logger.info(f"DNS servers used: {', '.join(nameservers)}")
    resolver.cancel()

async def test_dns_lookup():
    # Create a DNS resolver instance
    resolver = aiodns.DNSResolver()

    # Domain to test
    test_domain = "registry.hub.docker.com"

    try:
        # Perform an A record lookup with timing
        logger.info(f"Performing A record lookup for {test_domain}")
        start_time = asyncio.get_event_loop().time()
        result = await resolver.query(test_domain, 'A')
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        for record in result:
            logger.info(f"A record: {record.host}")
        logger.info(f"DNS resolution for {test_domain} took {duration:.3f} seconds")

    except aiodns.error.DNSError as e:
        logger.error(f"DNS lookup failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        # Clean up the resolver
        resolver.cancel()

async def test_multi_domain_with_timeout(domains, query_type, timeout=5.0):
    # Create a DNS resolver instance with timeout
    resolver = aiodns.DNSResolver(timeout=timeout)

    async def query_domain(domain):
        try:
            logger.info(f"Performing {query_type} record lookup for {domain}")
            start_time = asyncio.get_event_loop().time()
            result = await resolver.query(domain, query_type)
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            logger.info(f"DNS resolution for {domain} took {duration:.3f} seconds")
            return domain, [(record.host, getattr(record, 'priority', None)) for record in result]
        except aiodns.error.DNSError as e:
            logger.error(f"DNS lookup failed for {domain}: {e}")
            if e.args[0] == 4:  # ARES_ETIMEOUT
                logger.error(f"Timeout occurred for {domain}")
            return domain, None
        except Exception as e:
            logger.error(f"Unexpected error for {domain}: {e}")
            return domain, None

    # Perform concurrent DNS queries
    start_time = asyncio.get_event_loop().time()
    tasks = [query_domain(domain) for domain in domains]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = asyncio.get_event_loop().time()
    total_duration = end_time - start_time
    logger.info(f"Total DNS resolution for all domains took {total_duration:.3f} seconds")

    # Log results
    for domain, result in results:
        if result:
            for host, priority in result:
                logger.info(f"{domain} {query_type} record: {host}")
        else:
            logger.info(f"No {query_type} records found for {domain}")

    # Clean up the resolver after all queries
    resolver.cancel()

async def main():
    # Run original single-domain test
    await test_dns_lookup()

    # Run new multi-domain test with timeout
    domains = ["registry.hub.docker.com", "google.com", "nonexistent.domain"]
    await test_multi_domain_with_timeout(domains, 'A', timeout=2.0)

if __name__ == "__main__":
    log_dns_servers()  # Log DNS servers at the start
    asyncio.run(main())