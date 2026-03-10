"""
booking.py
==========
ไฟล์นี้จัดการ Booking, Appointment, และ Order
ซึ่งเป็น Transaction หลักของระบบ SoonSak

Entity IDs:
- Booking: BKG-001
- Order:   ORD-001
"""

from datetime import date, datetime


# ─────────────────────────────────────────────
# Appointment
# ─────────────────────────────────────────────

class Appointment:
    """
    นัดหมายของการสัก 1 ครั้ง
    Booking หนึ่งอาจมีหลาย Appointment (เช่น สักหลายนัด)
    Composition: Appointment อยู่ไม่ได้โดยไม่มี Booking
    """

    def __init__(self, appointment_id: str, date_list: list[date]):
        # Validation (B2)
        if not date_list:
            raise ValueError("ต้องมีวันนัดอย่างน้อย 1 วัน")
        self.__appointment_id = appointment_id
        self.__date_list: list[date] = date_list

    @property
    def appointment_id(self):
        return self.__appointment_id

    @property
    def date_list(self):
        return list(self.__date_list)

    def add_date(self, new_date: date):
        """เพิ่มวันนัดหมาย"""
        if new_date < date.today():
            raise ValueError("ไม่สามารถเพิ่มวันที่ผ่านมาแล้ว")
        self.__date_list.append(new_date)

    def __repr__(self):
        return f"<Appointment id={self.__appointment_id} dates={self.__date_list}>"


# ─────────────────────────────────────────────
# Booking
# ─────────────────────────────────────────────

class Booking:
    """
    การจองสักหนึ่งรายการ
    Status Flow: WAITING → ACCEPTED → COMPLETED
                                  ↘ CANCELLED / NO_SHOW

    ID format: BKG-001
    States (A3): WAITING, ACCEPTED, COMPLETED, CANCELLED, NO_SHOW
    """

    # ── Status Constants ──
    STATUS_WAITING = "WAITING"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_NO_SHOW = "NO_SHOW"

    def __init__(self, booking_id: str, user_id: str, artist_id: str,
                 body_part: str, size: str, color_tone: str,
                 reference_image: str = "", base_price: float = 0.0):
        # Validation (B2: ตรวจสอบข้อมูล)
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
        self.__reference_image = reference_image
        self.__base_price = base_price
        self.__status = self.STATUS_WAITING
        self.__appointment_list: list[Appointment] = []
        self.__user_submit: bool = False
        self.__artist_submit: bool = False
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()

    # ── Getters ──
    @property
    def booking_id(self):
        return self.__booking_id

    @property
    def user_id(self):
        return self.__user_id

    @property
    def artist_id(self):
        return self.__artist_id

    @property
    def status(self):
        return self.__status

    @property
    def base_price(self):
        return self.__base_price

    @property
    def appointments(self):
        return list(self.__appointment_list)

    def add_appointment(self, appointment: Appointment):
        """เพิ่มนัดหมายเข้าการจอง"""
        self.__appointment_list.append(appointment)
        self.__updated_at = datetime.now()

    # ── Status Methods ──

    def waiting(self):
        """รีเซ็ตกลับไป WAITING (กรณี Artist ยังไม่ตอบ)"""
        self.__status = self.STATUS_WAITING
        self.__updated_at = datetime.now()
        print(f"[Booking] {self.__booking_id} กลับไปสถานะ WAITING")

    def accept(self):
        """Artist ยอมรับงาน"""
        if self.__status != self.STATUS_WAITING:
            raise Exception(f"ไม่สามารถ accept Booking ที่มีสถานะ {self.__status}")
        self.__status = self.STATUS_ACCEPTED
        self.__artist_submit = True
        self.__updated_at = datetime.now()
        print(f"[Booking] {self.__booking_id} ถูก accept แล้ว")

    def cancel(self):
        """
        ยกเลิกการจอง
        Business Rule (A3): ยกเลิกได้เฉพาะ WAITING หรือ ACCEPTED เท่านั้น
        """
        if self.__status in [self.STATUS_COMPLETED, self.STATUS_NO_SHOW]:
            raise Exception(f"ไม่สามารถยกเลิก Booking ที่ {self.__status} แล้ว")
        self.__status = self.STATUS_CANCELLED
        self.__updated_at = datetime.now()
        print(f"[Booking] {self.__booking_id} ถูกยกเลิกแล้ว")

    def complete(self):
        """งานเสร็จสมบูรณ์"""
        if self.__status != self.STATUS_ACCEPTED:
            raise Exception("ต้อง accept ก่อนจึงจะ complete ได้")
        self.__status = self.STATUS_COMPLETED
        self.__updated_at = datetime.now()
        print(f"[Booking] {self.__booking_id} เสร็จสมบูรณ์")

    def mark_no_show(self):
        """User ไม่มาตามนัด"""
        if self.__status != self.STATUS_ACCEPTED:
            raise Exception("ต้อง accept ก่อนจึงจะ mark no-show ได้")
        self.__status = self.STATUS_NO_SHOW
        self.__updated_at = datetime.now()
        print(f"[Booking] {self.__booking_id} ถูก mark NO_SHOW")

    def set_price(self, price: float):
        """Artist กำหนดราคา"""
        if price < 0:
            raise ValueError("ราคาต้องไม่ติดลบ")
        self.__base_price = price
        print(f"[Booking] กำหนดราคา {price:.2f} บาท")

    def summary(self) -> dict:
        """สรุปข้อมูล Booking"""
        return {
            "booking_id": self.__booking_id,
            "user_id": self.__user_id,
            "artist_id": self.__artist_id,
            "body_part": self.__body_part,
            "size": self.__size,
            "color_tone": self.__color_tone,
            "base_price": self.__base_price,
            "status": self.__status,
            "appointments": len(self.__appointment_list),
        }

    def __repr__(self):
        return f"<Booking id={self.__booking_id} status={self.__status} price={self.__base_price}>"


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────

class Order:
    """
    Order รวม Booking หนึ่งหรือหลาย Booking เข้าด้วยกัน
    เชื่อมกับ Payment เพื่อชำระเงิน

    Status Flow: PENDING_PAYMENT → DEPOSIT_PAID → FULLY_PAID → CLOSED
                                               ↘ REFUNDED

    ID format: ORD-001
    States (A3): PENDING_PAYMENT, DEPOSIT_PAID, FULLY_PAID, CLOSED, REFUNDED
    """

    STATUS_PENDING_PAYMENT = "PENDING_PAYMENT"
    STATUS_DEPOSIT_PAID = "DEPOSIT_PAID"
    STATUS_FULLY_PAID = "FULLY_PAID"
    STATUS_CLOSED = "CLOSED"
    STATUS_REFUNDED = "REFUNDED"

    def __init__(self, order_id: str):
        if not order_id.startswith("ORD-"):
            raise ValueError("order_id ต้องขึ้นต้นด้วย ORD-")

        self.__order_id = order_id
        self.__bookings: list[Booking] = []   # Aggregation กับ Booking
        self.__deposit_amount: float = 0.0
        self.__full_price_amount: float = 0.0
        self.__status = self.STATUS_PENDING_PAYMENT
        self.__created_at = datetime.now()

    # ── Getters ──
    @property
    def order_id(self):
        return self.__order_id

    @property
    def status(self):
        return self.__status

    @property
    def deposit_amount(self):
        return self.__deposit_amount

    @property
    def full_price_amount(self):
        return self.__full_price_amount

    @property
    def bookings(self):
        return list(self.__bookings)

    def add_booking(self, booking: Booking):
        """เพิ่ม Booking เข้า Order"""
        self.__bookings.append(booking)
        # คำนวณราคารวมใหม่
        self.__full_price_amount = sum(b.base_price for b in self.__bookings)
        print(f"[Order] เพิ่ม {booking.booking_id} เข้า {self.__order_id}")

    def calculate_total(self) -> float:
        """คำนวณราคารวมทั้งหมด"""
        return sum(b.base_price for b in self.__bookings)

    def order_phase(self):
        """แสดงขั้นตอนปัจจุบันของ Order"""
        phases = {
            self.STATUS_PENDING_PAYMENT: "รอชำระมัดจำ",
            self.STATUS_DEPOSIT_PAID: "ชำระมัดจำแล้ว รอชำระส่วนที่เหลือ",
            self.STATUS_FULLY_PAID: "ชำระครบแล้ว",
            self.STATUS_CLOSED: "ปิด Order แล้ว",
            self.STATUS_REFUNDED: "คืนเงินแล้ว",
        }
        phase_text = phases.get(self.__status, "ไม่ทราบสถานะ")
        print(f"[Order] {self.__order_id} → {phase_text}")
        return self.__status

    def pay_deposit(self, amount: float):
        """บันทึกการชำระมัดจำ"""
        self.__deposit_amount = amount
        self.__status = self.STATUS_DEPOSIT_PAID
        print(f"[Order] ชำระมัดจำ {amount:.2f} บาท สำเร็จ")

    def pay_full(self):
        """บันทึกการชำระเต็มจำนวน"""
        self.__status = self.STATUS_FULLY_PAID
        print(f"[Order] ชำระเต็มจำนวนแล้ว")

    def close(self):
        """ปิด Order"""
        self.__status = self.STATUS_CLOSED
        print(f"[Order] {self.__order_id} ปิดแล้ว")

    def refund(self):
        """คืนเงิน"""
        if self.__status not in [self.STATUS_DEPOSIT_PAID, self.STATUS_FULLY_PAID]:
            raise Exception("ไม่สามารถคืนเงินได้ในสถานะนี้")
        self.__status = self.STATUS_REFUNDED
        print(f"[Order] {self.__order_id} คืนเงินแล้ว")

    def summary(self) -> dict:
        """สรุปข้อมูล Order"""
        return {
            "order_id": self.__order_id,
            "bookings": len(self.__bookings),
            "deposit_amount": self.__deposit_amount,
            "full_price_amount": self.__full_price_amount,
            "status": self.__status,
        }

    def __repr__(self):
        return (f"<Order id={self.__order_id} "
                f"bookings={len(self.__bookings)} "
                f"total={self.__full_price_amount} "
                f"status={self.__status}>")