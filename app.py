from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def getvalue():
    def linear_interpolation(value1, percentage1, value2, percentage2, target_value):
        return percentage1 + (target_value - value1) * (percentage2 - percentage1) / (value2 - value1)

    def calculate_interpolated_percentages(df, category, value):
        percentage_0 = 0
        percentage_25 = 25
        percentage_50 = 50
        percentage_75 = 75

        value_0 = 0  # Replace with the appropriate value
        value_25 = 25  # Replace with the appropriate value
        value_50 = 50  # Replace with the appropriate value
        value_75 = 75  # Replace with the appropriate value

        interpolated_percentages = {}

        df2021 = df[df['Year'] == 2021].reset_index(drop=True).set_index('Branch Code')
        df2022 = df[df['Year'] == 2022].reset_index(drop=True).set_index('Branch Code')

        for i in range(len(df2021.index)):
            for j in range(len(df2022.index)):
                if df2021[category][i] == 0.0 and df2022[category][j] == 0.0:
                    continue
                if df2021.index[i] == df2022.index[j]:
                    sum_val = df2021[category][i] + df2022[category][j]
                    num = 1 if sum_val <= 200 else 2
                    mean = sum_val / num
                    value_50 = mean

                    if df2021[category][i] > df2022[category][j]:
                        max_val = df2021[category][i]
                        min_val = df2022[category][j]
                    else:
                        max_val = df2022[category][j]
                        min_val = df2021[category][i]

                    value_75 = max_val
                    value_25 = max_val - 10 if min_val == 0 else min_val
                    value_0 = value_25 - 10

                    if value <= value_0:
                        interpolated_percentage = percentage_0
                    elif value <= value_25:
                        interpolated_percentage = linear_interpolation(value_0, percentage_0, value_25, percentage_25, value)
                    elif value <= value_50:
                        interpolated_percentage = linear_interpolation(value_0, percentage_0, value_50, percentage_50, value)
                    elif value > value_50:
                        interpolated_percentage = linear_interpolation(value_0, percentage_0, value_75, percentage_75, value)

                    interpolated_percentages[df2021.index[i]] = min(interpolated_percentage, 100)

        res = pd.DataFrame({
            'category': list(df2022.index),
            'percentage': [interpolated_percentages.get(idx, 0) for idx in df2022.index]
        })

        return res, interpolated_percentages

    category = request.form['category']
    value = float(request.form['cutoff'])
    college = request.form['college']

    if college == "KNOWLEDGE INSTITUTE OF TECHNOLOGY":
        college = "KIOT"
    elif college == "GOVERNMENT COLLEGE OF ENGINEERING":
        college = "GEC"
    elif college == "DHIRAJLAL GANDHI COLLEGE OF TECHNOLOGY":
        college = "DGCT"
    elif college == "SONA COLLEGE OF TECHNOLOGY":
        college = "SONA"

    if college in ["SONA", "KIOT", "DGCT", "GEC"]:
        df = pd.read_csv(f"{college}.csv")
        df = df.fillna(0)
        df = df[df['Year'] != 2020]

        res, interpolated_percentages = calculate_interpolated_percentages(df, category, value)
    else:
        return "Invalid College Selected"

    rounded_dict = {key: round(value, 1) for key, value in interpolated_percentages.items()}
    return render_template('nextpage.html', cat=rounded_dict)

if __name__ == '__main__':
    app.run(debug=True)
