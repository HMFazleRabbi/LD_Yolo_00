

def trace(message, flag = 0):
    if (flag):
        import sys
        import inspect
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        if (flag & 1):
            print(info.filename, ', %s' % info.function, '[%s]:' % info.lineno, message)
        elif (flag & 2):
            print('%s' % info.function, '[%s]:' % info.lineno, message)

# Dataframe Maninulation --------------------------------------|
# *************************************************************
#    Author          : JW
#    Description	 : Remove/Retrive rows containing "label_string" 
#    from dataframe data_df 
#    Last Modified   : 
#    Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************
def RemoveRowsInDF(data_df, label_string):
    return data_df[data_df.package != label_string]
def RetrieveRowsInDf(data_df, label_string):
    return data_df[data_df.package == label_string]
def RetrieveColsInDf(data_df, retrieve_key: list):
    
    flag = True
    for i in retrieve_key:
        if i in data_df.columns:
            flag = True
        else:
            flag = False
            raise ValueError('could not find {} in dataframe'.format(i))
    return data_df[retrieve_key]
# End: Dataframe Maninulation ----------------------------------|