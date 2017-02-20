# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 20:09:08 2016

@author: GDM
"""
####IMPORTING MODULES####
import pandas as pd
import cPickle as pickle
import os
from HaSAPPY_time import *
#########################


def main(Info):
    def print_save_analysis (string, storage_loc):
        print string
        with open (os.path.join(storage_loc,'analysis_info.txt'), 'a' ) as write:
            print >> write, string
    ####
    def create_table(Info,GroupAnalysis,summary,keys,filters,name):
        
        for instruction in filters:
            if instruction['parameter'][1] != 'Score' and instruction['parameter'][1] != 'Outliers':
                key  = '%s_%s_%s' %(instruction['parameter'][0],instruction['parameter'][1],instruction['parameter'][2])
            else:
                key = '%s_%s' % (instruction['parameter'][0],instruction['parameter'][1])
            operation  = instruction['operation']
            if not operation == 'ascending' and not operation == 'descending':
                number = float(instruction['number'])
                if operation == '>':
                    summary = summary[summary[key] > number]
                elif operation == '>=':
                    summary = summary[summary[key] >= number]
                elif operation == '<':
                    summary = summary[summary[key] > number]
                elif operation == '<=':
                    summary = summary[summary[key] >= number]
                elif operation == '==':
                    summary = summary[summary[key] == number]
            elif operation == 'ascending':
                summary = summary.sort_index(by = key, ascending = True)
            elif operation == 'descending':
                summary = summary.sort_index(by = key, ascending = False)
                    
        table = pd.DataFrame()
        table.name = name
        columns_name = []
        for instruction in keys:
            group = [instruction[0]]
            if group[0] == 'all':
                group = []
                group.append(GroupAnalysis.Reference.name)
                for group_exp in GroupAnalysis.Others.name:
                    group.append(group_exp)
            
            parameter = [instruction[1]]
            if parameter[0] == 'all':
                parameter = []
                if GroupAnalysis.Parameters.II:
                    parameter.append('II')
                if GroupAnalysis.Parameters.KI:
                    parameter.append('KI')
                if GroupAnalysis.Parameters.Bias:
                    parameter.append('Bias')
                    parameter.append('biasFW')
                    parameter.append('biasRV')
                if GroupAnalysis.Parameters.Reads:
                    parameter.append('Reads')
                if GroupAnalysis.Outlier.perform:
                    parameter.append('Outliers')
                    parameter.append('Score')
                            
            if instruction[1]  != 'Score' and instruction[1]  != 'Outliers':
                value = instruction[2]
                if value == 'raw' or value == 'all':
                    values = {}
                    if GroupAnalysis.Reference.name in group:
                        values[GroupAnalysis.Reference.name] = [exp for exp in GroupAnalysis.Reference.experiments]
                            
                    for group_exp in GroupAnalysis.Others.name:
                        if group_exp in group:
                            values[group_exp] = [exp for exp in GroupAnalysis.Others.experiments[GroupAnalysis.Others.name.index(group_exp)]]
                    
                    if value == 'all':
                        if GroupAnalysis.Reference.name in group:
                            values[GroupAnalysis.Reference.name]+=['mean','stdev']
                        for group_exp in GroupAnalysis.Others.name:
                            if group_exp in group:
                                values[group_exp]+=['mean','stdev','fold','ttest']
                    
                    
                else:
                    values = {}
                    if GroupAnalysis.Reference.name in group:
                        values[GroupAnalysis.Reference.name] = [value]
                    for group_exp in GroupAnalysis.Others.name:
                        if group_exp in group:
                            values[group_exp] = [value]
            
            
            for a in group:
                if not a == GroupAnalysis.Reference.name:
                    for b in parameter:
                        if b != 'Score' and b != 'Outliers':
                            for c in values[a]:
                                columns_name.append('%s_%s_%s'%(a,b,c))
                        elif b == 'Score' or b == 'Outliers':
                            columns_name.append('%s_%s'%(a,b))
                            
                elif a == GroupAnalysis.Reference.name:
                    for b in parameter:
                        if b != 'Score' and b != 'Outliers':
                            for c in values[a]:
                                if not c == 'fold' and not c == 'ttest':
                                    columns_name.append('%s_%s_%s'%(a,b,c))
                  
                
        for name in columns_name:
            if name in summary.columns:
                table[name] = summary[name]
                
            else:
                string = "\tWarning!!! %s is not among avaiable columns" % (name)
                print_save_analysis (string, GroupAnalysis.storage_loc)
                
        string = '\n\tColumns:\n\t%s' %(' | ').join(table.columns)
        print_save_analysis (string, GroupAnalysis.storage_loc)
        string = '\n\tFilters:%s\n\t' % (' | ').join(filters)
        print_save_analysis (string, GroupAnalysis.storage_loc)
                
        return table
        ########
    
    date_today = getDay()   
    
    #Printing statements    
    
    strings = []
    
    strings.append('\n***\tTable generation\t***\t\tDate: %s' % date_today)
    
        
    #Upload GroupAnalysis
    startTime = getCurrTime()      
    strings.append('\nRestoring GroupAnalysis information and RawData files\n\tStarted: %s' % startTime)
    
    with open(Info.Tables.input_files, 'rb') as loading:
        GroupAnalysis = pickle.load(loading)
    strings.append('\tGroupAnalysis location: %s' % Info.Tables.input_files)
            
    with open (os.path.join(GroupAnalysis.storage_loc,'raw', 'RawData.pkl'), 'rb') as loading:
        summary = (pickle.load(loading)).all
    strings.append('\tRowData.pkl location: %s' % os.path.join(GroupAnalysis.storage_loc,'raw', 'RawData.pkl'))
    
    strings.append('\tRunTime: %s' % computeRunTime(startTime,getCurrTime()))
    
    for string in strings:
        print_save_analysis (string, GroupAnalysis.storage_loc)
    
    startTime = getCurrTime() 
    string = '\nGeneration of Tables\n\tStarted: %s'% startTime
    print_save_analysis (string, GroupAnalysis.storage_loc)
        
    tables = []
    table_count = 0                
    for table in Info.Tables.names:  
        table_count +=1
        
        string = '%i) %s' %(table_count,table)
        print_save_analysis (string, GroupAnalysis.storage_loc)
        
        keys = Info.Tables.keys[Info.Tables.names.index(table)]
        filters = Info.Tables.filters[Info.Tables.names.index(table)]
        tables.append(create_table(Info,GroupAnalysis,summary,keys,filters,table))
    
    string = '\tRunTime: %s' % computeRunTime(startTime,getCurrTime())
    print_save_analysis (string, GroupAnalysis.storage_loc)
    
    
    startTime = getCurrTime()
    string = '\nGeneration of Excel table\n\tStarted: %s'% startTime
    print_save_analysis (string, GroupAnalysis.storage_loc)
    
    storing_loc = os.path.join(GroupAnalysis.storage_loc,'Table_%s.xlsx'% getDay())
    attempt = 0
    while os.path.isfile(storing_loc):
        attempt +=1
        storing_loc = os.path.join(GroupAnalysis.storage_loc,'Table_%s_%s.xlsx'%(getDay(),str(attempt)))
    
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    
    writer = pd.ExcelWriter(storing_loc, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.

    for table in tables:
        table.to_excel(writer, sheet_name= table.name,na_rep = 'NaN')
        
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    string = '\tSaved Table : %s' %(storing_loc)
    print_save_analysis (string, GroupAnalysis.storage_loc)
    
    string = '\tRunTime: %s' % computeRunTime(startTime,getCurrTime())
    print_save_analysis (string, GroupAnalysis.storage_loc)
    
    string = '\n***\tEND Table Generation\t***' 
    print_save_analysis (string, GroupAnalysis.storage_loc)
