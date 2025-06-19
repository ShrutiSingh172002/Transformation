# from .logger import Logger
import pandas as pd
from pyrfc import Connection
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import win32com.client as win32
import numpy as np
import os
import pythoncom
import multiprocessing
from datetime import datetime


# @log_execution_time
def connect_to_sap(strTbl, lstFields = '',lngrowcnt = '', lngrowskps = ''):
    # SAP connection parameters
    connection_params = {
        'user': 'SANDIP',
        'passwd': 'Welcome@123456789',
        'ashost': '11.11.11.13',
        'sysnr': '00',
        'client': '100',
        'lang': 'EN',
        'trace': '0'  # Disable RFC logging
    }
    
    try:
        # Establish SAP connection
        with Connection(**connection_params) as connection:
            # logger.info("Connected to SAP successfully.")
            lstActField = []

            # Call DDIF_FIELDINFO_GET
            result = connection.call('DDIF_FIELDINFO_GET',
                            TABNAME=strTbl,     # Replace with your table name
                            LANGU='EN',
                            LFIELDNAME='',
                            ALL_TYPES='X')      # Get all types including references

            # Display field metadata
            for field in result['DFIES_TAB']:
                # print(f"{field['FIELDNAME']}: {field['ROLLNAME']} ({field['INTTYPE']} - {field['LENG']})")
                lstActField.append(field['FIELDNAME'])

            lstActField = list(set(lstActField))
            print(lstActField)
            # result = connection.call('RFC_READ_TABLE', QUERY_TABLE=strTbl,ROWCOUNT = 0,FIELDS = ['TELF1','TELF2','TELFX','TELTX'])
            # for field in result['FIELDS']:
            #     lstActField.append(field['FIELDNAME'])


            # lstNotFoundField = [fld  for fld in lstFields if fld not in lstActField]
            # if len(lstNotFoundField) > 0:
            #     strNotFoundFiled = ",".join(lstNotFoundField)
            #     # logger.warning(f"fields: {strNotFoundFiled} Not Found in table: {strTbl}.")
            #     return pd.DataFrame()


            # Fetch data from SKA1 table
            # result = connection.call('RFC_READ_TABLE',DELIMITER = '|',QUERY_TABLE=strTbl,FIELDS = lstFields,ROWSKIPS = lngrowskps , ROWCOUNT = lngrowcnt)
            
            result = connection.call('RFC_READ_TABLE',DELIMITER = '|',QUERY_TABLE=strTbl,FIELDS =lstActField[0:10],ROWCOUNT = 0)
            #result = connection.call('RFC_READ_TABLE',DELIMITER = '|',QUERY_TABLE=strTbl,FIELDS = lstFields)
            if not result or 'DATA' not in result:
                # logger.warning("No data retrieved from SAP.")
                return pd.DataFrame()
            
            # Extract column names
            columns = [field['FIELDNAME'] for field in result['FIELDS']]
            
            # Extract data rows
            data_rows = [row['WA'] for row in result['DATA']]
            
            # # Split each row by the delimiter '|'
            # split_data = [row.split('|') for row in data_rows]

            # Convert to DataFrame
            df = pd.DataFrame([row.split('|') for row in data_rows], columns=columns)
    
            df.to_excel('Data_Test.xlsx',index=False)

            # logger.warning(f"{len(df)} Data Avilable Table.")
            
            # logger.info("Data successfully retrieved and converted to DataFrame.")
            
            return df
    
    except Exception as e:
        # logger.error(f"SAP Connection Error: {e}")
        print(str(e))
        return pd.DataFrame()
    

import pandas as pd
from pyrfc import Connection
from pyrfc import ABAPApplicationError, ABAPRuntimeError, LogonError, CommunicationError

def connect_to_sap_chunked_concat(strTbl, lstFields='', lngrowcnt=0, lngrowskps=0):
    connection_params = {
        'user': 'SANDIP',
        'passwd': 'Welcome@123456789',
        'ashost': '11.11.11.13',
        'sysnr': '00',
        'client': '100',
        'lang': 'EN',
        'trace': '0'
    }

    try:
        with Connection(**connection_params) as connection:
            print("Connected to SAP successfully.")

            # Get all available fields if none provided
            if not lstFields:
                result = connection.call('DDIF_FIELDINFO_GET',
                                         TABNAME=strTbl,
                                         LANGU='EN',
                                         ALL_TYPES='X')
                lstFields = list(set(field['FIELDNAME'] for field in result['DFIES_TAB']))

            final_df = pd.DataFrame()
            chunk_size = 10
            i = 0

            while i < len(lstFields):
                success = False
                current_chunk_size = chunk_size

                while not success and current_chunk_size > 0:
                    chunk_fields = lstFields[i:i + current_chunk_size]
                    try:
                        result = connection.call('RFC_READ_TABLE',
                                                 DELIMITER='|',
                                                 QUERY_TABLE=strTbl,
                                                 FIELDS=[{'FIELDNAME': f} for f in chunk_fields],
                                                 ROWCOUNT=lngrowcnt,
                                                 ROWSKIPS=lngrowskps)

                        if not result.get('DATA'):
                            print(f"No data returned for fields: {chunk_fields}")
                            break

                        columns = [f['FIELDNAME'] for f in result['FIELDS']]
                        data_rows = [row['WA'] for row in result['DATA']]
                        df_chunk = pd.DataFrame([r.split('|') for r in data_rows], columns=columns)

                        # Concatenate column-wise
                        final_df = pd.concat([final_df, df_chunk], axis=1)
                        print(f"Fetched fields {i} to {i + current_chunk_size}")

                        i += current_chunk_size
                        success = True

                    except (ABAPApplicationError, ABAPRuntimeError, CommunicationError, LogonError) as e:
                        print(f"Error on chunk size {current_chunk_size}: {e}")
                        current_chunk_size -= 2

                if current_chunk_size == 0:
                    print(f"Skipping field: {lstFields[i]} due to repeated failure.")
                    i += 1

            final_df.to_excel('SAP_Data_Concatenated.xlsx', index=False)
            return final_df

    except Exception as e:
        print(f"SAP Connection Error: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    multiprocessing.freeze_support()


connect_to_sap('CSKT')
# connect_to_sap_chunked_concat('CEPC')



