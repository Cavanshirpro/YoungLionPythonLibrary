# Environment variables

YoungLion keeps environment-controlled build behavior small and explicit.

## `YOUNGLION_STRICT`

When truthy during a local/native extension build, strict compiler warnings are enabled where supported. The project uses this mode in development to turn relevant warnings into errors.

Example on POSIX shells:

```bash
YOUNGLION_STRICT=1 python setup.py build_ext --inplace --force
```

PowerShell:

```powershell
$env:YOUNGLION_STRICT = "1"
python setup.py build_ext --inplace --force
```

## Runtime configuration

The core library does not rely on hidden mandatory runtime environment variables. E-mail/FTP credentials or application settings should be supplied explicitly by the application or its own secret-management layer rather than hard-coded into YoungLion.
