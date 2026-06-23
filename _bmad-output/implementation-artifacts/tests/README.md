# 🧪 Epic 4 Testing - Quick Reference

## One-Line Test Commands

```bash
# ⚡ Fast: All tests
python run_tests.py

# 📋 By Story
python run_tests.py --suite story-4.1    # User Profile
python run_tests.py --suite story-4.2    # Order History
python run_tests.py --suite story-4.3    # Subscriptions

# 🔍 By Component
python run_tests.py --suite registration     # Register flow
python run_tests.py --suite login            # Login flow
python run_tests.py --suite preferences      # Preferences CRUD
python run_tests.py --suite avoid-list       # Avoid-list CRUD
python run_tests.py --suite order-history    # Order history + pagination
python run_tests.py --suite decision-engine  # Decision engine integration
python run_tests.py --suite subscription     # Subscription lifecycle
python run_tests.py --suite journey          # Full user journey

# 📊 Verbose Output
python run_tests.py --verbose

# ✅ Check Dependencies Only
python run_tests.py --check-deps
```

## Setup (First Time)

```bash
# 1. Install Python dependencies
pip install pytest requests

# 2. Start Flask backend (in separate terminal)
cd _bmad-output/implementation-artifacts/nlu/
python app.py

# 3. Run tests from tests directory
cd _bmad-output/implementation-artifacts/tests/
python run_tests.py
```

## Test Coverage at a Glance

| Story | Tests | Topics |
|-------|-------|--------|
| 4.1 | 16 | Register, Login, Preferences, Avoid-List |
| 4.2 | 6 | Order History, Pagination, Filtering, Deduplication |
| 4.3 | 5 | Pause, Resume, Cancel, State Transitions |
| Integration | 2 | Decision Engine + Exclude-List |
| Journey | 2 | Complete workflows |
| **Total** | **31** | **All Stories + Integration** |

## What Gets Tested

✅ User registration with validation  
✅ Login with JWT token generation  
✅ Preferences CRUD (create, read, update)  
✅ Avoid-list management (add, retrieve, remove)  
✅ Order history with pagination & filtering  
✅ Exclude-list deduplication (no duplicate IDs)  
✅ Subscription lifecycle (pause, resume, cancel)  
✅ Decision engine with auto-fetched exclude-list  
✅ Full user journey (register to recommendation to order history)  
✅ Error handling (400, 401, 500 status codes)  

## Expected Test Duration

- **Quick:** 30-60 seconds (single story)
- **Medium:** 1-2 minutes (2-3 stories)
- **Full:** 2-5 minutes (all tests)

## Success Indicators

```
✓ Pytest reports "31 passed in X.XXs"
✓ No errors in console output
✓ JSON report file generated
✓ Overall Status shows: ALL TESTS PASSED
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| pytest not found | `pip install pytest` |
| Backend not running | `python app.py` from nlu/ |
| Connection refused | Check port 5000 is free |
| Timeout errors | Backend may be slow, wait 5s |
| JWT validation fails | Check token storage in localStorage |

## Files Reference

- **Test code:** `test_api_endpoints.py` (pytest tests)
- **E2E code:** `test_e2e.js` (Jest/Playwright ready)
- **Test runner:** `run_tests.py` (orchestration + reporting)
- **Full docs:** `TESTING-GUIDE.md` (comprehensive guide)

## Test Results Location

Test reports saved to: `test-report-YYYYMMDD-HHMMSS.json`

## Next Steps

1. **All tests pass?** ✅ → Ready for production deployment
2. **Some fail?** ❌ → Check TESTING-GUIDE.md troubleshooting
3. **Questions?** → See TESTING-GUIDE.md for detailed test cases

---

**Ready to test? Run:** `python run_tests.py` 🚀
