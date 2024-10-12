import pandas as pd
import matplotlib.pyplot as plt
import itertools

# Load the Excel file
file_path = 'linear_separable.xlsx'  # Replace with your file path
excel_data = pd.ExcelFile(file_path)

# Define a function to generate colors
def get_color_map(unique_labels):
    color_cycle = itertools.cycle(plt.cm.tab10.colors)  # You can choose any colormap you like
    return {label: next(color_cycle) for label in unique_labels}

# Loop through each sheet and plot the data
for sheet_name in excel_data.sheet_names:
    # Read the dataframe from the current sheet
    df = excel_data.parse(sheet_name)
    
    # Check if the dataframe has the required columns
    if df.shape[1] >= 3:
        plt.figure()
        
        # Get unique class labels and create a color map
        unique_labels = df.iloc[:, 2].unique()
        colors = get_color_map(unique_labels)
        
        # Plot each class with a different color
        for class_label in unique_labels:
            class_data = df[df.iloc[:, 2] == class_label]
            plt.scatter(class_data.iloc[:, 0], class_data.iloc[:, 1], 
                        color=colors[class_label], label=f'Class {class_label}')
        
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title(f'Scatter Plot of {sheet_name}')
        plt.legend()
        plt.savefig("linear.png")
        plt.show()
    else:
        print(f"Sheet {sheet_name} does not have the required columns for plotting")

print("Scatter plots have been generated for all sheets.")
