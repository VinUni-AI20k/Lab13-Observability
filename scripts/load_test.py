import argparse
import concurrent.futures
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")

# Enhanced: Track metrics for banking chatbot
class LoadTestMetrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.latencies: List[float] = []
        self.errors: Counter = Counter()
        self.feature_latencies: Dict[str, List[float]] = defaultdict(list)
        self.feature_errors: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()
    
    def record_success(self, feature: str, latency: float):
        self.total_requests += 1
        self.successful_requests += 1
        self.latencies.append(latency)
        self.feature_latencies[feature].append(latency)
    
    def record_error(self, feature: str, error_type: str):
        self.total_requests += 1
        self.failed_requests += 1
        self.errors[error_type] += 1
        self.feature_errors[feature] += 1
    
    def get_percentile(self, values: List[float], p: int) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        idx = max(0, min(len(sorted_values) - 1, int((p / 100) * len(sorted_values))))
        return sorted_values[idx]
    
    def print_summary(self):
        duration = time.time() - self.start_time
        print("\n" + "="*80)
        print("LOAD TEST SUMMARY - Banking Chatbot")
        print("="*80)
        print(f"Duration: {duration:.2f}s")
        print(f"Total Requests: {self.total_requests}")
        print(f"Successful: {self.successful_requests} ({self.successful_requests/self.total_requests*100:.1f}%)")
        print(f"Failed: {self.failed_requests} ({self.failed_requests/self.total_requests*100:.1f}%)")
        
        if self.latencies:
            print(f"\nLatency Statistics:")
            print(f"  P50: {self.get_percentile(self.latencies, 50):.1f}ms")
            print(f"  P95: {self.get_percentile(self.latencies, 95):.1f}ms")
            print(f"  P99: {self.get_percentile(self.latencies, 99):.1f}ms")
            print(f"  Min: {min(self.latencies):.1f}ms")
            print(f"  Max: {max(self.latencies):.1f}ms")
            print(f"  Avg: {sum(self.latencies)/len(self.latencies):.1f}ms")
        
        if self.errors:
            print(f"\nError Breakdown:")
            for error_type, count in self.errors.most_common():
                print(f"  {error_type}: {count}")
        
        if self.feature_latencies:
            print(f"\nFeature Performance:")
            for feature, latencies in sorted(self.feature_latencies.items()):
                error_count = self.feature_errors.get(feature, 0)
                total = len(latencies) + error_count
                success_rate = len(latencies) / total * 100 if total > 0 else 0
                print(f"  {feature}:")
                print(f"    Requests: {total} | Success: {success_rate:.1f}%")
                if latencies:
                    print(f"    P95: {self.get_percentile(latencies, 95):.1f}ms | Avg: {sum(latencies)/len(latencies):.1f}ms")
        
        print("="*80 + "\n")


metrics = LoadTestMetrics()


def send_request(client: httpx.Client, payload: dict) -> None:
    feature = payload.get('feature', 'unknown')
    try:
        start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        
        if r.status_code == 200:
            correlation_id = r.json().get('correlation_id', 'N/A')
            print(f"[{r.status_code}] {correlation_id} | {feature} | {latency:.1f}ms")
            metrics.record_success(feature, latency)
        else:
            print(f"[{r.status_code}] ERROR | {feature} | {latency:.1f}ms")
            metrics.record_error(feature, f"HTTP_{r.status_code}")
    except httpx.TimeoutException:
        print(f"[TIMEOUT] {feature}")
        metrics.record_error(feature, "TimeoutError")
    except httpx.ConnectError:
        print(f"[CONNECT_ERROR] {feature}")
        metrics.record_error(feature, "ConnectError")
    except Exception as e:
        print(f"[ERROR] {feature} | {type(e).__name__}: {e}")
        metrics.record_error(feature, type(e).__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test for Banking Chatbot")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0 = run once)")
    parser.add_argument("--filter-feature", type=str, default=None, help="Filter by feature (e.g., credit_inquiry)")
    args = parser.parse_args()

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    
    # Filter by feature if specified
    if args.filter_feature:
        lines = [line for line in lines if args.filter_feature in line]
        print(f"Filtered to {len(lines)} requests for feature: {args.filter_feature}")
    
    print(f"Starting load test with {args.concurrency} concurrent workers...")
    print(f"Total queries: {len(lines)}")
    
    with httpx.Client(timeout=30.0) as client:
        if args.duration > 0:
            # Sustained load test
            print(f"Running sustained load for {args.duration} seconds...")
            end_time = time.time() + args.duration
            while time.time() < end_time:
                if args.concurrency > 1:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                        futures = [executor.submit(send_request, client, json.loads(line)) for line in lines]
                        concurrent.futures.wait(futures)
                else:
                    for line in lines:
                        send_request(client, json.loads(line))
        else:
            # Single run
            if args.concurrency > 1:
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                    futures = [executor.submit(send_request, client, json.loads(line)) for line in lines]
                    concurrent.futures.wait(futures)
            else:
                for line in lines:
                    send_request(client, json.loads(line))
    
    # Print summary
    metrics.print_summary()


if __name__ == "__main__":
    main()
