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
            raise ValueError("Score must be between 1-5")
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
    POPULAR_STYLES = [
        "Traditional", "Realism", "Watercolor", "Japanese",
        "Tribal", "Geometric", "Blackwork", "New School",
        "Minimalist", "Neo-Traditional"
    ]
    
    def __init__(self, style_id: str, name: str, description: str = ""):
        if not style_id or not style_id.strip():
            raise ValueError("style_id cannot be empty")
        if not name or not name.strip():
            raise ValueError("name cannot be empty")
            
        self.__style_id = style_id.strip()
        self.__name = name.strip()
        self.__description = description.strip()
        self.__created_at = datetime.now()
    
    @property
    def style_id(self) -> str:
        return self.__style_id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @description.setter
    def description(self, value: str):
        self.__description = value.strip() if value else ""
    
    def update_description(self, new_description: str) -> None:
        self.description = new_description
        print(f"[TattooStyle] Updated description for '{self.__name}'")
    
    def is_popular(self) -> bool:
        return self.__name in self.POPULAR_STYLES
    
    def get_summary(self) -> str:
        popular = "* " if self.is_popular() else ""
        return f"{popular}{self.__name} ({self.__style_id})"
    
    def __repr__(self) -> str:
        return f"<TattooStyle id={self.__style_id} name={self.__name}>"
    
    def __str__(self) -> str:
        return self.__name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TattooStyle):
            return False
        return self.__style_id == other.style_id
    
    def __hash__(self) -> int:
        return hash(self.__style_id)


class Portfolio:
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    MAX_IMAGES = 50
    
    def __init__(self, portfolio_id: str, owner_id: str = "", 
                 style: Optional['TattooStyle'] = None, description: str = ""):
        if not portfolio_id or not portfolio_id.strip():
            raise ValueError("portfolio_id cannot be empty")
            
        self.__portfolio_id = portfolio_id.strip()
        self.__owner_id = owner_id.strip() if owner_id else ""
        self.__style = style
        self.__images: list = []
        self.__styles: list = []
        self.__description = description.strip()
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()
        self.__is_public = True
        self.__view_count = 0
    
    @property
    def portfolio_id(self) -> str:
        return self.__portfolio_id
    
    @property
    def owner_id(self) -> str:
        return self.__owner_id
    
    @property
    def style(self) -> Optional['TattooStyle']:
        return self.__style
    
    @property
    def description(self) -> str:
        return self.__description
    
    @property
    def images(self) -> list:
        return list(self.__images)
    
    @property
    def styles(self) -> list:
        result = list(self.__styles)
        if self.__style and self.__style not in result:
            result.append(self.__style)
        return result
    
    @property
    def image_count(self) -> int:
        return len(self.__images)
    
    @property
    def is_public(self) -> bool:
        return self.__is_public
    
    @property
    def view_count(self) -> int:
        return self.__view_count
    
    @property
    def created_at(self) -> datetime:
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        return self.__updated_at
    
    @style.setter
    def style(self, new_style: Optional['TattooStyle']):
        if new_style is not None and not isinstance(new_style, TattooStyle):
            raise TypeError("style must be TattooStyle object or None")
        self.__style = new_style
        self.__touch()
    
    @description.setter
    def description(self, value: str):
        self.__description = value.strip() if value else ""
        self.__touch()
    
    def add_image(self, image: str) -> bool:
        if not image or not image.strip():
            raise ValueError("image path/URL cannot be empty")
        
        image = image.strip()
        
        if image in self.__images:
            raise ValueError(f"Image '{image}' already exists in portfolio")
        
        if len(self.__images) >= self.MAX_IMAGES:
            raise ValueError(f"Portfolio is full (max {self.MAX_IMAGES} images)")
        
        if not image.startswith(('http://', 'https://')):
            if not any(image.lower().endswith(fmt) for fmt in self.SUPPORTED_FORMATS):
                print(f"Warning: '{image}' may not be a supported image format")
        
        self.__images.append(image)
        self.__touch()
        print(f"[Portfolio] Added image '{image}' ({self.image_count}/{self.MAX_IMAGES})")
        return True
    
    def remove_image(self, image: str) -> bool:
        if image not in self.__images:
            raise ValueError(f"Image '{image}' not found in portfolio")
        
        self.__images.remove(image)
        self.__touch()
        print(f"[Portfolio] Removed image '{image}' ({self.image_count}/{self.MAX_IMAGES})")
        return True
    
    def remove_image_by_index(self, index: int) -> str:
        if not 0 <= index < len(self.__images):
            raise IndexError(f"Index {index} out of range (total images: {len(self.__images)})")
        
        removed = self.__images.pop(index)
        self.__touch()
        print(f"[Portfolio] Removed image at index {index}: '{removed}'")
        return removed
    
    def clear_images(self) -> int:
        count = len(self.__images)
        self.__images.clear()
        self.__touch()
        print(f"[Portfolio] Cleared all {count} images")
        return count
    
    def get_images(self) -> list:
        return list(self.__images)
    
    def get_image_at(self, index: int) -> str:
        if not 0 <= index < len(self.__images):
            raise IndexError(f"Index {index} out of range")
        return self.__images[index]
    
    def has_image(self, image: str) -> bool:
        return image in self.__images
    
    def add_style(self, style: TattooStyle) -> None:
        if not isinstance(style, TattooStyle):
            raise TypeError("style must be TattooStyle object")
        if style not in self.__styles:
            self.__styles.append(style)
            self.__touch()
    
    def remove_style(self, style: TattooStyle) -> None:
        if style in self.__styles:
            self.__styles.remove(style)
            self.__touch()
    
    def update_description(self, description: str) -> None:
        self.description = description
        print(f"[Portfolio] Updated description")
    
    def append_description(self, additional_text: str) -> None:
        self.__description = f"{self.__description}\n{additional_text}".strip()
        self.__touch()
    
    def change_style(self, new_style: TattooStyle) -> None:
        old_style = self.__style
        self.style = new_style
        old_name = old_style.name if old_style else "None"
        new_name = new_style.name if new_style else "None"
        print(f"[Portfolio] Changed style: {old_name} -> {new_name}")
    
    def publish(self) -> None:
        if self.__is_public:
            print("[Portfolio] Portfolio is already published")
            return
        self.__is_public = True
        self.__touch()
        print("[Portfolio] Published portfolio")
    
    def unpublish(self) -> None:
        if not self.__is_public:
            print("[Portfolio] Portfolio is already private")
            return
        self.__is_public = False
        self.__touch()
        print("[Portfolio] Unpublished portfolio")
    
    def increment_view(self) -> int:
        self.__view_count += 1
        return self.__view_count
    
    def is_empty(self) -> bool:
        return len(self.__images) == 0
    
    def is_full(self) -> bool:
        return len(self.__images) >= self.MAX_IMAGES
    
    def can_add_images(self, count: int = 1) -> bool:
        return len(self.__images) + count <= self.MAX_IMAGES
    
    def get_summary(self) -> str:
        visibility = "Public" if self.__is_public else "Private"
        style_name = self.__style.name if self.__style else "No style"
        owner = f"Owner: {self.__owner_id}" if self.__owner_id else "No owner"
        return (
            f"Portfolio: {self.__portfolio_id}\n"
            f"  {owner}\n"
            f"  Style      : {style_name}\n"
            f"  Images     : {self.image_count}/{self.MAX_IMAGES}\n"
            f"  Visibility : {visibility}\n"
            f"  Views      : {self.__view_count}\n"
            f"  Updated    : {self.__updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
    
    def list_images(self) -> str:
        if self.is_empty():
            return "No images in portfolio"
        
        lines = [f"Images in Portfolio ({self.image_count} images):"]
        for i, img in enumerate(self.__images):
            lines.append(f"  [{i}] {img}")
        return "\n".join(lines)
    
    def __touch(self) -> None:
        self.__updated_at = datetime.now()
    
    def __repr__(self) -> str:
        style_name = self.__style.name if self.__style else "None"
        return (f"<Portfolio id={self.__portfolio_id} "
                f"style={style_name} images={self.image_count}>")
    
    def __str__(self) -> str:
        style_name = self.__style.name if self.__style else "No style"
        return f"{self.__portfolio_id} ({style_name} - {self.image_count} images)"
    
    def __len__(self) -> int:
        return len(self.__images)
    
    def __contains__(self, image: str) -> bool:
        return image in self.__images
    
    def __iter__(self):
        return iter(self.__images)
    
    def __getitem__(self, index: int) -> str:
        return self.__images[index]


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
        print(f"[StudioRequest] Submitted request {self.__request_id}, waiting for admin approval")

    def approve(self):
        if self.__status != self.STATUS_PENDING:
            raise Exception("Can only approve PENDING requests")
        self.__status = self.STATUS_APPROVED
        print(f"[StudioRequest] {self.__request_id} approved")

    def reject(self):
        if self.__status != self.STATUS_PENDING:
            raise Exception("Can only reject PENDING requests")
        self.__status = self.STATUS_REJECTED
        print(f"[StudioRequest] {self.__request_id} rejected")

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
            raise ValueError(f"Artist {artist_id} already in studio")
        self.__artist_list.append(artist_id)

    def delete_artist(self, artist_id: str):
        if artist_id not in self.__artist_list:
            raise ValueError(f"Artist {artist_id} not found in studio")
        self.__artist_list.remove(artist_id)

    def open_studio(self):
        self.__status = self.STATUS_OPEN
        print(f"[Studio] {self.__name} opened")

    def close_studio(self):
        self.__status = self.STATUS_CLOSED
        print(f"[Studio] {self.__name} closed")

    @property
    def studio_id(self): return self.__studio_id

    @property
    def name(self): return self.__name

    @property
    def status(self): return self.__status

    def __repr__(self):
        return f"<Studio id={self.__studio_id} name={self.__name} status={self.__status}>"


class User:
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

    def add_spent(self, amount: float):
        if amount > 0:
            self.__total_spent += amount
            print(f"[User] {self.__name} total spent: {self.__total_spent:.2f} THB")

    def add_credit(self, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        self.__credit += amount

    def deduct_credit(self, amount: float):
        if amount > self.__credit:
            raise ValueError("Insufficient credit")
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
                    raise ValueError("Coupon has expired")
                discount_amount = base_price * (coupon.discount / 100)
                self.__coupon_list.remove(coupon)
                print(f"[User] Used coupon {coupon_code} - {coupon.discount}% discount")
                return base_price - discount_amount
        raise ValueError(f"Coupon {coupon_code} not found")

    def submit(self):
        self.__submitting = True
        print(f"[User] {self.__name} confirmed booking")

    def suspend(self):
        self.__status = self.STATUS_SUSPENDED
        print(f"[User] Account {self.__name} suspended")

    def __repr__(self):
        return f"<User id={self.__user_id} name={self.__name} status={self.__status}>"


class VIPMember(User):
    RANK_SILVER   = "SILVER"
    RANK_GOLD     = "GOLD"
    RANK_PLATINUM = "PLATINUM"

    THRESHOLD_SILVER   = 15_000
    THRESHOLD_GOLD     = 25_000
    THRESHOLD_PLATINUM = 40_000

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
            print(f"[VIPMember] {self._name} upgraded rank: {old_rank} -> {new_rank} "
                  f"(total spent {spent:,.2f} THB)")

    def calculate_discount(self, base_price: float) -> float:
        if self.__rank == self.RANK_PLATINUM:
            rate = self.DISCOUNT_PLATINUM
        elif self.__rank == self.RANK_GOLD:
            rate = self.DISCOUNT_GOLD
        else:
            rate = self.DISCOUNT_SILVER
        discount = base_price * (rate / 100)
        print(f"[VIP] rank={self.__rank} discount {rate}% = {discount:.2f} THB")
        return discount

    def upgrade_rank(self, new_rank: str):
        if new_rank not in (self.RANK_SILVER, self.RANK_GOLD, self.RANK_PLATINUM):
            raise ValueError(f"Invalid rank: {new_rank}")
        old = self.__rank
        self.__rank = new_rank
        print(f"[VIPMember] Admin upgraded rank: {old} -> {new_rank}")

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
            next_info = f" | {self.THRESHOLD_GOLD - spent:,.0f} THB more to GOLD"
        elif self.__rank == self.RANK_GOLD:
            next_info = f" | {self.THRESHOLD_PLATINUM - spent:,.0f} THB more to PLATINUM"
        else:
            next_info = " | Max rank achieved"
        return f"rank={self.__rank} | total spent {spent:,.2f} THB | discount {rate}%{next_info}"

    def __repr__(self):
        return (f"<VIPMember id={self._user_id} name={self._name} "
                f"rank={self.__rank} spent={self._total_spent:,.2f}>")


class Staff(User, ABC):
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
    STATUS_PENDING   = "PENDING"
    STATUS_VERIFIED  = "VERIFIED"
    STATUS_SUSPENDED = "SUSPENDED"

    def __init__(self, staff_id: str, name: str, email: str, password: str, experience: int = 0):
        super().__init__(staff_id, name, email, password)
        self.__experience = experience
        self.__calendar = Calendar(staff_id)
        self.__booking_list: list = []
        self.__ratings: list = []
        self.__request_list: list = []
        self.__available_days: list[date] = []
        self.__status = "pending"
        self.__deposit_policy = None

    def set_available_days(self, days: list):
        self.__available_days = days
        print(f"[Artist] {self._name} set {len(days)} available days")

    def add_available_day(self, day):
        if day not in self.__available_days:
            self.__available_days.append(day)

    def get_available_days(self):
        return list(self.__available_days)

    def is_available(self, target_date):
        if target_date not in self.__available_days:
            return False
        busy = self.__calendar.get_busy_dates()
        return target_date not in busy

    def view_available_days(self):
        busy = self.__calendar.get_busy_dates()
        return [d for d in self.__available_days if d not in busy]

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
        print(f"[Artist] {self._name} identity verified")

    def set_calendar(self) -> Calendar:
        self.__calendar = Calendar(owner_id=self._user_id)
        return self.__calendar

    def set_deposit_policy(self, policy):
        self.__deposit_policy = policy
        print(f"[Artist] {self._name} set deposit policy: {policy}")

    def accept_job(self, booking) -> bool:
        if self.__status != self.STATUS_VERIFIED:
            raise Exception("Artist must be verified first")
        booking.accept()
        self.__booking_list.append(booking)
        print(f"[Artist] {self._name} accepted job {booking.booking_id}")
        return True

    def reject_job(self, booking, reason: str = ""):
        booking.cancel()
        print(f"[Artist] {self._name} rejected job {booking.booking_id}: {reason}")

    def complete_job(self, booking):
        booking.complete()
        print(f"[Artist] {self._name} completed job {booking.booking_id}")

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
        print(f"[Artist] Profile updated")

    def __repr__(self):
        return f"<Artist id={self._user_id} name={self._name} status={self.__status}>"


class Admin(Staff):
    def __init__(self, staff_id: str, name: str, email: str, password: str):
        super().__init__(staff_id, name, email, password)
        self.__requests: list = []

    @property
    def staff_id(self): return self._user_id

    def approve_artist(self, artist: Artist):
        artist.verify_identity()
        print(f"[Admin] Approved artist {artist.name}")

    def reject_artist(self, artist: Artist):
        artist._status = Artist.STATUS_SUSPENDED
        print(f"[Admin] Rejected artist {artist.name}")

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
        print(f"[Admin] Suspended user {user.name}")

    def manage_policy(self, policy_info: str):
        print(f"[Admin] Updated policy: {policy_info}")

    def view_schedule(self):
        return []

    def update_profile(self, **kwargs):
        if "name" in kwargs:
            self._name = kwargs["name"]
        print(f"[Admin] Profile updated")

    def __repr__(self):
        return f"<Admin id={self._user_id} name={self._name}>"
