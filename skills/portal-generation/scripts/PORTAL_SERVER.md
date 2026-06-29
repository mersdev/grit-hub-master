# Portal Server Quick Reference

## Start the Portal

```powershell
# Method 1: Python (Recommended)
cd grit-hub/skills/portal-generation/scripts
python start_portal.py

# Method 2: PowerShell
cd grit-hub/skills/portal-generation/scripts
.\start_portal.ps1
```

**Portal URL:** http://localhost:8080

## Features

✅ Automatically serves from `dist/` directory  
✅ Opens browser automatically  
✅ No-cache headers for development  
✅ Proper error handling  
✅ Works on localhost:8080 directly (no long path in URL)

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Regenerate Portal Content

```powershell
cd grit-hub/skills/portal-generation/scripts
python generate_portal.py
```

Then restart the server to see changes.

## Troubleshooting

### Port Already in Use

```powershell
# Find process using port 8080
Get-NetTCPConnection -LocalPort 8080 -State Listen | Select-Object OwningProcess

# Stop the process
Stop-Process -Id <PID>
```

### Portal Not Found

Run the generator first:
```powershell
cd grit-hub/skills/portal-generation/scripts
python generate_portal.py
```
