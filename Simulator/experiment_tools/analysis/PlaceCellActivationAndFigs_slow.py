import pickle
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from fairis_tools.experiment_tools.place_cell.PlaceCellLibrary import VisualPlaceCellNetwork
import os
from tqdm import tqdm

os.chdir("../../..")
print(os.getcwd())

# Load the new test data (800 data points)
maze_files = ['LM4', 'LM6', 'LM8', 'LMO8', 'LM8_addition', 'LMO8_remove', 'BR']
maze_index = 2
with open("data/VisualPlaceCellData/" + maze_files[maze_index] + "_Training", 'rb') as file:
    test_data = pickle.load(file)
# Load the three place cell networks
num_pcs = [100, 250, 500, 750]
networks = {}
for n in num_pcs:
    file_name = f'multimodal_gmm_{n}_clusters_' + maze_files[maze_index]
    with open(f"data/VisualPlaceCellData/VisualPlaceCellClusters/{file_name}", 'rb') as file:
        data = pickle.load(file)

    pc_network = VisualPlaceCellNetwork()
    for cluster in data:
        radius = cluster[1] if cluster[1] != 0 else 1
        pc_network.add_pc_to_network(cluster[0], radius=radius)
    networks[n] = pc_network


def get_activations_for_network(pc_network, test_data, feature_type='cnn'):
    """
    Compute place cell activations for all data points in test_data.

    Parameters:
    - pc_network: VisualPlaceCellNetwork object.
    - test_data: Object containing observations with cnn_feature_vector and (x, y) coordinates.
    - feature_type: str, 'cnn' or 'multimodal'.

    Returns:
    - DataFrame: Contains (x, y) coordinates and activations for each place cell.
    """
    activations_list = []
    total_steps = len(test_data.observations)
    with tqdm(total=total_steps, desc="Collecting training data") as pbar:
        for obs in test_data.observations:
            if feature_type == 'cnn':
                activations = pc_network.get_all_pc_activations_normalized(obs.cnn_feature_vector, norm_type='min_max')
            else:
                activations = pc_network.get_all_pc_activations_normalized(obs.multimodal_feature_vector,
                                                                           norm_type='min_max')
            # Store x, y, and activations for each place cell
            data = {'x': obs.x, 'y': obs.y}
            for i, act in enumerate(activations):
                data[f'pc_{i}'] = act
            activations_list.append(data)
            pbar.update(1)

    return pd.DataFrame(activations_list)


# Compute activations for each network
activations_dfs = {}
for n in num_pcs:
    activations_dfs[n] = get_activations_for_network(networks[n], test_data, feature_type='multimodel')

def _load_bg_image(image_path, flip_vertical=True):
    arr = np.asarray(Image.open(image_path).convert("RGB"))
    if flip_vertical:
        arr = np.flipud(arr)  # so +Y is up
    return arr


def plot_place_cell_activation_maps_colored(
        activations_df,
        n_place_cells,
        output_file_prefix=None,
        vmin=0.0,
        vmax=1.0,
        cmap='viridis',
        show_colorbar=False,
        threshold=None,
        # world/image overlay additions:
        image_path=None,
        world_width_m=None,
        world_height_m=None,
        image_alpha=0.55,
        flip_image_vertical=True,
        # legacy size args (used only if world_* not provided):
        width=6.0,
        height=6.0,
        cols=5
):
    """
    Generate subplots showing the spatial activation heatmap for each place cell,
    optionally superimposed on a top-down background image aligned to meters.

    Expected columns in activations_df: 'x', 'y', and 'pc_{i}' for i in [0, n_place_cells).
    """
    # Figure grid
    rows = int(np.ceil(n_place_cells / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    if rows * cols == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    # World dimensions and axis limits
    if (world_width_m is not None) and (world_height_m is not None):
        xlim = (-world_width_m / 2.0, world_width_m / 2.0)
        ylim = (-world_height_m / 2.0, world_height_m / 2.0)
        extent = [xlim[0], xlim[1], ylim[0], ylim[1]]
    else:
        # fallback to legacy symmetric limits
        xlim = (-width / 2.0, width / 2.0)
        ylim = (-height / 2.0, height / 2.0)
        extent = [xlim[0], xlim[1], ylim[0], ylim[1]]

    # Load background once (if provided)
    bg = None
    if image_path is not None:
        bg = _load_bg_image(image_path, flip_vertical=flip_image_vertical)

    x_coords = activations_df['x'].values
    y_coords = activations_df['y'].values

    for i in range(n_place_cells):
        ax = axes[i]
        pc_col = f'pc_{i}'
        if pc_col not in activations_df.columns:
            ax.axis('off')
            continue

        activations = activations_df[pc_col].values

        # Threshold points if requested
        if threshold is not None:
            mask = activations >= threshold
            x_plot = x_coords[mask]
            y_plot = y_coords[mask]
            act_plot = activations[mask]
        else:
            x_plot = x_coords
            y_plot = y_coords
            act_plot = activations

        # Draw background first (so scatter stays on top)
        if bg is not None:
            ax.imshow(bg, extent=extent, origin='lower', alpha=image_alpha, zorder=0)

        # Your scatter as-is
        sc = ax.scatter(
            x_plot, y_plot,
            c=act_plot, cmap=cmap, vmin=vmin, vmax=vmax, s=10,
            zorder=1
        )

        ax.set_title(f'Place Cell {i}')
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

        if show_colorbar:
            cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Activation')

    # Hide any unused axes
    for j in range(n_place_cells, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    if output_file_prefix is not None:
        os.makedirs(os.path.dirname(output_file_prefix), exist_ok=True)
        plt.savefig(f"{output_file_prefix}_pc_activation_map.png", dpi=200)
        plt.close()


for n, df in activations_dfs.items():
    n_pcs = len([col for col in df.columns if col.startswith('pc_')])
    if maze_files[maze_index] == 'BR':
        plot_place_cell_activation_maps_colored(
            activations_df=df,
            n_place_cells=n_pcs,
            output_file_prefix=f"data/figures/ActivationMaps/network_{n}_" + maze_files[maze_index],
            image_path="data/DataCache/" + maze_files[maze_index] + ".png",
            cmap='viridis',
            vmin=0.0,
            vmax=1.0,
            show_colorbar=True,
            width=12.86,
            height=7.7,
            flip_image_vertical=True
            # threshold=0.75  # <- Only plot if activation ≥ 0.05
        )
    else:
        plot_place_cell_activation_maps_colored(
            activations_df=df,
            n_place_cells=n_pcs,
            output_file_prefix=f"data/figures/ActivationMaps/network_{n}_" + maze_files[maze_index],
            image_path="data/DataCache/" + maze_files[maze_index] + ".png",
            cmap='viridis',
            vmin=0.0,
            vmax=1.0,
            show_colorbar=True,
            width=6,
            height=6,
            flip_image_vertical=True
            # threshold=0.75  # <- Only plot if activation ≥ 0.05
        )

with open("data/activations/activation_"+maze_files[maze_index], "wb") as fh:
    pickle.dump(activations_dfs, fh)

print("Done. Saved activations and figures.")