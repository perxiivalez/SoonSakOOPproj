"""
booking.py — Appointment, Booking, Order
"""

from datetime import datetime, date


class Appointment:
    """นัดหมายที่ผูกกับ Booking"""

    def __init__(self, appointment_id: str, booking_id: str,
                 appointment_date: date, start_time: str, end_time: str):
        self._appointment_id = appointment_id
        self._booking_id = booking_id
        self._date = appointment_date
        self._start_time = start_time
        self._end_time = end_time
        self._created_at = datetime.now()

    @property
    def appointment_id(self):
        return self._appointment_id

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def date(self):
        return self._date

    def __repr__(self):
        return f"<Appointment id={self._appointment_id} date={self._date}>"


class Booking:
    """การจองสักหนึ่งครั้ง
    Status: WAITING → ACCEPTED → COMPLETED / CANCELLED / NO_SHOW
    """

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

        self._booking_id = booking_id
        self._user_id = user_id
        self._artist_id = artist_id
        self._body_part = body_part
        self._size = size
        self._color_tone = color_tone
        self._base_price = base_price
        self._reference_image = reference_image
        self._status = self.STATUS_WAITING
        self._appointment_list: list[Appointment] = []
        self._created_at = datetime.now()

    @property
    def booking_id(self):
        return self._booking_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def artist_id(self):
        return self._artist_id

    @property
    def status(self):
        return self._status

    @property
    def base_price(self):
        return self._base_price

    def accept(self):
        if self._status != self.STATUS_WAITING:
            raise Exception("รับงานได้เฉพาะ WAITING เท่านั้น")
        self._status = self.STATUS_ACCEPTED
        print(f"[Booking] {self._booking_id} ถูก accept แล้ว")

    def cancel(self):
        if self._status in (self.STATUS_COMPLETED, self.STATUS_NO_SHOW):
            raise Exception("ยกเลิกไม่ได้")
        self._status = self.STATUS_CANCELLED
        print(f"[Booking] {self._booking_id} ถูกยกเลิกแล้ว")

    def complete(self):
        if self._status != self.STATUS_ACCEPTED:
            raise Exception("ต้อง ACCEPTED ก่อน complete")
        self._status = self.STATUS_COMPLETED
        print(f"[Booking] {self._booking_id} เสร็จสมบูรณ์")

    def no_show(self):
        self._status = self.STATUS_NO_SHOW
        print(f"[Booking] {self._booking_id} ไม่มาตามนัด")

    def set_price(self, price: float):
        if price < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")
        self._base_price = price
        print(f"[Booking] กำหนดราคา {price:.2f} บาท")

    def add_appointment(self, appointment: Appointment):
        self._appointment_list.append(appointment)

    def summary(self) -> str:
        return (
            f"booking_id   : {self._booking_id}\n"
            f"user_id      : {self._user_id}\n"
            f"artist_id    : {self._artist_id}\n"
            f"body_part    : {self._body_part}\n"
            f"size         : {self._size}\n"
            f"color_tone   : {self._color_tone}\n"
            f"base_price   : {self._base_price:.2f} บาท\n"
            f"status       : {self._status}\n"
            f"appointments : {len(self._appointment_list)} รายการ"
        )

    def __repr__(self):
        return f"<Booking id={self._booking_id} status={self._status} price={self._base_price}>"


class Order:
    """Order รวม Booking เพื่อชำระเงิน
    Status: PENDING_PAYMENT → DEPOSIT_PAID → FULLY_PAID → CLOSED / REFUNDED
    """

    STATUS_PENDING_PAYMENT = "PENDING_PAYMENT"
    STATUS_DEPOSIT_PAID    = "DEPOSIT_PAID"
    STATUS_FULLY_PAID      = "FULLY_PAID"
    STATUS_CLOSED          = "CLOSED"
    STATUS_REFUNDED        = "REFUNDED"

    def __init__(self, order_id: str):
        if not order_id.startswith("ORD-"):
            raise ValueError("order_id ต้องขึ้นต้นด้วย ORD-")
        self._order_id = order_id
        self._bookings: list[Booking] = []
        self._deposit_amount: float = 0.0
        self._full_price_amount: float = 0.0
        self._status = self.STATUS_PENDING_PAYMENT
        self._created_at = datetime.now()

    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self):
        return self._status

    @property
    def deposit_amount(self):
        return self._deposit_amount

    @property
    def full_price_amount(self):
        return self._full_price_amount

    @property
    def bookings(self):
        return list(self._bookings)

    def add_booking(self, booking: Booking):
        self._bookings.append(booking)
        self._full_price_amount = sum(b.base_price for b in self._bookings)
        print(f"[Order] เพิ่ม {booking.booking_id} เข้า {self._order_id}")

    def calculate_total(self) -> float:
        return sum(b.base_price for b in self._bookings)

    def order_phase(self):
        """แสดงสถานะปัจจุบัน"""
        if self._status == self.STATUS_PENDING_PAYMENT:
            phase = "รอชำระมัดจำ"
        elif self._status == self.STATUS_DEPOSIT_PAID:
            phase = "ชำระมัดจำแล้ว รอชำระส่วนที่เหลือ"
        elif self._status == self.STATUS_FULLY_PAID:
            phase = "ชำระครบแล้ว"
        elif self._status == self.STATUS_CLOSED:
            phase = "ปิด Order แล้ว"
        elif self._status == self.STATUS_REFUNDED:
            phase = "คืนเงินแล้ว"
        else:
            phase = "ไม่ทราบสถานะ"
        print(f"[Order] {self._order_id} → {phase}")
        return self._status

    def pay_deposit(self, amount: float):
        self._deposit_amount = amount
        self._status = self.STATUS_DEPOSIT_PAID
        print(f"[Order] ชำระมัดจำ {amount:.2f} บาท สำเร็จ")

    def pay_full(self):
        self._status = self.STATUS_FULLY_PAID
        print(f"[Order] ชำระเต็มจำนวนแล้ว")

    def close(self):
        self._status = self.STATUS_CLOSED
        print(f"[Order] {self._order_id} ปิดแล้ว")

    def refund(self):
        if self._status not in (self.STATUS_DEPOSIT_PAID, self.STATUS_FULLY_PAID):
            raise Exception("ไม่สามารถคืนเงินได้ในสถานะนี้")
        self._status = self.STATUS_REFUNDED
        print(f"[Order] {self._order_id} คืนเงินแล้ว")

    def summary(self) -> str:
        return (
            f"order_id          : {self._order_id}\n"
            f"bookings          : {len(self._bookings)} รายการ\n"
            f"deposit_amount    : {self._deposit_amount:.2f} บาท\n"
            f"full_price_amount : {self._full_price_amount:.2f} บาท\n"
            f"status            : {self._status}"
        )

    def __repr__(self):
        return (f"<Order id={self._order_id} bookings={len(self._bookings)} "
                f"total={self._full_price_amount} status={self._status}>")