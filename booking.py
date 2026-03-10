"""
booking.py — Appointment, Booking, Order
- ทุก attribute เป็น private (__attr)
- ไม่ใช้ Dict เลย ใช้ list ทั้งหมด
"""

from datetime import datetime, date


class Appointment:
    def __init__(self, appointment_id: str, booking_id: str,
                 appointment_date: date, start_time: str, end_time: str):
        self.__appointment_id = appointment_id
        self.__booking_id = booking_id
        self.__date = appointment_date
        self.__start_time = start_time
        self.__end_time = end_time
        self.__created_at = datetime.now()

    @property
    def appointment_id(self): return self.__appointment_id

    @property
    def booking_id(self): return self.__booking_id

    @property
    def date(self): return self.__date

    def __repr__(self):
        return f"<Appointment id={self.__appointment_id} date={self.__date}>"


class Booking:
    """Status: WAITING → ACCEPTED → COMPLETED / CANCELLED / NO_SHOW"""

    STATUS_WAITING   = "WAITING"
    STATUS_ACCEPTED  = "ACCEPTED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NO_SHOW   = "NO_SHOW"

    def __init__(self, booking_id: str, user_id: str, artist_id: str,
                 body_part: str, size: str, color_tone: str,
                 base_price: float, reference_image: str = ""):
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

    def accept(self):
        if self.__status != self.STATUS_WAITING:
            raise Exception("รับงานได้เฉพาะ WAITING เท่านั้น")
        self.__status = self.STATUS_ACCEPTED
        print(f"[Booking] {self.__booking_id} ถูก accept แล้ว")

    def cancel(self):
        if self.__status in (self.STATUS_COMPLETED, self.STATUS_NO_SHOW):
            raise Exception("ยกเลิกไม่ได้")
        self.__status = self.STATUS_CANCELLED
        print(f"[Booking] {self.__booking_id} ถูกยกเลิกแล้ว")

    def complete(self):
        if self.__status != self.STATUS_ACCEPTED:
            raise Exception("ต้อง ACCEPTED ก่อน complete")
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
        self.__appointment_list.append(appointment)

    def summary(self) -> str:
        return (
            f"booking_id   : {self.__booking_id}\n"
            f"user_id      : {self.__user_id}\n"
            f"artist_id    : {self.__artist_id}\n"
            f"body_part    : {self.__body_part}\n"
            f"size         : {self.__size}\n"
            f"color_tone   : {self.__color_tone}\n"
            f"base_price   : {self.__base_price:.2f} บาท\n"
            f"status       : {self.__status}\n"
            f"appointments : {len(self.__appointment_list)} รายการ"
        )

    def __repr__(self):
        return f"<Booking id={self.__booking_id} status={self.__status} price={self.__base_price}>"


class Order:
    """Status: PENDING_PAYMENT → DEPOSIT_PAID → FULLY_PAID → CLOSED / REFUNDED"""

    STATUS_PENDING_PAYMENT = "PENDING_PAYMENT"
    STATUS_DEPOSIT_PAID    = "DEPOSIT_PAID"
    STATUS_FULLY_PAID      = "FULLY_PAID"
    STATUS_CLOSED          = "CLOSED"
    STATUS_REFUNDED        = "REFUNDED"

    def __init__(self, order_id: str):
        if not order_id.startswith("ORD-"):
            raise ValueError("order_id ต้องขึ้นต้นด้วย ORD-")
        self.__order_id = order_id
        self.__bookings: list = []
        self.__deposit_amount: float = 0.0
        self.__full_price_amount: float = 0.0
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
    def bookings(self): return list(self.__bookings)

    def add_booking(self, booking: Booking):
        self.__bookings.append(booking)
        self.__full_price_amount = sum(b.base_price for b in self.__bookings)
        print(f"[Order] เพิ่ม {booking.booking_id} เข้า {self.__order_id}")

    def calculate_total(self) -> float:
        return sum(b.base_price for b in self.__bookings)

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
        self.__status = self.STATUS_DEPOSIT_PAID
        print(f"[Order] ชำระมัดจำ {amount:.2f} บาท สำเร็จ")

    def pay_full(self):
        self.__status = self.STATUS_FULLY_PAID
        print(f"[Order] ชำระเต็มจำนวนแล้ว")

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
            f"bookings          : {len(self.__bookings)} รายการ\n"
            f"deposit_amount    : {self.__deposit_amount:.2f} บาท\n"
            f"full_price_amount : {self.__full_price_amount:.2f} บาท\n"
            f"status            : {self.__status}"
        )

    def __repr__(self):
        return (f"<Order id={self.__order_id} bookings={len(self.__bookings)} "
                f"total={self.__full_price_amount} status={self.__status}>")