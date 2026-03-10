"""
entities.py — Entity classes หลักของระบบ SoonSak
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional


class Coupon:
    """คูปองส่วนลด — discount เป็น % (0-100)"""

    def __init__(self, coupon_code: str, discount: float, expired: date):
        self._coupon_code = coupon_code
        self._discount = discount
        self._expired = expired

    @property
    def coupon_code(self):
        return self._coupon_code

    @property
    def discount(self):
        return self._discount

    def is_valid(self) -> bool:
        return date.today() <= self._expired

    def __repr__(self):
        return f"<Coupon code={self._coupon_code} discount={self._discount}% expires={self._expired}>"


class Rating:
    """คะแนนรีวิวจาก User หลัง complete job — score 1-5"""

    def __init__(self, rating_id: str, score: int, comment: str,
                 user_id: str, artist_id: str):
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


class TattooStyle:
    """สไตล์การสัก เช่น Minimalist, Japanese"""

    def __init__(self, style_id: str, name: str, description: str = ""):
        self._style_id = style_id
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"<TattooStyle {self._name}>"


class Portfolio:
    """Portfolio ของ Artist — Aggregation กับ TattooStyle"""

    def __init__(self, portfolio_id: str):
        self._portfolio_id = portfolio_id
        self._images: list[str] = []
        self._styles: list[TattooStyle] = []

    def add_image(self, image_url: str):
        if not image_url:
            raise ValueError("image_url ต้องไม่ว่าง")
        self._images.append(image_url)

    def remove_image(self, image_url: str):
        if image_url not in self._images:
            raise ValueError("ไม่พบรูปภาพนี้ใน portfolio")
        self._images.remove(image_url)

    def add_style(self, style: TattooStyle):
        self._styles.append(style)

    @property
    def images(self):
        return list(self._images)

    @property
    def styles(self):
        return list(self._styles)

    def __repr__(self):
        return f"<Portfolio id={self._portfolio_id} images={len(self._images)}>"


class Event:
    """Event ใน Calendar เช่น นัดลูกค้า, วันหยุด"""

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
        if event_name:
            self._event_name = event_name
        if description:
            self._description = description

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
    """ปฏิทินของ Artist — Composition กับ Event"""

    def __init__(self, owner_id: str):
        self._owner_id = owner_id
        self._events: list[Event] = []

    def add_event(self, event: Event):
        self._events.append(event)

    def view_monthly(self, year: int, month: int) -> list[Event]:
        return [e for e in self._events
                if e.date.year == year and e.date.month == month]

    def view_daily(self, target_date: date) -> list[Event]:
        return [e for e in self._events if e.date == target_date]

    def get_busy_dates(self) -> list[date]:
        return [e.date for e in self._events]

    def __repr__(self):
        return f"<Calendar owner={self._owner_id} events={len(self._events)}>"


class StudioRequest:
    """คำขอเปิด Studio จาก Artist — รอ Admin อนุมัติ
    Status: PENDING → APPROVED / REJECTED
    """

    STATUS_PENDING  = "PENDING"
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
        print(f"[StudioRequest] ส่งคำขอ {self._request_id} แล้ว รอ Admin อนุมัติ")

    def approve(self):
        if self._status != self.STATUS_PENDING:
            raise Exception("อนุมัติได้เฉพาะ PENDING เท่านั้น")
        self._status = self.STATUS_APPROVED
        print(f"[StudioRequest] {self._request_id} ได้รับการอนุมัติแล้ว")

    def reject(self):
        if self._status != self.STATUS_PENDING:
            raise Exception("ปฏิเสธได้เฉพาะ PENDING เท่านั้น")
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


class Studio:
    """Studio ของ Artist
    Status: OPEN / CLOSED
    """

    STATUS_OPEN   = "OPEN"
    STATUS_CLOSED = "CLOSED"

    def __init__(self, studio_id: str, name: str, location: str):
        self._studio_id = studio_id
        self._name = name
        self._location = location
        self._artist_list: list[str] = []
        self._status = self.STATUS_CLOSED

    def add_artist(self, artist_id: str):
        if artist_id in self._artist_list:
            raise ValueError(f"Artist {artist_id} อยู่ใน Studio นี้แล้ว")
        self._artist_list.append(artist_id)

    def delete_artist(self, artist_id: str):
        if artist_id not in self._artist_list:
            raise ValueError(f"ไม่พบ Artist {artist_id} ใน Studio นี้")
        self._artist_list.remove(artist_id)

    def open_studio(self):
        self._status = self.STATUS_OPEN
        print(f"[Studio] {self._name} เปิดแล้ว")

    def close_studio(self):
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


class User:
    """ผู้ใช้งานทั่วไป
    Status: ACTIVE / SUSPENDED
    จองพร้อมกันได้ max_bookings ครั้ง, จองล่วงหน้าได้ max_calendar วัน
    """

    STATUS_ACTIVE    = "ACTIVE"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, user_id: str, name: str, email: str, phone_number: str):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._phone_number = phone_number
        self._credit: float = 0.0
        self._status = self.STATUS_ACTIVE
        self._bookings_history: list = []
        self._coupon_list: list[Coupon] = []
        self._transaction_list: list = []
        self._appointment_list: list = []
        self._submitting: bool = False
        self._completed_tattoo_count: int = 0
        self._total_spent: float = 0.0  # ยอดสะสมจาก full payment
        self._max_calendar: int = 60
        self._max_bookings: int = 3

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

    @property
    def completed_tattoo_count(self):
        return self._completed_tattoo_count

    @property
    def total_spent(self):
        return self._total_spent

    def add_spent(self, amount: float):
        """เพิ่มยอดสะสม — เรียกหลัง pay_full สำเร็จ"""
        if amount > 0:
            self._total_spent += amount
            print(f"[User] {self._name} ยอดสะสม: {self._total_spent:.2f} บาท")

    def add_credit(self, amount: float):
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self._credit += amount

    def deduct_credit(self, amount: float):
        if amount > self._credit:
            raise ValueError("เครดิตไม่เพียงพอ")
        self._credit -= amount

    def view_history(self) -> list:
        return list(self._bookings_history)

    def add_history(self, booking):
        self._bookings_history.append(booking)

    def calculate_discount(self, base_price: float) -> float:
        """User ทั่วไปไม่มีส่วนลด — VIPMember จะ override"""
        return 0.0

    def add_coupon(self, coupon: Coupon):
        self._coupon_list.append(coupon)

    def use_coupon(self, coupon_code: str, base_price: float) -> float:
        """ใช้คูปอง คืนราคาหลังหักส่วนลด"""
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
        self._submitting = True
        print(f"[User] {self._name} ยืนยันการจองแล้ว")

    def suspend(self):
        self._status = self.STATUS_SUSPENDED
        print(f"[User] บัญชี {self._name} ถูกระงับ")

    def __repr__(self):
        return f"<User id={self._user_id} name={self._name} status={self._status}>"


class VIPMember(User):
    """สมาชิก VIP — Inheritance: User → VIPMember
    rank อัปเกรดอัตโนมัติตามยอดสะสม (_total_spent):
      SILVER   ≥  5,000 บาท (ส่วนลด 5%)
      GOLD     ≥ 15,000 บาท (ส่วนลด 10%)
      PLATINUM ≥ 30,000 บาท (ส่วนลด 15%)
    """

    RANK_SILVER   = "SILVER"
    RANK_GOLD     = "GOLD"
    RANK_PLATINUM = "PLATINUM"

    THRESHOLD_SILVER   =  5_000
    THRESHOLD_GOLD     = 15_000
    THRESHOLD_PLATINUM = 30_000

    DISCOUNT_SILVER   =  5
    DISCOUNT_GOLD     = 10
    DISCOUNT_PLATINUM = 15

    def __init__(self, user_id: str, name: str, email: str,
                 phone_number: str, rank: str = "SILVER"):
        super().__init__(user_id, name, email, phone_number)
        self._rank = rank
        self._max_bookings = 6    # VIP จองได้มากกว่า
        self._max_calendar = 120

    @property
    def rank(self):
        return self._rank

    def check_and_upgrade(self):
        """เช็คยอดสะสมและ upgrade rank อัตโนมัติ"""
        spent = self._total_spent
        if spent >= self.THRESHOLD_PLATINUM:
            new_rank = self.RANK_PLATINUM
        elif spent >= self.THRESHOLD_GOLD:
            new_rank = self.RANK_GOLD
        elif spent >= self.THRESHOLD_SILVER:
            new_rank = self.RANK_SILVER
        else:
            new_rank = self._rank

        if new_rank != self._rank:
            old_rank = self._rank
            self._rank = new_rank
            print(f"[VIPMember] 🎉 {self._name} อัปเกรด rank: {old_rank} → {new_rank} "
                  f"(ยอดสะสม {spent:,.2f} บาท)")

    def calculate_discount(self, base_price: float) -> float:
        """Override: คำนวณส่วนลดตาม rank (Polymorphism)"""
        if self._rank == self.RANK_PLATINUM:
            rate = self.DISCOUNT_PLATINUM
        elif self._rank == self.RANK_GOLD:
            rate = self.DISCOUNT_GOLD
        else:
            rate = self.DISCOUNT_SILVER
        discount = base_price * (rate / 100)
        print(f"[VIP] rank={self._rank} ส่วนลด {rate}% = {discount:.2f} บาท")
        return discount

    def upgrade_rank(self, new_rank: str):
        """Admin สั่ง upgrade rank แบบ manual"""
        if new_rank not in (self.RANK_SILVER, self.RANK_GOLD, self.RANK_PLATINUM):
            raise ValueError(f"Rank ไม่ถูกต้อง: {new_rank}")
        old = self._rank
        self._rank = new_rank
        print(f"[VIPMember] Admin อัปเกรด rank: {old} → {new_rank}")

    def _get_discount_rate(self) -> int:
        if self._rank == self.RANK_PLATINUM:
            return self.DISCOUNT_PLATINUM
        elif self._rank == self.RANK_GOLD:
            return self.DISCOUNT_GOLD
        return self.DISCOUNT_SILVER

    def vip_status_summary(self) -> str:
        spent = self._total_spent
        rate  = self._get_discount_rate()
        if self._rank == self.RANK_SILVER:
            next_info = f" | อีก {self.THRESHOLD_GOLD - spent:,.0f} บาท → GOLD"
        elif self._rank == self.RANK_GOLD:
            next_info = f" | อีก {self.THRESHOLD_PLATINUM - spent:,.0f} บาท → PLATINUM"
        else:
            next_info = " | ระดับสูงสุดแล้ว"
        return f"rank={self._rank} | ยอดสะสม {spent:,.2f} บาท | ส่วนลด {rate}%{next_info}"

    def __repr__(self):
        return (f"<VIPMember id={self._user_id} name={self._name} "
                f"rank={self._rank} spent={self._total_spent:,.2f}>")
    
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


class Artist(Staff):
    """ช่างสักในระบบ — Inheritance: Staff → Artist
    Status: PENDING → VERIFIED → SUSPENDED
    """

    STATUS_PENDING   = "PENDING"
    STATUS_VERIFIED  = "VERIFIED"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, staff_id: str, name: str, email: str, experience: int = 0):
        super().__init__(staff_id, name, email)
        self._experience = experience
        self._deposit_policy = None
        self._portfolio: Optional[Portfolio] = None
        self._available_day_list: list[date] = []
        self._request_list: list[StudioRequest] = []
        self._booking_list: list = []
        self._appointment_list: list = []
        self._submitting: bool = False
        self._status = self.STATUS_PENDING
        self._calendar: Optional[Calendar] = None
        self._ratings: list[Rating] = []

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
        self._status = self.STATUS_VERIFIED
        print(f"[Artist] {self._name} ยืนยันตัวตนแล้ว")

    def set_calendar(self):
        self._calendar = Calendar(owner_id=self._staff_id)
        return self._calendar

    def set_deposit_policy(self, policy):
        self._deposit_policy = policy
        print(f"[Artist] {self._name} ตั้ง deposit policy แล้ว: {policy}")

    def accept_job(self, booking) -> bool:
        if self._status != self.STATUS_VERIFIED:
            raise Exception("Artist ต้องผ่านการยืนยันตัวตนก่อน")
        booking.accept()
        self._booking_list.append(booking)
        print(f"[Artist] {self._name} รับงาน {booking.booking_id}")
        return True

    def reject_job(self, booking, reason: str = ""):
        booking.cancel()
        print(f"[Artist] {self._name} ปฏิเสธงาน {booking.booking_id}: {reason}")

    def complete_job(self, booking):
        booking.complete()
        print(f"[Artist] {self._name} เสร็จงาน {booking.booking_id}")

    def manage_time(self, event: Event):
        if self._calendar is None:
            self.set_calendar()
        self._calendar.add_event(event)

    def request_studio(self, request: StudioRequest):
        self._request_list.append(request)
        request.submit()

    def add_rating(self, rating: Rating):
        self._ratings.append(rating)

    def average_rating(self) -> float:
        if not self._ratings:
            return 0.0
        return sum(r.score for r in self._ratings) / len(self._ratings)

    def view_schedule(self):
        if self._calendar is None:
            return []
        return self._calendar.view_monthly(datetime.now().year, datetime.now().month)

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self._name = kwargs["name"]
        if "experience" in kwargs:
            self._experience = kwargs["experience"]
        print(f"[Artist] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Artist id={self._staff_id} name={self._name} status={self._status}>"


class Admin(Staff):
    """ผู้ดูแลระบบ — Inheritance: Staff → Admin"""

    def __init__(self, staff_id: str, name: str, email: str):
        super().__init__(staff_id, name, email)
        self._requests: list[StudioRequest] = []

    def approve_artist(self, artist: Artist):
        artist.verify_identity()
        print(f"[Admin] อนุมัติ Artist {artist.name} แล้ว")

    def reject_artist(self, artist: Artist):
        artist._status = Artist.STATUS_SUSPENDED
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
        return []

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self._name = kwargs["name"]
        print(f"[Admin] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Admin id={self._staff_id} name={self._name}>"