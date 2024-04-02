# Ground Station Server
This is a ground station server which:
- Starts the initial Redis instance and fills it with data (amount of data is configurable),
- Migrates containers periodically (period is configurable),
- Logs the migration events in the `migration.csv` file.

For building instructions, see the [README](../../celestial-app/README.md) in `celestial-app`.