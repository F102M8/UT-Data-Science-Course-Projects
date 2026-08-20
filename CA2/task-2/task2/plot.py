import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm, lognorm


def do_histograms(df: pd.DataFrame, grouping_column: str, n_cols: int, n_bins: int, full=True):
    n_values = len(df[grouping_column].unique())
    sample_size = max(df[grouping_column].value_counts().min(), 100)
    grouping_column_str = grouping_column.replace('_', ' ')

    plt.figure()
    plt.title(f'Salary Distribution of Different {grouping_column_str}s')
    for label, group in df.groupby(grouping_column):
        data = group['Salary_in_USD'] if full else get_samples(group['Salary_in_USD'], sample_size)
        plt.hist(data, bins=n_bins, alpha=0.2, edgecolor='black', label=label)
        plt.legend()
        plt.xlabel('Salary')
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    n_rows = (n_values + n_cols - 1) // n_cols
    plt.figure(figsize=(8 * n_cols, 8 * n_rows))
    for i, (label, group) in enumerate(df.groupby(grouping_column)):
        data = group['Salary_in_USD'] if full else get_samples(group['Salary_in_USD'], sample_size)
        plt.subplot(n_rows, n_cols, i + 1)
        plt.hist(data, bins=n_bins, edgecolor='black')
        plot_fitted_normal(data, n_bins)
        plot_fitted_lognormal(data, n_bins)
        plt.xlim(xmin, xmax)
        _ymin, _ymax = plt.ylim()
        plt.ylim(min(ymin, _ymin), max(ymax, _ymax))
        plt.xlabel('Salary')
        plt.title(f'Salary Distribution of {grouping_column_str}={label}')
        plt.legend()
    plt.show()


def do_violin_plots(df: pd.DataFrame, grouping_column: str, n_cols: int, full=True):
    n_values = len(df[grouping_column].unique())
    sample_size = max(df[grouping_column].value_counts().min(), 100)
    grouping_column_str = grouping_column.replace('_', ' ')

    ymin, ymax = df['Salary_in_USD'].min(), df['Salary_in_USD'].max()
    n_rows = (n_values + n_cols - 1) // n_cols
    plt.figure(figsize=(8 * n_cols, 8 * n_rows))
    for i, (label, group) in enumerate(df.groupby(grouping_column)):
        data = group['Salary_in_USD'] if full else get_samples(group['Salary_in_USD'], sample_size)
        data = group['Salary_in_USD']
        plt.subplot(n_rows, n_cols, i + 1)
        plt.violinplot(data)
        plt.xlabel('Salary')
        plt.ylim(ymin, ymax)
        plt.title(f'Salary Distribution of {grouping_column_str}={label}')
    plt.show()


def do_quantile_plot(df: pd.DataFrame, grouping_column: str, ordered_values=None):
    grouping_column_str = grouping_column.replace('_', ' ')
    if ordered_values is None:
        ordered_values = np.sort(df[grouping_column].unique())
    medians = []
    means = []
    first_quartiles = []
    third_quartiles = []
    for value in ordered_values:
        data = df[df[grouping_column] == value]['Salary_in_USD']
        first_quartiles.append(data.quantile(0.25))
        medians.append(data.median())
        third_quartiles.append(data.quantile(0.75))
        means.append(data.mean())
    X = np.arange(len(ordered_values))
    plt.plot(X, first_quartiles, label='1st quartile')
    plt.plot(X, medians, label='median')
    plt.plot(X, third_quartiles, label='3rd quartile')
    plt.plot(X, means, label='mean')
    plt.xticks(X, ordered_values)
    plt.xlabel(grouping_column_str)
    plt.ylabel('Salary')
    plt.legend()
    plt.show()


def plot_fitted_normal(data: pd.Series | np.ndarray, n_bins: int, dx=1000):
    xmin, xmax = data.min(), data.max()
    x = np.arange(xmin, xmax, dx)
    loc, scale = norm.fit(data)
    y = norm.pdf(x, loc=loc, scale=scale)
    z = y * data.count() \
        * ((xmax - xmin) / n_bins) \
        * (1 / (y.sum() * dx))
    plt.plot(x, z, label="normal", linewidth=2, color='midnightblue')


def plot_fitted_lognormal(data: pd.Series | np.ndarray, n_bins: int, dx=1000):
    xmin, xmax = data.min(), data.max()
    x = np.arange(xmin, xmax, dx)
    shape, loc, scale = lognorm.fit(data)
    y = lognorm.pdf(x, shape, loc=loc, scale=scale)
    z = y * data.count() \
        * ((xmax - xmin) / n_bins) \
        * (1 / (y.sum() * dx))
    plt.plot(x, z, label="log normal", linewidth=2, color='maroon')


def get_samples(data: pd.Series | np.ndarray, sample_size: int):
    if data.count() > sample_size:
        return pd.Series(np.random.choice(data, size=sample_size, replace=False))
    else:
        return_value = pd.concat([
            data,
            pd.Series(
                np.random.normal(
                    loc=data.mean(),
                    scale=data.std(),
                    size=(sample_size - data.count())
                )
            )
        ])
        return return_value[return_value > 0]
