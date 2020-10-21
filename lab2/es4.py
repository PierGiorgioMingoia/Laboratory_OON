import pandas as pd
import matplotlib.pyplot as plt


def read_csv(filename):
    df = pd.read_csv(filename)
    return df


def read_and_plot_data(df):
    total_profit = df['total_profit']
    month = df['month_number']
    plt.plot(month, total_profit, label='Profit data last year', color='r', marker='o', markerfacecolor='k',
             linestyle='-', linewidth=3)
    plt.show()


def product_sales_multi(df):
    # month = df['month_number']
    # fc = df['facecream']
    # fw = df['facewash']
    # tp = df['toothpaste']
    # bs = df['bathingsoap']
    # s = df['shampoo']
    # m = df['moisturizer']
    plt.plot('month_number', 'facecream', data=df, marker='o', markerfacecolor='blue', markersize=12, color='skyblue',
             linewidth=4, label="fc")
    plt.plot('month_number', 'facewash', data=df, marker='', color='olive', linewidth=2, label="fw")
    plt.plot('month_number', 'toothpaste', data=df, marker='', color='olive', linewidth=2, linestyle='dashed',
             label="tp")
    plt.legend()
    plt.show()


def bathing_soap_bar_char(df):
    width = 0.35
    plt.bar('month_number', 'bathingsoap', data=df, width=width)
    plt.show()


def histogram(df):
    mP = df['total_profit']
    mP.plot.hist(bins=3, alpha=0.5)
    plt.show()


def sub_plot(df):
    df1 = df['bathingsoap']
    df2 = df['facewash']
    fig, axes = plt.subplots(nrows=1, ncols=2)
    df1.plot(ax=axes[0])
    df2.plot(ax=axes[1])
    plt.show()


if __name__ == '__main__':
    df = read_csv('./data/sales_data.csv')
    # read_and_plot_data(df)
    # product_sales_multi(df)
    # bathing_soap_bar_char(df)
    # histogram(df)
    sub_plot(df)
