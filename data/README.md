# Data Directory

This directory contains runtime data for the SRE monitoring dashboard.

## Structure

```
data/
├── logs/       # Application and system logs
└── devices/    # Device data storage (future use)
```

## logs/
Contains application logs and generated sample logs. Files in this directory are excluded from git.

## devices/
Reserved for future device data persistence. Currently, all device data is stored in memory.

## Note
This directory is created automatically when running the application.
All `.log` files are gitignored for security and to keep the repository clean.
