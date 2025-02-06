import os
import requests
import polars as pl

class CensusData():
    
    def __init__(self,years,state_code,dataset_path,
                 key_fields,api_key,
                 base_url='http://api.census.gov/data',chunk_size=48, 
                 variable_export_list=[],exclude_variables=None,
                 output_folder='output'):
        self.years = years
        self.state_code = str(state_code)
        self.dataset_path = dataset_path
        self.key_fields = key_fields
        self.base_url = base_url
        self.chunk_size = chunk_size
        self.api_url = "https://api.census.gov/data"
        self.api_key = api_key
        self.variable_export_list = variable_export_list
        self.exclude_variables = exclude_variables
        self.always_exclude_variables = ['for','in','ucgid']
        self.output_folder = output_folder
    
    def get_census_data(self):

        for year in self.years:
            print(f'Geting Census Data for {self.dataset_path} in {year}')
            exclude_vars_in_dp = self.exclude_variables.get(self.dataset_path)
            if exclude_vars_in_dp:
                exclude_vars_in_dp = exclude_vars_in_dp.get(str(year))
        
            specific_exclude_variables = exclude_vars_in_dp if exclude_vars_in_dp else []
            all_exclude_variables = self.always_exclude_variables + specific_exclude_variables

            if self.variable_export_list:
                self.variables_list = [x for x in self.variable_export_list if x not in all_exclude_variables]
            else:
                self.variables_url = f"{self.base_url}/{year}/{self.dataset_path}/variables.json"
                try:
                    variables_result = CensusData.get_response_json(self.variables_url)
                    self.variables_list = [k for k in variables_result['variables'].keys() if k not in all_exclude_variables]
                except Exception as e:
                    self.variables_list = []
            
            if self.variables_list:            
                self.chunk_variables()

                self.data_result = CensusData.get_response_json(f"{self.api_url}/{year}")
                self.dataset = [x for x in self.data_result['dataset'] if x['c_dataset'] == self.dataset_path.split('/')]
                
                if self.dataset:
                    self.dataset = self.dataset[0]
                    self.data = pl.concat(self.get_data(year),how='align')
            else:
                self.data = None
                
            if not self.data is None:
                out_path = f'{self.output_folder}/{self.state_code}/{self.dataset_path}'
                os.makedirs(out_path,exist_ok=True)
                file_name = f"{out_path}/{self.state_code}_{self.dataset_path.replace('/','_')}_{year}.csv"
                self.data.write_csv(file_name)
                print(f'Output written to {file_name}')
            else:
                print('There is no data available for this year.')  
            



    @staticmethod
    def get_response_json(url,params={}):
        response = requests.get(url,params)
        if response.status_code == 200:
            return response.json()
        else:
            pass
        
    def chunk_variables(self):
        variable_list_chunked = [self.variables_list[i:i + self.chunk_size] for i in range(0, len(self.variables_list), self.chunk_size)]
        self.variable_list_chunked =  [list(set(self.key_fields + v)) for v in variable_list_chunked]

    def get_data(self,year):
        return [self.get_data_from_api(var_list,year) for var_list in self.variable_list_chunked]

    def get_data_from_api(self,variable_list,year):
        print(f"Getting data for variables: {variable_list}")
        params = self.set_parameters(variable_list)
        access_url = f"{self.api_url}/{year}/{self.dataset_path}"
        data_json = CensusData.get_response_json(access_url,params=params)
        df = pl.DataFrame(data_json[1:],schema=data_json[0], orient='row')
        df = df.with_columns(
                pl.concat_str(['SERIALNO','SPORDER'],separator='_').alias('UNIQUE_KEY')
            )
        return df
    
    def set_parameters(self,variable_list):
        return {
            "get": ",".join(variable_list),
            "for": f"state:{self.state_code}",
            "key": self.api_key
            }
        
    @staticmethod
    def set_year_range(start,end=None,exclude_years=[]):
        year_list = []
        if start == end or end == None:
            year_list = [start]
        elif start > end:
            year_list = list(range(end,start+1))
        else:
            year_list = list(range(start,end+1))
        
        if exclude_years:
            return [year for year in year_list if year not in exclude_years]
        
        return year_list
        





        
