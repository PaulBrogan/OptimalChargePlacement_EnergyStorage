# this requires Numpy

# This is really just set up to run as a stand alone package, not as a library or module or whatever.

## fire the data you want to analyse into */ipData*.

run the script

## Find data in the */opData* folder


# Input Data Requirements

1. look at example data, it should be two columns, 'Price' and 'Time', both should be floats/integers
2. it should be in CSV format, ideally with a .csv extension
3. it can probably be as long as you want it, it works with 200,000+ rows
4. Time is expected in UTC, if this is not available, maybe just work with seconds.

# Script Variables

1. You can change the ip and op folders if you want, but why?
2. *self.ipList* is a list of all files you want analysed, please keep the *.csv*
3. *self.headers1* specifies the data to be output to the *StateOfCharge* folder, 
the values to be output need to be keys in the *self.DataDict*. Feel free to play around
4.  *self.headers2* specifies the values to be output to the *Trade* folder - we will discuss this more later
5. Various battery sizes can be specified in *self.batteryCapList*, the script will loops over these values, 
the battery capacity is specified as hours
6. The inverter size is considered to be 1 per unit, so if trades are megawatt hours (MWh) then the battery will be 1 MWh. 
If you want this to different then it is straight forward to multiply the relevant numpy arrays by the scalar size of the 
battery, or just do it afterwards.
7. The trading period is specified in hours, the default is 0.5 hours, so an energy storage array will exporting 1 per unit (MW) over 0.5 units of time (hours)
will export 0.5 units (MWh) and receive 0.5 x the energy price.
8. *self.startPrice* specifies the initial minimum acceptable trade value, once all trades above this value have been exhausted
the *self.startPrice* is multiplied by the *self.acceptableDrop* (which must be less than 1.), then the process continues, exhausting
all trades above this value.
9. The process stops at the *self.minimumPriceList* point, this is also a list that will be iterated through, as the minimum acceptable
price point will vary between storage technologies.

# Output Data

1. Data is dumped into two folders *StateOfCharge* and *Trade*
2. The *StateOfCharge* folder contains timeseries data on state of charge, power delivery, income/outgoings
3. The *Trade* folder contains data in order of transaction value, this creates a decay curve when trade price is plotted
on a scatter plot, it is best to sort the data after, I have not done this in the code as it has the potential to show up
issues in the analysis

-Paul