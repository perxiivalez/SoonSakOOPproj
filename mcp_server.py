"""
mcp_server.py — FastMCP Server สำหรับระบบ SoonSak
- ทุก attribute เป็น private (__attr)
- ไม่ใช้ Dict เลย ใช้ list + linear search แทน registries
"""

import sys
import io
from contextlib import redirect_stdout
from datetime import date, datetime
from typing import Optional

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

from fastmcp import FastMCP

mcp = FastMCP(
    name="SoonSak OOP Server",
    instructions="""
    MCP Server สำหรับทดสอบระบบ SoonSak ที่เขียนด้วย OOP Python
    ใช้ tools ด้านล่างเพื่อสร้าง User, Artist, Booking, Payment และทดสอบทุก flow
    """
)

# ── Global System Instance ──
# ── Global System Instance ──
_system: SoonSak = SoonSak()

# ── Registries — ใช้ list แทน dict ──
_booking_list: list  = []   # เก็บ Booking objects
_order_list: list    = []   # เก็บ Order objects
_request_list: list  = []   # เก็บ StudioRequest objects ← 🔴 ต้องมีบรรทัดนี้
_portfolio_list: list = []  # เก็บ Portfolio objects
_tattoo_style_list: list = []  # เก็บ TattooStyle objects
_appointment_list: list = []  # เก็บ Appointment objects ทั้งหมด


# ── Counters ──
_booking_counter  = 0
_order_counter    = 0
_portfolio_counter = 0
_style_counter = 0

# ── Mailbox Registry ──
_mailbox_registry: list = []  # [(user_id, Mailbox), ...]

# ── Appointment Helper Functions ── (🔴 เพิ่มใหม่)

def _find_appointment(appointment_id: str):
    """ค้นหา Appointment จาก ID"""
    for a in _appointment_list:
        if a.appointment_id == appointment_id:
            return a
    return None

def _get_appointment(appointment_id: str):
    """ดึง Appointment พร้อม error handling"""
    a = _find_appointment(appointment_id)
    if a is None:
        return f"❌ ไม่พบ Appointment {appointment_id}"
    return a



def _find_request(request_id: str):
    """ค้นหา StudioRequest จาก ID"""
    for r in _request_list:
        if r.request_id == request_id:
            return r
    return None

def _get_request(request_id: str):
    """ดึง StudioRequest พร้อม error handling"""
    r = _find_request(request_id)
    if r is None:
        return f"ไม่พบ StudioRequest {request_id}"
    return r


# ── Portfolio Helper Functions ── (🔴 เพิ่มใหม่)

def _find_portfolio(portfolio_id: str) -> 'Portfolio':
    """ค้นหา Portfolio จาก ID"""
    for p in _portfolio_list:
        if p.portfolio_id == portfolio_id:
            return p
    return None

def _find_tattoo_style(style_id: str) -> 'TattooStyle':
    """ค้นหา TattooStyle จาก ID"""
    for s in _tattoo_style_list:
        if s.style_id == style_id:
            return s
    return None

def _get_portfolio(portfolio_id: str):
    """ดึง Portfolio พร้อม error handling"""
    p = _find_portfolio(portfolio_id)
    if p is None:
        return f"ไม่พบ Portfolio {portfolio_id}"
    return p


# ── Seed Admin AD001 (login ไว้ล่วงหน้า) ──
_admin = _system.register_admin("AD001", "Super Admin", "admin@soonsak.com", "admin123")
_system._logged_in_users.append("AD001")

_artist = _system.register_artist("A001","Somchai","somchai@gmail.com","somchai001")
_system._logged_in_users.append("A001")

def base_data():
    admin = _system.register_admin(
        "AD001",
        "AdminDemo",
        "admin@soonsak.com",
        "1234"
    )


    user = _system.register_user(
        "U001",
        "UserDemo",
        "user@soonsak.com",
        "1234"
    )


    artist = _system.register_artist(
        "A001",
        "ArtistDemo",
        "artist@soonsak.com",
        "1234"
    )

    # approve artist
    artist.approve()


    artist.set_deposit_policy("FixedDeposit")

    
    artist.set_available_days([
        date(2026,3,20),
        date(2026,3,21),
        date(2026,3,22),
        date(2026,3,23)
    ])

  
    studio = _system.create_studio(
        "S001",
        "Demo Tattoo Studio",
        "Bangkok"
    )

  
    request = artist.request_studio("S001")

   
    admin.approve_studio_request(request)

   
    coupon = _system.create_coupon(
        "C001",
        "DISCOUNT10",
        10
    )


@mcp.tool()
def set_available_days(artist_id: str, days: list[str]) -> str:
    """
    Artist ตั้งวันว่าง
    example:
    set_available_days("A001", ["2026-03-20","2026-03-21"])
    """
    from datetime import date

    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"ไม่พบ Artist {artist_id}"

    parsed = [date.fromisoformat(d) for d in days]
    artist.set_available_days(parsed)

    return f"Artist {artist_id} ตั้งวันว่าง {len(parsed)} วัน"

@mcp.tool()
def view_available_days(artist_id: str) -> str:
    """
    View artist available days
    """

    artist = _system.find_artist(artist_id)

    if artist is None:
        return f" ไม่พบ Artist {artist_id}"

    days = artist.view_available_days()

    if not days:
        return " ไม่มีวันว่าง"

    result = "Available Days:\n"

    for d in days:
        result += f"- {d}\n"

    return result

# ── helpers: linear search แทน dict.get() ──

def _capture(fn, *args, **kwargs) -> str:
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


def _find_booking(booking_id: str) -> Booking:
    for b in _booking_list:
        if b.booking_id == booking_id:
            return b
    return None


def _find_order(order_id: str) -> Order:
    for o in _order_list:
        if o.order_id == order_id:
            return o
    return None


def _find_request(request_id: str) -> StudioRequest:
    for r in _request_list:
        if r.request_id == request_id:
            return r
    return None


def _get_booking(booking_id: str):
    b = _find_booking(booking_id)
    if b is None:
        return f"❌ ไม่พบ Booking {booking_id} — กรุณาสร้างด้วย create_booking ก่อน"
    return b


def _get_order(order_id: str):
    o = _find_order(order_id)
    if o is None:
        return f"ไม่พบ Order {order_id} — กรุณาสร้างด้วย create_order ก่อน"
    return o


# ═══════════════════════════════════════════════
# 👤 USER TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def register_user(
    user_id: str,
    name: str,
    email: str,
    phone: str,
    password: str = "1234"
) -> str:
    """
    ลงทะเบียน User ใหม่เข้าระบบ (เริ่มต้นเป็น Member ธรรมดาเท่านั้น)
    - user_id: รหัส เช่น U001
    - password: รหัสผ่าน (default: 1234)
    
    ⚠️ VIP จะได้จากการใช้จ่ายเท่านั้น:
    - Silver: ใช้จ่าย 15,000 บาท
    - Gold: ใช้จ่าย 25,000 บาท
    - Platinum: ใช้จ่าย 40,000 บาท
    """
    return _capture(_system.register_user, user_id, name, email, phone, password)

@mcp.tool()
def check_vip_status(user_id: str) -> str:
    """
    ตรวจสอบสถานะ VIP และยอดใช้จ่าย
    - แสดงยอดสะสมและระยะทางถึง rank ถัดไป
    """
    user = _system.find_user(user_id)
    if user is None:
        return f"❌ ไม่พบ User {user_id}"
    
    spent = user.total_spent
    lines = [f"💳 สถานะของ {user.name}"]
    lines.append(f"  ยอดใช้จ่ายสะสม: {spent:,.2f} บาท")
    
    if isinstance(user, VIPMember):
        lines.append(f"  🌟 ระดับ VIP: {user.rank}")
        lines.append(f"  ส่วนลด: {user.calculate_discount(100):.0f}%")
        
        if user.rank == VIPMember.RANK_SILVER:
            remain = VIPMember.THRESHOLD_GOLD - spent
            lines.append(f"  → อีก {remain:,.2f} บาท เป็น GOLD")
        elif user.rank == VIPMember.RANK_GOLD:
            remain = VIPMember.THRESHOLD_PLATINUM - spent
            lines.append(f"  → อีก {remain:,.2f} บาท เป็น PLATINUM")
        else:
            lines.append(f"  → ระดับสูงสุดแล้ว 🏆")
    else:
        lines.append(f"  ระดับ: Member ธรรมดา")
        remain = VIPMember.THRESHOLD_SILVER - spent
        lines.append(f"  → อีก {remain:,.2f} บาท เป็น VIP Silver")
    
    return "\n".join(lines)




@mcp.tool()
def login(user_id: str, password: str) -> str:
    """
    เข้าสู่ระบบ
    - ใช้ได้กับ User, Artist, Admin
    - ต้อง login ก่อนถึงจะทำ action อื่นได้
    """
    return _capture(_system.login, user_id, password)


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
        return f"ไม่พบ User {user_id}"
    history = user.view_history()
    lines = [f" User Info: {user_id}"]
    lines.append(f"  name                 : {user.name}")
    lines.append(f"  email                : {user.email}")
    lines.append(f"  status               : {user.status}")
    lines.append(f"  credit               : {user.credit}")
    lines.append(f"  type                 : {'VIPMember' if isinstance(user, VIPMember) else 'User'}")
    lines.append(f"  vip_rank             : {user.rank if isinstance(user, VIPMember) else '-'}")
    lines.append(f"  max_bookings         : {user.max_bookings}")
    lines.append(f"  max_calendar_days    : {user.max_calendar}")
    lines.append(f"  booking_history_count: {len(history)}")
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
# ARTIST TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def register_artist(
    staff_id: str,
    name: str,
    email: str,
    password: str = "1234",
    experience: int = 0
) -> str:
    """
    ลงทะเบียน Artist ใหม่ (สถานะ PENDING รอ Admin อนุมัติ)
    - staff_id: รหัส เช่น ART-001
    - password: รหัสผ่าน (default: 1234)
    - experience: ประสบการณ์เป็นปี
    """
    return _capture(_system.register_artist, staff_id, name, email, password, experience)

@mcp.tool()
def register_admin(
    admin_id: str,
    name: str,
    email: str,
    password: str
) -> str:
    """
    ลงทะเบียน Admin ใหม่เข้าระบบ
    - admin_id: รหัส เช่น AD001
    - name: ชื่อ Admin
    - email: อีเมล
    - password: รหัสผ่าน
    """
    return _capture(_system.register_admin, admin_id, name, email, password)

@mcp.tool()
def approve_artist(admin_id: str, artist_id: str) -> str:
    """
    Admin อนุมัติ Artist → สถานะเปลี่ยนเป็น VERIFIED
    - admin_id: ต้อง login แล้ว
    """
    return _capture(_system.admin_approve_artist, admin_id, artist_id)


@mcp.tool()
def set_deposit_policy(artist_id: str, policy_type: str, value: float) -> str:
    """
    Artist ตั้งนโยบายมัดจำ
    - policy_type: "percent" หรือ "fixed"
    - value: ถ้า percent = % เช่น 30 / ถ้า fixed = บาท เช่น 500
    """
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"ไม่พบ Artist {artist_id}"
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            if policy_type.lower() == "percent":
                policy = PercentDepositPolicy(percent=value)
            elif policy_type.lower() == "fixed":
                policy = FixedDepositPolicy(fixed_amount=value)
            else:
                return "policy_type ต้องเป็น 'percent' หรือ 'fixed'"
            artist.set_deposit_policy(policy)
        return buf.getvalue() or "ตั้ง policy สำเร็จ"
    except Exception as e:
        return f" Error: {e}"


@mcp.tool()
def get_artist_info(artist_id: str) -> str:
    """
    ดูข้อมูล Artist
    - แสดง status, experience, deposit policy, คะแนนเฉลี่ย
    """
    try:
        return _system.view_artist(artist_id)
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"


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
    """Artist ปฏิเสธงาน → Booking status เปลี่ยนเป็น CANCELLED"""
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
    """Artist ส่งคำขอเปิด Studio ใหม่ (รอ Admin อนุมัติ)"""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            req = _system.artist_request_studio(artist_id, studio_name, location)
        _request_list.append(req)
        return buf.getvalue() + f"\nrequest_id = {req.request_id}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


# ═══════════════════════════════════════════════
# 📋 BOOKING TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
@mcp.tool()
def create_booking(
    user_id: str,
    artist_id: str,
    body_part: str,
    size: str,
    color_tone: str,
    base_price: float = 1000.0,
    description: str = "",  # 🔴 เพิ่ม parameter
    reference_image: str = ""
) -> str:
    """
    Create booking สำหรับรอยสักหนึ่งชิ้น
    - ยังไม่มี appointment (เพิ่มทีหลังด้วย add_appointment)
    
    Args:
        user_id: รหัสลูกค้า
        artist_id: รหัส artist
        body_part: ตำแหน่งที่จะสัก (arm, back, leg, chest, etc.)
        size: ขนาด (small, medium, large)
        color_tone: โทนสี (full_color, black_grey, color_accent)
        base_price: ราคา (default: 1000 บาท)
        description: คำอธิบาย design (optional)
        reference_image: รูปอ้างอิง (optional)
    """
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            booking = _system.create_booking(
                user_id,
                artist_id,
                body_part,
                size,
                color_tone,
                base_price,
                description,  # 🔴 เพิ่ม
                reference_image
            )
        _booking_list.append(booking)
        return buf.getvalue() + f"\nBooking created: {booking.booking_id}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"



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
    """ดูข้อมูล Booking ทั้งหมด"""
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    summary = f"📋 Booking Info:\n{booking.summary()}"
    

    if booking.appointment_count > 0:
        summary += f"\n\n{booking.list_appointments()}"
    else:
        summary += "\n\n📅 ยังไม่มี appointment (ใช้ tool add_appointment เพื่อเพิ่ม)"
    
    return summary



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
# 📅 APPOINTMENT TOOLS (🔴 เพิ่มใหม่ทั้งหมด)
# ═══════════════════════════════════════════════

@mcp.tool()
def add_appointment(
    user_id: str,
    booking_id: str,
    appointment_date: str,
    start_time: str = "10:00",
    end_time: str = "18:00"
) -> str:
    """
    เพิ่ม appointment (นัดหมาย) เข้า booking
    - 1 booking สามารถมีหลาย appointments (สักหลายวัน)
    - แต่ละ appointment = 1 session
    
    Args:
        user_id: รหัสลูกค้า (ต้อง login)
        booking_id: รหัส booking เช่น BKG-001
        appointment_date: วันที่นัดหมาย (YYYY-MM-DD) เช่น "2026-03-20"
        start_time: เวลาเริ่ม (HH:MM) default: "10:00"
        end_time: เวลาสิ้นสุด (HH:MM) default: "18:00"
        
    Returns:
        appointment_id ที่สร้างขึ้น
    """
    from datetime import date
    
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    # Parse date
    try:
        appt_date = date.fromisoformat(appointment_date)
    except ValueError:
        return f"❌ รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD เช่น 2026-03-20"
    
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            appointment = _system.add_appointment(
                user_id,
                booking,
                appt_date,
                start_time,
                end_time
            )
        _appointment_list.append(appointment)
        return buf.getvalue() + f"\n✅ appointment_id = {appointment.appointment_id}"
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"


@mcp.tool()
def list_booking_appointments(booking_id: str) -> str:
    """
    ดูรายการ appointments ทั้งหมดของ booking
    
    Args:
        booking_id: รหัส booking
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    return booking.list_appointments()


@mcp.tool()
def get_appointment_info(appointment_id: str) -> str:
    """
    ดูข้อมูล appointment
    
    Args:
        appointment_id: รหัส appointment เช่น APT-001
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    booking = _get_booking(appointment.booking_id)
    if isinstance(booking, str):
        booking_info = appointment.booking_id
    else:
        booking_info = f"{booking.booking_id} ({booking.body_part}, {booking.size})"
    
    return (
        f"📅 Appointment Info\n"
        f"  ID          : {appointment.appointment_id}\n"
        f"  Booking     : {booking_info}\n"
        f"  Session #   : {appointment.session_number}\n"
        f"  Date        : {appointment.date}\n"
        f"  Time        : {appointment.start_time} - {appointment.end_time}\n"
        f"  Status      : {appointment.status}\n"
        f"  Notes       : {appointment.notes if appointment.notes else 'N/A'}"
    )


@mcp.tool()
def start_appointment(appointment_id: str) -> str:
    """
    เริ่มทำงานใน appointment นี้
    - เปลี่ยน status จาก SCHEDULED → IN_PROGRESS
    
    Args:
        appointment_id: รหัส appointment
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    return _capture(appointment.start)


@mcp.tool()
def complete_appointment(appointment_id: str) -> str:
    """
    ทำ appointment เสร็จแล้ว
    - เปลี่ยน status → COMPLETED
    
    Args:
        appointment_id: รหัส appointment
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    return _capture(appointment.complete)


@mcp.tool()
def cancel_appointment(appointment_id: str, reason: str = "") -> str:
    """
    ยกเลิก appointment
    - เปลี่ยน status → CANCELLED
    
    Args:
        appointment_id: รหัส appointment
        reason: เหตุผลที่ยกเลิก (optional)
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    return _capture(appointment.cancel, reason)


@mcp.tool()
def reschedule_appointment(
    appointment_id: str,
    new_date: str,
    new_start_time: str,
    new_end_time: str
) -> str:
    """
    เลื่อน appointment ใหม่
    - เปลี่ยน status → RESCHEDULED
    
    Args:
        appointment_id: รหัส appointment
        new_date: วันที่ใหม่ (YYYY-MM-DD)
        new_start_time: เวลาเริ่มใหม่ (HH:MM)
        new_end_time: เวลาสิ้นสุดใหม่ (HH:MM)
    """
    from datetime import date
    
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    try:
        new_date_obj = date.fromisoformat(new_date)
    except ValueError:
        return f"❌ รูปแบบวันที่ไม่ถูกต้อง ใช้ YYYY-MM-DD"
    
    return _capture(appointment.reschedule, new_date_obj, new_start_time, new_end_time)


@mcp.tool()
def mark_appointment_no_show(appointment_id: str) -> str:
    """
    ทำเครื่องหมาย appointment ว่าไม่มาตามนัด
    - เปลี่ยน status → NO_SHOW
    
    Args:
        appointment_id: รหัส appointment
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    return _capture(appointment.mark_no_show)


@mcp.tool()
def add_appointment_notes(appointment_id: str, notes: str) -> str:
    """
    เพิ่มบันทึกใน appointment
    
    Args:
        appointment_id: รหัส appointment
        notes: บันทึกที่ต้องการเพิ่ม
    """
    appointment = _get_appointment(appointment_id)
    if isinstance(appointment, str):
        return appointment
    
    return _capture(appointment.add_notes, notes)


@mcp.tool()
def list_all_appointments(status: str = "ALL") -> str:
    """
    ดูรายการ appointments ทั้งหมดในระบบ
    
    Args:
        status: กรองตามสถานะ (ALL/SCHEDULED/IN_PROGRESS/COMPLETED/CANCELLED)
    """
    if not _appointment_list:
        return "ยังไม่มี Appointment ในระบบ"
    
    # กรองตาม status
    if status.upper() == "ALL":
        appointments = _appointment_list
    else:
        appointments = [a for a in _appointment_list if a.status == status.upper()]
    
    if not appointments:
        return f"ไม่มี Appointment ที่มีสถานะ {status}"
    
    lines = [f"📅 Appointments ทั้งหมด ({len(appointments)} รายการ):"]
    
    # จัดกลุ่มตาม booking
    booking_groups = {}
    for appt in appointments:
        if appt.booking_id not in booking_groups:
            booking_groups[appt.booking_id] = []
        booking_groups[appt.booking_id].append(appt)
    
    for booking_id, appts in booking_groups.items():
        booking = _get_booking(booking_id)
        booking_name = booking_id if isinstance(booking, str) else f"{booking_id} ({booking.user_id})"
        
        lines.append(f"\n  📋 Booking: {booking_name}")
        for appt in sorted(appts, key=lambda a: a.session_number):
            emoji = {
                "SCHEDULED": "📅",
                "IN_PROGRESS": "🔄",
                "COMPLETED": "✅",
                "CANCELLED": "❌",
                "RESCHEDULED": "🔄",
                "NO_SHOW": "⚠️"
            }.get(appt.status, "📌")
            
            lines.append(f"    {emoji} {appt.appointment_id} - Session #{appt.session_number}")
            lines.append(f"       Date: {appt.date} | Time: {appt.start_time}-{appt.end_time}")
            lines.append(f"       Status: {appt.status}")
    
    return "\n".join(lines)



# ═══════════════════════════════════════════════
# 💳 PAYMENT TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def create_order(booking_id: str) -> str:
    """
    สร้าง Order จาก Booking
    - 1 Order = 1 Booking (1 design, 1 price)
    - คืน order_id ที่สร้างขึ้น
    
    Args:
        booking_id: รหัส booking
    """
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            order = _system.create_order(booking)
        _order_list.append(order)
        return buf.getvalue() + f"\n✅ order_id = {order.order_id}"
    except Exception as e:
        return f"❌ Error: {e}"



@mcp.tool()
def pay_deposit(
    user_id: str,
    order_id: str,
    promptpay_number: str,
    policy_type: str = "",
    policy_value: float = 0.0
) -> str:
    """
    ชำระมัดจำผ่าน PromptPay
    - policy_type: "percent" หรือ "fixed" (ถ้าว่างจะใช้ policy ของ Artist อัตโนมัติ)
    - policy_value: % หรือจำนวนบาท (ใช้เมื่อระบุ policy_type)
    """
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    if order.status != Order.STATUS_PENDING_PAYMENT:
        return f"❌ Order {order_id} สถานะ {order.status} — ไม่สามารถชำระมัดจำได้"
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            # หา deposit policy: ใช้ที่ระบุมา หรือ fallback ไปใช้ของ artist
            policy = None
            if policy_type.lower() == "percent" and policy_value > 0:
                policy = PercentDepositPolicy(policy_value)
            elif policy_type.lower() == "fixed" and policy_value > 0:
                policy = FixedDepositPolicy(policy_value)
            else:
                # หา artist จาก booking แรกใน order
                for booking in order.bookings:
                    artist = _system.find_artist(booking.artist_id)
                    if artist and artist.deposit_policy:
                        policy = artist.deposit_policy
                        break
            _system.process_payment(user_id, order, method, policy, pay_full=False)
        return buf.getvalue() or "✅ ชำระมัดจำสำเร็จ"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def pay_full(user_id: str, order_id: str, promptpay_number: str) -> str:
    """ชำระเต็มจำนวนที่เหลือผ่าน PromptPay"""
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    if order.status == Order.STATUS_FULLY_PAID:
        return f"❌ Order {order_id} ชำระครบแล้ว ไม่ต้องชำระเพิ่ม"
    if order.status not in (Order.STATUS_PENDING_PAYMENT, Order.STATUS_DEPOSIT_PAID):
        return f"❌ Order {order_id} สถานะ {order.status} — ไม่สามารถชำระได้"
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            _system.process_payment(user_id, order, method, pay_full=True)
        return buf.getvalue() or "✅ ชำระเต็มจำนวนสำเร็จ"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def calculate_deposit(order_id: str, user_type: str = "normal") -> str:
    """
    คำนวณยอดมัดจำของ Order
    - user_type: "normal" หรือ "vip"
    - ใช้ deposit_policy ของ artist อัตโนมัติ (ถ้าตั้งไว้)
    """
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    lines = [f"🧮 Calculate Deposit: {order_id}"]
    total = order.calculate_total()
    lines.append(f"  ราคารวม: {total:.2f} บาท")
    for booking in order.bookings:
        artist = _system.find_artist(booking.artist_id)
        policy = artist.deposit_policy if artist else None
        if policy:
            deposit = policy.calculate_deposit(total)
            lines.append(f"  deposit_policy: {policy}")
        else:
            deposit = total * 0.3
            lines.append(f"  deposit_policy: default 30%")
        lines.append(f"  ยอดมัดจำ ({user_type}): {deposit:.2f} บาท")
        lines.append(f"  ยอดที่เหลือ: {total - deposit:.2f} บาท")
    return "\n".join(lines)


@mcp.tool()
def view_schedule(artist_id: str) -> str:
    """
    ดูตารางนัดหมายของ Artist ในเดือนปัจจุบัน
    """
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"❌ ไม่พบ Artist {artist_id}"
    events = artist.view_schedule()
    if not events:
        return f"📅 Artist {artist_id} ไม่มีนัดหมายในเดือนนี้"
    lines = [f"📅 ตาราง Artist {artist_id} เดือนนี้ ({len(events)} รายการ):"]
    for e in events:
        lines.append(f"  {e.date} — {e.event_name}")
    return "\n".join(lines)


@mcp.tool()
def get_order_info(order_id: str) -> str:
    """ดูข้อมูล Order"""
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    return f"💳 Order Info:\n{order.summary()}"


# ═══════════════════════════════════════════════
# 🏢 STUDIO TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def approve_studio(admin_id: str, request_id: str) -> str:
    """
    Admin อนุมัติ StudioRequest → สร้าง Studio ใหม่
    - ต้องมี request_id จาก request_studio ก่อน
    """
    req = _find_request(request_id)  # ← 🔴 ใช้ helper function
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_approve_studio, admin_id, req)


@mcp.tool()
def reject_studio(admin_id: str, request_id: str) -> str:
    """Admin ปฏิเสธ StudioRequest"""
    req = _find_request(request_id)  # ← 🔴 ใช้ helper function
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_reject_studio, admin_id, req)


# ═══════════════════════════════════════════════
# 🎨 PORTFOLIO & STYLE TOOLS (🔴 เพิ่มใหม่)
# ═══════════════════════════════════════════════

@mcp.tool()
def create_tattoo_style(
    style_id: str,
    name: str,
    description: str = ""
) -> str:
    """
    สร้างสไตล์รอยสักใหม่
    
    Args:
        style_id: รหัสสไตล์ เช่น TS001
        name: ชื่อสไตล์ เช่น Realism, Japanese, Watercolor
        description: คำอธิบายสไตล์
        
    Popular styles: Traditional, Realism, Watercolor, Japanese,
                   Tribal, Geometric, Blackwork, New School,
                   Minimalist, Neo-Traditional
    """
    from entities import TattooStyle
    
    # เช็คว่ามีอยู่แล้วหรือไม่
    if _find_tattoo_style(style_id):
        return f" TattooStyle {style_id} มีอยู่แล้ว"
    
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            style = TattooStyle(style_id, name, description)
            _tattoo_style_list.append(style)
            print(f"[TattooStyle] สร้าง {style.get_summary()} สำเร็จ")
            if style.is_popular():
                print(f" สไตล์ยอดนิยม!")
        return buf.getvalue() or f"สร้าง TattooStyle {style_id} สำเร็จ"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


@mcp.tool()
def list_tattoo_styles() -> str:
    """ดูรายการสไตล์รอยสักทั้งหมด"""
    if not _tattoo_style_list:
        return "ยังไม่มี TattooStyle ในระบบ"
    
    lines = [f"Tattoo Styles ทั้งหมด ({len(_tattoo_style_list)} สไตล์):"]
    for style in _tattoo_style_list:
        lines.append(f"  {style.get_summary()}")
        if style.description:
            lines.append(f"    └─ {style.description}")
    return "\n".join(lines)


@mcp.tool()
def create_portfolio(
    artist_id: str,
    style_id: str = "",
    description: str = ""
) -> str:
    """
    Artist สร้าง Portfolio ผลงานใหม่
    
    Args:
        artist_id: รหัส Artist (ต้อง login แล้ว)
        style_id: รหัสสไตล์หลัก (optional, ถ้าไม่ระบุจะเป็น None)
        description: คำอธิบาย portfolio
        
    Returns:
        portfolio_id ที่สร้างขึ้น
    """
    from entities import Portfolio, TattooStyle
    
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"ไม่พบ Artist {artist_id}"
    
    # ดึงสไตล์ (ถ้ามี)
    style = None
    if style_id:
        style = _find_tattoo_style(style_id)
        if style is None:
            return f"ไม่พบ TattooStyle {style_id}"
    
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            global _portfolio_counter
            _portfolio_counter += 1
            portfolio_id = f"PF-{_portfolio_counter:03d}"
            
            portfolio = Portfolio(
                portfolio_id=portfolio_id,
                owner_id=artist_id,
                style=style,
                description=description
            )
            _portfolio_list.append(portfolio)
            print(f"[Portfolio] {artist.name} สร้าง Portfolio {portfolio_id} สำเร็จ")
            if style:
                print(f"  Style: {style.get_summary()}")
        
        return buf.getvalue() + f"\nportfolio_id = {portfolio_id}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


@mcp.tool()
def add_portfolio_image(
    artist_id: str,
    portfolio_id: str,
    image: str
) -> str:
    """
    เพิ่มรูปภาพเข้า Portfolio
    
    Args:
        artist_id: รหัส Artist (เจ้าของ portfolio)
        portfolio_id: รหัส Portfolio
        image: URL หรือ path ของรูปภาพ
        
    รองรับ: .jpg, .jpeg, .png, .gif, .webp
    สูงสุด: 50 รูปต่อ Portfolio
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    # เช็คว่าเป็นเจ้าของหรือไม่
    if portfolio.owner_id != artist_id:
        return f"คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    return _capture(portfolio.add_image, image)


@mcp.tool()
def remove_portfolio_image(
    artist_id: str,
    portfolio_id: str,
    image: str = "",
    index: int = -1
) -> str:
    """
    ลบรูปภาพจาก Portfolio
    
    Args:
        artist_id: รหัส Artist
        portfolio_id: รหัส Portfolio
        image: URL/path ของรูปที่จะลบ (ใช้อันใดอันหนึ่ง)
        index: ตำแหน่งของรูป (0-based, ใช้อันใดอันหนึ่ง)
        
    ตัวอย่าง:
    - ลบด้วย URL: remove_portfolio_image("A001", "PF-001", image="tattoo.jpg")
    - ลบด้วย index: remove_portfolio_image("A001", "PF-001", index=0)
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if portfolio.owner_id != artist_id:
        return f"คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            if index >= 0:
                portfolio.remove_image_by_index(index)
            elif image:
                portfolio.remove_image(image)
            else:
                return "ต้องระบุ image หรือ index"
        return buf.getvalue() or "ลบรูปภาพสำเร็จ"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


@mcp.tool()
def update_portfolio_description(
    artist_id: str,
    portfolio_id: str,
    description: str
) -> str:
    """
    อัปเดตคำอธิบาย Portfolio
    
    Args:
        artist_id: รหัส Artist
        portfolio_id: รหัส Portfolio
        description: คำอธิบายใหม่
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if portfolio.owner_id != artist_id:
        return f"คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    return _capture(portfolio.update_description, description)


@mcp.tool()
def change_portfolio_style(
    artist_id: str,
    portfolio_id: str,
    style_id: str
) -> str:
    """
    เปลี่ยนสไตล์หลักของ Portfolio
    
    Args:
        artist_id: รหัส Artist
        portfolio_id: รหัส Portfolio
        style_id: รหัสสไตล์ใหม่
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if portfolio.owner_id != artist_id:
        return f"คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    style = _find_tattoo_style(style_id)
    if style is None:
        return f"ไม่พบ TattooStyle {style_id}"
    
    return _capture(portfolio.change_style, style)


@mcp.tool()
def publish_portfolio(artist_id: str, portfolio_id: str) -> str:
    """
    เผยแพร่ Portfolio ให้ทุกคนเห็น
    
    Args:
        artist_id: รหัส Artist
        portfolio_id: รหัส Portfolio
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if portfolio.owner_id != artist_id:
        return f"❌ คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    return _capture(portfolio.publish)


@mcp.tool()
def unpublish_portfolio(artist_id: str, portfolio_id: str) -> str:
    """
    ซ่อน Portfolio (ตั้งเป็น Private)
    
    Args:
        artist_id: รหัส Artist
        portfolio_id: รหัส Portfolio
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if portfolio.owner_id != artist_id:
        return f"คุณไม่ใช่เจ้าของ Portfolio {portfolio_id}"
    
    return _capture(portfolio.unpublish)


@mcp.tool()
def view_portfolio(portfolio_id: str, viewer_id: str = "") -> str:
    """
    ดูข้อมูล Portfolio (จะนับ view ด้วย)
    
    Args:
        portfolio_id: รหัส Portfolio
        viewer_id: รหัสผู้ดู (optional, ใช้นับ analytics)
    """
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    # เช็คว่า public หรือไม่
    if not portfolio.is_public and viewer_id != portfolio.owner_id:
        return f"Portfolio {portfolio_id} ถูกตั้งเป็น Private"
    
    # นับ view (ถ้าไม่ใช่เจ้าของดูเอง)
    if viewer_id != portfolio.owner_id:
        portfolio.increment_view()
    
    lines = [portfolio.get_summary()]
    
    # แสดงรายการรูป
    if not portfolio.is_empty():
        lines.append("\n" + portfolio.list_images())
    else:
        lines.append("\n📷 ยังไม่มีรูปภาพ")
    
    return "\n".join(lines)


@mcp.tool()
def list_artist_portfolios(artist_id: str) -> str:
    """
    ดู Portfolio ทั้งหมดของ Artist
    
    Args:
        artist_id: รหัส Artist
    """
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"ไม่พบ Artist {artist_id}"
    
    # หา portfolio ทั้งหมดของ artist
    portfolios = [p for p in _portfolio_list if p.owner_id == artist_id]
    
    if not portfolios:
        return f"📂 {artist.name} ยังไม่มี Portfolio"
    
    lines = [f"📂 Portfolios ของ {artist.name} ({len(portfolios)} รายการ):"]
    for p in portfolios:
        visibility = "public" if p.is_public else "locked"
        style_name = p.style.name if p.style else "No style"
        lines.append(f"\n  {visibility} {p.portfolio_id} — {style_name}")
        lines.append(f"    Images: {p.image_count}/{p.MAX_IMAGES}")
        lines.append(f"    Views: {p.view_count}")
        if p.description:
            desc = p.description[:60] + "..." if len(p.description) > 60 else p.description
            lines.append(f"    Description: {desc}")
    
    return "\n".join(lines)


@mcp.tool()
def list_all_portfolios(show_private: bool = False) -> str:
    """
    ดู Portfolio ทั้งหมดในระบบ
    
    Args:
        show_private: แสดง private portfolios ด้วยหรือไม่ (default: False)
    """
    if not _portfolio_list:
        return "ยังไม่มี Portfolio ในระบบ"
    
    portfolios = _portfolio_list
    if not show_private:
        portfolios = [p for p in portfolios if p.is_public]
    
    if not portfolios:
        return "ไม่มี Public Portfolio"
    
    lines = [f"Portfolios ทั้งหมด ({len(portfolios)} รายการ):"]
    for p in portfolios:
        visibility = "public" if p.is_public else "locked"
        style_name = p.style.name if p.style else "No style"
        owner = _system.find_artist(p.owner_id)
        owner_name = owner.name if owner else p.owner_id
        
        lines.append(f"\n  {visibility} {p.portfolio_id}")
        lines.append(f"    Artist: {owner_name}")
        lines.append(f"    Style: {style_name}")
        lines.append(f"    Images: {p.image_count} | Views: {p.view_count}")
    
    return "\n".join(lines)



# ═══════════════════════════════════════════════
# 📊 REPORT TOOLS
# ═══════════════════════════════════════════════

@mcp.tool()
def report_bank() -> str:
    """รายงานยอดเงินใน SoonSak Bank"""
    return _capture(_system.report_bank_balance)


@mcp.tool()
def report_artist_rating(artist_id: str) -> str:
    """รายงานคะแนนเฉลี่ยของ Artist"""
    return _capture(_system.report_artist_ratings, artist_id)


@mcp.tool()
def list_all_users() -> str:
    """ดูรายชื่อ User ทั้งหมดในระบบ"""
    users = _system._user_list
    if not users:
        return "ยังไม่มี User ในระบบ"
    lines = [f"👥 Users ทั้งหมด ({len(users)} คน):"]
    for u in users:
        utype = "VIP" if isinstance(u, VIPMember) else "User"
        lines.append(f"  [{u.user_id}] {u.name} | {utype} | status={u.status}")
    return "\n".join(lines)


@mcp.tool()
def list_all_artists() -> str:
    """ดูรายชื่อ Artist ทั้งหมดในระบบ"""
    artists = _system._artist_list
    if not artists:
        return "ยังไม่มี Artist ในระบบ"
    lines = [f"🎨 Artists ทั้งหมด ({len(artists)} คน):"]
    for a in artists:
        avg = a.average_rating()
        lines.append(f"  [{a.staff_id}] {a.name} | status={a.status} | rating={avg:.1f}/5")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
# 💬 MESSAGING TOOLS
# ═══════════════════════════════════════════════

# registry เก็บ mailbox แยกต่างหาก (ใช้ entities.Mailbox)
_mailbox_registry: list = []  # [(user_id, Mailbox), ...]


def _get_or_create_mailbox(user_id: str):
    """หรือสร้าง Mailbox ให้ user_id นั้น"""
    from entities import Mailbox
    for uid, mb in _mailbox_registry:
        if uid == user_id:
            return mb
    mb = Mailbox(user_id)
    _mailbox_registry.append((user_id, mb))
    return mb


@mcp.tool()
def send_message(sender_id: str, receiver_id: str, message: str) -> str:
    """
    ส่งข้อความระหว่าง User / Artist / System
    - sender_id: ID ผู้ส่ง (หรือ SYSTEM)
    - receiver_id: ID ผู้รับ
    - message: ข้อความ
    """
    from entities import Mail
    try:
        sender_mb = _get_or_create_mailbox(sender_id)
        receiver_mb = _get_or_create_mailbox(receiver_id)
        sender_mb.send_message(receiver_mb, message)
        return f"✅ ส่งข้อความจาก {sender_id} → {receiver_id} สำเร็จ\n   💬 \"{message}\""
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
def view_message(user_id: str) -> str:
    """
    ดูกล่องข้อความของ user_id
    - แสดงข้อความทั้งหมดที่ได้รับ
    """
    mb = _get_or_create_mailbox(user_id)
    messages = mb.get_messages()
    if not messages:
        return f"📭 {user_id} ไม่มีข้อความ"
    lines = [f"📬 กล่องข้อความของ {user_id} ({len(messages)} ข้อความ):"]
    for i, mail in enumerate(messages, 1):
        lines.append(f"  [{i}] จาก {mail.sender_id}: {mail.message}")
    return "\n".join(lines)


@mcp.tool()
def system_send_message(receiver_id: str, message: str) -> str:
    """
    ระบบส่งข้อความอัตโนมัติให้ผู้ใช้
    - receiver_id: ID ผู้รับ
    - message: ข้อความแจ้งเตือน
    """
    return send_message("SYSTEM", receiver_id, message)

@mcp.tool()
def reset_system() -> str:
    """รีเซ็ตระบบทั้งหมด — ใช้สำหรับ testing เท่านั้น"""
    global _system, _booking_list, _order_list, _request_list, _mailbox_registry
    global _portfolio_list, _tattoo_style_list, _portfolio_counter, _style_counter
    global _appointment_list  # 🔴 เพิ่มบรรทัดนี้
    
    _system       = SoonSak()
    _booking_list = []
    _order_list   = []
    _request_list = []
    _mailbox_registry = []
    _portfolio_list = []
    _tattoo_style_list = []
    _appointment_list = []  # 🔴 เพิ่มบรรทัดนี้
    _portfolio_counter = 0
    _style_counter = 0
    
    # Seed Admin ใหม่
    _system.register_admin("AD001", "Super Admin", "admin@soonsak.com", "admin123")
    _system._logged_in_users.append("AD001")
    return "✅ ระบบถูกรีเซ็ตแล้ว — พร้อมเทสใหม่"


# ═══════════════════════════════════════════════
# 🏢 STUDIO TOOLS (เพิ่มเติม)
# ═══════════════════════════════════════════════

@mcp.tool()
def list_studio_requests(status: str = "ALL") -> str:
    """
    ดูรายการคำขอเปิด Studio ทั้งหมด
    
    Args:
        status: PENDING / APPROVED / REJECTED / ALL (default: ALL)
    """
    if not _request_list:
        return "ยังไม่มีคำขอเปิด Studio ในระบบ"
    
    # กรองตาม status
    if status.upper() == "ALL":
        requests = _request_list
    else:
        requests = [r for r in _request_list if r.status == status.upper()]
    
    if not requests:
        return f"ไม่มีคำขอที่มีสถานะ {status}"
    
    lines = [f"🏢 Studio Requests ({len(requests)} รายการ):"]
    for req in requests:
        artist = _system.find_artist(req.artist_id)
        artist_name = artist.name if artist else req.artist_id
        
        # เลือก emoji ตาม status
        if req.status == "PENDING":
            emoji = "⏳"
        elif req.status == "APPROVED":
            emoji = "✅"
        else:  # REJECTED
            emoji = "❌"
        
        lines.append(f"\n  {emoji} {req.request_id}")
        lines.append(f"    Artist: {artist_name}")
        lines.append(f"    Studio: {req.studio_name}")
        lines.append(f"    Location: {req.location}")
        lines.append(f"    Status: {req.status}")
    
    return "\n".join(lines)


@mcp.tool()
def view_artist_studio_requests(artist_id: str) -> str:
    """
    Artist ดูคำขอเปิด Studio ของตัวเอง
    
    Args:
        artist_id: รหัส Artist
    """
    artist = _system.find_artist(artist_id)
    if artist is None:
        return f"❌ ไม่พบ Artist {artist_id}"
    
    # หาคำขอทั้งหมดของ artist คนนี้
    requests = [r for r in _request_list if r.artist_id == artist_id]
    
    if not requests:
        return f"📂 {artist.name} ยังไม่เคยส่งคำขอเปิด Studio"
    
    lines = [f"📂 คำขอเปิด Studio ของ {artist.name} ({len(requests)} รายการ):"]
    for req in requests:
        if req.status == "PENDING":
            emoji = "⏳"
        elif req.status == "APPROVED":
            emoji = "✅"
        else:
            emoji = "❌"
        
        lines.append(f"\n  {emoji} {req.request_id}")
        lines.append(f"    Studio: {req.studio_name}")
        lines.append(f"    Location: {req.location}")
        lines.append(f"    Status: {req.status}")
    
    return "\n".join(lines)


@mcp.tool()
def get_studio_request_info(request_id: str) -> str:
    """
    ดูข้อมูลคำขอเปิด Studio
    
    Args:
        request_id: รหัสคำขอ เช่น REQ-001
    """
    req = _find_request(request_id)
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    
    artist = _system.find_artist(req.artist_id)
    artist_name = artist.name if artist else req.artist_id
    
    # หา Studio ที่สร้างจาก request นี้ (ถ้า approved)
    studio_info = ""
    if req.status == "APPROVED":
        for studio in _system._studio_list:
            if studio.name == req.studio_name:
                studio_info = f"\n  ✅ Studio ID: {studio.studio_id} ({studio.status})"
                break
    
    return (
        f"🏢 Studio Request: {request_id}\n"
        f"  Artist       : {artist_name} ({req.artist_id})\n"
        f"  Studio Name  : {req.studio_name}\n"
        f"  Location     : {req.location}\n"
        f"  Status       : {req.status}{studio_info}"
    )


@mcp.tool()
def list_all_studios() -> str:
    """ดูรายการ Studio ทั้งหมดในระบบ"""
    studios = _system._studio_list
    
    if not studios:
        return "ยังไม่มี Studio ในระบบ"
    
    lines = [f"🏢 Studios ทั้งหมด ({len(studios)} แห่ง):"]
    for studio in studios:
        emoji = "🟢" if studio.status == "OPEN" else "🔴"
        lines.append(f"\n  {emoji} {studio.studio_id} — {studio.name}")
        lines.append(f"    Location: {studio.location}")
        lines.append(f"    Status: {studio.status}")
    
    return "\n".join(lines)



if __name__ == "__main__":
    print("สูนเสิดโดนข้าปัก")
    mcp.run()
    base_data()