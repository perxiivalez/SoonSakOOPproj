"""
entities.py
===========
ไฟล์นี้รวม Entity Classes หลักของระบบ SoonSak ได้แก่
User, VIPMember, Artist, Admin, Studio, Coupon, Rating,
Portfolio, TattooStyle, Calendar, Event, StudioRequest
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional


# ─────────────────────────────────────────────
# Abstract Base: Staff
# ─────────────────────────────────────────────

class Staff(ABC):
    """
    คลาสนามธรรม (Abstract) สำหรับพนักงานในระบบ
    ทั้ง Artist และ Admin ต้อง inherit จากคลาสนี้
    """

    def __init__(self, staff_id: str, name: str, email: str):
        self._staff_id = staff_id  # private: ปิดการเข้าถึงตรง ๆ
        self._name = name
        self._email = email

    # Getter
    @property
    def staff_id(self):
        return self._staff_id

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @abstractmethod
    def view_schedule(self):
        """แต่ละประเภท Staff ดู schedule ต่างกัน (Polymorphism)"""
        pass

    @abstractmethod
    def update_profile(self, **kwargs):
        """แต่ละประเภท Staff อัปเดต profile ต่างกัน (Polymorphism)"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self._staff_id} name={self._name}>"


# ─────────────────────────────────────────────
# Coupon
# ─────────────────────────────────────────────

class Coupon:
    """
    คูปองส่วนลดสำหรับผู้ใช้งาน
    - coupon_code: รหัสคูปอง
    - discount: เปอร์เซ็นต์ส่วนลด (0-100)
    - expired: วันหมดอายุ
    """

    def __init__(self, coupon_code: str, discount: float, expired: date):
        self._coupon_code = coupon_code
        self._discount = discount    # % ส่วนลด
        self._expired = expired

    @property
    def coupon_code(self):
        return self._coupon_code

    @property
    def discount(self):
        return self._discount

    def is_valid(self) -> bool:
        """ตรวจสอบว่าคูปองยังไม่หมดอายุ"""
        return date.today() <= self._expired

    def __repr__(self):
        return f"<Coupon code={self._coupon_code} discount={self._discount}% expires={self._expired}>"


# ─────────────────────────────────────────────
# Rating
# ─────────────────────────────────────────────

class Rating:
    """
    คะแนนรีวิวที่ User ให้กับ Artist หลังจาก Complete Job
    - rating_id: รหัสเฉพาะ เช่น RAT-001
    - score: คะแนน 1-5
    - comment: ความคิดเห็น
    """

    def __init__(self, rating_id: str, score: int, comment: str,
                 user_id: str, artist_id: str):
        # Validation (B2: ตรวจสอบค่าที่ถูกต้อง)
        if not (1 <= score <= 5):
            raise ValueError("Score ต้องอยู่ระหว่าง 1-5")
        self._rating_id = rating_id
        self._score = score
        self._comment = comment
        self._user_id = user_id
        self._artist_id = artist_id
        self._created_at = datetime.now()

    @property
    def rating_id(self):
        return self._rating_id

    @property
    def score(self):
        return self._score

    @property
    def artist_id(self):
        return self._artist_id

    def __repr__(self):
        return f"<Rating id={self._rating_id} score={self._score}/5>"


# ─────────────────────────────────────────────
# TattooStyle
# ─────────────────────────────────────────────

class TattooStyle:
    """สไตล์การสัก เช่น Minimalist, Japanese, Old School"""

    def __init__(self, style_id: str, name: str, description: str = ""):
        self._style_id = style_id
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"<TattooStyle {self._name}>"


# ─────────────────────────────────────────────
# Portfolio
# ─────────────────────────────────────────────

class Portfolio:
    """
    Portfolio ของ Artist เก็บรูปผลงานและสไตล์
    มีความสัมพันธ์ Aggregation กับ TattooStyle
    """

    def __init__(self, portfolio_id: str):
        self._portfolio_id = portfolio_id
        self._images: list[str] = []          # รายการ URL รูปภาพ
        self._styles: list[TattooStyle] = []  # สไตล์ที่ Artist ถนัด

    def add_image(self, image_url: str):
        """เพิ่มรูปผลงานเข้า portfolio"""
        if not image_url:
            raise ValueError("image_url ต้องไม่ว่าง")
        self._images.append(image_url)
        print(f"[Portfolio] เพิ่มรูปภาพแล้ว: {image_url}")

    def remove_image(self, image_url: str):
        """ลบรูปออกจาก portfolio"""
        if image_url not in self._images:
            raise ValueError("ไม่พบรูปภาพนี้ใน portfolio")
        self._images.remove(image_url)
        print(f"[Portfolio] ลบรูปภาพแล้ว: {image_url}")

    def add_style(self, style: TattooStyle):
        """เพิ่มสไตล์ที่ Artist ถนัด"""
        self._styles.append(style)

    @property
    def images(self):
        return list(self._images)

    @property
    def styles(self):
        return list(self._styles)

    def __repr__(self):
        return f"<Portfolio id={self._portfolio_id} images={len(self._images)}>"


# ─────────────────────────────────────────────
# Event & Calendar
# ─────────────────────────────────────────────

class Event:
    """
    เหตุการณ์ใน Calendar เช่น นัดลูกค้า, วันหยุด
    - event_name: ชื่อเหตุการณ์
    - date: วันที่
    - start_time / end_time: เวลาเริ่ม/สิ้นสุด
    """

    def __init__(self, event_id: str, event_name: str,
                 event_date: date, start_time: str, end_time: str,
                 description: str = ""):
        self._event_id = event_id
        self._event_name = event_name
        self._date = event_date
        self._start_time = start_time
        self._end_time = end_time
        self._description = description

    def edit(self, event_name: str = None, description: str = None):
        """แก้ไขข้อมูล Event"""
        if event_name:
            self._event_name = event_name
        if description:
            self._description = description
        print(f"[Event] แก้ไข event '{self._event_name}' แล้ว")

    def delete(self):
        """ทำเครื่องหมายว่า event ถูกลบ (soft delete)"""
        print(f"[Event] ลบ event '{self._event_name}' แล้ว")

    @property
    def event_id(self):
        return self._event_id

    @property
    def date(self):
        return self._date

    @property
    def event_name(self):
        return self._event_name

    def __repr__(self):
        return f"<Event {self._event_name} on {self._date}>"


class Calendar:
    """
    ปฏิทินของ Artist หรือ User
    มีความสัมพันธ์ Composition กับ Event (Event อยู่ไม่ได้โดยไม่มี Calendar)
    """

    def __init__(self, owner_id: str):
        self._owner_id = owner_id
        self._events: list[Event] = []

    def add_event(self, event: Event):
        """เพิ่ม Event เข้า Calendar"""
        self._events.append(event)
        print(f"[Calendar] เพิ่ม event '{event.event_name}' สำเร็จ")

    def view_monthly(self, year: int, month: int) -> list[Event]:
        """ดู Event ทั้งหมดในเดือนที่กำหนด"""
        result = [e for e in self._events
                  if e.date.year == year and e.date.month == month]
        return result

    def view_daily(self, target_date: date) -> list[Event]:
        """ดู Event ในวันที่กำหนด"""
        return [e for e in self._events if e.date == target_date]

    def get_busy_dates(self) -> list[date]:
        """คืนรายการวันที่มี Event (ใช้ตรวจสอบว่า Artist ว่างไหม)"""
        return [e.date for e in self._events]

    def __repr__(self):
        return f"<Calendar owner={self._owner_id} events={len(self._events)}>"


# ─────────────────────────────────────────────
# StudioRequest
# ─────────────────────────────────────────────

class StudioRequest:
    """
    คำขอเปิด Studio โดย Artist ต้องรอ Admin อนุมัติ
    Status: PENDING → APPROVED / REJECTED
    """

    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    def __init__(self, request_id: str, artist_id: str,
                 studio_name: str, location: str):
        self._request_id = request_id
        self._artist_id = artist_id
        self._studio_name = studio_name
        self._location = location
        self._status = self.STATUS_PENDING
        self._created_at = datetime.now()

    def submit(self):
        """ส่งคำขอ (ยืนยันการส่ง)"""
        print(f"[StudioRequest] ส่งคำขอ {self._request_id} แล้ว รอ Admin อนุมัติ")

    def approve(self):
        """Admin อนุมัติ Studio"""
        if self._status != self.STATUS_PENDING:
            raise Exception("สามารถอนุมัติได้เฉพาะคำขอที่ PENDING เท่านั้น")
        self._status = self.STATUS_APPROVED
        print(f"[StudioRequest] {self._request_id} ได้รับการอนุมัติแล้ว")

    def reject(self):
        """Admin ปฏิเสธ Studio"""
        if self._status != self.STATUS_PENDING:
            raise Exception("สามารถปฏิเสธได้เฉพาะคำขอที่ PENDING เท่านั้น")
        self._status = self.STATUS_REJECTED
        print(f"[StudioRequest] {self._request_id} ถูกปฏิเสธ")

    @property
    def request_id(self):
        return self._request_id

    @property
    def status(self):
        return self._status

    @property
    def studio_name(self):
        return self._studio_name

    @property
    def artist_id(self):
        return self._artist_id

    def __repr__(self):
        return f"<StudioRequest id={self._request_id} studio={self._studio_name} status={self._status}>"


# ─────────────────────────────────────────────
# Studio
# ─────────────────────────────────────────────

class Studio:
    """
    Studio สำหรับ Artist ทำงาน
    Status: OPEN / CLOSED
    ID format: STU-001
    """

    STATUS_OPEN = "OPEN"
    STATUS_CLOSED = "CLOSED"

    def __init__(self, studio_id: str, name: str, location: str):
        self._studio_id = studio_id
        self._name = name
        self._location = location
        self._artist_list: list[str] = []  # เก็บ artist_id
        self._status = self.STATUS_CLOSED

    def add_artist(self, artist_id: str):
        """เพิ่ม Artist เข้า Studio"""
        if artist_id in self._artist_list:
            raise ValueError(f"Artist {artist_id} อยู่ใน Studio นี้แล้ว")
        self._artist_list.append(artist_id)
        print(f"[Studio] เพิ่ม Artist {artist_id} เข้า {self._name}")

    def delete_artist(self, artist_id: str):
        """ลบ Artist ออกจาก Studio"""
        if artist_id not in self._artist_list:
            raise ValueError(f"ไม่พบ Artist {artist_id} ใน Studio นี้")
        self._artist_list.remove(artist_id)
        print(f"[Studio] ลบ Artist {artist_id} ออกจาก {self._name}")

    def open_studio(self):
        """เปิด Studio"""
        self._status = self.STATUS_OPEN
        print(f"[Studio] {self._name} เปิดแล้ว")

    def close_studio(self):
        """ปิด Studio"""
        self._status = self.STATUS_CLOSED
        print(f"[Studio] {self._name} ปิดแล้ว")

    @property
    def studio_id(self):
        return self._studio_id

    @property
    def name(self):
        return self._name

    @property
    def status(self):
        return self._status

    def __repr__(self):
        return f"<Studio id={self._studio_id} name={self._name} status={self._status}>"


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────

class User:
    """
    ผู้ใช้งานทั่วไปของระบบ SoonSak
    - user_id: รหัสผู้ใช้ เช่น USR-001
    - credit: เงินสะสมในระบบ
    - status: ACTIVE / SUSPENDED
    - max_bookings: จำนวนการจองสูงสุดพร้อมกัน (Business Rule)
    - max_calendar: จำนวนวันที่จองล่วงหน้าสูงสุด (Business Rule)
    """

    STATUS_ACTIVE = "ACTIVE"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, user_id: str, name: str, email: str, phone_number: str):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._phone_number = phone_number
        self._credit: float = 0.0
        self._status = self.STATUS_ACTIVE
        self._bookings_history: list = []    # ประวัติการจอง (B3: เก็บ History)
        self._coupon_list: list[Coupon] = []
        self._transaction_list: list = []
        self._appointment_list: list = []
        self._submitting: bool = False
        # Business Rule (A3): จำกัดจำนวน
        self._max_calendar: int = 60         # จองล่วงหน้าได้สูงสุด 60 วัน
        self._max_bookings: int = 3          # จองพร้อมกันได้สูงสุด 3 ครั้ง

    # ── Getters ──
    @property
    def user_id(self):
        return self._user_id

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def status(self):
        return self._status

    @property
    def max_bookings(self):
        return self._max_bookings

    @property
    def max_calendar(self):
        return self._max_calendar

    @property
    def credit(self):
        return self._credit

    def add_credit(self, amount: float):
        """เติมเงินเข้าระบบ"""
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self._credit += amount

    def deduct_credit(self, amount: float):
        """หักเงินออกจากระบบ"""
        if amount > self._credit:
            raise ValueError("เครดิตไม่เพียงพอ")
        self._credit -= amount

    def view_history(self) -> list:
        """ดูประวัติการจองทั้งหมด"""
        return list(self._bookings_history)

    def add_history(self, booking):
        """เพิ่ม Booking เข้าประวัติ (B3: เก็บ History)"""
        self._bookings_history.append(booking)

    def calculate_discount(self, base_price: float) -> float:
        """
        คำนวณส่วนลด (Polymorphism - VIPMember จะ override)
        User ทั่วไปไม่มีส่วนลด
        """
        return 0.0

    def add_coupon(self, coupon: Coupon):
        """เพิ่มคูปองให้ User"""
        self._coupon_list.append(coupon)

    def use_coupon(self, coupon_code: str, base_price: float) -> float:
        """
        ใช้คูปองส่วนลด
        คืนค่าราคาหลังหักส่วนลด
        """
        for coupon in self._coupon_list:
            if coupon.coupon_code == coupon_code:
                if not coupon.is_valid():
                    raise ValueError("คูปองหมดอายุแล้ว")
                discount_amount = base_price * (coupon.discount / 100)
                self._coupon_list.remove(coupon)
                print(f"[User] ใช้คูปอง {coupon_code} ลด {coupon.discount}%")
                return base_price - discount_amount
        raise ValueError(f"ไม่พบคูปอง {coupon_code}")

    def submit(self):
        """กดยืนยันการจอง"""
        self._submitting = True
        print(f"[User] {self._name} ยืนยันการจองแล้ว")

    def suspend(self):
        """ถูก Admin ระงับบัญชี"""
        self._status = self.STATUS_SUSPENDED
        print(f"[User] บัญชี {self._name} ถูกระงับ")

    def __repr__(self):
        return f"<User id={self._user_id} name={self._name} status={self._status}>"


# ─────────────────────────────────────────────
# VIPMember (User + extra privileges)
# ─────────────────────────────────────────────

class VIPMember(User):
    """
    สมาชิก VIP ได้รับสิทธิพิเศษเพิ่มเติม
    Inheritance ลำดับที่ 1: User → VIPMember
    - rank: ระดับ VIP (SILVER / GOLD / PLATINUM)
    - max_bookings และ max_calendar สูงกว่า User ทั่วไป
    """

    RANK_SILVER = "SILVER"
    RANK_GOLD = "GOLD"
    RANK_PLATINUM = "PLATINUM"

    DISCOUNT_RATE = {
        "SILVER": 5,
        "GOLD": 10,
        "PLATINUM": 15,
    }

    def __init__(self, user_id: str, name: str, email: str,
                 phone_number: str, rank: str = "SILVER"):
        super().__init__(user_id, name, email, phone_number)
        self._rank = rank
        # VIP ได้สิทธิ์จองมากกว่า (B1: Polymorphism via override)
        self._max_bookings = 6       # จองพร้อมกันได้ 6 ครั้ง
        self._max_calendar = 120     # จองล่วงหน้าได้ 120 วัน

    @property
    def rank(self):
        return self._rank

    def calculate_discount(self, base_price: float) -> float:
        """
        Override: VIP มีส่วนลดตาม rank (Polymorphism)
        SILVER=5%, GOLD=10%, PLATINUM=15%
        """
        rate = self.DISCOUNT_RATE.get(self._rank, 0)
        discount = base_price * (rate / 100)
        print(f"[VIP] ส่วนลด {rate}% = {discount:.2f} บาท")
        return discount

    def upgrade_rank(self, new_rank: str):
        """อัปเกรด rank ของ VIP"""
        if new_rank not in self.DISCOUNT_RATE:
            raise ValueError(f"Rank ไม่ถูกต้อง: {new_rank}")
        self._rank = new_rank
        print(f"[VIPMember] อัปเกรด rank เป็น {new_rank}")

    def __repr__(self):
        return f"<VIPMember id={self._user_id} name={self._name} rank={self._rank}>"


# ─────────────────────────────────────────────
# Artist (Staff → Artist)
# Inheritance ลำดับที่ 2: Staff → Artist
# ─────────────────────────────────────────────

class Artist(Staff):
    """
    ช่างสักในระบบ SoonSak
    Inheritance ลำดับที่ 2: Staff → Artist
    - experience: ประสบการณ์ (ปี)
    - deposit_policy: นโยบายมัดจำของ Artist คนนี้
    - status: PENDING / VERIFIED / SUSPENDED
    """

    STATUS_PENDING = "PENDING"
    STATUS_VERIFIED = "VERIFIED"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, staff_id: str, name: str, email: str,
                 experience: int = 0):
        super().__init__(staff_id, name, email)
        self._experience = experience
        self._deposit_policy = None          # DepositPolicy object
        self._portfolio: Optional[Portfolio] = None
        self._available_day_list: list[date] = []
        self._request_list: list[StudioRequest] = []
        self._booking_list: list = []
        self._appointment_list: list = []
        self._submitting: bool = False
        self._status = self.STATUS_PENDING
        self._calendar: Optional[Calendar] = None
        self._ratings: list[Rating] = []

    # ── Getters ──
    @property
    def status(self):
        return self._status

    @property
    def deposit_policy(self):
        return self._deposit_policy

    @property
    def calendar(self):
        return self._calendar

    def verify_identity(self):
        """ยืนยันตัวตนเพื่อเริ่มรับงาน (Admin ต้อง approve ก่อน)"""
        self._status = self.STATUS_VERIFIED
        print(f"[Artist] {self._name} ยืนยันตัวตนแล้ว")

    def set_calendar(self):
        """สร้าง Calendar ให้ Artist"""
        self._calendar = Calendar(owner_id=self._staff_id)
        print(f"[Artist] {self._name} ตั้ง Calendar แล้ว")
        return self._calendar

    def set_deposit_policy(self, policy):
        """กำหนด DepositPolicy ของ Artist (import จาก payment.py ที่ controller)"""
        self._deposit_policy = policy
        print(f"[Artist] {self._name} ตั้ง deposit policy แล้ว: {policy}")

    def accept_job(self, booking) -> bool:
        """
        รับงาน Booking
        - ตรวจสอบว่า Artist ว่างในวันนั้น
        - เปลี่ยน status ของ Booking เป็น ACCEPTED
        """
        if self._status != self.STATUS_VERIFIED:
            raise Exception("Artist ต้องผ่านการยืนยันตัวตนก่อน")
        booking.accept()
        self._booking_list.append(booking)
        print(f"[Artist] {self._name} รับงาน {booking.booking_id}")
        return True

    def reject_job(self, booking, reason: str = ""):
        """ปฏิเสธ Booking"""
        booking.cancel()
        print(f"[Artist] {self._name} ปฏิเสธงาน {booking.booking_id}: {reason}")

    def complete_job(self, booking):
        """ทำงานเสร็จ - เปลี่ยน Booking เป็น COMPLETED"""
        booking.complete()
        print(f"[Artist] {self._name} เสร็จงาน {booking.booking_id}")

    def manage_time(self, event: Event):
        """จัดการเวลาว่าง เพิ่ม Event เข้า Calendar"""
        if self._calendar is None:
            self.set_calendar()
        self._calendar.add_event(event)

    def request_studio(self, request: StudioRequest):
        """ส่งคำขอเปิด Studio"""
        self._request_list.append(request)
        request.submit()

    def add_rating(self, rating: Rating):
        """รับ Rating จาก User"""
        self._ratings.append(rating)

    def average_rating(self) -> float:
        """คำนวณคะแนนเฉลี่ย"""
        if not self._ratings:
            return 0.0
        return sum(r.score for r in self._ratings) / len(self._ratings)

    def view_schedule(self):
        """ดูตารางงานของ Artist (implement abstract method)"""
        if self._calendar is None:
            print(f"[Artist] {self._name} ยังไม่มี Calendar")
            return []
        events = self._calendar.view_monthly(
            datetime.now().year, datetime.now().month
        )
        print(f"[Artist] {self._name} มี {len(events)} งานเดือนนี้")
        return events

    def update_profile(self, **kwargs):
        """อัปเดตโปรไฟล์ Artist (implement abstract method)"""
        if "name" in kwargs:
            self._name = kwargs["name"]
        if "experience" in kwargs:
            self._experience = kwargs["experience"]
        print(f"[Artist] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Artist id={self._staff_id} name={self._name} status={self._status}>"


# ─────────────────────────────────────────────
# Admin (Staff → Admin)
# Inheritance ลำดับที่ 2: Staff → Admin
# ─────────────────────────────────────────────

class Admin(Staff):
    """
    ผู้ดูแลระบบ
    Inheritance ลำดับที่ 2: Staff → Admin
    มีสิทธิ์จัดการ Artist, Studio, User, Policy
    """

    def __init__(self, staff_id: str, name: str, email: str):
        super().__init__(staff_id, name, email)
        self._requests: list[StudioRequest] = []

    def approve_artist(self, artist: Artist):
        """อนุมัติ Artist ให้เข้าระบบ"""
        artist.verify_identity()
        print(f"[Admin] อนุมัติ Artist {artist.name} แล้ว")

    def reject_artist(self, artist: Artist):
        """ปฏิเสธ Artist"""
        artist._status = Artist.STATUS_SUSPENDED
        print(f"[Admin] ปฏิเสธ Artist {artist.name}")

    def approve_studio(self, request: StudioRequest, studio_list: list):
        """อนุมัติ StudioRequest และสร้าง Studio ใหม่"""
        request.approve()
        new_studio = Studio(
            studio_id=f"STU-{len(studio_list)+1:03d}",
            name=request.studio_name,
            location=""
        )
        new_studio.open_studio()
        studio_list.append(new_studio)
        return new_studio

    def reject_studio(self, request: StudioRequest):
        """ปฏิเสธคำขอ Studio"""
        request.reject()

    def suspend_user(self, user: User):
        """ระงับบัญชีผู้ใช้"""
        user.suspend()
        print(f"[Admin] ระงับ User {user.name} แล้ว")

    def manage_policy(self, policy_info: str):
        """จัดการนโยบายของระบบ"""
        print(f"[Admin] อัปเดต policy: {policy_info}")

    def view_schedule(self):
        """Admin ดู schedule overview (implement abstract method)"""
        print(f"[Admin] {self._name} กำลังดู schedule overview")
        return []

    def update_profile(self, **kwargs):
        """อัปเดตโปรไฟล์ Admin (implement abstract method)"""
        if "name" in kwargs:
            self._name = kwargs["name"]
        print(f"[Admin] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Admin id={self._staff_id} name={self._name}>"
