#!/bin/bash
# Cafef AI Facebook Poster Launcher for macOS / Linux

echo "======================================================="
echo "  KHỞI CHẠY CÔNG CỤ CÀO CAFEF & FB AI POSTER"
echo "======================================================="
echo ""
echo "[1/2] Đang kiểm tra và tự động cài đặt các thư viện cần thiết..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo "[LỖI] Không thể cài đặt các thư viện. Vui lòng kiểm tra xem Python3 và pip3 đã được cài đặt chưa."
    read -p "Nhấn Enter để thoát..."
    exit 1
fi
echo ""
echo "[2/2] Đang khởi chạy giao diện Web UI..."
echo "(Trình duyệt web sẽ tự động mở địa chỉ http://localhost:5000 sau vài giây)"
echo ""
echo "Nhấn Ctrl+C trên cửa sổ này để tắt ứng dụng."
echo "-------------------------------------------------------"

# Tự động mở trình duyệt tùy hệ điều hành sau 2 giây
(sleep 2 && (
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5000
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:5000
    else
        echo "Vui lòng mở trình duyệt và truy cập: http://localhost:5000"
    fi
)) &

python3 app.py
