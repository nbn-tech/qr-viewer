import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO
from fastapi import FastAPI, Request
import uvicorn
from starlette.responses import JSONResponse
from streamlit.runtime.scriptrunner import add_script_run_ctx
import threading
import time
import datetime

# グローバル変数
generated_qr = None
current_event = None
current_id = None
current_pass = None
generated_time = None

lock = threading.Lock()

# FastAPIアプリケーションの作成
api = FastAPI()


@api.post("/generate-qr")
async def generate_qr(request: Request):
    global generated_qr, current_event, current_id, current_pass, generated_time
    try:
        data = await request.json()
    except Exception as e:
        return JSONResponse(content={"status": "リクエストボディの解析に失敗しました", "error": str(e)}, status_code=400)

    event = data.get("event") or data.get("eventcode")
    id = data.get("id")
    password = data.get("pass")

    if id and password:
        # URL生成
        url = f"https://viddownloader.tech.nagoyatv.com?event={event}&id={id}&pass={password}"
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        with lock:
            generated_qr = buffer.getvalue()
            current_event = event
            current_id = id
            current_pass = password
            generated_time = datetime.datetime.now()  # QRコードが生成された時間を記録
        return JSONResponse(content={"status": "QRコードが生成されました"})
    else:
        return JSONResponse(content={"status": "IDとPASSが必要です"}, status_code=400)

# FastAPIアプリケーションを別スレッドで実行


def start_api():
    add_script_run_ctx(threading.current_thread())
    uvicorn.run(api, host="0.0.0.0", port=8000)


api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()

# Streamlit部分
st.title("QR Code Viewer")

placeholder = st.empty()


def display_qr():
    with lock:
        if generated_qr:
            with placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"EVENT: {current_event}")
                    st.write(f"ID: {current_id}")
                    st.write(f"PASS: {current_pass}")
                    if generated_time:
                        elapsed_time = (
                            datetime.datetime.now() - generated_time).seconds
                        st.write(f"経過秒数: {elapsed_time}秒")
                with col2:
                    st.image(generated_qr, caption='早めに読み込んでください',
                             use_column_width=True)


while True:
    display_qr()
    time.sleep(1)  # 1秒ごとにチェック

# 手動でQRコードを生成する部分（オプション）
id = st.text_input("IDを入力してください")
password = st.text_input("PASSを入力してください", type="password")

if st.button("QRコード生成"):
    if id and password:
        # URL生成
        url = f"https://example.com?id={id}&pass={password}"
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        st.image(buffer.getvalue(), caption='QRコード', use_column_width=True)
    else:
        st.error("IDとPASSを入力してください")
