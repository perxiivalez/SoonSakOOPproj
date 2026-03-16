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
    name="SoonSak Tattoo Booking System",
    instructions="MCP Server for SoonSak Tattoo Booking System"
)

_trap = io.StringIO()
with redirect_stdout(_trap):
    _system: SoonSak = SoonSak()
    
    _booking_list: list = []
    _order_list: list = []
    _request_list: list = []
    _portfolio_list: list = []
    _tattoo_style_list: list = []
    _appointment_list: list = []
    _mailbox_registry: list = []

_booking_counter = 0
_order_counter = 0
_portfolio_counter = 0
_style_counter = 0

def _capture(fn, *args, **kwargs) -> str:
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            result = fn(*args, **kwargs)
        output = buf.getvalue()
        if result is not None and str(result) not in output:
            output += f"\nReturn: {result}"
        return output.strip() if output.strip() else "Success"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def _find_booking(booking_id: str):
    for b in _booking_list:
        if b.booking_id == booking_id:
            return b
    return None

def _find_order(order_id: str):
    for o in _order_list:
        if o.order_id == order_id:
            return o
    return None

def _find_request(request_id: str):
    for r in _request_list:
        if r.request_id == request_id:
            return r
    return None

def _find_appointment(appointment_id: str):
    for a in _appointment_list:
        if a.appointment_id == appointment_id:
            return a
    return None

def _find_portfolio(portfolio_id: str):
    for p in _portfolio_list:
        if p.portfolio_id == portfolio_id:
            return p
    return None

def _find_tattoo_style(style_id: str):
    for s in _tattoo_style_list:
        if s.style_id == style_id:
            return s
    return None

def _get_or_create_mailbox(user_id: str):
    from entities import Mailbox
    for uid, mb in _mailbox_registry:
        if uid == user_id:
            return mb
    mb = Mailbox(user_id)
    _mailbox_registry.append((user_id, mb))
    return mb


def _get_booking(booking_id: str):
    b = _find_booking(booking_id)
    return b if b else f"Booking {booking_id} not found"

def _get_order(order_id: str):
    o = _find_order(order_id)
    return o if o else f"Order {order_id} not found"

def _get_appointment(appointment_id: str):
    a = _find_appointment(appointment_id)
    return a if a else f"Appointment {appointment_id} not found"

def _get_portfolio(portfolio_id: str):
    p = _find_portfolio(portfolio_id)
    return p if p else f"Portfolio {portfolio_id} not found"


@mcp.tool()
def register_user(user_id: str, name: str, email: str, phone: str, password: str = "1234") -> str:
    return _capture(_system.register_user, user_id, name, email, phone, password)

@mcp.tool()
def register_artist(staff_id: str, name: str, email: str, password: str = "1234", experience: int = 0) -> str:
    return _capture(_system.register_artist, staff_id, name, email, password, experience)

@mcp.tool()
def register_admin(admin_id: str, name: str, email: str, password: str) -> str:
    return _capture(_system.register_admin, admin_id, name, email, password)

@mcp.tool()
def login(user_id: str, password: str) -> str:
    return _capture(_system.login, user_id, password)

@mcp.tool()
def logout(user_id: str) -> str:
    return _capture(_system.logout, user_id)

@mcp.tool()
def get_user_info(user_id: str) -> str:
    user = _system.find_user(user_id)
    if not user:
        return f"User {user_id} not found"
    history = user.view_history()
    return (
        f"User Info: {user_id}\n"
        f"  name        : {user.name}\n"
        f"  email       : {user.email}\n"
        f"  status      : {user.status}\n"
        f"  type        : {'VIPMember' if isinstance(user, VIPMember) else 'User'}\n"
        f"  vip_rank    : {user.rank if isinstance(user, VIPMember) else '-'}\n"
        f"  max_bookings: {user.max_bookings}\n"
        f"  total_spent : {user.total_spent:,.2f} THB\n"
        f"  history     : {len(history)} bookings"
    )

@mcp.tool()
def check_vip_status(user_id: str) -> str:
    user = _system.find_user(user_id)
    if not user:
        return f"User {user_id} not found"
    
    spent = user.total_spent
    lines = [f"Status for {user.name}", f"  Total spent: {spent:,.2f} THB"]
    
    if isinstance(user, VIPMember):
        lines.append(f"  VIP: {user.rank}")
        discount = user.calculate_discount(100)
        lines.append(f"  Discount: {discount:.0f}%")
        if user.rank == "SILVER":
            lines.append(f"  {VIPMember.THRESHOLD_GOLD - spent:,.0f} THB more to GOLD")
        elif user.rank == "GOLD":
            lines.append(f"  {VIPMember.THRESHOLD_PLATINUM - spent:,.0f} THB more to PLATINUM")
        else:
            lines.append(f"  Max rank achieved")
    else:
        lines.append(f"  {VIPMember.THRESHOLD_SILVER - spent:,.0f} THB more to VIP Silver")
    
    return "\n".join(lines)

@mcp.tool()
def list_all_users() -> str:
    users = _system._user_list
    if not users:
        return "No users"
    
    lines = [f"Users ({len(users)} total):"]
    for u in users:
        utype = "VIP" if isinstance(u, VIPMember) else "User"
        lines.append(f"  [{u.user_id}] {u.name} | {utype} | {u.status}")
    return "\n".join(lines)


@mcp.tool()
def approve_artist(admin_id: str, artist_id: str) -> str:
    return _capture(_system.admin_approve_artist, admin_id, artist_id)

@mcp.tool()
def set_deposit_policy(artist_id: str, policy_type: str, value: float) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            if policy_type.lower() == "percent":
                policy = PercentDepositPolicy(percent=value)
            elif policy_type.lower() == "fixed":
                policy = FixedDepositPolicy(fixed_amount=value)
            else:
                return "policy_type must be 'percent' or 'fixed'"
            
            artist.set_deposit_policy(policy)
        return buf.getvalue() or f"Artist {artist_id} set deposit policy: {policy}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_available_days(artist_id: str, days: list[str]) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            parsed = [date.fromisoformat(d) for d in days]
            artist.set_available_days(parsed)
        return buf.getvalue() or f"Artist {artist_id} set {len(parsed)} available days"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def view_available_days(artist_id: str) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    days = artist.view_available_days()
    if not days:
        return "No available days"
    
    result = f"Available Days ({len(days)} days):\n"
    for d in days:
        result += f"  - {d}\n"
    return result.strip()

@mcp.tool()
def get_artist_info(artist_id: str) -> str:
    try:
        return _system.view_artist(artist_id)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def artist_accept_job(artist_id: str, booking_id: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_accept_job, artist_id, booking)

@mcp.tool()
def artist_reject_job(artist_id: str, booking_id: str, reason: str = "") -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_reject_job, artist_id, booking, reason)

@mcp.tool()
def artist_complete_job(artist_id: str, booking_id: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.artist_complete_job, artist_id, booking)

@mcp.tool()
def request_studio(artist_id: str, studio_name: str, location: str) -> str:
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            req = _system.artist_request_studio(artist_id, studio_name, location)
        _request_list.append(req)
        return buf.getvalue() + f"\nrequest_id = {req.request_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_all_artists() -> str:
    artists = _system._artist_list
    if not artists:
        return "No artists"
    
    lines = [f"Artists ({len(artists)} total):"]
    for a in artists:
        avg = a.average_rating()
        lines.append(f"  [{a.staff_id}] {a.name} | {a.status} | {avg:.1f}/5")
    return "\n".join(lines)


@mcp.tool()
def create_booking(
    user_id: str,
    artist_id: str,
    body_part: str,
    size: str,
    color_tone: str,
    base_price: float = 1000.0,
    description: str = "",
    reference_image: str = ""
) -> str:
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            booking = _system.create_booking(
                user_id, artist_id, body_part, size, color_tone,
                base_price, description, reference_image
            )
        _booking_list.append(booking)
        return buf.getvalue() + f"\nbooking_id = {booking.booking_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def cancel_booking(user_id: str, booking_id: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.cancel_booking, user_id, booking)

@mcp.tool()
def get_booking_info(booking_id: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    summary = f"Booking Info:\n{booking.summary()}"
    if booking.appointment_count > 0:
        summary += f"\n\n{booking.list_appointments()}"
    else:
        summary += "\n\nNo appointments"
    return summary

@mcp.tool()
def rate_artist(user_id: str, artist_id: str, booking_id: str, score: int, comment: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    return _capture(_system.rate_artist, user_id, artist_id, booking, score, comment)


@mcp.tool()
def add_appointment(
    user_id: str,
    booking_id: str,
    appointment_date: str,
    start_time: str = "10:00",
    end_time: str = "18:00"
) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    try:
        appt_date = date.fromisoformat(appointment_date)
        buf = io.StringIO()
        with redirect_stdout(buf):
            appointment = _system.add_appointment(user_id, booking, appt_date, start_time, end_time)
        _appointment_list.append(appointment)
        return buf.getvalue() + f"\nappointment_id = {appointment.appointment_id}"
    except ValueError:
        return "Invalid date format, use YYYY-MM-DD"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_booking_appointments(booking_id: str) -> str:
    booking = _get_booking(booking_id)
    return booking.list_appointments() if not isinstance(booking, str) else booking

@mcp.tool()
def get_appointment_info(appointment_id: str) -> str:
    appt = _get_appointment(appointment_id)
    if isinstance(appt, str):
        return appt
    
    booking = _get_booking(appt.booking_id)
    booking_info = appt.booking_id if isinstance(booking, str) else f"{booking.booking_id} ({booking.body_part})"
    
    return (
        f"Appointment Info\n"
        f"  ID       : {appt.appointment_id}\n"
        f"  Booking  : {booking_info}\n"
        f"  Session  : #{appt.session_number}\n"
        f"  Date     : {appt.date}\n"
        f"  Time     : {appt.start_time} - {appt.end_time}\n"
        f"  Status   : {appt.status}\n"
        f"  Notes    : {appt.notes or 'N/A'}"
    )

@mcp.tool()
def start_appointment(appointment_id: str) -> str:
    appt = _get_appointment(appointment_id)
    return _capture(appt.start) if not isinstance(appt, str) else appt

@mcp.tool()
def complete_appointment(appointment_id: str) -> str:
    appt = _get_appointment(appointment_id)
    return _capture(appt.complete) if not isinstance(appt, str) else appt

@mcp.tool()
def cancel_appointment(appointment_id: str, reason: str = "") -> str:
    appt = _get_appointment(appointment_id)
    return _capture(appt.cancel, reason) if not isinstance(appt, str) else appt

@mcp.tool()
def reschedule_appointment(appointment_id: str, new_date: str, new_start_time: str, new_end_time: str) -> str:
    appt = _get_appointment(appointment_id)
    if isinstance(appt, str):
        return appt
    try:
        new_date_obj = date.fromisoformat(new_date)
        return _capture(appt.reschedule, new_date_obj, new_start_time, new_end_time)
    except ValueError:
        return "Invalid date format"

@mcp.tool()
def mark_appointment_no_show(appointment_id: str) -> str:
    appt = _get_appointment(appointment_id)
    return _capture(appt.mark_no_show) if not isinstance(appt, str) else appt

@mcp.tool()
def add_appointment_notes(appointment_id: str, notes: str) -> str:
    appt = _get_appointment(appointment_id)
    return _capture(appt.add_notes, notes) if not isinstance(appt, str) else appt

@mcp.tool()
def list_all_appointments(status: str = "ALL") -> str:
    if not _appointment_list:
        return "No appointments"
    
    appointments = _appointment_list if status.upper() == "ALL" else [a for a in _appointment_list if a.status == status.upper()]
    
    if not appointments:
        return f"No appointments with status {status}"
    
    lines = [f"Appointments ({len(appointments)} total):"]
    
    booking_groups = {}
    for appt in appointments:
        if appt.booking_id not in booking_groups:
            booking_groups[appt.booking_id] = []
        booking_groups[appt.booking_id].append(appt)
    
    for booking_id, appts in booking_groups.items():
        booking = _get_booking(booking_id)
        booking_name = booking_id if isinstance(booking, str) else f"{booking_id} ({booking.user_id})"
        lines.append(f"\n  Booking: {booking_name}")
        
        for appt in sorted(appts, key=lambda a: a.session_number):
            lines.append(f"    {appt.appointment_id} - Session #{appt.session_number}")
            lines.append(f"       {appt.date} | {appt.start_time}-{appt.end_time} | {appt.status}")
    
    return "\n".join(lines)


@mcp.tool()
def create_order(booking_id: str) -> str:
    booking = _get_booking(booking_id)
    if isinstance(booking, str):
        return booking
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            order = _system.create_order(booking)
        _order_list.append(order)
        return buf.getvalue() + f"\norder_id = {order.order_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def pay_deposit(user_id: str, order_id: str, promptpay_number: str, policy_type: str = "", policy_value: float = 0.0) -> str:
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    if order.status != Order.STATUS_PENDING_PAYMENT:
        return f"Order {order_id} status is {order.status}"
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            
            policy = None
            if policy_type.lower() == "percent" and policy_value > 0:
                policy = PercentDepositPolicy(policy_value)
            elif policy_type.lower() == "fixed" and policy_value > 0:
                policy = FixedDepositPolicy(policy_value)
            else:
                booking = order.booking
                artist = _system.find_artist(booking.artist_id)
                if artist and artist.deposit_policy:
                    policy = artist.deposit_policy
            
            _system.process_payment(user_id, order, method, policy, pay_full=False)
        
        return buf.getvalue() or "Deposit payment successful"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def pay_full(user_id: str, order_id: str, promptpay_number: str) -> str:
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    if order.status == Order.STATUS_FULLY_PAID:
        return f"Order {order_id} already fully paid"
    if order.status not in (Order.STATUS_PENDING_PAYMENT, Order.STATUS_DEPOSIT_PAID):
        return f"Order {order_id} status is {order.status}"
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            method = Promptpay(phone_or_id=promptpay_number)
            _system.process_payment(user_id, order, method, pay_full=True)
        return buf.getvalue() or "Full payment successful"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def calculate_deposit(order_id: str, user_type: str = "normal") -> str:
    order = _get_order(order_id)
    if isinstance(order, str):
        return order
    
    total = order.calculate_total()
    booking = order.booking
    artist = _system.find_artist(booking.artist_id)
    policy = artist.deposit_policy if artist else None
    
    if policy:
        buf = io.StringIO()
        with redirect_stdout(buf):
            deposit = policy.calculate_deposit(total)
        policy_str = buf.getvalue().strip() or str(policy)
    else:
        deposit = total * 0.3
        policy_str = "default 30%"
    
    return (
        f"Calculate Deposit: {order_id}\n"
        f"  Total      : {total:.2f} THB\n"
        f"  Policy     : {policy_str}\n"
        f"  Deposit    : {deposit:.2f} THB\n"
        f"  Remaining  : {total - deposit:.2f} THB"
    )

@mcp.tool()
def get_order_info(order_id: str) -> str:
    order = _get_order(order_id)
    return f"Order Info:\n{order.summary()}" if not isinstance(order, str) else order

@mcp.tool()
def view_schedule(artist_id: str) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    events = artist.view_schedule()
    if not events:
        return f"Artist {artist_id} has no appointments this month"
    
    lines = [f"Artist {artist_id} Schedule ({len(events)} events):"]
    for e in events:
        lines.append(f"  {e.date} - {e.event_name}")
    return "\n".join(lines)


@mcp.tool()
def approve_studio(admin_id: str, request_id: str) -> str:
    req = _find_request(request_id)
    if not req:
        return f"StudioRequest {request_id} not found"
    return _capture(_system.admin_approve_studio, admin_id, req)

@mcp.tool()
def reject_studio(admin_id: str, request_id: str) -> str:
    req = _find_request(request_id)
    if not req:
        return f"StudioRequest {request_id} not found"
    return _capture(_system.admin_reject_studio, admin_id, req)

@mcp.tool()
def list_studio_requests(status: str = "ALL") -> str:
    if not _request_list:
        return "No studio requests"
    
    requests = _request_list if status.upper() == "ALL" else [r for r in _request_list if r.status == status.upper()]
    
    if not requests:
        return f"No requests with status {status}"
    
    lines = [f"Studio Requests ({len(requests)} total):"]
    for req in requests:
        artist = _system.find_artist(req.artist_id)
        artist_name = artist.name if artist else req.artist_id
        lines.append(f"\n  {req.request_id}")
        lines.append(f"    Artist: {artist_name}")
        lines.append(f"    Studio: {req.studio_name} @ {req.location}")
        lines.append(f"    Status: {req.status}")
    
    return "\n".join(lines)

@mcp.tool()
def view_artist_studio_requests(artist_id: str) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    requests = [r for r in _request_list if r.artist_id == artist_id]
    
    if not requests:
        return f"{artist.name} has no studio requests"
    
    lines = [f"Studio Requests by {artist.name} ({len(requests)} total):"]
    for req in requests:
        lines.append(f"\n  {req.request_id}")
        lines.append(f"    Studio: {req.studio_name}")
        lines.append(f"    Location: {req.location}")
        lines.append(f"    Status: {req.status}")
    
    return "\n".join(lines)

@mcp.tool()
def get_studio_request_info(request_id: str) -> str:
    req = _find_request(request_id)
    if not req:
        return f"StudioRequest {request_id} not found"
    
    artist = _system.find_artist(req.artist_id)
    artist_name = artist.name if artist else req.artist_id
    
    studio_info = ""
    if req.status == "APPROVED":
        for studio in _system._studio_list:
            if studio.name == req.studio_name:
                studio_info = f"\n  Studio ID: {studio.studio_id} ({studio.status})"
                break
    
    return (
        f"Studio Request: {request_id}\n"
        f"  Artist       : {artist_name} ({req.artist_id})\n"
        f"  Studio Name  : {req.studio_name}\n"
        f"  Location     : {req.location}\n"
        f"  Status       : {req.status}{studio_info}"
    )

@mcp.tool()
def list_all_studios() -> str:
    studios = _system._studio_list
    if not studios:
        return "No studios"
    
    lines = [f"Studios ({len(studios)} total):"]
    for studio in studios:
        lines.append(f"\n  {studio.studio_id} - {studio.name}")
        lines.append(f"    Location: {studio.location}")
        lines.append(f"    Status: {studio.status}")
    
    return "\n".join(lines)


@mcp.tool()
def create_tattoo_style(style_id: str, name: str, description: str = "") -> str:
    if _find_tattoo_style(style_id):
        return f"TattooStyle {style_id} already exists"
    
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            style = TattooStyle(style_id, name, description)
            _tattoo_style_list.append(style)
        return buf.getvalue() or f"Created TattooStyle {style_id}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_tattoo_styles() -> str:
    if not _tattoo_style_list:
        return "No tattoo styles"
    
    lines = [f"Tattoo Styles ({len(_tattoo_style_list)} total):"]
    for style in _tattoo_style_list:
        lines.append(f"  {style.get_summary()}")
        if style.description:
            lines.append(f"    {style.description}")
    return "\n".join(lines)

@mcp.tool()
def create_portfolio(artist_id: str, style_id: str = "", description: str = "") -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    style = _find_tattoo_style(style_id) if style_id else None
    if style_id and not style:
        return f"TattooStyle {style_id} not found"
    
    try:
        global _portfolio_counter
        _portfolio_counter += 1
        portfolio_id = f"PF-{_portfolio_counter:03d}"
        
        portfolio = Portfolio(portfolio_id=portfolio_id, owner_id=artist_id, style=style, description=description)
        _portfolio_list.append(portfolio)
        
        return f"Created Portfolio {portfolio_id}\n  Artist: {artist.name}\n  Style: {style.name if style else 'None'}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def add_portfolio_image(artist_id: str, portfolio_id: str, image: str) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    return _capture(portfolio.add_image, image)

@mcp.tool()
def remove_portfolio_image(artist_id: str, portfolio_id: str, image: str = "", index: int = -1) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    try:
        if index >= 0:
            return _capture(portfolio.remove_image_by_index, index)
        elif image:
            return _capture(portfolio.remove_image, image)
        else:
            return "Must specify image or index"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def update_portfolio_description(artist_id: str, portfolio_id: str, description: str) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    return _capture(portfolio.update_description, description)

@mcp.tool()
def change_portfolio_style(artist_id: str, portfolio_id: str, style_id: str) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    style = _find_tattoo_style(style_id)
    if not style:
        return f"TattooStyle {style_id} not found"
    
    return _capture(portfolio.change_style, style)

@mcp.tool()
def publish_portfolio(artist_id: str, portfolio_id: str) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    return _capture(portfolio.publish)

@mcp.tool()
def unpublish_portfolio(artist_id: str, portfolio_id: str) -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    if portfolio.owner_id != artist_id:
        return f"You are not the owner of Portfolio {portfolio_id}"
    
    return _capture(portfolio.unpublish)

@mcp.tool()
def view_portfolio(portfolio_id: str, viewer_id: str = "") -> str:
    portfolio = _get_portfolio(portfolio_id)
    if isinstance(portfolio, str):
        return portfolio
    
    if not portfolio.is_public and viewer_id != portfolio.owner_id:
        return f"Portfolio {portfolio_id} is private"
    
    if viewer_id != portfolio.owner_id:
        portfolio.increment_view()
    
    lines = [portfolio.get_summary()]
    if not portfolio.is_empty():
        lines.append("\n" + portfolio.list_images())
    else:
        lines.append("\nNo images")
    
    return "\n".join(lines)

@mcp.tool()
def list_artist_portfolios(artist_id: str) -> str:
    artist = _system.find_artist(artist_id)
    if not artist:
        return f"Artist {artist_id} not found"
    
    portfolios = [p for p in _portfolio_list if p.owner_id == artist_id]
    if not portfolios:
        return f"{artist.name} has no portfolios"
    
    lines = [f"Portfolios by {artist.name} ({len(portfolios)} total):"]
    for p in portfolios:
        visibility = "Public" if p.is_public else "Private"
        style_name = p.style.name if p.style else "No style"
        lines.append(f"\n  [{visibility}] {p.portfolio_id} - {style_name}")
        lines.append(f"    Images: {p.image_count}/{p.MAX_IMAGES} | Views: {p.view_count}")
        if p.description:
            desc = p.description[:50] + "..." if len(p.description) > 50 else p.description
            lines.append(f"    Description: {desc}")
    
    return "\n".join(lines)

@mcp.tool()
def list_all_portfolios(show_private: bool = False) -> str:
    if not _portfolio_list:
        return "No portfolios"
    
    portfolios = _portfolio_list if show_private else [p for p in _portfolio_list if p.is_public]
    
    if not portfolios:
        return "No public portfolios"
    
    lines = [f"Portfolios ({len(portfolios)} total):"]
    for p in portfolios:
        visibility = "Public" if p.is_public else "Private"
        style_name = p.style.name if p.style else "No style"
        owner = _system.find_artist(p.owner_id)
        owner_name = owner.name if owner else p.owner_id
        
        lines.append(f"\n  [{visibility}] {p.portfolio_id}")
        lines.append(f"    Artist: {owner_name} | Style: {style_name}")
        lines.append(f"    Images: {p.image_count} | Views: {p.view_count}")
    
    return "\n".join(lines)


@mcp.tool()
def send_message(sender_id: str, receiver_id: str, message: str) -> str:
    try:
        sender_mb = _get_or_create_mailbox(sender_id)
        receiver_mb = _get_or_create_mailbox(receiver_id)
        sender_mb.send_message(receiver_mb, message)
        return f"Message sent from {sender_id} to {receiver_id}\n\"{message}\""
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def view_messages(user_id: str) -> str:
    mb = _get_or_create_mailbox(user_id)
    messages = mb.get_messages()
    if not messages:
        return f"{user_id} has no messages"
    
    lines = [f"Messages for {user_id} ({len(messages)} total):"]
    for i, mail in enumerate(messages, 1):
        lines.append(f"  [{i}] from {mail.sender_id}: {mail.message}")
    return "\n".join(lines)

@mcp.tool()
def system_send_message(receiver_id: str, message: str) -> str:
    return send_message("SYSTEM", receiver_id, message)


@mcp.tool()
def suspend_user(admin_id: str, user_id: str) -> str:
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
    try:
        expired = date(expired_year, expired_month, expired_day)
        return _capture(_system.admin_add_coupon, admin_id, user_id, coupon_code, discount, expired)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def report_bank() -> str:
    return _capture(_system.report_bank_balance)

@mcp.tool()
def report_artist_rating(artist_id: str) -> str:
    return _capture(_system.report_artist_ratings, artist_id)


@mcp.tool()
def reset_system() -> str:
    global _system, _booking_list, _order_list, _request_list, _mailbox_registry
    global _portfolio_list, _tattoo_style_list, _appointment_list, _portfolio_counter, _style_counter
    
    _trap_local = io.StringIO()
    with redirect_stdout(_trap_local):
        _system = SoonSak()
        _booking_list = []
        _order_list = []
        _request_list = []
        _mailbox_registry = []
        _portfolio_list = []
        _tattoo_style_list = []
        _appointment_list = []
        _portfolio_counter = 0
        _style_counter = 0
    
    return "System reset successfully"

@mcp.tool()
def initialize_demo_data() -> str:
    try:
        results = []
        
        _trap_local = io.StringIO()
        with redirect_stdout(_trap_local):
            _system.register_admin("AD001", "Admin Demo", "admin@soonsak.com", "1234")
            _system.login("AD001", "1234")
            results.append("Created Admin: AD001")
            
            _system.register_user("U001", "User Demo", "user@soonsak.com", "081-234-5678", "1234")
            _system.login("U001", "1234")
            results.append("Created User: U001")
            
            _system.register_artist("A001", "Artist One", "artist@soonsak.com", "1234", experience=5)
            _system.login("A001", "1234")
            results.append("Created Artist: A001")
            
            _system.admin_approve_artist("AD001", "A001")
            results.append("Approved Artist: A001")
            
            artist = _system.find_artist("A001")
            policy = FixedDepositPolicy(fixed_amount=500.0)
            artist.set_deposit_policy(policy)
            results.append("Set deposit policy: 500 THB")
            
            artist.set_available_days([
                date(2026, 3, 20), date(2026, 3, 21),
                date(2026, 3, 22), date(2026, 3, 23)
            ])
            results.append("Set available days: 4 days")
            
            studio = Studio("S001", "SoonSak Studio", "Bangkok")
            _system._studio_list.append(studio)
            studio.open_studio()
            results.append("Created Studio: S001")
            
            _system.admin_add_coupon("AD001", "U001", "WELCOME10", 10.0, date(2026, 12, 31))
            results.append("Added Coupon: WELCOME10")
            
            style = TattooStyle("TS001", "Japanese", "Traditional Japanese tattoo style")
            _tattoo_style_list.append(style)
            results.append("Created TattooStyle: Japanese")
        
        return "Demo data initialized successfully\n\n" + "\n".join(results) + "\n\n" + \
               "Available accounts:\n" + \
               "  - User: U001 (password: 1234)\n" + \
               "  - Artist: A001 (password: 1234)\n" + \
               "  - Admin: AD001 (password: 1234)"
        
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import sys
    
    print("Starting SoonSak MCP Server...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("  SoonSak Tattoo Booking System", file=sys.stderr)
    print("  MCP Server Ready", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    mcp.run()
