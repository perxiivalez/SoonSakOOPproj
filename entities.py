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
# Coupon
# ─────────────────────────────────────────────

class Coupon:
    def __init__(self, coupon_code: str, discount: float, expired: date):
        self.__coupon_code = coupon_code
        self.__discount = discount    
        self.__expired = expired

    @property
    def coupon_code(self):
        return self.__coupon_code

    @property
    def discount(self):
        return self.__discount

    def is_valid(self) -> bool:
        return date.today() <= self.__expired

    def __repr__(self):
        return f"<Coupon code={self.__coupon_code} discount={self.__discount}% expires={self.__expired}>"


# ─────────────────────────────────────────────
# Rating
# ─────────────────────────────────────────────

class Rating:
    def __init__(self, rating_id: str, score: int, comment: str,
                 user_id: str, artist_id: str):
        if not (1 <= score <= 5):
            raise ValueError("Score ต้องอยู่ระหว่าง 1-5")
        self.__rating_id = rating_id
        self.__score = score
        self.__comment = comment
        self.__user_id = user_id
        self.__artist_id = artist_id
        self.__created_at = datetime.now()

    @property
    def rating_id(self):
        return self.__rating_id

    @property
    def score(self):
        return self.__score

    @property
    def artist_id(self):
        return self.__artist_id

    def __repr__(self):
        return f"<Rating id={self.__rating_id} score={self.__score}/5>"


# ─────────────────────────────────────────────
# TattooStyle
# ─────────────────────────────────────────────

class TattooStyle:
    def __init__(self, style_id: str, name: str, description: str = ""):
        self.__style_id = style_id
        self.__name = name
        self.__description = description

    @property
    def name(self):
        return self.__name

    def __repr__(self):
        return f"<TattooStyle {self.__name}>"


# ─────────────────────────────────────────────
# Portfolio
# ─────────────────────────────────────────────

class Portfolio:
    def __init__(self, portfolio_id: str):
        self.__portfolio_id = portfolio_id
        self.__images: list[str] = []          
        self.__styles: list[TattooStyle] = []  

    def add_image(self, image_url: str):
        if not image_url:
            raise ValueError("image_url ต้องไม่ว่าง")
        self.__images.append(image_url)
        print(f"[Portfolio] เพิ่มรูปภาพแล้ว: {image_url}")

    def remove_image(self, image_url: str):
        if image_url not in self.__images:
            raise ValueError("ไม่พบรูปภาพนี้ใน portfolio")
        self.__images.remove(image_url)
        print(f"[Portfolio] ลบรูปภาพแล้ว: {image_url}")

    def add_style(self, style: TattooStyle):
        self.__styles.append(style)

    @property
    def images(self):
        return list(self.__images)

    @property
    def styles(self):
        return list(self.__styles)

    def __repr__(self):
        return f"<Portfolio id={self.__portfolio_id} images={len(self.__images)}>"


# ─────────────────────────────────────────────
# Event & Calendar
# ─────────────────────────────────────────────

class Event:
    def __init__(self, event_id: str, event_name: str,
                 event_date: date, start_time: str, end_time: str,
                 description: str = ""):
        self.__event_id = event_id
        self.__event_name = event_name
        self.__date = event_date
        self.__start_time = start_time
        self.__end_time = end_time
        self.__description = description

    def edit(self, event_name: str = None, description: str = None):
        if event_name:
            self.__event_name = event_name
        if description:
            self.__description = description
        print(f"[Event] แก้ไข event '{self.__event_name}' แล้ว")

    def delete(self):
        print(f"[Event] ลบ event '{self.__event_name}' แล้ว")

    @property
    def event_id(self):
        return self.__event_id

    @property
    def date(self):
        return self.__date

    @property
    def event_name(self):
        return self.__event_name

    def __repr__(self):
        return f"<Event {self.__event_name} on {self.__date}>"


class Calendar:
    def __init__(self, owner_id: str):
        self.__owner_id = owner_id
        self.__events: list[Event] = []

    def add_event(self, event: Event):
        self.__events.append(event)
        print(f"[Calendar] เพิ่ม event '{event.event_name}' สำเร็จ")

    def view_monthly(self, year: int, month: int) -> list[Event]:
        result = [e for e in self.__events
                  if e.date.year == year and e.date.month == month]
        return result

    def view_daily(self, target_date: date) -> list[Event]:
        return [e for e in self.__events if e.date == target_date]

    def get_busy_dates(self) -> list[date]:
        return [e.date for e in self.__events]

    def __repr__(self):
        return f"<Calendar owner={self.__owner_id} events={len(self.__events)}>"


# ─────────────────────────────────────────────
# StudioRequest
# ─────────────────────────────────────────────

class StudioRequest:
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    def __init__(self, request_id: str, artist_id: str,
                 studio_name: str, location: str):
        self.__request_id = request_id
        self.__artist_id = artist_id
        self.__studio_name = studio_name
        self.__location = location
        self.__status = self.STATUS_PENDING
        self.__created_at = datetime.now()

    def submit(self):
        print(f"[StudioRequest] ส่งคำขอ {self.__request_id} แล้ว รอ Admin อนุมัติ")

    def approve(self):
        if self.__status != self.STATUS_PENDING:
            raise Exception("สามารถอนุมัติได้เฉพาะคำขอที่ PENDING เท่านั้น")
        self.__status = self.STATUS_APPROVED
        print(f"[StudioRequest] {self.__request_id} ได้รับการอนุมัติแล้ว")

    def reject(self):
        if self.__status != self.STATUS_PENDING:
            raise Exception("สามารถปฏิเสธได้เฉพาะคำขอที่ PENDING เท่านั้น")
        self.__status = self.STATUS_REJECTED
        print(f"[StudioRequest] {self.__request_id} ถูกปฏิเสธ")

    @property
    def request_id(self):
        return self.__request_id

    @property
    def status(self):
        return self.__status

    @property
    def studio_name(self):
        return self.__studio_name

    @property
    def artist_id(self):
        return self.__artist_id

    def __repr__(self):
        return f"<StudioRequest id={self.__request_id} studio={self.__studio_name} status={self.__status}>"


# ─────────────────────────────────────────────
# Studio
# ─────────────────────────────────────────────

class Studio:
    STATUS_OPEN = "OPEN"
    STATUS_CLOSED = "CLOSED"

    def __init__(self, studio_id: str, name: str, location: str):
        self.__studio_id = studio_id
        self.__name = name
        self.__location = location
        self.__artist_list: list[str] = [] 
        self.__status = self.STATUS_CLOSED

    def add_artist(self, artist_id: str):
        if artist_id in self.__artist_list:
            raise ValueError(f"Artist {artist_id} อยู่ใน Studio นี้แล้ว")
        self.__artist_list.append(artist_id)
        print(f"[Studio] เพิ่ม Artist {artist_id} เข้า {self.__name}")

    def delete_artist(self, artist_id: str):
        if artist_id not in self.__artist_list:
            raise ValueError(f"ไม่พบ Artist {artist_id} ใน Studio นี้")
        self.__artist_list.remove(artist_id)
        print(f"[Studio] ลบ Artist {artist_id} ออกจาก {self.__name}")

    def open_studio(self):
        self.__status = self.STATUS_OPEN
        print(f"[Studio] {self.__name} เปิดแล้ว")

    def close_studio(self):
        self.__status = self.STATUS_CLOSED
        print(f"[Studio] {self.__name} ปิดแล้ว")

    @property
    def studio_id(self):
        return self.__studio_id

    @property
    def name(self):
        return self.__name

    @property
    def status(self):
        return self.__status

    def __repr__(self):
        return f"<Studio id={self.__studio_id} name={self.__name} status={self.__status}>"


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────

class User:
    STATUS_ACTIVE = "ACTIVE"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, user_id: str, name: str, email: str, phone_number: str):
        self.__user_id = user_id
        self.__name = name
        self.__email = email
        self.__phone_number = phone_number
        self.__credit: float = 0.0
        self.__status = self.STATUS_ACTIVE
        self.__bookings_history: list = []
        self.__coupon_list: list[Coupon] = []
        self.__transaction_list: list = []
        self.__appointment_list: list = []
        self.__submitting: bool = False
        self.__completed_tattoo_count: int = 0  
        self.__total_spent: float = 0.0         
        self.__max_calendar: int = 60         
        self.__max_bookings: int = 3          

    # ── Getters / Setters ──
    @property
    def user_id(self): return self.__user_id

    @property
    def name(self): return self.__name

    @property
    def email(self): return self.__email

    @property
    def status(self): return self.__status

    @property
    def credit(self): return self.__credit

    @property
    def completed_tattoo_count(self): return self.__completed_tattoo_count

    @property
    def total_spent(self): return self.__total_spent

    # Getter & Setter สำหรับตัวแปรที่คลาสลูก (VIPMember) ต้องนำไปแก้ไข
    @property
    def max_bookings(self): return self.__max_bookings
    
    @max_bookings.setter
    def max_bookings(self, value: int): self.__max_bookings = value

    @property
    def max_calendar(self): return self.__max_calendar

    @max_calendar.setter
    def max_calendar(self, value: int): self.__max_calendar = value

    def add_spent(self, amount: float):
        if amount > 0:
            self.__total_spent += amount
            print(f"[User] {self.__name} ยอดสะสม: {self.__total_spent:.2f} บาท")

    def add_credit(self, amount: float):
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self.__credit += amount

    def deduct_credit(self, amount: float):
        if amount > self.__credit:
            raise ValueError("เครดิตไม่เพียงพอ")
        self.__credit -= amount

    def view_history(self) -> list:
        return list(self.__bookings_history)

    def add_history(self, booking):
        self.__bookings_history.append(booking)

    def calculate_discount(self, base_price: float) -> float:
        return 0.0

    def add_coupon(self, coupon: Coupon):
        self.__coupon_list.append(coupon)

    def use_coupon(self, coupon_code: str, base_price: float) -> float:
        for coupon in self.__coupon_list:
            if coupon.coupon_code == coupon_code:
                if not coupon.is_valid():
                    raise ValueError("คูปองหมดอายุแล้ว")
                discount_amount = base_price * (coupon.discount / 100)
                self.__coupon_list.remove(coupon)
                print(f"[User] ใช้คูปอง {coupon_code} ลด {coupon.discount}%")
                return base_price - discount_amount
        raise ValueError(f"ไม่พบคูปอง {coupon_code}")

    def submit(self):
        self.__submitting = True
        print(f"[User] {self.__name} ยืนยันการจองแล้ว")

    def suspend(self):
        self.__status = self.STATUS_SUSPENDED
        print(f"[User] บัญชี {self.__name} ถูกระงับ")

    def __repr__(self):
        return f"<User id={self.__user_id} name={self.__name} status={self.__status}>"


# ─────────────────────────────────────────────
# VIPMember
# ─────────────────────────────────────────────

class VIPMember(User):
    RANK_SILVER   = "SILVER"
    RANK_GOLD     = "GOLD"
    RANK_PLATINUM = "PLATINUM"

    RANK_THRESHOLD = {
        "SILVER":    5_000,
        "GOLD":     15_000,
        "PLATINUM": 30_000,
    }

    DISCOUNT_RATE = {
        "SILVER":    5,
        "GOLD":     10,
        "PLATINUM": 15,
    }

    def __init__(self, user_id: str, name: str, email: str,
                 phone_number: str, rank: str = "SILVER"):
        super().__init__(user_id, name, email, phone_number)
        self.__rank = rank
        # เรียกใช้ Setter ของคลาสแม่ (User) เนื่องจาก __max_bookings เป็น Strictly Private
        self.max_bookings = 6    
        self.max_calendar = 120  

    @property
    def rank(self):
        return self.__rank

    def check_and_upgrade(self):
        spent = self.total_spent # เรียกจาก property getter ของคลาสแม่
        if spent >= self.RANK_THRESHOLD["PLATINUM"]:
            new_rank = self.RANK_PLATINUM
        elif spent >= self.RANK_THRESHOLD["GOLD"]:
            new_rank = self.RANK_GOLD
        else:
            new_rank = self.RANK_SILVER

        if new_rank != self.__rank:
            old_rank = self.__rank
            self.__rank = new_rank
            print(f"[VIPMember] 🎉 {self.name} อัปเกรด rank: {old_rank} → {new_rank} "
                  f"(ยอดสะสม {spent:,.2f} บาท)")

    def calculate_discount(self, base_price: float) -> float:
        rate = self.DISCOUNT_RATE.get(self.__rank, 0)
        discount = base_price * (rate / 100)
        print(f"[VIP] rank={self.__rank} ส่วนลด {rate}% = {discount:.2f} บาท")
        return discount

    def upgrade_rank(self, new_rank: str):
        if new_rank not in self.DISCOUNT_RATE:
            raise ValueError(f"Rank ไม่ถูกต้อง: {new_rank}")
        old = self.__rank
        self.__rank = new_rank
        print(f"[VIPMember] Admin อัปเกรด rank: {old} → {new_rank}")

    def vip_status_summary(self) -> str:
        spent = self.total_spent
        next_info = ""
        if self.__rank == self.RANK_SILVER:
            need = self.RANK_THRESHOLD["GOLD"] - spent
            next_info = f" | อีก {need:,.0f} บาท → GOLD"
        elif self.__rank == self.RANK_GOLD:
            need = self.RANK_THRESHOLD["PLATINUM"] - spent
            next_info = f" | อีก {need:,.0f} บาท → PLATINUM"
        else:
            next_info = " | ระดับสูงสุดแล้ว"
        return (f"rank={self.__rank} | ยอดสะสม {spent:,.2f} บาท"
                f" | ส่วนลด {self.DISCOUNT_RATE[self.__rank]}%{next_info}")

    def __repr__(self):
        return (f"<VIPMember id={self.user_id} name={self.name} "
                f"rank={self.__rank} spent={self.total_spent:,.2f}>")
    
# ─────────────────────────────────────────────
# Abstract Base: Staff
# ─────────────────────────────────────────────

class Staff(User,ABC):
    """
    คลาสนามธรรม (Abstract) สำหรับพนักงานในระบบ
    ทั้ง Artist และ Admin ต้อง inherit จากคลาสนี้
    """

    def __init__(self, staff_id: str, name: str, email: str):
        super().__init__(staff_id,name,email)

    # Getter & Setter
    @property
    def staff_id(self):
        return self.__staff_id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        self.__email = value

    @abstractmethod
    def view_schedule(self):
        pass

    @abstractmethod
    def update_profile(self, **kwargs):
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.__staff_id} name={self.__name}>"


# ─────────────────────────────────────────────
# Artist 
# ─────────────────────────────────────────────

class Artist(Staff):
    STATUS_PENDING = "PENDING"
    STATUS_VERIFIED = "VERIFIED"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, staff_id: str, name: str, email: str,
                 experience: int = 0):
        super().__init__(staff_id, name, email)
        self.__experience = experience
        self.__deposit_policy = None          
        self.__portfolio: Optional[Portfolio] = None
        self.__available_day_list: list[date] = []
        self.__request_list: list[StudioRequest] = []
        self.__booking_list: list = []
        self.__appointment_list: list = []
        self.__submitting: bool = False
        self.__status = self.STATUS_PENDING
        self.__calendar: Optional[Calendar] = None
        self.__ratings: list[Rating] = []

    @property
    def status(self):
        return self.__status
        
    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def deposit_policy(self):
        return self.__deposit_policy

    @property
    def calendar(self):
        return self.__calendar

    def verify_identity(self):
        self.__status = self.STATUS_VERIFIED
        print(f"[Artist] {self.name} ยืนยันตัวตนแล้ว")

    def set_calendar(self):
        self.__calendar = Calendar(owner_id=self.__staff_id)
        print(f"[Artist] {self.name} ตั้ง Calendar แล้ว")
        return self.__calendar

    def set_deposit_policy(self, policy):
        self.__deposit_policy = policy
        print(f"[Artist] {self.__name} deposit policy แล้ว: {policy}")

    def accept_job(self, booking) -> bool:
        if self.__status != self.STATUS_VERIFIED:
            raise Exception("Artist ต้องผ่านการยืนยันตัวตนก่อน")
        booking.accept()
        self.__booking_list.append(booking)
        print(f"[Artist] {self.name} รับงาน {booking.booking_id}")
        return True

    def reject_job(self, booking, reason: str = ""):
        booking.cancel()
        print(f"[Artist] {self.name} ปฏิเสธงาน {booking.booking_id}: {reason}")

    def complete_job(self, booking):
        booking.complete()
        print(f"[Artist] {self.name} เสร็จงาน {booking.booking_id}")

    def manage_time(self, event: Event):
        if self.__calendar is None:
            self.set_calendar()
        self.__calendar.add_event(event)

    def request_studio(self, request: StudioRequest):
        self.__request_list.append(request)
        request.submit()

    def add_rating(self, rating: Rating):
        self.__ratings.append(rating)

    def average_rating(self) -> float:
        if not self.__ratings:
            return 0.0
        return sum(r.score for r in self.__ratings) / len(self.__ratings)

    def view_schedule(self):
        if self.__calendar is None:
            print(f"[Artist] {self.name} ยังไม่มี Calendar")
            return []
        events = self.__calendar.view_monthly(
            datetime.now().year, datetime.now().month
        )
        print(f"[Artist] {self.name} มี {len(events)} งานเดือนนี้")
        return events

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"] # ส่งไปที่ setter ของ Staff
        if "experience" in kwargs:
            self.__experience = kwargs["experience"]
        print(f"[Artist] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Artist id={self.staff_id} name={self.name} status={self.__status}>"


# ─────────────────────────────────────────────
# Admin
# ─────────────────────────────────────────────

class Admin(Staff):
    def __init__(self, staff_id: str, name: str, email: str):
        super().__init__(staff_id, name, email)
        self.__requests: list[StudioRequest] = []

    def approve_artist(self, artist: Artist):
        artist.verify_identity()
        print(f"[Admin] อนุมัติ Artist {artist.name} แล้ว")

    def reject_artist(self, artist: Artist):
        # เปลี่ยน status โดยเรียกใช้ setter ที่เราสร้างไว้ใน Artist
        artist.status = Artist.STATUS_SUSPENDED
        print(f"[Admin] ปฏิเสธ Artist {artist.name}")

    def approve_studio(self, request: StudioRequest, studio_list: list):
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
        request.reject()

    def suspend_user(self, user: User):
        user.suspend()
        print(f"[Admin] ระงับ User {user.name} แล้ว")

    def manage_policy(self, policy_info: str):
        print(f"[Admin] อัปเดต policy: {policy_info}")

    def view_schedule(self):
        print(f"[Admin] {self.name} กำลังดู schedule overview")
        return []

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self.name = kwargs["name"]
        print(f"[Admin] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Admin id={self.staff_id} name={self.name}>"
    

    