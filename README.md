# TheHostBoy checker for Python

Measures a bounded SHA-256 workload, temporary-file read/write timing, Python runtime version, and available CPUs, then submits one schema v1 report to TheHostBoy.

## Requirements

- Python 3.8 or newer
- HTTPS access to your TheHostBoy instance

Uses only the Python standard library.

## Community checker setup

Create an account and checker installation on TheHostBoy, verify a domain you control, and copy the one-time key. Use the community report endpoint:

```sh
export HOSTBOY_REPORT_URL='https://HOSTBOY_DOMAIN/api/v1/community/reports'
export HOSTBOY_CHECKER_KEY='YOUR_INSTALLATION_KEY'
python3 hostboy-checker.py
```

The report URL and key are provided by TheHostBoy. Keep the key private; it allows submissions for this installation. To run periodically, configure both environment variables in the hosting account's cron environment and schedule `python3 /absolute/path/hostboy-checker.py`. Do not commit a key or a `.env` file.

The script sends a report at most once per run, retries bounded transient failures, times out requests, and refuses redirects. It performs local CPU and temporary-storage work; it does not scan site files or collect visitor data.

The default endpoint for a user-contributed installation is `/api/v1/community/reports`. Provider-authorized installations use the exact report URL supplied by an administrator. Community results are labeled self-reported and kept out of provider plan rankings.
