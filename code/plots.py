from database_functions import get_expense_vs_monthly_data, get_monthly_categorical_spendings_data
from utility import print_red
def get_expense_vs_monthly_plot(user_id):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np


    

    df = get_expense_vs_monthly_data(user_id)
    df = df[int(len(df) / 2) : ]

    #If dataframe is empty:
    #Then save an empty figure
    if df.empty:
        print_red("DataFrame is empty")

        # Create a figure without axes
        fig = plt.figure()
        
        # Add a title directly to the figure (not an axis)
        fig.text(
            0.5, 0.5, "Income vs Expenses Plot",
            fontsize=17, fontweight="bold", color="#1a4d6f",
            ha="center", va="top"
        )

        # Save the empty figure with only text
        plt.savefig("static/images/expense-plot.png", bbox_inches="tight")
        return



    # Create Plot
    sns.set_style("white")  # Removes default axis styling
    fig, ax = plt.subplots()
    
    
    sns.lineplot(data=df, x="Month", y="Income", ax=ax, marker=None, color="#1a4d6f", linestyle="-", linewidth = 3, label = "Income")
    
    # Add circles at each intersection
    ax.scatter(df["Month"], df["Income"], color="#1a4d6f", edgecolor="black", s=80, zorder=3)  # Circles appear on to
    
    sns.lineplot(data=df, x="Month", y="expense", ax=ax, marker=None, color="#8dd4af", linestyle="--", label = "Expense")
    
    # Add circles at each intersection
    ax.scatter(df["Month"], df["expense"], color="#8dd4af", edgecolor="black", s=80, zorder=3)  # Circles appear on to
    
    # Ensure all x-values appear
    ax.set_xticks(df["Month"])  # Set all x-values as ticks
    
    # Customize Grid
    ax.grid(True, axis="y", linestyle="--", alpha=0.7)  # Enables horizontal grid lines
    ax.spines['bottom'].set_visible(False)  # Removes x-axis line
    ax.spines['left'].set_visible(False)    # Removes y-axis line
    ax.spines['top'].set_visible(False)  # Removes x-axis line
    ax.spines['right'].set_visible(False)    # Removes y-axis line
    
    plt.xlabel(None)
    plt.ylabel(None)
    plt.title("Income vs Expenses", fontdict={"fontsize" : 17, "fontweight" : "bold", "color" : "#1a4d6f"}, loc = "left")
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=16, frameon=False)
    
    #If the user has no data to plot, When trying to display legend.
    #We get an error, so incase of TypeError save image without legend
    try:
        plt.savefig("static/images/expense-plot.png", bbox_inches = "tight")
    except Exception as e:
        print_red(e)
        plt.savefig("static/images/expense-plot.png")
        



def get_monthly_categorical_spending_plot(user_id , month):

    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = get_monthly_categorical_spendings_data(user_id , month)

    #If dataframe is empty:
    #Then save an empty figure
    if df.empty:
        print_red("DataFrame is empty")

        # Create a figure without axes
        fig = plt.figure()
        
        # Add a title directly to the figure (not an axis)
        fig.text(
            0.5, 0.5, "Spendings by Category Plot",
            fontsize=17, fontweight="bold", color="#1a4d6f",
            ha="center", va="top"
        )

        # Save the empty figure with only text
        plt.savefig("static/images/spendings-pie-chart.png", bbox_inches="tight")
        return
    
    
    pallete_color = sns.color_palette("mako").as_hex()

    plt.figure(figsize = (5,5))
    plt.pie(df["amount_spent"], 
            labels = df["category_name"],
            colors = pallete_color ,
            autopct = "%.0f%%"
           )

    # draw circle
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
     
    # Adding Circle in Pie chart
    fig.gca().add_artist(centre_circle)
    
    # plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8, frameon=False)
    plt.title(f"Spendings by Category")

    plt.savefig("static/images/spendings-pie-chart.png")
    # plt.title(f"{username} categorised spendings for month : {month}")


# get_expense_vs_monthly_plot(1)
get_monthly_categorical_spending_plot(1,12)