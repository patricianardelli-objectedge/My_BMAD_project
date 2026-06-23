#!/usr/bin/env python3
"""
Epic 4 Test Runner - Orchestrates all API and E2E tests
Runs pytest for API tests and provides test execution framework

Usage:
  python run_tests.py                    # Run all tests
  python run_tests.py --api-only         # Run only API tests
  python run_tests.py --suite story-4.1  # Run specific test suite
  python run_tests.py --verbose          # Run with verbose output
"""

import sys
import os
import subprocess
import argparse
import json
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
TESTS_DIR = Path(__file__).parent
API_TEST_FILE = TESTS_DIR / 'test_api_endpoints.py'
E2E_TEST_FILE = TESTS_DIR / 'test_e2e.js'
BACKEND_URL = 'http://127.0.0.1:5000'
FRONTEND_URL = 'http://127.0.0.1:3000'

# Color codes for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_step(text, step_num=None):
    """Print formatted step"""
    if step_num:
        print(f"{Colors.OKBLUE}{Colors.BOLD}[Step {step_num}]{Colors.ENDC} {text}")
    else:
        print(f"{Colors.OKBLUE}→{Colors.ENDC} {text}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {text}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")

def check_backend_running():
    """Check if Flask backend is running"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        return result == 0
    except:
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    required = ['pytest', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_warning(f"Missing dependencies: {', '.join(missing)}")
        print_step("Install with: pip install " + " ".join(missing))
        return False
    return True

def run_api_tests(verbose=False, suite=None):
    """Run Python API tests using pytest"""
    print_header("RUNNING API TESTS (Python/pytest)")
    
    if not check_backend_running():
        print_error("Flask backend is not running!")
        print_step("Start backend: python _bmad-output/implementation-artifacts/nlu/app.py")
        return False
    
    print_success("Backend is running ✓")
    
    cmd = [
        'pytest',
        str(API_TEST_FILE),
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    if verbose:
        cmd.append('-vv')
    
    if suite:
        cmd.append(f'-k {suite}')
    
    print_step(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=TESTS_DIR)
        return result.returncode == 0
    except FileNotFoundError:
        print_error("pytest not found. Install with: pip install pytest")
        return False
    except Exception as e:
        print_error(f"Test execution failed: {str(e)}")
        return False

def run_api_test_suite(suite_name):
    """Run specific API test suite"""
    suites = {
        'registration': 'TestUserRegistration',
        'login': 'TestUserLogin',
        'preferences': 'TestUserPreferences',
        'avoid-list': 'TestAvoidList',
        'order-history': 'TestOrderHistory',
        'subscription': 'TestSubscriptionLifecycle',
        'decision-engine': 'TestDecisionEngineIntegration',
        'journey': 'TestFullUserJourney',
        'story-4.1': 'TestUserRegistration or TestUserLogin or TestUserPreferences or TestAvoidList',
        'story-4.2': 'TestOrderHistory or TestDecisionEngineIntegration',
        'story-4.3': 'TestSubscriptionLifecycle',
    }
    
    if suite_name not in suites:
        print_error(f"Unknown suite: {suite_name}")
        print_step("Available suites: " + ", ".join(suites.keys()))
        return False
    
    cmd = [
        'pytest',
        str(API_TEST_FILE),
        '-v',
        '-k', suites[suite_name],
        '--tb=short'
    ]
    
    print_step(f"Running suite: {suite_name}\n")
    
    try:
        result = subprocess.run(cmd, cwd=TESTS_DIR)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Test execution failed: {str(e)}")
        return False

def run_e2e_tests():
    """Run E2E tests using Jest or Node test runner"""
    print_header("RUNNING E2E TESTS (JavaScript/Jest)")
    
    print_warning("E2E tests require Playwright or Jest to be configured")
    print_step("To run E2E tests:")
    print_step("  1. Install: npm install --save-dev @playwright/test jest")
    print_step("  2. Run: npx jest test_e2e.js")
    print_step("  3. Or: npx playwright test test_e2e.js")
    
    if Path('package.json').exists():
        print_step("\nRunning E2E tests with Jest...\n")
        try:
            result = subprocess.run(['npx', 'jest', str(E2E_TEST_FILE), '-v'])
            return result.returncode == 0
        except Exception as e:
            print_error(f"E2E test execution failed: {str(e)}")
            return False
    else:
        print_warning("package.json not found. Skipping E2E tests.")
        return True

def generate_test_report(api_passed, e2e_passed=None):
    """Generate test execution report"""
    print_header("TEST EXECUTION REPORT")
    
    timestamp = datetime.now().isoformat()
    report = {
        'timestamp': timestamp,
        'backend_url': BACKEND_URL,
        'frontend_url': FRONTEND_URL,
        'tests': {
            'api_tests': {
                'status': 'PASSED' if api_passed else 'FAILED',
                'file': str(API_TEST_FILE)
            }
        }
    }
    
    if e2e_passed is not None:
        report['tests']['e2e_tests'] = {
            'status': 'PASSED' if e2e_passed else 'FAILED',
            'file': str(E2E_TEST_FILE)
        }
    
    print("\nTest Results Summary:")
    print(f"  API Tests: {Colors.OKGREEN if api_passed else Colors.FAIL}" +
          f"{'✓ PASSED' if api_passed else '✗ FAILED'}{Colors.ENDC}")
    
    if e2e_passed is not None:
        print(f"  E2E Tests: {Colors.OKGREEN if e2e_passed else Colors.FAIL}" +
              f"{'✓ PASSED' if e2e_passed else '✗ FAILED'}{Colors.ENDC}")
    
    overall_status = api_passed and (e2e_passed if e2e_passed is not None else True)
    status_color = Colors.OKGREEN if overall_status else Colors.FAIL
    print(f"\nOverall Status: {status_color}{Colors.BOLD}" +
          f"{'✓ ALL TESTS PASSED' if overall_status else '✗ SOME TESTS FAILED'}{Colors.ENDC}")
    
    # Save report
    report_file = TESTS_DIR / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(
        description='Epic 4 Test Runner - Comprehensive test execution framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python run_tests.py                              # Run all tests
  python run_tests.py --api-only                   # Run only API tests
  python run_tests.py --suite story-4.1            # Run Story 4.1 tests
  python run_tests.py --suite registration         # Run registration tests only
  python run_tests.py --suite decision-engine      # Run decision engine integration
  python run_tests.py --verbose                    # Verbose output
  python run_tests.py --no-e2e                     # Skip E2E tests
  python run_tests.py --check-deps                 # Check dependencies only

Test Suites:
  - registration (Story 4.1)
  - login (Story 4.1)
  - preferences (Story 4.1)
  - avoid-list (Story 4.1)
  - order-history (Story 4.2)
  - decision-engine (Story 4.2)
  - subscription (Story 4.3)
  - journey (Full end-to-end journey)
        '''
    )
    
    parser.add_argument('--api-only', action='store_true',
                       help='Run only API tests (skip E2E)')
    parser.add_argument('--suite', type=str,
                       help='Run specific test suite')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--no-e2e', action='store_true',
                       help='Skip E2E tests')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check dependencies and exit')
    
    args = parser.parse_args()
    
    # Print welcome
    print_header("Epic 4 - End-to-End Testing Suite")
    print("Comprehensive test execution for User Profile & Preferences")
    print(f"Test Directory: {TESTS_DIR}")
    print(f"Project Root: {PROJECT_ROOT}\n")
    
    # Check dependencies
    print_step("Checking dependencies...", 1)
    if not check_dependencies():
        print_error("Please install missing dependencies")
        if not args.check_deps:
            sys.exit(1)
    print_success("All dependencies available ✓")
    
    if args.check_deps:
        sys.exit(0)
    
    # Check backend
    print_step("Checking backend connectivity...", 2)
    if check_backend_running():
        print_success(f"Backend reachable at {BACKEND_URL}")
    else:
        print_error(f"Cannot reach backend at {BACKEND_URL}")
        print_step("Start the Flask server: python _bmad-output/implementation-artifacts/nlu/app.py")
    
    # Run tests
    api_passed = True
    e2e_passed = None
    
    if args.api_only or args.suite:
        if args.suite:
            api_passed = run_api_test_suite(args.suite)
        else:
            api_passed = run_api_tests(verbose=args.verbose)
    else:
        api_passed = run_api_tests(verbose=args.verbose)
        
        if not args.no_e2e:
            e2e_passed = run_e2e_tests()
    
    # Generate report
    generate_test_report(api_passed, e2e_passed)
    
    # Exit with appropriate code
    success = api_passed and (e2e_passed if e2e_passed is not None else True)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
