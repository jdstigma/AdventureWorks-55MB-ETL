# Contoso-DW-10M-ETL
Repo is designed to be a project demonstration of the full ETL process from raw database to Power BI reports, dashboards &amp; apps.

Further details as to the order to view the sources and their details will be tracked here.

Directory Tree -- Repo File Tree with summary of file --

## ├── AdventureWorks.db                  [Datbase file used for the whole project]

├── AdventureWorks_doc.txt             [.txt output of new documentation]

├── README.md                          [Explains details of the Repo]

├── adventureworks_pbi.py              [Python script to create large summary]

├── db_doc.py                          [Python script to create large summary]

├── dot-documentation.html             [Documentation created using .dot commnds]

## ├── notebooks                        [jupyter notebook to run regression]

│      ├── regression_analysis.ipynb     [Regression analysis script]

│      └── regression_pipeline.py         [Python script creates pipeline for regression]

## ├── outputs                            [csv outputs produced for regression analysis]

│      ├── regression_results_20260506_202735.csv       [Data to analyze regression]

│      ├── regression_results_20260506_214843.csv       [Data to analyze regression]

│      └── regression_results_20260506_215233.csv       [Data to analyze regression]

## ├── png charts                                       [png files created by jupyter notebook]

│      ├── confusion_matrix_bucketed.png                [png chart for download]

│      ├── confusion_matrix_orderquantity.png           [png chart for download]

│      ├── correlation_heatmap.png                      [png chart for download]

│      ├── regression_OrderQuantity.png                 [png chart for download]

│      ├── regression_SalesAmount.png                   [png chart for download]

│      ├── residuals_RandomForest_OrderQuantity.png     [png chart for download]

│      ├── residuals_RandomForest_SalesAmount.png       [png chart for download]

│      ├── rf_importance_OrderQuantity.png              [png chart for download]

│      └── rf_importance_SalesAmount.png                [png chart for download]

### └── png_charts.zip                       [zip file containing all the individual png charts]
