import pandas as pd

# Getting median
import statistics
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.lines import Line2D
from matplotlib.animation import FuncAnimation

true_launch_time_ms = 1.1737e7

threshold = 50
window_size_ms = 1000
data_interval_ms = 60

plt.switch_backend('TkAgg')
acl_mags = {}  # Bunch of timestamp: magnitude pairs
acl_comps = {} # Bunch of timestamp:

# load in the all_data.csv
df = pd.read_csv("all_data.csv", header=None)
"""
Head

0    NaN  2144.000000  2283.000000  ...  3.813041e+07  3.813054e+07  3.813072e+07
1    xac    18.223738     4.120440  ... -8.877372e+00 -8.877372e+00 -8.882158e+00
2    yac   -30.699915    -9.126225  ...  5.120640e-01  4.977071e-01  5.024928e-01
3    zac    -3.785445    -1.124627  ...  4.465007e+00  4.469792e+00  4.469792e+00
4    mag    35.901518    10.076250  ...  9.950187e+00  9.951607e+00  9.956118e+00

"""


last_timestamp_ms = 0
intervals = []
for i in range(1, len(df.columns)):
    timestamp = df.iloc[0, i]
    # Skip if not at the data_interval_ms has passed
    if timestamp - last_timestamp_ms < data_interval_ms:
        continue
    if last_timestamp_ms != 0:
        intervals.append(timestamp - last_timestamp_ms)
    mag = df.iloc[4, i]
    x = df.iloc[1, i]
    y = df.iloc[2, i]
    z = df.iloc[3, i]
    acl_comps[timestamp] = {"x": x, "y": y, "z": z}


    acl_mags[timestamp] = mag
    last_timestamp_ms = timestamp

    if timestamp > 1.5e7:
        break

print("-------Interval stats (ms)---------")
print("average interval after culling: ", statistics.mean(intervals))
print("median interval after culling: ", statistics.median(intervals))
print("max interval after culling: ", max(intervals))
print("min interval after culling: ", min(intervals))
print("-----------------------------------")

fig, ax = plt.subplots()
def update_reference_line(frame):  # Note: Doesn't use the 'frame' argument directly
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    mid_y = (ymin + ymax) / 2

    # Actual y should be a bit above the mid_y
    y = mid_y + 0.1 * (ymax - ymin)
    left = xmin + window_size_ms
    ref_line.set_data([left, left + window_size_ms], [y, y])
    return ref_line,


def get_launch_moments(window_size_ms, threshold_ms2, data_interval_ms) -> list[int]:
    """
    Takes the median at each window of size window_size_ms and returns the timestamps where the magnitude of the acceleration
    is greater than threshold_ms2

    :param window_size_ms: The size of the window in milliseconds to take the median of the magnitude of the acceleration
    :param threshold_ms2: The threshold in m/s^2 to determine if the magnitude of the acceleration is greater than
    :return: A list of timestamps where the magnitude of the acceleration is greater than threshold_ms2
    """
    launch_moments_ms = []

    largest_timestamp = max(acl_mags)

    debug_x = []
    debug_y_median_of_comps_first = []
    debug_y_median_of_mags = []


    # iterate through the acl_mags dict
    for i, end_timestamp in enumerate(acl_mags):
        # Looking backwards to get the start_timestamp
        start_timestamp = end_timestamp - window_size_ms
        while start_timestamp not in acl_mags and start_timestamp > 0:
            start_timestamp -= 1

        if start_timestamp <= 0:
            continue

        vals = []

        # Rolling window for each component
        x_vals = []
        y_vals = []
        z_vals = []
        # iterate through the acl_mags dict and populate the vals list
        for j in range(int(start_timestamp), int(end_timestamp + 1)):
            if j in acl_mags:
                vals.append(acl_mags[j])
            if j in acl_comps:
                x_vals.append(acl_comps[j]["x"])
                y_vals.append(acl_comps[j]["y"])
                z_vals.append(acl_comps[j]["z"])

        # Get the median of each component and then calculate the magnitude from the medians
        m_x = statistics.median(x_vals)
        m_y = statistics.median(y_vals)
        m_z = statistics.median(z_vals)
        m_mag = (m_x**2 + m_y**2 + m_z**2)**0.5

        mags_median = statistics.median(vals)

        debug_x.append(end_timestamp)
        debug_y_median_of_comps_first.append(m_mag)
        debug_y_median_of_mags.append(mags_median)

        if m_mag > threshold_ms2:
            launch_moments_ms.append(end_timestamp)

    return launch_moments_ms, debug_x, debug_y_median_of_comps_first, debug_y_median_of_mags

def good_launch_moment(launch_moment, true_launch_time_ms):
    return abs(launch_moment - true_launch_time_ms) < 2500
def find_min_max_params(window_size):
    """
    Finds the best parameters for the window size and threshold

    For each window size, find the min and max thresholds that still work
    """

    min_threshold = 0
    max_threshold = 80
    temperature = 50
    while min_threshold < max_threshold:
        print(
            f"Window: {window_size}, Temperature: {temperature}")
        # If the min works, lower it
        moments, _, _, _ = get_launch_moments(window_size, min_threshold, data_interval_ms)
        if moments and good_launch_moment(min(moments), true_launch_time_ms):
            print(f"Working min: {min_threshold}")
            min_threshold -= temperature
        else:
            min_threshold += temperature

        # If the max works, raise it
        moments, _, _, _ = get_launch_moments(window_size, max_threshold, data_interval_ms)
        if moments and good_launch_moment(min(moments), true_launch_time_ms):
            print(f"Working max: {max_threshold}")
            max_threshold += temperature
        else:
            max_threshold -= temperature

        temperature /= 2



launch_moments, debug_x, debug_y_median_of_comps_first, debug_y_median_of_mags  = get_launch_moments(window_size_ms, threshold, data_interval_ms)



# Plot the launch moments as point on the mag line
# How to make these showup ontop of the mag line? A:
plt.scatter(launch_moments, [threshold] * len(launch_moments), color='gold', label="Launch Moments", zorder=5)
# Plot a reference line showing the window size
# from 0 to window_size on the x axis and the threshold on the y axis

# Also plot the threshold
plt.plot([min(acl_mags.keys()), max(acl_mags.keys())], [threshold, threshold], label="Threshold", color='orange')

# Plot the magnitude of the acceleration
plt.plot(acl_mags.keys(), acl_mags.values(), label="Magnitude of Acceleration", color="navy")

# Plot the median of the acceleration
plt.plot(debug_x, debug_y_median_of_mags, label="Median of Magnitude of Acceleration", color="green")
plt.plot(debug_x, debug_y_median_of_comps_first, label="Median of Components First", color="red")


plt.xlabel("Timestamp (ms)")
plt.ylabel("Magnitude of Acceleration (m/s^2)")


# Animate the reference line
ref_line, = ax.plot([0, window_size_ms], [threshold, threshold],
                    label="Window (Size Reference)", color='red', linestyle='-')
ani = FuncAnimation(fig, update_reference_line, frames=range(1), blit=True, interval=100)

# legend
plt.legend()

# Putting all hyperparameters in the title
plt.title(f"Launch Detection\nThreshold: {threshold} m/s^2, Window Size: {window_size_ms} ms, Minimum Data Interval: {data_interval_ms} ms")


earliest_launch_moment = min(launch_moments)
offset = earliest_launch_moment - true_launch_time_ms  # Calculate time difference


text_x = earliest_launch_moment + window_size_ms / 2  # Place text near window midpoint
text_y = threshold + (max(acl_mags.values()) - threshold) / 3  # Above the threshold line

# Create the text box
plt.text(text_x, text_y, f"Earliest Launch Moment\n({offset:.2f} ms off)",
         ha='center', va='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

# Add an arrow
plt.annotate('', xy=(earliest_launch_moment, threshold),
             xytext=(text_x, text_y),
             arrowprops=dict(facecolor='black', shrink=0.05))





# Setting the initial min and max x and y values
plt.xlim((1.172e7, 1.177e7))
plt.ylim((0, 90))




plt.show(block=True)
print(launch_moments)



