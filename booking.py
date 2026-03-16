"""
booking.py — Appointment, Booking, Order
- ทุก attribute เป็น private (__attr)
- ไม่ใช้ Dict เลย ใช้ list ทั้งหมด
"""

from datetime import datetime, date


class Appointment:
    """
    การนัดหมายแต่ละครั้ง (1 Booking มีได้หลาย Appointments)
    
    Status Flow:
    SCHEDULED → IN_PROGRESS → COMPLETED
              → CANCELLED
              → RESCHEDULED → SCHEDULED
              → NO_SHOW
    """
    
    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_RESCHEDULED = "RESCHEDULED"
    STATUS_NO_SHOW = "NO_SHOW"
    
    def __init__(self, appointment_id: str, booking_id: str,
                 session_number: int,
                 appointment_date: date, start_time: str, end_time: str):
        self.__appointment_id = appointment_id
        self.__booking_id = booking_id
        self.__session_number = session_number
        self.__date = appointment_date
        self.__start_time = start_time
        self.__end_time = end_time
        self.__status = self.STATUS_SCHEDULED
        self.__notes = ""
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()

    @property
    def appointment_id(self): return self.__appointment_id

    @property
    def booking_id(self): return self.__booking_id
    
    @property
    def session_number(self): return self.__session_number

    @property
    def date(self): return self.__date
    
    @property
    def start_time(self): return self.__start_time
    
    @property
    def end_time(self): return self.__end_time
    
    @property
    def status(self): return self.__status
    
    @property
    def notes(self): return self.__notes
    
    @notes.setter
    def notes(self, value: str):
        self.__notes = value.strip() if value else ""
        self.__touch()
    
    def start(self) -> None:
        if self.__status != self.STATUS_SCHEDULED:
            raise Exception("เริ่มได้เฉพาะ SCHEDULED เท่านั้น")
        self.__status = self.STATUS_IN_PROGRESS
        self.__touch()
        print(f"[Appointment] {self.__appointment_id} เริ่มทำงานแล้ว")
    
    def complete(self) -> None:
        if self.__status not in (self.STATUS_SCHEDULED, self.STATUS_IN_PROGRESS):
            raise Exception("complete ได้เฉพาะ SCHEDULED หรือ IN_PROGRESS")
        self.__status = self.STATUS_COMPLETED
        self.__touch()
        print(f"[Appointment] {self.__appointment_id} เสร็จสมบูรณ์")
    
    def cancel(self, reason: str = "") -> None:
        if self.__status in (self.STATUS_COMPLETED, self.STATUS_NO_SHOW):
            raise Exception("ยกเลิกไม่ได้แล้ว")
        self.__status = self.STATUS_CANCELLED
        if reason:
            self.__notes = f"[Cancelled] {reason}"
        self.__touch()
        print(f"[Appointment] {self.__appointment_id} ถูกยกเลิก")
    
    def reschedule(self, new_date: date, new_start_time: str, new_end_time: str) -> None:
        if self.__status in (self.STATUS_COMPLETED, self.STATUS_CANCELLED):
            raise Exception("เลื่อนนัดไม่ได้แล้ว")
        old_date = self.__date
        self.__date = new_date
        self.__start_time = new_start_time
        self.__end_time = new_end_time
        self.__status = self.STATUS_RESCHEDULED
        self.__notes = f"Rescheduled from {old_date} to {new_date}"
        self.__touch()
        print(f"[Appointment] {self.__appointment_id} เลื่อนนัดจาก {old_date} → {new_date}")
    
    def mark_no_show(self) -> None:
        self.__status = self.STATUS_NO_SHOW
        self.__touch()
        print(f"[Appointment] {self.__appointment_id} ไม่มาตามนัด")
    
    def add_notes(self, notes: str) -> None:
        self.__notes = f"{self.__notes}\n{notes}".strip()
        self.__touch()
    
    def __touch(self) -> None:
        self.__updated_at = datetime.now()
    
    def get_summary(self) -> str:
        emoji = {
            self.STATUS_SCHEDULED: "📅",
            self.STATUS_IN_PROGRESS: "🔄",
            self.STATUS_COMPLETED: "✅",
            self.STATUS_CANCELLED: "❌",
            self.STATUS_RESCHEDULED: "🔄",
            self.STATUS_NO_SHOW: "⚠️"
        }.get(self.__status, "📌")
        
        return (
            f"{emoji} Session #{self.__session_number} ({self.__appointment_id})\n"
            f"  Date   : {self.__date}\n"
            f"  Time   : {self.__start_time} - {self.__end_time}\n"
            f"  Status : {self.__status}\n"
            f"  Notes  : {self.__notes if self.__notes else 'N/A'}"
        )

    def __repr__(self):
        return f"<Appointment id={self.__appointment_id} #{self.__session_number} date={self.__date} status={self.__status}>"


class Booking:
    """
    Booking สำหรับรอยสักหนึ่งชิ้น
    - 1 Booking = 1 design (มี size, body_part, color_tone, price)
    - 1 Booking → Multiple Appointments (สักหลายวัน)
    
    Status: WAITING → ACCEPTED → IN_PROGRESS → COMPLETED / CANCELLED / NO_SHOW
    """

    STATUS_WAITING   = "WAITING"
    STATUS_ACCEPTED  = "ACCEPTED"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NO_SHOW   = "NO_SHOW"

    def __init__(self, booking_id: str, user_id: str, artist_id: str,
                 body_part: str, size: str, color_tone: str,
                 base_price: float, 
                 description: str = "",
                 reference_image: str = ""):
        if not booking_id.startswith("BKG-"):
            raise ValueError("booking_id ต้องขึ้นต้นด้วย BKG-")
        if base_price < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")

        self.__booking_id = booking_id
        self.__user_id = user_id
        self.__artist_id = artist_id
        self.__body_part = body_part
        self.__size = size
        self.__color_tone = color_tone
        self.__base_price = base_price
        self.__description = description
        self.__reference_image = reference_image
        self.__status = self.STATUS_WAITING
        self.__appointment_list: list = []
        self.__created_at = datetime.now()

    @property
    def booking_id(self): return self.__booking_id

    @property
    def user_id(self): return self.__user_id

    @property
    def artist_id(self): return self.__artist_id

    @property
    def status(self): return self.__status

    @property
    def base_price(self): return self.__base_price
    
    @property
    def description(self): return self.__description
    
    @property
    def body_part(self): return self.__body_part
    
    @property
    def size(self): return self.__size
    
    @property
    def color_tone(self): return self.__color_tone
    
    @property
    def appointments(self) -> list:
        return list(self.__appointment_list)
    
    @property
    def appointment_count(self) -> int:
        return len(self.__appointment_list)
    
    @property
    def completed_appointments(self) -> list:
        return [a for a in self.__appointment_list if a.status == Appointment.STATUS_COMPLETED]

    def accept(self):
        if self.__status != self.STATUS_WAITING:
            raise Exception("รับงานได้เฉพาะ WAITING เท่านั้น")
        self.__status = self.STATUS_ACCEPTED
        print(f"[Booking] {self.__booking_id} ถูก accept แล้ว")

    def cancel(self):
        if self.__status in (self.STATUS_COMPLETED, self.STATUS_NO_SHOW):
            raise Exception("ยกเลิกไม่ได้")
        self.__status = self.STATUS_CANCELLED
        for appt in self.__appointment_list:
            if appt.status not in (Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED):
                appt.cancel("Booking cancelled")
        print(f"[Booking] {self.__booking_id} ถูกยกเลิกแล้ว")
    
    def start(self):
        if self.__status != self.STATUS_ACCEPTED:
            raise Exception("ต้อง ACCEPTED ก่อน start")
        self.__status = self.STATUS_IN_PROGRESS
        print(f"[Booking] {self.__booking_id} เริ่มทำงานแล้ว")

    def complete(self):
        if self.__status not in (self.STATUS_ACCEPTED, self.STATUS_IN_PROGRESS):
            raise Exception("ต้อง ACCEPTED หรือ IN_PROGRESS ก่อน complete")
        
        pending_appts = [a for a in self.__appointment_list 
                        if a.status not in (Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED)]
        if pending_appts:
            raise Exception(f"ยังมี appointment ที่ยังไม่เสร็จ: {len(pending_appts)} appointments")
        
        self.__status = self.STATUS_COMPLETED
        print(f"[Booking] {self.__booking_id} เสร็จสมบูรณ์")

    def no_show(self):
        self.__status = self.STATUS_NO_SHOW
        print(f"[Booking] {self.__booking_id} ไม่มาตามนัด")

    def set_price(self, price: float):
        if price < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")
        self.__base_price = price
        print(f"[Booking] กำหนดราคา {price:.2f} บาท")

    def add_appointment(self, appointment: Appointment):
        if not isinstance(appointment, Appointment):
            raise TypeError("appointment ต้องเป็น Appointment object")
        if appointment.booking_id != self.__booking_id:
            raise ValueError(f"Appointment {appointment.appointment_id} ไม่ได้สังกัด Booking {self.__booking_id}")
        self.__appointment_list.append(appointment)
        print(f"[Booking] เพิ่ม Appointment #{appointment.session_number} เข้า {self.__booking_id}")
    
    def remove_appointment(self, appointment_id: str):
        appt = self.get_appointment_by_id(appointment_id)
        if appt is None:
            raise ValueError(f"ไม่พบ Appointment {appointment_id}")
        self.__appointment_list.remove(appt)
        print(f"[Booking] ลบ Appointment {appointment_id} ออกจาก {self.__booking_id}")
    
    def get_appointment_by_id(self, appointment_id: str):
        for appt in self.__appointment_list:
            if appt.appointment_id == appointment_id:
                return appt
        return None
    
    def get_appointment_by_session(self, session_number: int):
        for appt in self.__appointment_list:
            if appt.session_number == session_number:
                return appt
        return None
    
    def list_appointments(self) -> str:
        if not self.__appointment_list:
            return "📅 ยังไม่มี appointment"
        
        lines = [f"📅 Appointments ({len(self.__appointment_list)} sessions):"]
        for appt in sorted(self.__appointment_list, key=lambda a: a.session_number):
            lines.append(f"\n{appt.get_summary()}")
        return "\n".join(lines)

    def summary(self) -> str:
        progress = len(self.completed_appointments) / len(self.__appointment_list) * 100 if self.__appointment_list else 0
        
        return (
            f"booking_id      : {self.__booking_id}\n"
            f"user_id         : {self.__user_id}\n"
            f"artist_id       : {self.__artist_id}\n"
            f"body_part       : {self.__body_part}\n"
            f"size            : {self.__size}\n"
            f"color_tone      : {self.__color_tone}\n"
            f"description     : {self.__description}\n"
            f"base_price      : {self.__base_price:.2f} บาท\n"
            f"status          : {self.__status}\n"
            f"appointments    : {len(self.__appointment_list)} total ({len(self.completed_appointments)} completed)\n"
            f"progress        : {progress:.1f}%"
        )

    def __repr__(self):
        return f"<Booking id={self.__booking_id} appointments={self.appointment_count} status={self.__status} price={self.__base_price}>"


class Order:
    """
    Order สำหรับรอยสักหนึ่งชิ้น
    - 1 Order = 1 Booking (1 design, 1 price)
    - 1 Booking → Multiple Appointments
    
    Status: PENDING_PAYMENT → DEPOSIT_PAID → FULLY_PAID → CLOSED / REFUNDED
    """

    STATUS_PENDING_PAYMENT = "PENDING_PAYMENT"
    STATUS_DEPOSIT_PAID    = "DEPOSIT_PAID"
    STATUS_FULLY_PAID      = "FULLY_PAID"
    STATUS_CLOSED          = "CLOSED"
    STATUS_REFUNDED        = "REFUNDED"

    def __init__(self, order_id: str, booking: 'Booking'):
        if not order_id.startswith("ORD-"):
            raise ValueError("order_id ต้องขึ้นต้นด้วย ORD-")
        if not isinstance(booking, Booking):
            raise TypeError("booking ต้องเป็น Booking object")
        
        self.__order_id = order_id
        self.__booking = booking
        self.__deposit_amount: float = 0.0
        self.__full_price_amount: float = booking.base_price
        self.__paid_amount: float = 0.0
        self.__status = self.STATUS_PENDING_PAYMENT
        self.__created_at = datetime.now()

    @property
    def order_id(self): return self.__order_id

    @property
    def status(self): return self.__status

    @property
    def deposit_amount(self): return self.__deposit_amount

    @property
    def full_price_amount(self): return self.__full_price_amount
    
    @property
    def paid_amount(self): return self.__paid_amount
    
    @property
    def remaining_amount(self) -> float:
        return max(0, self.__full_price_amount - self.__paid_amount)

    @property
    def booking(self) -> 'Booking':
        return self.__booking

    def calculate_total(self) -> float:
        return self.__booking.base_price

    def order_phase(self):
        phases = {
            self.STATUS_PENDING_PAYMENT: "รอชำระมัดจำ",
            self.STATUS_DEPOSIT_PAID:    "ชำระมัดจำแล้ว รอชำระส่วนที่เหลือ",
            self.STATUS_FULLY_PAID:      "ชำระครบแล้ว",
            self.STATUS_CLOSED:          "ปิด Order แล้ว",
            self.STATUS_REFUNDED:        "คืนเงินแล้ว",
        }
        phase = phases.get(self.__status, "ไม่ทราบสถานะ")
        print(f"[Order] {self.__order_id} → {phase}")
        return self.__status

    def pay_deposit(self, amount: float):
        self.__deposit_amount = amount
        self.__paid_amount += amount
        self.__status = self.STATUS_DEPOSIT_PAID
        print(f"[Order] ชำระมัดจำ {amount:.2f} บาท สำเร็จ")

    def pay_full(self):
        remaining = self.__full_price_amount - self.__paid_amount
        self.__paid_amount = self.__full_price_amount
        self.__status = self.STATUS_FULLY_PAID
        print(f"[Order] ชำระเต็มจำนวนแล้ว (จ่ายเพิ่ม {remaining:.2f} บาท)")

    def close(self):
        self.__status = self.STATUS_CLOSED
        print(f"[Order] {self.__order_id} ปิดแล้ว")

    def refund(self):
        if self.__status not in (self.STATUS_DEPOSIT_PAID, self.STATUS_FULLY_PAID):
            raise Exception("ไม่สามารถคืนเงินได้ในสถานะนี้")
        self.__status = self.STATUS_REFUNDED
        print(f"[Order] {self.__order_id} คืนเงินแล้ว")

    def summary(self) -> str:
        return (
            f"order_id          : {self.__order_id}\n"
            f"booking_id        : {self.__booking.booking_id}\n"
            f"design            : {self.__booking.body_part} ({self.__booking.size}, {self.__booking.color_tone})\n"
            f"appointments      : {self.__booking.appointment_count} sessions\n"
            f"deposit_amount    : {self.__deposit_amount:.2f} บาท\n"
            f"paid_amount       : {self.__paid_amount:.2f} บาท\n"
            f"total_price       : {self.__full_price_amount:.2f} บาท\n"
            f"remaining         : {self.remaining_amount:.2f} บาท\n"
            f"status            : {self.__status}"
        )

    def __repr__(self):
        return (f"<Order id={self.__order_id} booking={self.__booking.booking_id} "
                f"total={self.__full_price_amount} status={self.__status}>")
