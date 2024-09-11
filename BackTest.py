# 일일 종가 기준 이동평균선 초과시 최대 매수, 미만시 최대 매도
# average_length : 이동평균 계산 기간, ticker : 암호화폐 종류

import pyupbit
import matplotlib.pyplot as plt

average_length = 30
ticker = "KRW-BTC"

def get_moving_average(df, window):
    return df['close'].rolling(window=window).mean()

def backtest(start_date, end_date, cash=1000000, fee=0.0005):
    # 1. 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval="day", count=10000)
    df = df.loc[start_date:end_date]

    # 2. average_length일 이동평균선 계산
    df['MA_average_length'] = get_moving_average(df, average_length)

    # 3. 백테스트 변수 초기화
    balance = cash  # 초기 현금
    bitcoin = 0     # 초기 비트코인 보유량
    buy_signals = []
    sell_signals = []

    # 4. 백테스트 시작
    for i in range(average_length, len(df)):
        current_price = df['close'].iloc[i]
        ma_average_length = df['MA_average_length'].iloc[i]

        # 매수 조건: 현재가 > average_length일 이동평균선
        if current_price > ma_average_length and balance > 0:
            bitcoin = balance / current_price * (1 - fee)  # 최대 매수
            balance = 0  # 현금 잔액 업데이트
            buy_signals.append(df.index[i])
            print(f"Buy {ticker} at {current_price:.2f} on {df.index[i].date()}, {ticker} : {bitcoin:.6f}")

        # 매도 조건: 현재가 < average_length일 이동평균선
        elif current_price < ma_average_length and bitcoin > 0:
            balance = bitcoin * current_price * (1 - fee)  # 최대 매도
            bitcoin = 0  # 비트코인 보유량 업데이트
            sell_signals.append(df.index[i])
            print(f"Sell {ticker} at {current_price:.2f} on {df.index[i].date()}, Cash: {balance:.2f}")

    # 5. 백테스트 결과 출력
    final_balance = balance + (bitcoin * df['close'].iloc[-1] if bitcoin > 0 else 0)
    profit = (final_balance - cash)/cash * 100
    print(f"Initial Cash: {cash}, Final Balance: {final_balance:.2f}, 수익률 : {profit:.2f}%")

    #df.to_csv("price_data.csv", index=True)

    # 6. 그래프 시각화
    plt.figure(figsize=(14,7))
    plt.plot(df.index, df['close'], label='Closing Price', color='black')
    plt.plot(df.index, df['MA_average_length'], label=f'{average_length}-Day Moving Average', color='blue')
    plt.scatter(buy_signals, df.loc[buy_signals]['close'], marker='^', color='green', label='Buy Signal', alpha=1)
    plt.scatter(sell_signals, df.loc[sell_signals]['close'], marker='v', color='red', label='Sell Signal', alpha=1)
    plt.title(f'Backtest of {ticker} from {start_date} to {end_date}')
    plt.xlabel('Date')
    plt.ylabel('Price (KRW)')
    plt.legend()
    plt.text(df.index.min(), df['close'].min(), f'profit : {profit:.2f}%', fontsize=15, color='orange', verticalalignment='top',
        horizontalalignment='left', fontdict={'weight': 'bold'})
    plt.show()

# 백테스트 실행
backtest("2020-09-11", "2021-06-30")