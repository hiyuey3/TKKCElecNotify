import pandas as pd;import numpy as np;import matplotlib.pyplot as plt;import matplotlib;
matplotlib.rcParams['font.family'] = 'Microsoft YaHei'  # Windows
matplotlib.rcParams['font.family'] = 'Arial Unicode MS'  # Mac

class PowerData:
    def __init__(self, dataFrame):
        self.DataFrame = dataFrame.sort_values('日期').copy()

    def Calc7DayAvg(self):
        self.DataFrame['SevenDayAvg'] = self.DataFrame['用量（度/吨）'].rolling(window=7, min_periods=1).mean()
        return self.DataFrame

    def FindAnomaly(self):
        x = self.DataFrame['用量（度/吨）'].values
        meanVal = np.mean(x)
        stdVal = np.std(x, ddof=1)
        low = meanVal - ( 2 * stdVal )
        high = meanVal + ( 2 * stdVal )
        self.DataFrame['IsAnomaly'] = (x < low) | (x > high)
        return self.DataFrame

    def CalcDayDiff(self):
        x = self.DataFrame['用量（度/吨）'].values
        self.DataFrame['DayDiff'] = np.insert(np.diff(x), 0, np.nan)
        return self.DataFrame

    def AvgByWeekDay(self):
        self.DataFrame['WeekDay'] = self.DataFrame['日期'].dt.day_name()
        order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return self.DataFrame.groupby('WeekDay')['用量（度/吨）'].mean().reindex(order)

    def MonthTotal(self):
        self.DataFrame['YearMonth'] = self.DataFrame['日期'].dt.to_period('M')
        return self.DataFrame.groupby('YearMonth')['用量（度/吨）'].sum()

    def PredictPayDate(self, balanceDataFrame):
        df = balanceDataFrame.sort_values('日期').copy()
        df['Prev'] = df['缴费余额（元）'].shift(1)
        df['Paid'] = df['缴费余额（元）'] > df['Prev']
        payDates = df.loc[df['Paid'], '日期'] - pd.Timedelta(days=1)
        payDates = payDates.dropna().reset_index(drop=True)

        if len(payDates) < 2:
            return list(payDates), None

        avgGap = payDates.diff().dt.days.dropna().mean()
        nextPay = payDates.iloc[-1] + pd.Timedelta(days=int(round(avgGap)))
        return list(payDates), nextPay.strftime('%Y-%m-%d')

    def SaveToCSV(self, fileName='ResultElecData.csv'):
        self.DataFrame.to_csv(fileName, index=False)
        print(f"数据已保存到 {fileName}")


class PowerPlot:
    def __init__(self, dataFrame):
        self.DataFrame = dataFrame.copy()

    def PlotUsageTrend(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.DataFrame['日期'], self.DataFrame['用量（度/吨）'], label='用电量')
        plt.plot(self.DataFrame['日期'], self.DataFrame['SevenDayAvg'], label='7日均值')
        plt.scatter(self.DataFrame[self.DataFrame['IsAnomaly']]['日期'],
                    self.DataFrame[self.DataFrame['IsAnomaly']]['用量（度/吨）'],
                    color='red', label='异常点')
        plt.title('图1 用电趋势')
        plt.xlabel('日期')
        plt.ylabel('用量（度/吨）')
        plt.legend()
        plt.tight_layout()
        plt.savefig('图1_用电趋势.png')
        plt.show()

    def PlotWeekDayPie(self, weekAvg):
        weekAvg.dropna().plot.pie(autopct='%.1f%%', startangle=90)
        plt.title('图2 星期平均用电')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig('图2_星期平均用电.png')
        plt.show()

    def PlotMonthSum(self, monthSum):
        monthSum.plot(marker='o')
        plt.title('图3 月度总用电')
        plt.xlabel('月份')
        plt.ylabel('用量（度/吨）')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('图3_月度总用电.png')
        plt.show()

    def PlotDayDiff(self):
        plt.figure(figsize=(10, 4))
        plt.plot(self.DataFrame['日期'], self.DataFrame['DayDiff'], label='日用电差值')
        plt.axhline(0, color='gray', linestyle='--')
        plt.title('图4 日用电变化')
        plt.xlabel('日期')
        plt.ylabel('差值（度/吨）')
        plt.tight_layout()
        plt.savefig('图4_日用电变化.png')
        plt.show()

    def PlotPayPrediction(self, payDates, nextPayDate):
        if not payDates:
            return
        plt.figure(figsize=(10, 2.5))
        plt.eventplot(payDates, lineoffsets=1, colors='green', label='历史交费')
        if nextPayDate:
            nextPayDateDt = pd.to_datetime(nextPayDate)
            plt.eventplot([nextPayDateDt], lineoffsets=1.2, colors='red', label='预测交费')
            plt.text(nextPayDateDt, 1.25, nextPayDate, color='red')
        plt.title('图5 缴费日期预测')
        plt.yticks([])
        plt.legend()
        plt.tight_layout()
        plt.savefig('图5_缴费预测.png')
        plt.show()


# if __name__ == "__main__":
#     try:
#         df = pd.read_csv('ElecData.csv', parse_dates=['日期'])
#
#         analyzer = PowerData(df)
#         analyzer.Calc7DayAvg()
#         analyzer.FindAnomaly()
#         analyzer.CalcDayDiff()
#         analyzer.SaveToCSV()
#
#         plotter = PowerPlot(analyzer.DataFrame)
#         plotter.PlotUsageTrend()
#         plotter.PlotWeekDayPie(analyzer.AvgByWeekDay())
#         plotter.PlotMonthSum(analyzer.MonthTotal())
#         plotter.PlotDayDiff()
#
#         if '缴费余额（元）' in df.columns:
#             balanceDf = df[['日期', '缴费余额（元）']].dropna()
#             payDates, nextPay = analyzer.PredictPayDate(balanceDf)
#             print("预测下次交费：", nextPay)
#             plotter.PlotPayPrediction(payDates, nextPay)
#     except Exception as e:
#         print("Error:", e)

