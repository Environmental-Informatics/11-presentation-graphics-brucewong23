#!/bin/env python
# Shizhang Wang
# 4/21/2020
# The program below takes raw files and metrics file containing hydrological 
# data and generate plots for visual comparison between tippecanoe river and 
# wildcat creek

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    # gross error check and discard
    DataDF['Discharge'].mask((DataDF['Discharge'] < 0), np.nan, inplace=True)
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    # clip data-frame to desired period, since index is already datetime series,
    # simply using pd.loc to subset/clip
    DataDF = DataDF[startDate:endDate]
    # report missing value counts
    MissingValues = DataDF["Discharge"].isna().sum()
    return( DataDF, MissingValues )

def ReadMetrics( metricsfile ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    metricsDF = pd.read_csv(metricsfile, header=0, delimiter=',',
                            parse_dates=['Date'], comment='#')
    metricsDF=metricsDF.set_index('Date')
    return( metricsDF )
    
def GetMonthlyStatistics(DataDF):
    """This function calculates monthly descriptive statistics and metrics 
    for the given streamflow time series.  Values are returned as a dataframe
    of monthly values for each year."""
    # resample and aggregate into monthly values
    monthlyData = DataDF.resample('MS')
    monthly = monthlyData.mean()
    # New DF column names
    colnames = ['Discharge']
    # New monthly DF
    MoDataDF=pd.DataFrame(index=monthly.index, columns=colnames)
    MoDataDF['Discharge']=monthlyData['Discharge'].mean()
    # combined stat and average function
    MonthlyAverages=MoDataDF.groupby(MoDataDF.index.month).mean()
    
    return ( MonthlyAverages )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
    
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    metricsfile = { "Annual": "Annual_Metrics.csv", 
                   "Monthly": "Monthly_Metrics.csv"}
    
    DataDF={}
    MissingValues={}
    metricsDF={}
    plt.figure(1)
    # from last assignment
    for file in fileName.keys():
               
        DataDF[file], MissingValues[file] = ReadData(fileName[file])
                
        # clip to consistent and plot required period
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '2014-10-01', '2019-09-30' )
        
        # plot for each file/stream
        plt.plot(DataDF[file].Discharge, label = riverName[file])
    # add label, title and legend, etc. for presentation
    plt.legend(loc='upper right')
    plt.title('Fig.1 Daily Flow for Last 5 Years', y=-0.3, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Discharge (cfs)')
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    plt.tight_layout()
    plt.savefig('daily_flow.png', dpi=96) # ppt resolution
#    plt.close()
    
    plt.figure(2)
    # metrics df
    annual_metrics = ReadMetrics(metricsfile['Annual'])
    monthly_metrics =ReadMetrics(metricsfile['Monthly'])
    # individual annual metrics
    tippe_annual= annual_metrics[annual_metrics['Station']=='Tippe']
    wildcat_annual= annual_metrics[annual_metrics['Station']=='Wildcat']
        
    # plots, coef of var
    plt.plot(tippe_annual['Coeff Var'], label=riverName['Tippe'])
    plt.plot(wildcat_annual['Coeff Var'], label=riverName['Wildcat'])    
    plt.legend(framealpha=0.8)
    plt.title('Fig.2 Annual Coefficient of Variation', y=-0.3, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Coefficient of Variation')
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    # https://stackoverflow.com/questions/3899980/how-to-change-the-font-size-on-a-matplotlib-plot
    plt.tight_layout()
    plt.savefig('coefVar.png', dpi=96) # ppt resolution
#    plt.close()
    
    plt.figure(3)
    # TQmean
    plt.plot(tippe_annual['Tqmean'], label=riverName['Tippe'])
    plt.plot(wildcat_annual['Tqmean'], label=riverName['Wildcat'])    
    plt.legend()
    plt.title('Fig.3 Annual Tqmean', y=-0.3, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Tqmean (days)')
    plt.tight_layout()
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    plt.savefig('Tqmean.png', dpi=96) # ppt resolution
#    plt.close()
    
    plt.figure(4)
    # R-B index
    plt.plot(tippe_annual['R-B Index'], label=riverName['Tippe'])
    plt.plot(wildcat_annual['R-B Index'], label=riverName['Wildcat'])    
    plt.legend()
    plt.title('Fig.4 Annual R-B Index', y=-0.3, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('R-B Index')
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    plt.tight_layout()
    plt.savefig('R-Bindex.png', dpi=96) # ppt resolution
#    plt.close()
    
    plt.figure(5)
    # average annual monthly flow
    tippe_aamf = GetMonthlyStatistics(DataDF['Tippe'])
    wildcat_aamf = GetMonthlyStatistics(DataDF['Wildcat'])
    
    # plot average annual monthly flow
    plt.plot(tippe_aamf['Discharge'], label=riverName['Tippe'])
    plt.plot(wildcat_aamf['Discharge'], label=riverName['Wildcat'])    
    plt.legend()
    plt.title('Fig.5 Average Annual Monthly Flow',y=-0.3, fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Average Annual Monthly Flow (cfs)')
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    plt.tight_layout()
    plt.savefig('aamf.png', dpi=96) # ppt resolution
#    plt.close()
    
    plt.figure(6)
    # return period of annual peak flow event
    tippe_peak = tippe_annual['Peak Flow'].sort_values(ascending=False)
    wildcat_peak = wildcat_annual['Peak Flow'].sort_values(ascending=False)
    # rank and exceedence for tippe
    tippe_rank = stats.rankdata(tippe_peak, method='average')
    trank_rev = tippe_rank[::-1]    
    tippe_exc =[(trank_rev[i]/(len(tippe_peak)+1)) for i in range(len(tippe_peak))]

    # rank and exceedence for wildcat
    wildcat_rank = stats.rankdata(wildcat_peak, method='average')
    wrank_rev = wildcat_rank[::-1]    
    wildcat_exc =[(wrank_rev[i]/(len(wildcat_peak)+1)) for i in range(len(wildcat_peak))] 
    
    # plot exceedence
    plt.scatter(tippe_exc, tippe_peak, label=riverName['Tippe'])
    plt.scatter(wildcat_exc, wildcat_peak, label=riverName['Wildcat'])
    plt.xlim(0,1)
    plt.legend()
    plt.title('Fig.6 Return Period of Annual Peak Flow', y=-0.3, fontsize=16)
    plt.xlabel('Exceedence Probability')
    plt.ylabel('Discharge (cfs)')
    plt.rcParams.update({'font.size': 12}) # minimum of 20 looks very big on fig
    plt.tight_layout()
    plt.savefig('exceedence.png', dpi=96) # ppt resolution
#    plt.close()