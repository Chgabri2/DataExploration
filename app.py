from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            data = pd.read_csv(file)

            # Data exploration steps
            data_head = data.head().to_html()
            data_types = data.dtypes.to_frame(name='Data Type').to_html()
            data_description = data.describe(include='all').to_html()
            data_null = data.isnull().sum().to_frame(name='Null Values').to_html()
            data_duplicates = data.duplicated().sum()

            categorical_columns = data.select_dtypes(include='object').columns
            value_counts = {col: data[col].value_counts().to_frame(name='Count').to_html() for col in categorical_columns}

            numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns

            data_distribution = {}
            for col in numerical_columns:
                plt.figure()
                sns.histplot(data[col], kde=True)
                plt.title(f'Distribution of {col}')
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                data_distribution[col] = f'data:image/png;base64,{plot_url}'
                plt.close()

            plt.figure(figsize=(12, 10))
            numerical_data = data.select_dtypes(include=['int64', 'float64'])
            correlation_matrix = numerical_data.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
            plt.title('Correlation Matrix')
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            correlation_matrix_path = f'data:image/png;base64,{plot_url}'
            plt.close()

            outliers = {}
            for col in numerical_columns:
                plt.figure()
                sns.boxplot(y=data[col])
                plt.title(f'Box Plot of {col}')
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                outliers[col] = f'data:image/png;base64,{plot_url}'
                plt.close()

            scatter_plots = {}
            for i, col1 in enumerate(numerical_columns):
                for j, col2 in enumerate(numerical_columns):
                    if i != j:
                        plt.figure()
                        sns.scatterplot(x=data[col1], y=data[col2])
                        plt.title(f'Scatter Plot of {col1} vs {col2}')
                        img = io.BytesIO()
                        plt.savefig(img, format='png')
                        img.seek(0)
                        plot_url = base64.b64encode(img.getvalue()).decode()
                        scatter_plots[f'{col1}_{col2}'] = f'data:image/png;base64,{plot_url}'
                        plt.close()

            bar_plots = {}
            for col in categorical_columns:
                plt.figure()
                sns.countplot(y=data[col], order=data[col].value_counts().index)
                plt.title(f'Bar Plot of {col}')
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                bar_plots[col] = f'data:image/png;base64,{plot_url}'
                plt.close()

            return render_template('index.html',
                                   data_head=data_head,
                                   data_types=data_types,
                                   data_description=data_description,
                                   data_null=data_null,
                                   data_duplicates=data_duplicates,
                                   value_counts=value_counts,
                                   data_distribution=data_distribution,
                                   correlation_matrix_path=correlation_matrix_path,
                                   outliers=outliers,
                                   scatter_plots=scatter_plots,
                                   bar_plots=bar_plots)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
