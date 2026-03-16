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
_system: SoonSak = SoonSak()

# ── Registries — ใช้ list แทน dict ──
_booking_list: list  = []   # เก็บ Booking objects
_order_list: list    = []   # เก็บ Order objects
_request_list: list  = []   # เก็บ StudioRequest objects

# ── Seed Admin AD001 (login ไว้ล่วงหน้า) ──
_admin = _system.register_admin("AD001", "Super Admin", "admin@soonsak.com", "admin123")
_system._logged_in_users.append("AD001")


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
        return f"❌ ไม่พบ Order {order_id} — กรุณาสร้างด้วย create_order ก่อน"
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
    password: str = "1234",
    is_vip: bool = False,
    vip_rank: str = "SILVER"
) -> str:
    """
    ลงทะเบียน User ใหม่เข้าระบบ
    - user_id: รหัส เช่น USR-001
    - password: รหัสผ่าน (default: 1234)
    - is_vip: True = สร้างเป็น VIPMember
    - vip_rank: SILVER / GOLD / PLATINUM (ใช้เมื่อ is_vip=True)
    """
    if is_vip:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                if _system.find_user(user_id):
                    return f"❌ User {user_id} มีอยู่แล้ว"
                vip = VIPMember(user_id, name, email, phone, password, vip_rank)
                _system._user_list.append(vip)
                print(f"[Register] ลงทะเบียน {vip} สำเร็จ (VIP rank={vip_rank})")
            return buf.getvalue() + f"\n✅ Return: {vip}"
        except Exception as e:
            return f"❌ Error: {e}"
    return _capture(_system.register_user, user_id, name, email, phone, password)


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
        return f"❌ ไม่พบ User {user_id}"
    history = user.view_history()
    lines = [f"👤 User Info: {user_id}"]
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
# 🎨 ARTIST TOOLS
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
        return buf.getvalue() + f"\n✅ request_id = {req.request_id}"
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"


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
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            booking = _system.create_booking(
                user_id, artist_id,
                body_part, size, color_tone,
                base_price, reference_image
            )
        _booking_list.append(booking)
        return buf.getvalue() + f"\n✅ booking_id = {booking.booking_id}"
    except Exception as e:
        return f"❌ Error: {type(e).__name__}: {e}"


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
    return f"📋 Booking Info:\n{booking.summary()}"


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
    req = None
    for r in _request_list:
        if r.request_id == request_id:
            req = r
            break
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_approve_studio, admin_id, req)


@mcp.tool()
def reject_studio(admin_id: str, request_id: str) -> str:
    """Admin ปฏิเสธ StudioRequest"""
    req = None
    for r in _request_list:
        if r.request_id == request_id:
            req = r
            break
    if req is None:
        return f"❌ ไม่พบ StudioRequest {request_id}"
    return _capture(_system.admin_reject_studio, admin_id, req)


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
    _system       = SoonSak()
    _booking_list = []
    _order_list   = []
    _request_list = []
    _mailbox_registry = []
    # Seed Admin ใหม่
    _system.register_admin("AD001", "Super Admin", "admin@soonsak.com", "admin123")
    _system._logged_in_users.append("AD001")
    return "✅ ระบบถูกรีเซ็ตแล้ว — พร้อมเทสใหม่"


if __name__ == "__main__":
    print("🚀 SoonSak MCP Server กำลังเริ่มต้น...")
    mcp.run()