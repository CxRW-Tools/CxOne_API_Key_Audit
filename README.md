# CxOne API Key Audit Tool

This tool provides information about existing API keys in a Checkmarx One tenant, including the user and last access date. The information is output as CSV, JSON, or a table on screen.

## Configuration

Settings are read from an env file (`.env` by default). Copy [example.env](example.env) to `.env` and fill in your values. `.env` is gitignored; never commit it.

| Variable | Required | Flag |
|---|---|---|
| `CXONE_BASE_URL` | yes | `--base-url` |
| `CXONE_TENANT` | yes | `--tenant-name` (or `--tenant`) |
| `CXONE_API_KEY` | yes | `--api-key` |
| `CXONE_IAM_BASE_URL` | no | none |
| `CXONE_DEBUG` | no | `--debug` |
| `CXONE_FORMAT` | no | `--format` (`csv`, `json` or `table`; default `table`) |
| `CXONE_OUTPUT` | no | `--output` (file path; default `api_keys.<format>`) |
| `CXONE_STDOUT` | no | `--stdout` (print to screen) |

Precedence: CLI flag > environment variable > env file > built-in default. To use a different env file, pass `--env-file`.

## Usage

```bash
pip install -r requirements.txt
python audit_api_keys.py
```

Using a separate env file (for example, one per tenant kept outside the repo):

```bash
python audit_api_keys.py --env-file "path/to/tenant.env"
```

Flags still work and override the env file:

```bash
python audit_api_keys.py --base-url https://ast.checkmarx.net --tenant-name my_tenant --api-key my_api_key --output custom_output.csv --debug
```

Prefer the env file to `--api-key`: command-line arguments appear in shell history and process lists.

## Output options

By default the tool prints a table to the screen and writes no file. Choose the format and destination with flags (or the matching variables):

```bash
python audit_api_keys.py                           # table on screen (default)
python audit_api_keys.py --format csv              # writes api_keys.csv
python audit_api_keys.py --format json             # writes api_keys.json
python audit_api_keys.py --format csv --stdout     # CSV on screen, no file
python audit_api_keys.py --format json --stdout > keys.json   # status messages go to stderr
python audit_api_keys.py --format csv --stdout --output keys.csv  # screen and file
python audit_api_keys.py --output keys.txt         # table on screen and in a file
```

`--format csv` and `--format json` write a file unless you pass `--stdout`. A table prints to screen only unless you also pass `--output`.

## Output

The script outputs the following information for each API key:
- Username
- User ID
- Created date/time
- Last access date/time

## License

MIT License

Copyright (c) 2025 CxRW-Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

