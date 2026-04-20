from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    # --- ĐỊA ĐIỂM VUI CHƠI ---
    "bà nà": ["Giá vé Bà Nà Hills là 900k cho khách ngoại tỉnh, bao gồm cáp treo và hầm rượu."],
    "ngũ hành sơn": ["Ngũ Hành Sơn gồm 5 ngọn núi Kim-Mộc-Thủy-Hỏa-Thổ, vé tham quan khoảng 40k."],
    "cầu rồng": ["Cầu Rồng phun lửa và nước vào lúc 21:00 tối Thứ 7 và Chủ Nhật hàng tuần."],
    "sơn trà": ["Bán đảo Sơn Trà có Chùa Linh Ứng với tượng Phật Bà cao 67m, vào cửa miễn phí."],
    "biển": ["Biển Mỹ Khê có bãi cát mịn, nước ấm, phù hợp chơi các môn thể thao nước."],
    "chợ cồn": ["Chợ Cồn là thiên đường ăn vặt Đà Nẵng, nên đi vào tầm chiều từ 15h đến 18h."],

    # --- ĂN UỐNG ĐẶC SẢN ---
    "mì quảng": ["Mì Quảng ếch Trang (24 Pasteur) hoặc Mì Quảng Bà Mua là những lựa chọn hàng đầu."],
    "bánh xèo": ["Bánh xèo Bà Dưỡng (K280/23 Hoàng Diệu) nổi tiếng với nước tương đậu phộng đặc trưng."],
    "bê thui": ["Bê thui Cầu Mống nổi tiếng nhất là quán Rô (Bắc Sơn) hoặc quán Mười."],
    "hải sản": ["Hải sản Năm Đảnh nổi tiếng giá rẻ, hoặc hải sản Bé Mặn nếu muốn ăn sát bờ biển."],

    # --- DI CHUYỂN & KINH NGHIỆM ---
    "xe máy": ["Giá thuê xe máy ở Đà Nẵng dao động từ 100k-150k/ngày, giao tận nơi khách sạn."],
    "grab": ["Grab ở Đà Nẵng rất phổ biến và dễ đặt, cả ô tô lẫn xe máy đều có sẵn 24/7."],
    "tháng mấy": ["Thời điểm du lịch Đà Nẵng đẹp nhất là từ tháng 4 đến tháng 8, trời nắng ráo."],
    "check-in": ["Nên check-in sân bay sớm 2 tiếng. Sân bay Đà Nẵng chỉ cách trung tâm 10 phút đi xe."],
}


def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            return docs
    return ["No domain document matched. Use general fallback answer."]
