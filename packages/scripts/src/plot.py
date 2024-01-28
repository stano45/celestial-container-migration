import io
import pandas as pd
import matplotlib.pyplot as plt

# Sample data provided
data = """
timestamp,source_sat,target_sat,total_duration,total_checkpoint_duration,checkpoint_stats.podman_checkpoint_duration,checkpoint_stats.container_statistics.runtime_checkpoint_duration,checkpoint_stats.container_statistics.criu_statistics.freezing_time,checkpoint_stats.container_statistics.criu_statistics.frozen_time,checkpoint_stats.container_statistics.criu_statistics.memdump_time,checkpoint_stats.container_statistics.criu_statistics.memwrite_time,checkpoint_stats.container_statistics.criu_statistics.pages_scanned,checkpoint_stats.container_statistics.criu_statistics.pages_written,checkpoint_stats.container_statistics.criu_statistics.memdump_time,total_restore_duration,restore_stats.podman_restore_duration,restore_stats.container_statistics.runtime_restore_duration,restore_stats.container_statistics.criu_statistics.forking_time,restore_stats.container_statistics.criu_statistics.pages_restored,restore_stats.container_statistics.criu_statistics.restore_time
1706480748.934885,43,42,1397408.7238311768,744864.2253875732,494392,98692,1096,80185,13941,12314,8097,594,13941,652544.4984436035,502997,171875,4,594,82959
1706480800.6339068,42,41,1326827.7645111084,630672.2164154053,416090,45954,1110,27366,2567,1403,8097,596,2567,696155.5480957031,504416,180945,5,596,77542
1706480882.806055,41,40,1450296.16355896,774911.4036560059,550936,144603,101462,28063,3078,1241,8097,596,3078,675384.7599029541,483760,197313,4,596,98118
1706480960.0431428,40,39,1455039.5011901855,775802.1354675293,551219,147352,101458,28294,2614,1259,8097,598,2614,679237.3657226562,528906,165275,4,598,94650
1706481042.0851,39,38,1254076.4808654785,614919.900894165,403161,42123,1015,25575,3097,1896,8097,598,3097,639156.5799713135,492084,178475,5,598,86765
1706481124.1682744,38,37,1284128.189086914,620206.8328857422,403024,45363,938,28964,2929,1346,8097,598,2929,663921.3562011719,518017,183898,4,598,91684
1706481206.366758,37,36,1417376.0414123535,714406.9671630859,513737,148669,101314,29712,2796,1398,8097,598,2796,702969.0742492676,526072,202890,5,598,97283
1706481288.4080312,36,35,1289877.4147033691,636352.3006439209,422753,45818,1136,27158,3460,2198,8097,598,3460,653525.1140594482,504633,171882,5,598,85948
1706481370.5254512,35,34,1360268.1159973145,702967.643737793,477382,46316,1002,27558,2742,1447,8097,598,2742,657300.4722595215,502991,173814,4,598,83673
1706481452.7803438,34,33,1426625.2517700195,775892.7345275879,528650,146189,101319,29155,3195,1455,8097,598,3195,650732.5172424316,498585,187934,3,598,90117
"""

# Reading the data into a DataFrame
df = pd.read_csv(io.StringIO(data))

# Extracting relevant columns
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df.set_index("timestamp", inplace=True)
total_duration = df["total_duration"]
checkpoint_duration = df["total_checkpoint_duration"]
restore_duration = df["total_restore_duration"]

# Plotting the data
plt.figure(figsize=(12, 6))
plt.plot(total_duration, label="Total Duration")
plt.plot(checkpoint_duration, label="Checkpoint Duration")
plt.plot(restore_duration, label="Restore Duration")
plt.xlabel("Timestamp")
plt.ylabel("Duration (in seconds)")
plt.title("Total vs Checkpoint vs Restore Duration Over Time")
plt.legend()
plt.grid(True)
plt.show()
