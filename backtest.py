import pandas as pd 
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates

def one_stock_pnl(df, delta):
	df['pct'] = df['Adj Close'].pct_change()
	df['signal'] = False
	for row in range(len(df)-1):
		if row < delta:
			pass
		else:
			df.at[row + 1,'signal'] = df.at[row,'Volume'] >= max(df['Volume'][row - delta:row])
	df = df.drop(df.index[0])	
	df['pnl'] = df['pct']*df['signal']
	df = df.set_index('Date')
	df = df[~df.index.duplicated()]
	return df['pnl']

def visualize_df(df):
	df['total'] = df.sum(axis=1)
	df['count'] = (df>0).sum(axis=1)
	df['cumulative'] = df['total'].cumsum()
	df = pd.merge(left=df, left_index=True, right=hsi, right_index=True, how='inner')
	ax = df.plot(x=df.index, y='count', kind='bar', secondary_y=True)
	df.plot(x=df.index, y='cumulative', ax=ax) 
	plt.show()

if __name__ == '__main__':
	hsi = pd.read_csv('^HSI.csv',index_col='Date',usecols=['Date','Close'],na_values=['null']).pct_change()
	hsi.fillna(0,inplace=True)
	hsi['Index_Cumulative'] = hsi.cumsum()

	consol = []
	path = 'stock_data/'
	extension = 'csv'
	os.chdir(path)
	result = [i for i in glob.glob('*.{}'.format(extension))]

	for file in result:
		df = pd.read_csv(file, index_col=None, usecols=['Date', 'Adj Close', 'Volume'], na_values=['null'])
		df.fillna(method='ffill')
		consol.append(one_stock_pnl(df, 60))
	consol_pnl = pd.concat(consol,axis=1)
	consol_pnl.fillna(value=0, inplace=True)

	visualize_df(consol_pnl)
			
