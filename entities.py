"""
entities.py — Entity classes หลักของระบบ SoonSak
- ทุก attribute เป็น private (__attr)
- ไม่ใช้ Dict เลย ใช้ list ทั้งหมด
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional


class Mail:
    def __init__(self, sender_id: str, receiver_id: str, message: str):
        self.__sender_id = sender_id
        self.__receiver_id = receiver_id
        self.__message = message
        self.__sent_time = datetime.now()

    @property
    def sender_id(self): return self.__sender_id

    @property
    def receiver_id(self): return self.__receiver_id

    @property
    def message(self): return self.__message

    def __repr__(self):
        return f"<Mail from={self.__sender_id} to={self.__receiver_id}>"


class Mailbox:
    def __init__(self, user_id: str):
        self.__user_id = user_id
        self.__messages: list = []

    def receive_message(self, mail: Mail):
        self.__messages.append(mail)

    def send_message(self, receiver_mailbox: "Mailbox", message: str):
        mail = Mail(self.__user_id, receiver_mailbox.__user_id, message)
        receiver_mailbox.receive_message(mail)

    def get_messages(self) -> list:
        return list(self.__messages)


class Coupon:
    def __init__(self, coupon_code: str, discount: float, expired: date):
        self.__coupon_code = coupon_code
        self.__discount = discount
        self.__expired = expired

    @property
    def coupon_code(self): return self.__coupon_code

    @property
    def discount(self): return self.__discount

    def is_valid(self) -> bool:
        return date.today() <= self.__expired

    def __repr__(self):
        return f"<Coupon code={self.__coupon_code} discount={self.__discount}% expires={self.__expired}>"


class Rating:
    def __init__(self, rating_id: str, score: int, comment: str, user_id: str, artist_id: str):
        if not (1 <= score <= 5):
            raise ValueError("Score ต้องอยู่ระหว่าง 1-5")
        self.__rating_id = rating_id
        self.__score = score
        self.__comment = comment
        self.__user_id = user_id
        self.__artist_id = artist_id
        self.__created_at = datetime.now()

    @property
    def rating_id(self): return self.__rating_id

    @property
    def score(self): return self.__score

    @property
    def artist_id(self): return self.__artist_id

    def __repr__(self):
        return f"<Rating id={self.__rating_id} score={self.__score}/5>"


class TattooStyle:
    def __init__(self, style_id: str, name: str, description: str = ""):
        self.__style_id = style_id
        self.__name = name
        self.__description = description

    @property
    def name(self): return self.__name

    def __repr__(self):
        return f"<TattooStyle {self.__name}>"


class Portfolio:
    def __init__(self, portfolio_id: str):
        self.__portfolio_id = portfolio_id
        self.__images: list = []
        self.__styles: list = []

    def add_image(self, image_url: str):
        if not image_url:
            raise ValueError("image_url ต้องไม่ว่าง")
        self.__images.append(image_url)

    def remove_image(self, image_url: str):
        if image_url not in self.__images:
            raise ValueError("ไม่พบรูปภาพนี้ใน portfolio")
        self.__images.remove(image_url)

    def add_style(self, style: TattooStyle):
        self.__styles.append(style)

    @property
    def images(self): return list(self.__images)

    @property
    def styles(self): return list(self.__styles)


class Event:
    def __init__(self, event_id: str, event_name: str, event_date: date,
                 start_time: str, end_time: str, description: str = ""):
        self.__event_id = event_id
        self.__event_name = event_name
        self.__date = event_date
        self.__start_time = start_time
        self.__end_time = end_time
        self.__description = description

    @property
    def date(self): return self.__date

    @property
    def event_name(self): return self.__event_name


class Calendar:
    def __init__(self, owner_id: str):
        self.__owner_id = owner_id
        self.__events: list = []

    def add_event(self, event: Event):
        self.__events.append(event)

    def view_monthly(self, year: int, month: int) -> list:
        return [e for e in self.__events if e.date.year == year and e.date.month == month]

    def view_daily(self, target_date: date) -> list:
        return [e for e in self.__events if e.date == target_date]

    def get_busy_dates(self) -> list:
        return [e.date for e in self.__events]

    def __repr__(self):
        return f"<Calendar owner={self.__owner_id} events={len(self.__events)}>"


class StudioRequest:
    """Status: PENDING → APPROVED / REJECTED"""

    STATUS_PENDING  = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    def __init__(self, request_id: str, artist_id: str, studio_name: str, location: str):
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
            raise Exception("อนุมัติได้เฉพาะ PENDING เท่านั้น")
        self.__status = self.STATUS_APPROVED
        print(f"[StudioRequest] {self.__request_id} ได้รับการอนุมัติแล้ว")

    def reject(self):
        if self.__status != self.STATUS_PENDING:
            raise Exception("ปฏิเสธได้เฉพาะ PENDING เท่านั้น")
        self.__status = self.STATUS_REJECTED
        print(f"[StudioRequest] {self.__request_id} ถูกปฏิเสธ")

    @property
    def request_id(self): return self.__request_id

    @property
    def status(self): return self.__status

    @property
    def studio_name(self): return self.__studio_name

    @property
    def artist_id(self): return self.__artist_id

    @property
    def location(self): return self.__location

    def __repr__(self):
        return f"<StudioRequest id={self.__request_id} studio={self.__studio_name} status={self.__status}>"


class Studio:
    """Status: OPEN / CLOSED"""

    STATUS_OPEN   = "OPEN"
    STATUS_CLOSED = "CLOSED"

    def __init__(self, studio_id: str, name: str, location: str):
        self.__studio_id = studio_id
        self.__name = name
        self.__location = location
        self.__artist_list: list = []
        self.__status = self.STATUS_CLOSED

    def add_artist(self, artist_id: str):
        if artist_id in self.__artist_list:
            raise ValueError(f"Artist {artist_id} อยู่ใน Studio นี้แล้ว")
        self.__artist_list.append(artist_id)

    def delete_artist(self, artist_id: str):
        if artist_id not in self.__artist_list:
            raise ValueError(f"ไม่พบ Artist {artist_id} ใน Studio นี้")
        self.__artist_list.remove(artist_id)

    def open_studio(self):
        self.__status = self.STATUS_OPEN
        print(f"[Studio] {self.__name} เปิดแล้ว")

    def close_studio(self):
        self.__status = self.STATUS_CLOSED
        print(f"[Studio] {self.__name} ปิดแล้ว")

    @property
    def studio_id(self): return self.__studio_id

    @property
    def name(self): return self.__name

    @property
    def status(self): return self.__status

    def __repr__(self):
        return f"<Studio id={self.__studio_id} name={self.__name} status={self.__status}>"


class User:
    """Status: ACTIVE / SUSPENDED"""

    STATUS_ACTIVE    = "ACTIVE"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, user_id: str, name: str, email: str, phone_number: str, password: str):
        self.__user_id = user_id
        self.__name = name
        self.__email = email
        self.__mailbox = Mailbox(user_id)
        self.__phone_number = phone_number
        self.__credit: float = 0.0
        self.__status = self.STATUS_ACTIVE
        self.__bookings_history: list = []
        self.__coupon_list: list = []
        self.__transaction_list: list = []
        self.__appointment_list: list = []
        self.__submitting: bool = False
        self.__completed_tattoo_count: int = 0
        self.__total_spent: float = 0.0
        self.__max_calendar: int = 60
        self.__max_bookings: int = 3
        self.__password = password

    def check_password(self, password: str) -> bool:
        return self.__password == password

    # ── public properties ──
    @property
    def user_id(self): return self.__user_id

    @property
    def name(self): return self.__name

    @property
    def email(self): return self.__email

    @property
    def status(self): return self.__status

    @property
    def max_bookings(self): return self.__max_bookings

    @property
    def max_calendar(self): return self.__max_calendar

    @property
    def credit(self): return self.__credit

    @property
    def completed_tattoo_count(self): return self.__completed_tattoo_count

    @property
    def total_spent(self): return self.__total_spent

    @property
    def mailbox(self): return self.__mailbox

    # ── protected properties (สำหรับ subclass / controller เข้าถึง) ──
    @property
    def _user_id(self): return self.__user_id

    @property
    def _name(self): return self.__name

    @_name.setter
    def _name(self, v): self.__name = v

    @property
    def _email(self): return self.__email

    @_email.setter
    def _email(self, v): self.__email = v

    @property
    def _phone_number(self): return self.__phone_number

    @property
    def _password(self): return self.__password

    @property
    def _status(self): return self.__status

    @_status.setter
    def _status(self, v): self.__status = v

    @property
    def _total_spent(self): return self.__total_spent

    @_total_spent.setter
    def _total_spent(self, v): self.__total_spent = v

    @property
    def _completed_tattoo_count(self): return self.__completed_tattoo_count

    @_completed_tattoo_count.setter
    def _completed_tattoo_count(self, v): self.__completed_tattoo_count = v

    @property
    def _credit(self): return self.__credit

    @_credit.setter
    def _credit(self, v): self.__credit = v

    @property
    def _max_bookings(self): return self.__max_bookings

    @_max_bookings.setter
    def _max_bookings(self, v): self.__max_bookings = v

    @property
    def _max_calendar(self): return self.__max_calendar

    @_max_calendar.setter
    def _max_calendar(self, v): self.__max_calendar = v

    @property
    def _bookings_history(self): return self.__bookings_history

    @property
    def _coupon_list(self): return self.__coupon_list

    # ── methods ──
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


class VIPMember(User):
    """Inheritance: User → VIPMember"""

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
                 phone_number: str, password: str, rank: str = "SILVER"):
        super().__init__(user_id, name, email, phone_number, password)
        self.__rank = rank
        self._max_bookings = 6
        self._max_calendar = 120

    @property
    def rank(self): return self.__rank

    @property
    def _rank(self): return self.__rank

    @_rank.setter
    def _rank(self, v): self.__rank = v

    def check_and_upgrade(self):
        spent = self._total_spent
        if spent >= self.THRESHOLD_PLATINUM:
            new_rank = self.RANK_PLATINUM
        elif spent >= self.THRESHOLD_GOLD:
            new_rank = self.RANK_GOLD
        elif spent >= self.THRESHOLD_SILVER:
            new_rank = self.RANK_SILVER
        else:
            new_rank = self.__rank
        if new_rank != self.__rank:
            old_rank = self.__rank
            self.__rank = new_rank
            print(f"[VIPMember] {self._name} อัปเกรด rank: {old_rank} → {new_rank} "
                  f"(ยอดสะสม {spent:,.2f} บาท)")

    def calculate_discount(self, base_price: float) -> float:
        if self.__rank == self.RANK_PLATINUM:
            rate = self.DISCOUNT_PLATINUM
        elif self.__rank == self.RANK_GOLD:
            rate = self.DISCOUNT_GOLD
        else:
            rate = self.DISCOUNT_SILVER
        discount = base_price * (rate / 100)
        print(f"[VIP] rank={self.__rank} ส่วนลด {rate}% = {discount:.2f} บาท")
        return discount

    def upgrade_rank(self, new_rank: str):
        if new_rank not in (self.RANK_SILVER, self.RANK_GOLD, self.RANK_PLATINUM):
            raise ValueError(f"Rank ไม่ถูกต้อง: {new_rank}")
        old = self.__rank
        self.__rank = new_rank
        print(f"[VIPMember] Admin อัปเกรด rank: {old} → {new_rank}")

    def __get_discount_rate(self) -> int:
        if self.__rank == self.RANK_PLATINUM:
            return self.DISCOUNT_PLATINUM
        elif self.__rank == self.RANK_GOLD:
            return self.DISCOUNT_GOLD
        return self.DISCOUNT_SILVER

    def vip_status_summary(self) -> str:
        spent = self._total_spent
        rate  = self.__get_discount_rate()
        if self.__rank == self.RANK_SILVER:
            next_info = f" | อีก {self.THRESHOLD_GOLD - spent:,.0f} บาท → GOLD"
        elif self.__rank == self.RANK_GOLD:
            next_info = f" | อีก {self.THRESHOLD_PLATINUM - spent:,.0f} บาท → PLATINUM"
        else:
            next_info = " | ระดับสูงสุดแล้ว"
        return f"rank={self.__rank} | ยอดสะสม {spent:,.2f} บาท | ส่วนลด {rate}%{next_info}"

    def __repr__(self):
        return (f"<VIPMember id={self._user_id} name={self._name} "
                f"rank={self.__rank} spent={self._total_spent:,.2f}>")


class Staff(User, ABC):
    """Abstract สำหรับพนักงาน — Artist และ Admin ต้อง inherit"""

    def __init__(self, staff_id: str, name: str, email: str, password: str):
        super().__init__(staff_id, name, email, "", password)
        self.__staff_mailbox = Mailbox(staff_id)

    @property
    def staff_id(self): return self._user_id

    @property
    def name(self): return self._name

    @name.setter
    def name(self, value): self._name = value

    @property
    def email(self): return self._email

    @email.setter
    def email(self, value): self._email = value

    @property
    def mailbox(self): return self.__staff_mailbox

    @property
    def _mailbox(self): return self.__staff_mailbox

    @abstractmethod
    def view_schedule(self): pass

    @abstractmethod
    def update_profile(self, **kwargs): pass

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self._user_id} name={self._name}>"


class Artist(Staff):
    """Status: PENDING → VERIFIED → SUSPENDED"""

    STATUS_PENDING   = "PENDING"
    STATUS_VERIFIED  = "VERIFIED"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, staff_id: str, name: str, email: str, password: str, experience: int = 0):
        super().__init__(staff_id, name, email, password)
        self.__experience = experience
        self.__deposit_policy = None
        self.__portfolio: Optional[Portfolio] = None
        self.__available_day_list: list = []
        self.__request_list: list = []
        self.__booking_list: list = []
        self.__appointment_list: list = []
        self.__submitting: bool = False
        self.__status = self.STATUS_PENDING
        self.__calendar: Optional[Calendar] = None
        self.__ratings: list = []

    @property
    def staff_id(self): return self._user_id

    @property
    def status(self): return self.__status

    @property
    def deposit_policy(self): return self.__deposit_policy

    @property
    def calendar(self): return self.__calendar

    @property
    def _experience(self): return self.__experience

    @property
    def _status(self): return self.__status

    @_status.setter
    def _status(self, v): self.__status = v

    def verify_identity(self):
        self.__status = self.STATUS_VERIFIED
        print(f"[Artist] {self._name} ยืนยันตัวตนแล้ว")

    def set_calendar(self) -> Calendar:
        self.__calendar = Calendar(owner_id=self._user_id)
        return self.__calendar

    def set_deposit_policy(self, policy):
        self.__deposit_policy = policy
        print(f"[Artist] {self._name} ตั้ง deposit policy แล้ว: {policy}")

    def accept_job(self, booking) -> bool:
        if self.__status != self.STATUS_VERIFIED:
            raise Exception("Artist ต้องผ่านการยืนยันตัวตนก่อน")
        booking.accept()
        self.__booking_list.append(booking)
        print(f"[Artist] {self._name} รับงาน {booking.booking_id}")
        return True

    def reject_job(self, booking, reason: str = ""):
        booking.cancel()
        print(f"[Artist] {self._name} ปฏิเสธงาน {booking.booking_id}: {reason}")

    def complete_job(self, booking):
        booking.complete()
        print(f"[Artist] {self._name} เสร็จงาน {booking.booking_id}")

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
            return []
        return self.__calendar.view_monthly(datetime.now().year, datetime.now().month)

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self._name = kwargs["name"]
        if "experience" in kwargs:
            self.__experience = kwargs["experience"]
        print(f"[Artist] อัปเดต profile แล้ว")

    def __repr__(self):
        return f"<Artist id={self._user_id} name={self._name} status={self.__status}>"


class Admin(Staff):
    """ผู้ดูแลระบบ — Inheritance: Staff → Admin"""

    def __init__(self, staff_id: str, name: str, email: str, password: str):
        super().__init__(staff_id, name, email, password)
        self.__requests: list = []

    @property
    def staff_id(self): return self._user_id

    
        
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
            location=request.location
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
        return f"<Admin id={self._user_id} name={self._name}>"