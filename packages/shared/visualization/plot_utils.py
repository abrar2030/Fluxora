# packages/shared/visualization/plot_utils.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np # Added missing import
from packages.shared.utils.logger import get_logger

logger = get_logger(__name__)

class PlottingUtilities:
    """Provides utility functions for creating common plots for data analysis and model evaluation."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid", palette: str = "viridis"):
        """
        Initializes PlottingUtilities with a default style and palette.
        Args:
            style (str): Matplotlib style to use (e.g., 	ggplot	, 	seaborn-v0_8-darkgrid	).
            palette (str): Seaborn color palette to use.
        """
        plt.style.use(style)
        self.palette = sns.color_palette(palette)
        sns.set_palette(self.palette)
        logger.info(f"Plotting style set to: {style}, palette: {palette}")

    def plot_histogram(self, data: pd.Series, title: str, xlabel: str, ylabel: str = "Frequency", 
                       bins: int = 30, figsize: tuple = (10, 6), save_path: str = None):
        """
        Plots a histogram for a given series.
        Args:
            data (pd.Series): Data series to plot.
            title (str): Title of the plot.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            bins (int): Number of bins for the histogram.
            figsize (tuple): Figure size (width, height).
            save_path (str, optional): Path to save the figure. If None, plot is shown.
        """
        plt.figure(figsize=figsize)
        sns.histplot(data, bins=bins, kde=True)
        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Histogram saved to {save_path}")
            plt.close()
        else:
            plt.show()

    def plot_correlation_matrix(self, df: pd.DataFrame, title: str = "Correlation Matrix", 
                                figsize: tuple = (12, 10), annot: bool = True, cmap: str = "coolwarm",
                                save_path: str = None):
        """
        Plots a heatmap of the correlation matrix for a DataFrame.
        Args:
            df (pd.DataFrame): DataFrame to calculate correlations from.
            title (str): Title of the plot.
            figsize (tuple): Figure size.
            annot (bool): Whether to annotate cells with correlation values.
            cmap (str): Colormap for the heatmap.
            save_path (str, optional): Path to save the figure. If None, plot is shown.
        """
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            logger.warning("No numeric columns found in DataFrame for correlation matrix.")
            return
        
        corr_matrix = numeric_df.corr()
        plt.figure(figsize=figsize)
        sns.heatmap(corr_matrix, annot=annot, cmap=cmap, fmt=".2f", linewidths=.5)
        plt.title(title, fontsize=16)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Correlation matrix saved to {save_path}")
            plt.close()
        else:
            plt.show()

    def plot_line(self, x_data, y_data, title: str, xlabel: str, ylabel: str, 
                  labels: list = None, figsize: tuple = (12, 6), save_path: str = None):
        """
        Plots one or more lines on the same axes.
        Args:
            x_data (list or pd.Series): X-axis data. Can be a list of series for multiple lines.
            y_data (list or pd.Series): Y-axis data. Can be a list of series for multiple lines.
            title (str): Title of the plot.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            labels (list, optional): List of labels for multiple lines. Length must match y_data if provided.
            figsize (tuple): Figure size.
            save_path (str, optional): Path to save the figure. If None, plot is shown.
        """
        plt.figure(figsize=figsize)
        if isinstance(y_data, list):
            if not isinstance(x_data, list) or len(x_data) != len(y_data):
                 # Assume same x_data for all y_data if x_data is not a list of same length
                x_data_list = [x_data] * len(y_data)
            else:
                x_data_list = x_data

            for i, y_series in enumerate(y_data):
                label = labels[i] if labels and i < len(labels) else f"Line {i+1}"
                sns.lineplot(x=x_data_list[i], y=y_series, label=label)
            plt.legend()
        else:
            sns.lineplot(x=x_data, y=y_data)
        
        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Line plot saved to {save_path}")
            plt.close()
        else:
            plt.show()

    def plot_scatter(self, x_data, y_data, title: str, xlabel: str, ylabel: str, 
                     hue_data=None, size_data=None, style_data=None,
                     figsize: tuple = (10, 6), save_path: str = None):
        """
        Creates a scatter plot.
        Args:
            x_data: Data for the x-axis.
            y_data: Data for the y-axis.
            title (str): Title of the plot.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
            hue_data (optional): Data for color encoding.
            size_data (optional): Data for size encoding.
            style_data (optional): Data for style encoding.
            figsize (tuple): Figure size.
            save_path (str, optional): Path to save the figure. If None, plot is shown.
        """
        plt.figure(figsize=figsize)
        sns.scatterplot(x=x_data, y=y_data, hue=hue_data, size=size_data, style=style_data, palette=self.palette)
        plt.title(title, fontsize=16)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        if hue_data is not None or size_data is not None or style_data is not None:
            plt.legend(title=hue_data.name if hue_data is not None else None)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Scatter plot saved to {save_path}")
            plt.close()
        else:
            plt.show()

# Example Usage
if __name__ == "__main__":
    plot_util = PlottingUtilities()
    
    # Create dummy data
    data_hist = pd.Series(np.random.randn(1000))
    df_corr = pd.DataFrame(np.random.rand(10, 4), columns=["A", "B", "C", "D"])
    x_line = np.linspace(0, 10, 100)
    y_line1 = np.sin(x_line)
    y_line2 = np.cos(x_line)
    x_scatter = np.random.rand(50)
    y_scatter = np.random.rand(50)
    hue_scatter = pd.Series(np.random.choice(["cat1", "cat2"], 50), name="Category")

    # Test plots (will show if not saving, or save if path provided)
    # Ensure 	plots	 directory exists if saving
    # import os
    # if not os.path.exists("plots"):
    #     os.makedirs("plots")

    logger.info("Testing histogram plot...")
    plot_util.plot_histogram(data_hist, "Sample Histogram", "Value", save_path=None) # "plots/histogram.png")

    logger.info("Testing correlation matrix...")
    plot_util.plot_correlation_matrix(df_corr, save_path=None) # "plots/correlation_matrix.png")

    logger.info("Testing single line plot...")
    plot_util.plot_line(x_line, y_line1, "Sine Wave", "X-axis", "Y-axis", save_path=None) # "plots/single_line.png")

    logger.info("Testing multiple line plot...")
    plot_util.plot_line([x_line, x_line], [y_line1, y_line2], "Sine and Cosine Waves", 
                        "X-axis", "Y-axis", labels=["Sine", "Cosine"], save_path=None) # "plots/multi_line.png")

    logger.info("Testing scatter plot...")
    plot_util.plot_scatter(x_scatter, y_scatter, "Sample Scatter Plot", "X Value", "Y Value", 
                           hue_data=hue_scatter, save_path=None) # "plots/scatter_plot.png")
    
    logger.info("Plotting examples complete.")
    # Need to import numpy for example to run (already added at the top)

