import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
from pathlib import Path
import itertools
from scipy.stats import norm
import pandas as pd


########################################################################################################################
# Q and V table plotting functions
########################################################################################################################

def plot_q_table(q_table, action_num_to_str, episode_num=None, save_dir=None):

    # Create a list of action names as column labels
    actions = [action_num_to_str[i] for i in range(len(action_num_to_str))]

    # Transpose the Q-table to orient it the other way round
    q_table = q_table.T

    # Round down Q-values to 1 significant figure
    q_table = np.round(q_table, decimals=1)

    # Plot the Q-table
    fig, ax = plt.subplots()
    im = ax.imshow(q_table, cmap='plasma')

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax, orientation="horizontal")
    cbar.ax.set_xlabel('Q-value')

    # Set ticks and labels for x and y axes
    ax.set_xticks(np.arange(q_table.shape[1]))
    ax.set_yticks(np.arange(len(actions)))
    ax.set_xticklabels(np.arange(q_table.shape[1]))
    ax.set_yticklabels(actions)

    # Add text annotations inside the cells
    for i in range(len(actions)):
        for j in range(q_table.shape[1]):
            text = ax.text(j, i, str(q_table[i, j]), ha="center", va="center",
                           color="w" if abs(q_table[i, j]) < np.max(np.abs(q_table)) / 2 else "k")

    # Set title
    if episode_num is not None:
        ax.set_title(f"Q-table after {episode_num} episodes")
    else:
        ax.set_title("Q-table")

    # Rotate the x-axis tick labels for better visibility
    plt.xticks(rotation=90)

    # Adjust the layout to prevent overlap of annotations
    plt.tight_layout()

    # Save the plot if save_dir and episode_num are provided
    if save_dir and episode_num is not None:
        save_dir_path = Path(save_dir)
        save_dir_path.mkdir(parents=True, exist_ok=True)
        save_file_path = save_dir_path / f"q_table_episode_{episode_num}.png"
        plt.savefig(save_file_path)


def plot_v_table_with_arrows(array, action_num_to_str, grid_rows, grid_cols, episode_num=None, save_dir=None):
    """
    Plots a heatmap with arrows on top of it. The heatmap is a square grid of values, and the arrows are placed in the
    center of each grid cell. The arrows are colored according to the value of the grid cell they are in.
    Args:
        array: an agent's Q-table
        action_num_to_str: maps Q-table row indices to action strings
            - Frozen Lake: {0: "Left", 1: "Down", 2: "Right", 3: "Up"}
            - Cliff Walking: {0: "up", 1: "right", 2: "down", 3: "left"}
        grid_rows: the number of rows in the gridworld
        grid_cols: the number of columns in the gridworld
        episode_num: the episode number
        save_dir: the directory to save the plot in

    Returns:
    """

    # QLearningAgent's Q table is of shape (num_states, num_actions) whereas this function requires
    # (num_actions, num_states)
    array = array.T

    # Create a reverse mapping dictionary to get action numbers from strings
    str_to_action_num = {v: k for k, v in action_num_to_str.items()}

    # Store states where all action vals are 0 (typically represent terminal states / zero-initialised states)
    mask_all_zero_actions = (array == 0).all(axis=0)

    # Then shift array so no negatives (environments which return only negative rewards can lead to all negative
    # Q-tables)
    array = array - array.min()

    # Find the maximum action value per column (state)
    max_action_val = np.max(array, axis=0)

    # Reshape the max_action_val to match the gridworld space
    space_values = max_action_val.reshape((grid_rows, grid_cols))
    mask_all_zero_actions = mask_all_zero_actions.reshape((grid_rows, grid_cols))

    # Create a meshgrid for the coordinates of the grid cells
    x, y = np.meshgrid(range(grid_cols), range(grid_rows))

    # Plot the heatmap with 'plasma' colormap
    plt.figure(figsize=(6, 4))
    plt.imshow(space_values, cmap='plasma', interpolation='nearest')

    # Calculate and plot the arrows for each element
    for i in range(array.shape[1]):

        # Calculate the vector components using action strings
        up_value = np.abs(array[str_to_action_num["up"], i])
        right_value = np.abs(array[str_to_action_num["right"], i])
        down_value = np.abs(array[str_to_action_num["down"], i])
        left_value = np.abs(array[str_to_action_num["left"], i])

        # Scale arrows within grid to show relative values
        max_action_val = np.max([up_value, right_value, down_value, left_value])
        min_action_val = np.min([up_value, right_value, down_value, left_value])
        action_range = max_action_val - min_action_val
        if action_range == 0:
            action_range = 1
        up_value = (up_value - min_action_val) / action_range
        right_value = (right_value - min_action_val) / action_range
        down_value = (down_value - min_action_val) / action_range
        left_value = (left_value - min_action_val) / action_range

        # Calculate the center coordinates of the grid cell
        x_center = x.flatten()[i]
        y_center = y.flatten()[i]

        # Calculate the arrow colors based on the background color
        arrow_color = 'black'
        value_mags = np.abs(space_values)
        if value_mags[y_center, x_center] < np.mean(np.abs(value_mags)):
            if ~mask_all_zero_actions[y_center, x_center]:
                arrow_color = 'white'

        # Calculate the half-length of the arrow
        arrow_length = 0.35
        head_length = arrow_length * 0.33
        head_width = arrow_length * 0.2

        # Plot the arrows centered in the grid cell
        plt.arrow(
            x_center, y_center,
            0, -up_value * arrow_length,
            head_width=head_width, head_length=head_length, fc=arrow_color, ec=arrow_color
        )
        plt.arrow(
            x_center, y_center,
            right_value * arrow_length, 0,
            head_width=head_width, head_length=head_length, fc=arrow_color, ec=arrow_color
        )
        plt.arrow(
            x_center, y_center,
            0, down_value * arrow_length,
            head_width=head_width, head_length=head_length, fc=arrow_color, ec=arrow_color
        )
        plt.arrow(
            x_center, y_center,
            -left_value * arrow_length, 0,
            head_width=head_width, head_length=head_length, fc=arrow_color, ec=arrow_color
        )

    # Apply mask
    cmap_mask = plt.cm.colors.ListedColormap(["none", "black"])
    plt.imshow(mask_all_zero_actions, cmap=cmap_mask, interpolation='nearest')

    # Set the tick labels for the x and y axes
    plt.xticks(range(grid_cols), range(grid_cols))
    plt.yticks(range(grid_rows), range(grid_rows))

    # Set title
    if episode_num is not None:
        plt.title(f"V-table after {episode_num} episodes")
    else:
        plt.title("V-table")

    # Adjust the layout to prevent overlap of annotations
    plt.tight_layout()

    # Save the plot if save_dir and episode_num are provided
    if save_dir and episode_num is not None:
        save_dir_path = Path(save_dir)
        save_dir_path.mkdir(parents=True, exist_ok=True)
        save_file_path = save_dir_path / f"v_table_episode_{episode_num}.png"
        plt.savefig(save_file_path)


########################################################################################################################
# Metric plotting
########################################################################################################################

def plot_training_metrics_single_trial(training_metrics, window_size=100, metric_name=None, save_dir=None):
    """
    Takes a dictionary of training metrics (can be one, or a multiple of experiments) and plots the running average of
    each metric on top of a running variance fill between the upper and lower bounds.
    Args:
        training_metrics: dictionary of training metrics, where each key is the name of an experiment and each value
        is the experiment data for a single trial (so mean and varinance are calculated in a running window,
        rather than across multiple trials)
        window_size: int, controls the size of the rolling window used to calculate the running average and variance
        metric_name: str, for titles and save names
        save_dir: str or None, if None then the plot is shown, otherwise it is saved to the specified directory

    Returns:

    """
    colors = itertools.cycle(mcolors.TABLEAU_COLORS)

    for name, metric in training_metrics.items():
        # Calculate running average using a rolling window
        running_average = np.convolve(metric, (np.ones(window_size) / window_size), mode="valid")

        # Calculate running variance using a rolling window
        squared_diff = (metric - running_average.mean()) ** 2
        running_variance = np.convolve(squared_diff, (np.ones(window_size) / window_size), mode="valid")

        # Calculate the upper and lower bounds for the fill between
        upper_bound = running_average + np.sqrt(running_variance)
        lower_bound = running_average - np.sqrt(running_variance)

        # Plot the running average
        color = next(colors)
        plt.plot(running_average, label=name, color=color)

        # Plot the fill between the upper and lower bounds
        plt.fill_between(range(len(running_average)), upper_bound, lower_bound, alpha=0.3, color=color)

    # Set the plot title and labels
    if metric_name is None:
        title = "Training Metric per Episode"
    else:
        title = f"{metric_name}"
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Metric Value")

    # Show the legend
    plt.legend()

    # Save the plot
    if save_dir is not None:
        plt.savefig(os.path.join(save_dir, f"{metric_name}_per_episode.png"))
        plt.close()
    else:
        plt.show()


def calculate_experiment_statistics(metric_over_multiple_trials, confidence_interval=0.95):

    experiment_statistics = pd.DataFrame(columns=["mean", "std", "upper_bound", "lower_bound"])

    experiment_mean = np.mean(metric_over_multiple_trials, axis=0)
    experiment_std = np.std(metric_over_multiple_trials, axis=0)
    z_value = norm.ppf((1 + confidence_interval) / 2)
    num_trials = metric_over_multiple_trials.shape[0]
    upper_bound = experiment_mean + (z_value * (experiment_std / np.sqrt(num_trials)))
    lower_bound = experiment_mean - (z_value * (experiment_std / np.sqrt(num_trials)))

    experiment_statistics["mean"] = experiment_mean
    experiment_statistics["std"] = experiment_std
    experiment_statistics["upper_bound"] = upper_bound
    experiment_statistics["lower_bound"] = lower_bound

    return experiment_statistics


def plot_training_metrics_multiple_trials(
        metrics_over_multiple_trials,
        metric_name=None,
        save_dir=None,
        show_individual_trials=False
):
    """
    Takes the dataframe returned by `calculate_experiment_statistics` and plots the mean trace on top of a confidence
    interval fill between the upper and lower bounds. Optionally, individual trial traces can be shown as well.

    Args:
        metrics_over_multiple_trials: dict of data. The data is a numpy array of shape (num_trials, num_episodes) where each
        row is the data for a single trial. The dict keys are the names of the experiments.
        `calculate_experiment_statistics`
        metric_name: if None, set the title to "Training Metric per Episode"
        save_dir: if None, show the plot instead of saving it
        show_individual_trials: if True, individual trial traces will be plotted with alpha=0.1
    """

    colors = itertools.cycle(mcolors.TABLEAU_COLORS)

    for run_name, metric in metrics_over_multiple_trials.items():

        # Get training metric stats
        training_metric_stats = calculate_experiment_statistics(metric)

        # Plot the mean trace
        color = next(colors)
        plt.plot(training_metric_stats["mean"], label=run_name, color=color)

        # Plot the fill between the upper and lower bounds
        plt.fill_between(range(len(training_metric_stats["mean"])),
                         training_metric_stats["upper_bound"],
                         training_metric_stats["lower_bound"],
                         alpha=0.3,
                         color=color,
                         )

        # Plot the individual trial traces, if desired
        if show_individual_trials:
            for trial in metric:
                plt.plot(trial, alpha=0.05, color=color)

    # Set the plot title and labels
    if metric_name is None:
        title = "Training Metric per Episode"
    else:
        title = f"{metric_name}"
    plt.title(title)
    plt.xlabel("Episode")
    plt.ylabel("Metric Value")

    # Show the legend
    plt.legend()

    # Save the plot
    if save_dir is not None:
        plt.savefig(os.path.join(save_dir, f"{metric_name}_per_episode.png"))
        plt.close()
    else:
        plt.show()

