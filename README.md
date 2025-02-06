# Downloading Census Data Through API

Author: Nick Occhipinti

This Python code will allow you to download Census data through the API url at [https://api.census.gov/data](https://api.census.gov/data).  The following information is required in order to use the code:
 * **years**: The list of years you want from the dataset.  In the **census_data_notebook.ipynb** There is a call made to ```CensusData.set_year_range()``` where you can provide the start and end year and if there are any years you want to exclude.  It will provide a list of years that the code will then use to loop through the years and get the Census data for each year.
![alt text](img/year_list.png) 
 * **state_code**:  North Carolina is **'37'** and South Carolina is **'45'**.
 * **dataset_path**: The dataset path that will be used to navigate through the API URL in order to get the data.  For example in order to get the **ACS 1 Year Estimates for PUMS** data, the dataset path is **acs/acs1/pums**.  In the API you can find the different parts of dataset path in the **c_dataset** key in the API.
  ![alt text](img/c_dataset.png)
* **key_fields**: This is the unique column(s) that identifies each record. This is needed because the code will make multiple requests to the API with different variables and then they will be combined into one data frame using the key fields.  For example the fields that make the PUMS data unique is SERIALNO and SPORDER so key_fields is set to **['SERIALNO','SPORDER']**.
* **api_key**: This is the key provide by the Census when you request a key at [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html).
* **variable_export_list**: By default this is set to **None**, meaning it will get all the variables listed in the **variables.json** file linked to each year and dataset in the API.  If you are interested in only a subset of variables you can add it to this parameter in the format **['VARIABLE_1','VARIABLE_2',...VARIABLE_N]**.
* **exclude_variables**: There is JSON file called **exclude_variables.json** which is organized by the dataset path and further by year and it contains a list of variables that should be excluded from the requests related to the dataset and time period because they are not available and generate an error.  As new cases are found they will be added to this file.
![alt text](img/exclude_variables.png)

## How it Works
The code will loop through the provided year list and create a variable list based on if there are variables provided by the user or if all the variables in the associated year and datasets variables.json will be exported.  The variable list will exclude any exclude_variables that are found for the year and dataset specified.  Since the API only allows at most 50 variable to be made to an API request the variable list into broken out into chunks of 50 variables.  Each chuck will also include the key fields that are passed.  The key fields are needed to concatenate all the API results for each chunk into one main dataset.

The requests are made to the API for each chunk of variables and as mentioned earlier concatenated into one main dataset with all the variables.  The data is then exported as a CSV to the folder specified in the output_folder parameter.  The folder structure will follow the following pattern: **_\<output_folder>/\<state_code>/\<dataset_path>_**.  The filename will follow the pattern: **_\<state_code\>\_\<dataset_path.replace('/', '\_')>\_\<year>\.csv_**.  So for example if the code was run for 2005 for state_code 45 for the acs/acs1/pums dataset path the file name would be: **45_acs_acs1_pums_2005.csv**. 

## Python Code
The code is written in Python and the only additional package you have to install is [**polars**](https://pola.rs/).  There is a Jupyter notebook called **census_data_notebook.ipynb** that will show you how to run the code.




