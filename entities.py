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
    """
    คลาสสำหรับเก็บข้อมูลสไตล์รอยสัก
    
    Attributes:
        style_id: รหัสเฉพาะของสไตล์
        name: ชื่อสไตล์ (เช่น Traditional, Realism, Watercolor)
        description: คำอธิบายสไตล์
    """
    
    # Class variable: Popular tattoo styles
    POPULAR_STYLES = [
        "Traditional", "Realism", "Watercolor", "Japanese",
        "Tribal", "Geometric", "Blackwork", "New School",
        "Minimalist", "Neo-Traditional"
    ]
    
    def __init__(self, style_id: str, name: str, description: str = ""):
        """
        สร้าง TattooStyle object
        
        Args:
            style_id: รหัสสไตล์ (ต้องไม่ว่าง)
            name: ชื่อสไตล์ (ต้องไม่ว่าง)
            description: คำอธิบายสไตล์ (optional)
            
        Raises:
            ValueError: ถ้า style_id หรือ name ว่าง
        """
        if not style_id or not style_id.strip():
            raise ValueError("style_id ต้องไม่ว่าง")
        if not name or not name.strip():
            raise ValueError("name ต้องไม่ว่าง")
            
        self.__style_id = style_id.strip()
        self.__name = name.strip()
        self.__description = description.strip()
        self.__created_at = datetime.now()
    
    # ── Properties (Read-only) ──
    
    @property
    def style_id(self) -> str:
        """รหัสสไตล์ (read-only)"""
        return self.__style_id
    
    @property
    def name(self) -> str:
        """ชื่อสไตล์"""
        return self.__name
    
    @property
    def description(self) -> str:
        """คำอธิบายสไตล์"""
        return self.__description
    
    @property
    def created_at(self) -> datetime:
        """วันที่สร้าง (read-only)"""
        return self.__created_at
    
    # ── Setters (เฉพาะ description สามารถแก้ไขได้) ──
    
    @description.setter
    def description(self, value: str):
        """อัปเดตคำอธิบายสไตล์"""
        self.__description = value.strip() if value else ""
    
    # ── Methods ──
    
    def update_description(self, new_description: str) -> None:
        """
        อัปเดตคำอธิบายสไตล์
        
        Args:
            new_description: คำอธิบายใหม่
        """
        self.description = new_description
        print(f"[TattooStyle] อัปเดตคำอธิบาย '{self.__name}' แล้ว")
    
    def is_popular(self) -> bool:
        """ตรวจสอบว่าเป็นสไตล์ยอดนิยมหรือไม่"""
        return self.__name in self.POPULAR_STYLES
    
    def get_summary(self) -> str:
        """สรุปข้อมูลสไตล์แบบย่อ"""
        popular = "⭐ " if self.is_popular() else ""
        return f"{popular}{self.__name} ({self.__style_id})"
    
    # ── Magic Methods ──
    
    def __repr__(self) -> str:
        return f"<TattooStyle id={self.__style_id} name={self.__name}>"
    
    def __str__(self) -> str:
        return self.__name
    
    def __eq__(self, other) -> bool:
        """เปรียบเทียบสไตล์ตาม style_id"""
        if not isinstance(other, TattooStyle):
            return False
        return self.__style_id == other.style_id
    
    def __hash__(self) -> int:
        """ทำให้ TattooStyle ใช้ใน set/dict ได้"""
        return hash(self.__style_id)


class Portfolio:
    """
    คลาสสำหรับเก็บ Portfolio ผลงานรอยสัก
    
    Attributes:
        portfolio_id: รหัสเฉพาะของ portfolio
        owner_id: รหัสเจ้าของ (artist_id)
        style: สไตล์หลักของ portfolio (optional)
        images: รายการรูปภาพ (paths/URLs)
        description: คำอธิบาย portfolio
    """
    
    # Class variable: รูปแบบไฟล์ที่รองรับ
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    MAX_IMAGES = 50  # จำนวนรูปสูงสุด
    
    def __init__(self, portfolio_id: str, owner_id: str = "", 
                 style: Optional['TattooStyle'] = None, description: str = ""):
        """
        สร้าง Portfolio object
        
        Args:
            portfolio_id: รหัส portfolio (ต้องไม่ว่าง)
            owner_id: รหัสเจ้าของ (optional สำหรับ backward compatibility)
            style: สไตล์หลัก (TattooStyle object, optional)
            description: คำอธิบาย portfolio
            
        Raises:
            ValueError: ถ้า portfolio_id ว่าง
        """
        if not portfolio_id or not portfolio_id.strip():
            raise ValueError("portfolio_id ต้องไม่ว่าง")
            
        self.__portfolio_id = portfolio_id.strip()
        self.__owner_id = owner_id.strip() if owner_id else ""
        self.__style = style
        self.__images: list = []
        self.__styles: list = []  # รักษาไว้สำหรับ backward compatibility
        self.__description = description.strip()
        self.__created_at = datetime.now()
        self.__updated_at = datetime.now()
        self.__is_public = True
        self.__view_count = 0
    
    # ── Properties ──
    
    @property
    def portfolio_id(self) -> str:
        """รหัส portfolio (read-only)"""
        return self.__portfolio_id
    
    @property
    def owner_id(self) -> str:
        """รหัสเจ้าของ (read-only)"""
        return self.__owner_id
    
    @property
    def style(self) -> Optional['TattooStyle']:
        """สไตล์หลัก"""
        return self.__style
    
    @property
    def description(self) -> str:
        """คำอธิบาย portfolio"""
        return self.__description
    
    @property
    def images(self) -> list:
        """รายการรูปภาพ (copy เพื่อป้องกันการแก้ไขโดยตรง)"""
        return list(self.__images)
    
    @property
    def styles(self) -> list:
        """รายการสไตล์ทั้งหมด (backward compatibility)"""
        result = list(self.__styles)
        if self.__style and self.__style not in result:
            result.append(self.__style)
        return result
    
    @property
    def image_count(self) -> int:
        """จำนวนรูปภาพ"""
        return len(self.__images)
    
    @property
    def is_public(self) -> bool:
        """สถานะการเผยแพร่"""
        return self.__is_public
    
    @property
    def view_count(self) -> int:
        """จำนวนครั้งที่ถูกดู"""
        return self.__view_count
    
    @property
    def created_at(self) -> datetime:
        """วันที่สร้าง (read-only)"""
        return self.__created_at
    
    @property
    def updated_at(self) -> datetime:
        """วันที่อัปเดตล่าสุด (read-only)"""
        return self.__updated_at
    
    # ── Setters ──
    
    @style.setter
    def style(self, new_style: Optional['TattooStyle']):
        """เปลี่ยนสไตล์หลัก"""
        if new_style is not None and not isinstance(new_style, TattooStyle):
            raise TypeError("style ต้องเป็น TattooStyle object หรือ None")
        self.__style = new_style
        self.__touch()
    
    @description.setter
    def description(self, value: str):
        """อัปเดตคำอธิบาย"""
        self.__description = value.strip() if value else ""
        self.__touch()
    
    # ── Image Management Methods ──
    
    def add_image(self, image: str) -> bool:
        """
        เพิ่มรูปภาพเข้า portfolio
        
        Args:
            image: path หรือ URL ของรูปภาพ
            
        Returns:
            True ถ้าเพิ่มสำเร็จ
            
        Raises:
            ValueError: ถ้ารูปภาพว่าง, ซ้ำ, หรือเกินจำนวนสูงสุด
        """
        if not image or not image.strip():
            raise ValueError("image path/URL ต้องไม่ว่าง")
        
        image = image.strip()
        
        # เช็คว่าซ้ำหรือไม่
        if image in self.__images:
            raise ValueError(f"รูปภาพ '{image}' มีอยู่ใน portfolio แล้ว")
        
        # เช็คจำนวนสูงสุด
        if len(self.__images) >= self.MAX_IMAGES:
            raise ValueError(f"Portfolio เต็มแล้ว (สูงสุด {self.MAX_IMAGES} รูป)")
        
        # เช็ครูปแบบไฟล์ (สำหรับ file path)
        if not image.startswith(('http://', 'https://')):
            if not any(image.lower().endswith(fmt) for fmt in self.SUPPORTED_FORMATS):
                print(f"⚠️ Warning: '{image}' อาจไม่ใช่ไฟล์รูปภาพที่รองรับ")
        
        self.__images.append(image)
        self.__touch()
        print(f"[Portfolio] เพิ่มรูปภาพ '{image}' สำเร็จ ({self.image_count}/{self.MAX_IMAGES})")
        return True
    
    def remove_image(self, image: str) -> bool:
        """
        ลบรูปภาพออกจาก portfolio
        
        Args:
            image: path หรือ URL ของรูปภาพที่ต้องการลบ
            
        Returns:
            True ถ้าลบสำเร็จ
            
        Raises:
            ValueError: ถ้าไม่พบรูปภาพ
        """
        if image not in self.__images:
            raise ValueError(f"ไม่พบรูปภาพ '{image}' ใน portfolio")
        
        self.__images.remove(image)
        self.__touch()
        print(f"[Portfolio] ลบรูปภาพ '{image}' สำเร็จ ({self.image_count}/{self.MAX_IMAGES})")
        return True
    
    def remove_image_by_index(self, index: int) -> str:
        """
        ลบรูปภาพตำแหน่งที่ระบุ
        
        Args:
            index: ตำแหน่งของรูปภาพ (0-based)
            
        Returns:
            path/URL ของรูปภาพที่ถูกลบ
            
        Raises:
            IndexError: ถ้า index ไม่ถูกต้อง
        """
        if not 0 <= index < len(self.__images):
            raise IndexError(f"index {index} ไม่ถูกต้อง (มีรูปทั้งหมด {len(self.__images)} รูป)")
        
        removed = self.__images.pop(index)
        self.__touch()
        print(f"[Portfolio] ลบรูปภาพตำแหน่ง {index} สำเร็จ: '{removed}'")
        return removed
    
    def clear_images(self) -> int:
        """
        ลบรูปภาพทั้งหมด
        
        Returns:
            จำนวนรูปที่ถูกลบ
        """
        count = len(self.__images)
        self.__images.clear()
        self.__touch()
        print(f"[Portfolio] ลบรูปภาพทั้งหมด {count} รูป")
        return count
    
    def get_images(self) -> list:
        """
        รับรายการรูปภาพทั้งหมด
        
        Returns:
            List ของ image paths/URLs (copy)
        """
        return list(self.__images)
    
    def get_image_at(self, index: int) -> str:
        """
        รับรูปภาพตำแหน่งที่ระบุ
        
        Args:
            index: ตำแหน่งของรูปภาพ
            
        Returns:
            path/URL ของรูปภาพ
            
        Raises:
            IndexError: ถ้า index ไม่ถูกต้อง
        """
        if not 0 <= index < len(self.__images):
            raise IndexError(f"index {index} ไม่ถูกต้อง")
        return self.__images[index]
    
    def has_image(self, image: str) -> bool:
        """ตรวจสอบว่ามีรูปภาพนี้หรือไม่"""
        return image in self.__images
    
    # ── Style Management Methods ──
    
    def add_style(self, style: TattooStyle) -> None:
        """
        เพิ่มสไตล์เข้า portfolio (backward compatibility)
        
        Args:
            style: TattooStyle object
        """
        if not isinstance(style, TattooStyle):
            raise TypeError("style ต้องเป็น TattooStyle object")
        if style not in self.__styles:
            self.__styles.append(style)
            self.__touch()
    
    def remove_style(self, style: TattooStyle) -> None:
        """ลบสไตล์ออกจาก portfolio"""
        if style in self.__styles:
            self.__styles.remove(style)
            self.__touch()
    
    # ── Description Methods ──
    
    def update_description(self, description: str) -> None:
        """
        อัปเดตคำอธิบาย portfolio
        
        Args:
            description: คำอธิบายใหม่
        """
        self.description = description
        print(f"[Portfolio] อัปเดตคำอธิบายแล้ว")
    
    def append_description(self, additional_text: str) -> None:
        """เพิ่มข้อความต่อท้ายคำอธิบาย"""
        self.__description = f"{self.__description}\n{additional_text}".strip()
        self.__touch()
    
    # ── Style Methods ──
    
    def change_style(self, new_style: TattooStyle) -> None:
        """
        เปลี่ยนสไตล์หลัก
        
        Args:
            new_style: สไตล์ใหม่
        """
        old_style = self.__style
        self.style = new_style
        old_name = old_style.name if old_style else "None"
        new_name = new_style.name if new_style else "None"
        print(f"[Portfolio] เปลี่ยนสไตล์: {old_name} → {new_name}")
    
    # ── Visibility Methods ──
    
    def publish(self) -> None:
        """เผยแพร่ portfolio ให้ทุกคนเห็น"""
        if self.__is_public:
            print("[Portfolio] portfolio เผยแพร่อยู่แล้ว")
            return
        self.__is_public = True
        self.__touch()
        print("[Portfolio] เผยแพร่ portfolio สำเร็จ")
    
    def unpublish(self) -> None:
        """ซ่อน portfolio (ตั้งเป็น private)"""
        if not self.__is_public:
            print("[Portfolio] portfolio ถูกซ่อนอยู่แล้ว")
            return
        self.__is_public = False
        self.__touch()
        print("[Portfolio] ซ่อน portfolio แล้ว")
    
    def increment_view(self) -> int:
        """เพิ่มจำนวนการดู (เมื่อมีคนเปิดดู portfolio)"""
        self.__view_count += 1
        return self.__view_count
    
    # ── Validation Methods ──
    
    def is_empty(self) -> bool:
        """ตรวจสอบว่า portfolio ว่างเปล่าหรือไม่"""
        return len(self.__images) == 0
    
    def is_full(self) -> bool:
        """ตรวจสอบว่า portfolio เต็มหรือไม่"""
        return len(self.__images) >= self.MAX_IMAGES
    
    def can_add_images(self, count: int = 1) -> bool:
        """ตรวจสอบว่าสามารถเพิ่มรูปได้อีกหรือไม่"""
        return len(self.__images) + count <= self.MAX_IMAGES
    
    # ── Display Methods ──
    
    def get_summary(self) -> str:
        """สรุปข้อมูล portfolio"""
        visibility = "🌐 Public" if self.__is_public else "🔒 Private"
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
        """แสดงรายการรูปภาพทั้งหมดพร้อม index"""
        if self.is_empty():
            return "📷 ไม่มีรูปภาพใน portfolio"
        
        lines = [f"📷 รูปภาพใน Portfolio ({self.image_count} รูป):"]
        for i, img in enumerate(self.__images):
            lines.append(f"  [{i}] {img}")
        return "\n".join(lines)
    
    # ── Helper Methods ──
    
    def __touch(self) -> None:
        """อัปเดตเวลาที่แก้ไขล่าสุด (private method)"""
        self.__updated_at = datetime.now()
    
    # ── Magic Methods ──
    
    def __repr__(self) -> str:
        style_name = self.__style.name if self.__style else "None"
        return (f"<Portfolio id={self.__portfolio_id} "
                f"style={style_name} images={self.image_count}>")
    
    def __str__(self) -> str:
        style_name = self.__style.name if self.__style else "No style"
        return f"{self.__portfolio_id} ({style_name} - {self.image_count} images)"
    
    def __len__(self) -> int:
        """ใช้ len(portfolio) เพื่อดูจำนวนรูป"""
        return len(self.__images)
    
    def __contains__(self, image: str) -> bool:
        """ใช้ 'image' in portfolio เพื่อเช็ครูปภาพ"""
        return image in self.__images
    
    def __iter__(self):
        """ทำให้ portfolio วนลูปได้"""
        return iter(self.__images)
    
    def __getitem__(self, index: int) -> str:
        """ใช้ portfolio[index] เพื่อเข้าถึงรูปภาพ"""
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

    # 🔴 แก้เกณฑ์ใหม่ตามที่กำหนด
    THRESHOLD_SILVER   = 15_000  # เดิม 5,000
    THRESHOLD_GOLD     = 25_000  # เดิม 15,000
    THRESHOLD_PLATINUM = 40_000  # เดิม 30,000

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
        self.__calendar = Calendar(staff_id)
        self.__booking_list: list = []
        self.__ratings: list = []
        self.__request_list: list = []
        self.__available_days: list[date] = []
        self.__status = "pending"
        self.__deposit_policy = None  # 🔴 เพิ่มบรรทัดนี้

 
    def set_available_days(self, days: list):
        """Artist ตั้งวันว่าง"""
        self.__available_days = days
        print(f"[Artist] {self._name} ตั้งวันว่าง {len(days)} วัน")

    def add_available_day(self, day):
        """เพิ่มวันว่าง"""
        if day not in self.__available_days:
            self.__available_days.append(day)

    def get_available_days(self):
        """คืนรายการวันว่าง"""
        return list(self.__available_days)

    def is_available(self, target_date):
        """เช็คว่าวันนี้ว่างไหม"""
        if target_date not in self.__available_days:
            return False

        busy = self.__calendar.get_busy_dates()
        return target_date not in busy

    def view_available_days(self):
        """ดูวันว่างที่ยังไม่ถูกจอง"""
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