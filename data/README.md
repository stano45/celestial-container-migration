# Experiment Data
This folder contains the data collected from the experiments. The data is stored in CSV files. The data is organized in the following way:
- `migration-{instance-size}.csv`: Contains the measurements for each migration event. Each row is a migration event from `source_sat` to `target_sat`, containing time measurements for a variety of operations.
- `client-{instance-size}.csv`: Contains the measurements for each client request. Each row is a client request, containing the target host, the operation performed (get, set or delete), the status (success or failure), an error message (if the operation failed), and time measurements for the operation.
- `stats_downtime_client_{instance-size}.csv`: Contains aggregated stats about the downtime for each instance size.

There are also 2 directories:
- `original`: Which contains the original data collected from the experiments. We cleaned the data and removed rows from the front and back of the data to remove the noise and restrict the time window to the actual migration time. This was to visualize the data consistently.
- `with_zero_byte_redis_keys`: This is misleading data from when the Redis instance was filled with zero bytes. This led to even 2GB container checkpoints being compressed to a few MB, which naturally skews the migration speed. We still kept this data because it might be useful for future analysis, but it was not used in the final analysis. 