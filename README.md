# CxOne API Key Audit Tool

This tool provides information about existing API keys in a Checkmarx One tenant, including the user and last access date. The information is output to a CSV file.

## Syntax and Arguments

Run the script using the following syntax:

```bash
python audit_api_keys.py --base-url BASE_URL --tenant TENANT --api-key API_KEY [OPTIONS]
```

### Required Arguments

- `--base-url`: The base URL of the CxOne region (e.g., https://ast.checkmarx.net).
- `--tenant`: The name of the tenant.
- `--api-key`: The API key used for authentication.

### Optional Arguments

- `--output`: Output CSV file (default: api_keys.csv).
- `--debug`: Enable debug output. (Flag, no value required)

## Usage Examples

Basic usage:

```bash
python audit_api_keys.py --base-url https://ast.checkmarx.net --tenant my_tenant --api-key my_api_key
```

Specify custom output file:

```bash
python audit_api_keys.py --base-url https://ast.checkmarx.net --tenant my_tenant --api-key my_api_key --output custom_output.csv
```

Enable debug output:

```bash
python audit_api_keys.py --base-url https://ast.checkmarx.net --tenant my_tenant --api-key my_api_key --debug
```

## Output

The script generates a CSV file containing the following information for each API key:
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

