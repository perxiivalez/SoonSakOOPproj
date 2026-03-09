"""
mcp_server.py
=============
FastMCP Server สำหรับระบบ SoonSak
ทำให้ Claude Desktop สามารถเรียกใช้และทดสอบ OOP ทั้งหมดได้โดยตรง

วิธีรัน:
    pip install fastmcp
    python mcp_server.py

หรือใช้กับ Claude Desktop โดยเพิ่มใน claude_desktop_config.json:
{
  "mcpServers": {
    "soonsak": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}

Tools ที่ expose:
─────────────────────────────────────────────
👤 USER
  - register_user         ลงทะเบียน User / VIP
  - login                 เข้าสู่ระบบ
  - logout                ออกจากระบบ
  - get_user_info         ดูข้อมูล User
  - add_coupon_to_user    เพิ่มคูปอง (Admin)
  - suspend_user          ระงับบัญชี (Admin)

🎨 ARTIST
  - register_artist       ลงทะเบียน Artist
  - approve_artist        Admin อนุมัติ Artist
  - set_deposit_policy    Artist ตั้ง deposit policy
  - artist_accept_job     Artist รับงาน
  - artist_reject_job     Artist ปฏิเสธงาน
  - artist_complete_job   Artist งานเสร็จ
  - request_studio        Artist ขอ Studio
  - get_artist_info       ดูข้อมูล Artist

📋 BOOKING
  - create_booking        สร้างการจอง
  - cancel_booking        ยกเลิกการจอง
  - get_booking_info      ดูข้อมูล Booking
  - rate_artist           รีวิว Artist

💳 PAYMENT
  - create_order          สร้าง Order
  - pay_deposit           ชำระมัดจำ
  - pay_full              ชำระเต็มจำนวน
  - get_order_info        ดูข้อมูล Order

🏢 STUDIO
  - approve_studio        Admin อนุมัติ Studio
  - reject_studio         Admin ปฏิเสธ Studio

📊 REPORTS
  - report_bank           รายงานยอดเงิน
  - report_artist_rating  รายงานคะแนน Artist
  - list_all_users        ดูรายชื่อ User ทั้งหมด
  - list_all_artists      ดูรายชื่อ Artist ทั้งหมด

🧪 TEST
  - run_full_demo         รัน demo สมบูรณ์ทั้งระบบ
  - reset_system          รีเซ็ตระบบกลับเป็น state ว่าง
─────────────────────────────────────────────
"""

import sys
import io
from contextlib import redirect_stdout
from datetime import date, datetime
from typing import Optional

# ── import OOP classes ──
from entities import (
    User, VIPMember, Artist, Admin,
    Studio, Coupon, Rating,
    Portfolio, TattooStyle,
    Calendar, Event,
    StudioRequest
)
from booking import Booking, Appointment, Order
from payment import (
    Payment, Promptpay, Transaction,
    SoonSakBank, PaymentMethod,
    FixedDepositPolicy, PercentDepositPolicy,
    DepositPolicy
)
from controller import SoonSak

# ── FastMCP ──
from fastmcp import FastMCP

# ─────────────────────────────────────────────
# สร้าง FastMCP App และ SoonSak instance เดียว
# (state อยู่ใน memory ตลอด session)
# ─────────────────────────────────────────────

mcp = FastMCP(
    name="SoonSak OOP Server",
    instructions="""
    MCP Server สำหรับทดสอบระบบ SoonSak ที่เขียนด้วย OOP Python
    ใช้ tools ด้านล่างเพื่อสร้าง User, Artist, Booking, Payment และทดสอบทุก flow
    สามารถรัน run_full_demo เพื่อทดสอบระบบทั้งหมดในครั้งเดียว
    หรือเรียกแต่ละ tool เพื่อทดสอบแยกส่วนได้
    """
)

# ── Global System Instance ──
# state จะถูกเก็บไว้ตลอด session นี้
_system: SoonSak = SoonSak()

# ── helper: capture stdout ออกมาเป็น string ──
def _capture(fn, *args, **kwargs) -> str:
    """รัน fn แล้วจับ stdout กลับมาเป็น string เพื่อส่งให้ Claude อ่าน"""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            result = fn(*args, **kwargs)
        output = buf.getvalue()
        if result is not None:
            output += f"\n✅ Return: {result}"
        return output if output.strip() else "✅ สำเร็จ (ไม่มี output)"
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"


# ═══════════════════════════════════════════════
# 👤 USER TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def register_user(
    user_id: str,
    name: str,
    email: str,
    phone: str,
    is_vip: bool = False,
    vip_rank: str = "SILVER"
) -> str:
    """
    ลงทะเบียน User ใหม่เข้าระบบ
    - user_id: รหัส เช่น USR-001
    - is_vip: True = สร้างเป็น VIPMember
    - vip_rank: SILVER / GOLD / PLATINUM (ใช้เมื่อ is_vip=True)
    """
    return _capture(_system.register_user, user_id, name, email, phone, is_vip, vip_rank)


@mcp.tool()
def login(user_id: str) -> str:
    """
    เข้าสู่ระบบ
    - ใช้ได้กับ User, Artist, Admin
    - ต้อง login ก่อนถึงจะทำ action อื่นได้
    """
    return _capture(_system.login, user_id)


@mcp.tool()
def logout(user_id: str) -> str:
    """ออกจากระบบ"""
    return _capture(_system.logout, user_id)


@mcp.tool()
def get_user_info(user_id: str) -> str:
    """
    ดูข้อมูล User
    - แสดง name, email, status, credit, max_bookings, ประวัติการจอง
    """
    user = _system.find_user(user_id)
    if user is None:
        return f"❌ ไม่พบ User {user_id}"
    history = user.view_history()
    info = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "status": user.status,
        "credit": user.credit,
        "type": "VIPMember" if isinstance(user, VIPMember) else "User",
        "vip_rank": user.rank if isinstance(user, VIPMember) else "-",
        "max_bookings": user.max_bookings,
        "max_calendar_days": user.max_calendar,
        "booking_history_count": len(history),
    }
    lines = [f"👤 User Info: {user_id}"]
    for k, v in info.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


@mcp.tool()
def suspend_user(admin_id: str, user_id: str) -> str:
    """
    Admin ระงับบัญชี User
    - admin_id: ต้อง login แล้ว
    """
    return _capture(_system.admin_suspend_user, admin_id, user_id)


@mcp.tool()
def add_coupon_to_user(
    admin_id: str,
    user_id: str,
    coupon_code: str,
    discount: float,
    expired_year: int,
    expired_month: int,
    expired_day: int
) -> str:
    """
    Admin เพิ่มคูปองส่วนลดให้ User
    - discount: เปอร์เซ็นต์ส่วนลด เช่น 10 = 10%
    - expired_*: วันหมดอายุ
    """
    expired = date(expired_year, expired_month, expired_day)
    return _capture(_system.admin_add_coupon, admin_id, user_id, coupon_code, discount, expired)


# ═══════════════════════════════════════════════
# 🎨 ARTIST TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def register_artist(
    staff_id: str,
    name: str,
    email: str,
    experience: int = 0
) -> str:
    """
    ลงทะเบียน Artist ใหม่ (สถานะ PENDING รอ Admin อนุมัติ)
    - staff_id: รหัส เช่น ART-001
    - experience: ประสบการณ์เป็นปี
    """
    return _capture(_system.register_artist, staff_id, name, email, experience)


@mcp.tool()
def approve_artist(admin_id: str, artist_id: str) -> str:
    """
    Admin อนุมัติ Artist → สถานะเปลี่ยนเป็น VERIFIED
    - admin_id: ต้อง login แล้ว
    """
    return _capture(_system.admin_approve_artist, admin_id, artist_id)


@mcp.tool()
def set_deposit_policy(
    artist_id: str,
    policy_type: str,
    value: float
) -> str:
    """
    Artist ตั้งนโยบายมัดจำ
    - policy_type: "percent" หรือ "fixed"
    - value: ถ้า percent = % เช่น 30 / ถ้า fixed = บาท เช่น 500
    """
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"❌ ไม่พบ Artist {artist_id}"

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            if policy_type.lower() == "percent":
                policy = PercentDepositPolicy(percent=value)
            elif policy_type.lower() == "fixed":
                policy = FixedDepositPolicy(fixed_amount=value)
            else:
                return "❌ policy_type ต้องเป็น 'percent' หรือ 'fixed'"
            artist.set_deposit_policy(policy)
        return buf.getvalue() or "✅ ตั้ง policy สำเร็จ"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def get_artist_info(artist_id: str) -> str:
    """
    ดูข้อมูล Artist
    - แสดง status, experience, deposit policy, คะแนนเฉลี่ย
    """
    try:
        info = _system.view_artist(artist_id)
        lines = [f"🎨 Artist Info: {artist_id}"]
        for k, v in info.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def artist_accept_job(artist_id: str, booking_id: str) -> str:
    """
    Artist รับงาน → Booking status เปลี่ยนเป็น ACCEPTED
    - booking ต้องอยู่ใน state WAITING
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_accept_job, artist_id, booking)


@mcp.tool()
def artist_reject_job(artist_id: str, booking_id: str, reason: str = "") -> str:
    """
    Artist ปฏิเสธงาน → Booking status เปลี่ยนเป็น CANCELLED
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_reject_job, artist_id, booking, reason)


@mcp.tool()
def artist_complete_job(artist_id: str, booking_id: str) -> str:
    """
    Artist กดงานเสร็จ → Booking status เปลี่ยนเป็น COMPLETED
    - booking ต้องอยู่ใน state ACCEPTED ก่อน
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_complete_job, artist_id, booking)


@mcp.tool()
def request_studio(artist_id: str, studio_name: str, location: str) -> str:
    """
    Artist ส่งคำขอเปิด Studio ใหม่ (รอ Admin อนุมัติ)
    """
    return _capture(_system.artist_request_studio, artist_id, studio_name, location)


# ═══════════════════════════════════════════════
# 📋 BOOKING TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def create_booking(
    user_id: str,
    artist_id: str,
    body_part: str,
    size: str,
    color_tone: str,
    base_price: float,
    reference_image: str = ""
) -> str:
    """
    สร้าง Booking ใหม่
    - user_id: ต้อง login แล้ว
    - body_part: ตำแหน่งที่สัก เช่น แขน, หลัง
    - size: small / medium / large
    - color_tone: ขาว-ดำ / สี
    - base_price: ราคาประมาณ (บาท)
    """
    return _capture(
        _system.create_booking,
        user_id, artist_id,
        body_part, size, color_tone,
        base_price, reference_image
    )


@mcp.tool()
def cancel_booking(user_id: str, booking_id: str) -> str:
    """
    User ยกเลิก Booking
    - ยกเลิกได้เฉพาะ WAITING หรือ ACCEPTED เท่านั้น
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.cancel_booking, user_id, booking)


@mcp.tool()
def get_booking_info(booking_id: str) -> str:
    """
    ดูข้อมูล Booking ทั้งหมด
    - แสดง status, user, artist, ราคา, นัดหมาย
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    summary = booking.summary()
    lines = [f"📋 Booking Info: {booking_id}"]
    for k, v in summary.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


@mcp.tool()
def rate_artist(
    user_id: str,
    artist_id: str,
    booking_id: str,
    score: int,
    comment: str
) -> str:
    """
    User รีวิว Artist หลังงานเสร็จ
    - booking ต้องมีสถานะ COMPLETED ก่อน
    - score: 1-5
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.rate_artist, user_id, artist_id, booking, score, comment)


# ═══════════════════════════════════════════════
# 💳 PAYMENT TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def create_order(booking_id: str) -> str:
    """
    สร้าง Order จาก Booking
    - คืน order_id ที่สร้างขึ้น
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            order = _system.create_order(booking)
        # เก็บ order ไว้ใน registry
        _order_registry[order.order_id] = order
        return buf.getvalue() + f"\n✅ order_id = {order.order_id}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def pay_deposit(
    user_id: str,
    order_id: str,
    promptpay_number: str,
    policy_type: str = "percent",
    policy_value: float = 30.0
) -> str:
    """
    ชำระมัดจำผ่าน PromptPay
    - policy_type: "percent" หรือ "fixed"
    - policy_value: % หรือจำนวนบาท
    """
    order = _get_order(order_id)
    if isinstance(order, str):
        return order

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            policy = (PercentDepositPolicy(policy_value)
                      if policy_type == "percent"
                      else FixedDepositPolicy(policy_value))
            _system.process_payment(user_id, order, method, policy, pay_full=False)
        return buf.getvalue() or "✅ ชำระมัดจำสำเร็จ"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def pay_full(
    user_id: str,
    order_id: str,
    promptpay_number: str
) -> str:
    """
    ชำระเต็มจำนวนที่เหลือผ่าน PromptPay
    """
    order = _get_order(order_id)
    if isinstance(order, str):
        return order

    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            _system.process_payment(user_id, order, method, pay_full=True)
        return buf.getvalue() or "✅ ชำระเต็มจำนวนสำเร็จ"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def get_order_info(order_id: str) -> str:
    """
    ดูข้อมูล Order
    - แสดง status, deposit, ยอดรวม, Bookings ใน Order
    """
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    summary = order.summary()
    lines = [f"💳 Order Info: {order_id}"]
    for k, v in summary.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# 🏢 STUDIO TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def approve_studio(admin_id: str, request_id: str) -> str:
    """
    Admin อนุมัติ StudioRequest → สร้าง Studio ใหม่
    - ต้องมี request_id จาก request_studio ก่อน
    """
    req = _request_registry.get(request_id)
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_approve_studio, admin_id, req)


@mcp.tool()
def reject_studio(admin_id: str, request_id: str) -> str:
    """
    Admin ปฏิเสธ StudioRequest
    """
    req = _request_registry.get(request_id)
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_reject_studio, admin_id, req)


# ═══════════════════════════════════════════════
# 📊 REPORT TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def report_bank() -> str:
    """
    รายงานยอดเงินใน SoonSak Bank
    - แสดงยอดคงเหลือและ Transaction ทั้งหมด
    """
    return _capture(_system.report_bank_balance)


@mcp.tool()
def report_artist_rating(artist_id: str) -> str:
    """
    รายงานคะแนนเฉลี่ยของ Artist
    """
    return _capture(_system.report_artist_ratings, artist_id)


@mcp.tool()
def list_all_users() -> str:
    """
    ดูรายชื่อ User ทั้งหมดในระบบ
    """
    users = _system._user_list
    if not users:
        return "ยังไม่มี User ในระบบ"
    lines = [f"👥 Users ทั้งหมด ({len(users)} คน):"]
    for uid, u in users.items():
        utype = "VIP" if isinstance(u, VIPMember) else "User"
        lines.append(f"  [{uid}] {u.name} | {utype} | status={u.status}")
    return "\n".join(lines)


@mcp.tool()
def list_all_artists() -> str:
    """
    ดูรายชื่อ Artist ทั้งหมดในระบบ
    """
    artists = _system._artist_list
    if not artists:
        return "ยังไม่มี Artist ในระบบ"
    lines = [f"🎨 Artists ทั้งหมด ({len(artists)} คน):"]
    for aid, a in artists.items():
        avg = a.average_rating()
        lines.append(f"  [{aid}] {a.name} | status={a.status} | rating={avg:.1f}/5")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# 🧪 TEST TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def run_full_demo() -> str:
    """
    รัน Demo สมบูรณ์ทั้งระบบ ครอบคลุมทุก Flow:
    1. Register User, VIP, Artist, Admin
    2. Login ทุกคน
    3. Admin อนุมัติ Artist
    4. Artist ตั้ง Deposit Policy
    5. สร้าง Booking (User + VIP)
    6. Artist รับงาน
    7. ชำระมัดจำ (Percent + Fixed)
    8. คำนวณส่วนลด VIP
    9. งานเสร็จ + Rate Artist
    10. Admin เพิ่ม Coupon
    11. Request + Approve Studio
    12. Report ทั้งหมด
    """
    global _system, _booking_registry, _order_registry, _request_registry

    # รีเซ็ตระบบก่อนรัน demo ใหม่
    buf = io.StringIO()
    with redirect_stdout(buf):
        _system = SoonSak()
        _booking_registry.clear()
        _order_registry.clear()
        _request_registry.clear()

        # ── 1. Register ──
        user1 = _system.register_user("USR-001", "อาทิตย์", "sun@mail.com", "0811111111")
        vip1  = _system.register_user("USR-002", "มีนา", "mina@mail.com", "0822222222",
                                       is_vip=True, vip_rank="GOLD")
        artist1 = _system.register_artist("ART-001", "ช่างแจ็ค", "jack@mail.com", experience=5)
        admin1  = _system.register_admin("ADM-001", "ผู้ดูแล", "admin@soonsak.com")

        # ── 2. Login ──
        _system.login("ADM-001")
        _system.login("ART-001")
        _system.login("USR-001")
        _system.login("USR-002")

        # ── 3. Admin อนุมัติ Artist ──
        _system.admin_approve_artist("ADM-001", "ART-001")

        # ── 4. Deposit Policy ──
        policy = PercentDepositPolicy(percent=30)
        artist1.set_deposit_policy(policy)

        # ── 5. Booking ──
        b1 = _system.create_booking(
            "USR-001", "ART-001", "แขน", "กลาง", "ขาว-ดำ", 3000.0)
        b2 = _system.create_booking(
            "USR-002", "ART-001", "หลัง", "ใหญ่", "สี", 8000.0)
        _booking_registry[b1.booking_id] = b1
        _booking_registry[b2.booking_id] = b2

        # ── 6. Artist รับงาน ──
        _system.artist_accept_job("ART-001", b1)
        _system.artist_accept_job("ART-001", b2)

        # ── 7. Payment ──
        o1 = _system.create_order(b1)
        _order_registry[o1.order_id] = o1
        _system.process_payment("USR-001", o1, Promptpay("0811111111"), policy)
        o1.order_phase()

        # ── 8. VIP Discount ──
        discount = vip1.calculate_discount(b2.base_price)
        print(f"VIP ส่วนลด: {discount:.2f} บาท (ราคาจริง: {b2.base_price - discount:.2f})")
        o2 = _system.create_order(b2)
        _order_registry[o2.order_id] = o2
        _system.process_payment("USR-002", o2, Promptpay("0822222222"),
                                 FixedDepositPolicy(500))

        # ── 9. Complete + Rate ──
        _system.artist_complete_job("ART-001", b1)
        _system.rate_artist("USR-001", "ART-001", b1, 5, "สวยมากค่ะ!")

        # ── 10. Coupon ──
        _system.admin_add_coupon("ADM-001", "USR-001", "SOONSAK10",
                                  10, date(2026, 12, 31))

        # ── 11. Studio ──
        req = _system.artist_request_studio("ART-001", "Jack's Ink Studio", "กรุงเทพฯ")
        _request_registry[req.request_id] = req
        _system.admin_approve_studio("ADM-001", req)

        # ── 12. Reports ──
        _system.report_artist_ratings("ART-001")
        _system.report_bank_balance()

    output = buf.getvalue()
    return f"🧪 Full Demo เสร็จสิ้น\n{'='*50}\n{output}"


@mcp.tool()
def reset_system() -> str:
    """
    รีเซ็ตระบบกลับเป็น state ว่างเปล่า
    ลบ User, Artist, Booking, Order, Transaction ทั้งหมด
    """
    global _system, _booking_registry, _order_registry, _request_registry
    _system = SoonSak()
    _booking_registry.clear()
    _order_registry.clear()
    _request_registry.clear()
    return "✅ รีเซ็ตระบบสำเร็จ พร้อมเริ่มใหม่"


# ═══════════════════════════════════════════════
# Internal Registries
# (เก็บ object references ที่สร้างจาก tools)
# ═══════════════════════════════════════════════

# booking_id → Booking object
_booking_registry: dict[str, Booking] = {}

# order_id → Order object
_order_registry: dict[str, Order] = {}

# request_id → StudioRequest object
_request_registry: dict[str, StudioRequest] = {}


def _get_booking(booking_id: str):
    """helper ดึง Booking จาก registry หรือ user history"""
    # ค้นใน registry ก่อน
    if booking_id in _booking_registry:
        return _booking_registry[booking_id]
    # ค้นใน user history ทุกคน
    for user in _system._user_list.values():
        for b in user.view_history():
            if hasattr(b, "booking_id") and b.booking_id == booking_id:
                _booking_registry[booking_id] = b
                return b
    return f"❌ ไม่พบ Booking {booking_id}"


def _get_order(order_id: str):
    """helper ดึง Order"""
    if order_id in _order_registry:
        return _order_registry[order_id]
    order = _system.find_order(order_id)
    if order:
        return order
    return f"❌ ไม่พบ Order {order_id}"


# ═══════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    print("🚀 SoonSak MCP Server กำลังเริ่มต้น...")
    print(f"   Tools ที่พร้อมใช้งาน: พร้อมใช้งานแล้ว")
    mcp.run()