from telethon import TelegramClient, events
import pandas as pd
import re
from datetime import datetime

api_id = 12345678
api_hash = "YOUR_API_HASH"

channel = "channelusername"

file = "signals.csv"

client = TelegramClient("session", api_id, api_hash)

try:
    df = pd.read_csv(file)
except:
    df = pd.DataFrame(columns=[
        "date","pair","entry","sl","tp","result"
    ])

def detect_signal(text):

    pair = re.findall(r"[A-Z]{3,6}\/?[A-Z]{3,6}", text)
    entry = re.findall(r"ENTRY[: ]([\d\.]+)", text)
    sl = re.findall(r"SL[: ]([\d\.]+)", text)
    tp = re.findall(r"TP[: ]([\d\.]+)", text)

    if pair and entry and sl and tp:
        return {
            "pair": pair[0],
            "entry": entry[0],
            "sl": sl[0],
            "tp": tp[0]
        }

    return None


def detect_result(text):

    text = text.upper()

    if "TP" in text or "TARGET HIT" in text:
        return "TP"

    if "SL" in text or "STOP LOSS" in text:
        return "SL"

    return None


@client.on(events.NewMessage(chats=channel))
async def handler(event):

    global df

    text = event.message.text

    signal = detect_signal(text)
    result = detect_result(text)

    if signal:

        row = {
            "date": datetime.now(),
            "pair": signal["pair"],
            "entry": signal["entry"],
            "sl": signal["sl"],
            "tp": signal["tp"],
            "result": "OPEN"
        }

        df = pd.concat([df, pd.DataFrame([row])])
        df.to_csv(file,index=False)

        print("New signal saved:", signal)


    elif result:

        pair = re.findall(r"[A-Z]{3,6}\/?[A-Z]{3,6}", text)

        if pair:

            pair = pair[0]

            open_trade = df[
                (df["pair"] == pair) &
                (df["result"] == "OPEN")
            ].tail(1)

            if not open_trade.empty:

                index = open_trade.index[0]
                df.loc[index,"result"] = result

                df.to_csv(file,index=False)

                print(pair, "updated as", result)


client.start()
print("Bot running...")
client.run_until_disconnected()
