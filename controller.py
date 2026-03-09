"""
controller.py
=============
SoonSak - ระบบหลักที่รวมการทำงานทั้งหมด
ทำหน้าที่เป็น Facade: User ติดต่อผ่านคลาสนี้เพื่อเรียกใช้ระบบย่อยต่าง ๆ

การ import:
- entities.py : User, VIPMember, Artist, Admin, Studio, Coupon, Rating, ...
- booking.py  : Booking, Appointment, Order
- payment.py  : Payment, Promptpay, Transaction, SoonSakBank, DepositPolicy, ...
"""

from datetime import date, datetime
from entities import (
    User, VIPMember, Artist, Admin,
    Studio, Coupon, Rating,
    Portfolio, TattooStyle,
    Calendar, Event,
    StudioRequest
)
from booking import Booking, Appointment, Order
from payment import (
    Payment, Promptpay, Transaction,
    SoonSakBank, PaymentMethod,
    FixedDepositPolicy, PercentDepositPolicy,
    DepositPolicy
)


class SoonSak:
    """
    Controller หลักของระบบ SoonSak
    ─────────────────────────────────────────────
    จัดการ:
    - การ login / logout
    - การสร้าง / ยกเลิก Booking
    - การชำระเงิน (deposit & full)
    - การ rate Artist
    - การจัดการ Artist, Studio โดย Admin
    ─────────────────────────────────────────────
    """

    def __init__(self):
        # ── ข้อมูลหลักของระบบ ──
        self._user_list: dict[str, User] = {}       # user_id → User
        self._artist_list: dict[str, Artist] = {}   # staff_id → Artist
        self._admin_list: dict[str, Admin] = {}      # staff_id → Admin
        self._order_list: dict[str, Order] = {}     # order_id → Order
        self._studio_list: list[Studio] = []
        self._bank = SoonSakBank(bank_id="SSB-001")

        # ── Counters สำหรับ generate ID ──
        self._booking_counter = 0
        self._order_counter = 0
        self._txn_counter = 0
        self._rating_counter = 0
        self._event_counter = 0
        self._request_counter = 0

        # ── Session ──
        self._logged_in_users: set[str] = set()

        print("=" * 50)
        print("  ระบบ SoonSak เริ่มต้นแล้ว")
        print("=" * 50)

    # ─────────────────────────────────────────────
    # ID Generators
    # ─────────────────────────────────────────────

    def _new_booking_id(self) -> str:
        self._booking_counter += 1
        return f"BKG-{self._booking_counter:03d}"

    def _new_order_id(self) -> str:
        self._order_counter += 1
        return f"ORD-{self._order_counter:03d}"

    def _new_txn_id(self) -> str:
        self._txn_counter += 1
        return f"TXN-{self._txn_counter:03d}"

    def _new_rating_id(self) -> str:
        self._rating_counter += 1
        return f"RAT-{self._rating_counter:03d}"

    def _new_event_id(self) -> str:
        self._event_counter += 1
        return f"EVT-{self._event_counter:03d}"

    def _new_request_id(self) -> str:
        self._request_counter += 1
        return f"REQ-{self._request_counter:03d}"

    # ─────────────────────────────────────────────
    # Authentication
    # ─────────────────────────────────────────────

    def login(self, user_id: str) -> bool:
        """
        ล็อกอินเข้าระบบ
        - ตรวจสอบว่า user มีอยู่จริง
        - ตรวจสอบ status ไม่ถูก suspend
        """
        # ค้นหาใน user_list หรือ artist_list
        entity = self.find_user(user_id) or self._artist_list.get(user_id) or self._admin_list.get(user_id)

        if entity is None:
            print(f"[Login] ไม่พบ ID: {user_id}")
            return False

        # ตรวจสอบ User ว่าถูก suspend หรือไม่ (B2: Validation)
        if isinstance(entity, User) and entity.status == User.STATUS_SUSPENDED:
            print(f"[Login] บัญชี {user_id} ถูกระงับ ไม่สามารถล็อกอินได้")
            return False

        self._logged_in_users.add(user_id)
        print(f"[Login] {entity.name} ล็อกอินสำเร็จ")
        return True

    def logout(self, user_id: str):
        """ออกจากระบบ"""
        if user_id in self._logged_in_users:
            self._logged_in_users.discard(user_id)
            print(f"[Logout] {user_id} ออกจากระบบแล้ว")
        else:
            print(f"[Logout] {user_id} ยังไม่ได้ล็อกอิน")

    def _require_login(self, user_id: str):
        """ตรวจสอบว่า login แล้วก่อนทำงาน (B2: Validation)"""
        if user_id not in self._logged_in_users:
            raise PermissionError(f"{user_id} ต้องล็อกอินก่อน")

    # ─────────────────────────────────────────────
    # User Management
    # ─────────────────────────────────────────────

    def register_user(self, user_id: str, name: str,
                      email: str, phone: str,
                      is_vip: bool = False, vip_rank: str = "SILVER") -> User:
        """
        ลงทะเบียนผู้ใช้ใหม่
        - is_vip=True จะสร้าง VIPMember แทน User ทั่วไป
        """
        if user_id in self._user_list:
            raise ValueError(f"User {user_id} มีอยู่แล้ว")

        if is_vip:
            user = VIPMember(user_id, name, email, phone, vip_rank)
        else:
            user = User(user_id, name, email, phone)

        self._user_list[user_id] = user
        print(f"[Register] ลงทะเบียน {user} สำเร็จ")
        return user

    def register_artist(self, staff_id: str, name: str,
                        email: str, experience: int = 0) -> Artist:
        """ลงทะเบียน Artist ใหม่ (รอ Admin approve)"""
        if staff_id in self._artist_list:
            raise ValueError(f"Artist {staff_id} มีอยู่แล้ว")
        artist = Artist(staff_id, name, email, experience)
        self._artist_list[staff_id] = artist
        print(f"[Register] ลงทะเบียน {artist} สำเร็จ รอ Admin อนุมัติ")
        return artist

    def register_admin(self, staff_id: str, name: str, email: str) -> Admin:
        """สร้าง Admin ใหม่"""
        admin = Admin(staff_id, name, email)
        self._admin_list[staff_id] = admin
        print(f"[Register] สร้าง Admin {admin} สำเร็จ")
        return admin

    def find_user(self, user_id: str) -> User:
        """ค้นหา User ด้วย ID (คืน None ถ้าไม่พบ)"""
        return self._user_list.get(user_id)

    def find_artist(self, artist_id: str) -> Artist:
        """ค้นหา Artist ด้วย ID"""
        return self._artist_list.get(artist_id)

    def find_order(self, order_id: str) -> Order:
        """ค้นหา Order ด้วย ID"""
        return self._order_list.get(order_id)

    # ─────────────────────────────────────────────
    # Booking Flow
    # ─────────────────────────────────────────────

    def create_booking(self, user_id: str, artist_id: str,
                       body_part: str, size: str,
                       color_tone: str, base_price: float,
                       reference_image: str = "") -> Booking:
        """
        สร้าง Booking ใหม่
        Business Rules (A3):
        - User ต้องล็อกอิน
        - User ต้อง ACTIVE ไม่ถูก suspend
        - จำนวน Booking ที่ active ต้องไม่เกิน max_bookings
        - Artist ต้องผ่านการยืนยันตัวตน
        """
        self._require_login(user_id)

        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")

        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        # B2: Validation - Artist ต้อง verified
        if artist.status != Artist.STATUS_VERIFIED:
            raise Exception(f"Artist {artist_id} ยังไม่ผ่านการยืนยันตัวตน")

        # Business Rule: จำกัดจำนวน Booking พร้อมกัน (A3)
        active_bookings = [
            b for b in user.view_history()
            if hasattr(b, 'status') and b.status in [
                Booking.STATUS_WAITING, Booking.STATUS_ACCEPTED
            ]
        ]
        if len(active_bookings) >= user.max_bookings:
            raise Exception(
                f"จองพร้อมกันได้สูงสุด {user.max_bookings} รายการ "
                f"(ปัจจุบัน {len(active_bookings)} รายการ)"
            )

        booking_id = self._new_booking_id()
        booking = Booking(
            booking_id=booking_id,
            user_id=user_id,
            artist_id=artist_id,
            body_part=body_part,
            size=size,
            color_tone=color_tone,
            reference_image=reference_image,
            base_price=base_price
        )

        # เพิ่มเข้าประวัติของ User (B3: History)
        user.add_history(booking)
        print(f"[SoonSak] สร้าง {booking} สำเร็จ")
        return booking

    def cancel_booking(self, user_id: str, booking: Booking):
        """
        ยกเลิก Booking โดย User
        Business Rule: ยกเลิกได้เฉพาะ WAITING หรือ ACCEPTED
        """
        self._require_login(user_id)

        # ตรวจสอบว่าเป็นเจ้าของ Booking
        if booking.user_id != user_id:
            raise PermissionError("ไม่มีสิทธิ์ยกเลิก Booking ของคนอื่น")

        booking.cancel()
        print(f"[SoonSak] {user_id} ยกเลิก {booking.booking_id} สำเร็จ")

    # ─────────────────────────────────────────────
    # Order & Payment Flow
    # ─────────────────────────────────────────────

    def create_order(self, booking: Booking,
                     apply_vip_discount: bool = True,
                     coupon_code: str = None) -> Order:
        """
        สร้าง Order จาก Booking
        - apply_vip_discount: ถ้า True และ User เป็น VIP จะหักส่วนลดจากราคาจริงเลย
        - coupon_code: ถ้าระบุ จะใช้คูปองหักราคาด้วย
        ราคาที่หักแล้วจะถูก set กลับเข้า Booking ก่อนสร้าง Order
        """
        user = self.find_user(booking.user_id)
        final_price = booking.base_price

        # ── Apply VIP Discount ──
        if apply_vip_discount and user is not None and isinstance(user, VIPMember):
            discount = user.calculate_discount(final_price)
            final_price -= discount
            print(f"[SoonSak] หักส่วนลด VIP {user.rank}: ราคาจาก {booking.base_price:.2f} → {final_price:.2f} บาท")

        # ── Apply Coupon ──
        if coupon_code and user is not None:
            try:
                final_price = user.use_coupon(coupon_code, final_price)
                print(f"[SoonSak] หักคูปอง {coupon_code}: ราคาสุดท้าย {final_price:.2f} บาท")
            except ValueError as e:
                print(f"[SoonSak] ⚠️ ใช้คูปองไม่ได้: {e}")

        # อัปเดตราคาใน Booking ให้ตรงกับราคาที่หักแล้ว
        booking.set_price(final_price)

        order_id = self._new_order_id()
        order = Order(order_id=order_id)
        order.add_booking(booking)
        self._order_list[order_id] = order
        print(f"[SoonSak] สร้าง {order} สำเร็จ")
        return order

    def process_payment(self, user_id: str, order: Order,
                        payment_method: PaymentMethod,
                        deposit_policy: DepositPolicy = None,
                        pay_full: bool = False) -> Payment:
        """
        ดำเนินการชำระเงิน
        - ถ้า pay_full=False → ชำระมัดจำก่อน
        - ถ้า pay_full=True  → ชำระส่วนที่เหลือ + สะสมยอดเงินให้ User

        หลัง pay_full:
        - เพิ่มยอด _total_spent ให้ User
        - ถ้า User ทั่วไปยอดสะสมถึง 5,000 → เลื่อนเป็น VIPMember SILVER
        - ถ้าเป็น VIPMember อยู่แล้ว → เช็ค rank upgrade อัตโนมัติ
        """
        self._require_login(user_id)

        payment = Payment(
            payment_id=f"PAY-{self._order_counter:03d}",
            order=order,
            bank=self._bank
        )
        payment.set_payment_method(payment_method)

        if deposit_policy:
            payment.set_deposit_policy(deposit_policy)

        if pay_full:
            txn = payment.pay_full(user_id, self._txn_counter + 1)
            self._txn_counter += 1

            # ── สะสมยอดเงิน + เช็ค VIP upgrade ──
            total_paid = order.calculate_total()
            user = self.find_user(user_id)
            if user is not None:
                user.add_spent(total_paid)
                self._check_vip_upgrade(user)
        else:
            txn = payment.pay_deposit(user_id, self._txn_counter + 1)
            self._txn_counter += 1

        return payment

    def _check_vip_upgrade(self, user):
        """
        ตรวจสอบและอัปเกรด VIP status ตามยอดสะสม
        - User ทั่วไป ยอด >= 5,000  → กลายเป็น VIPMember SILVER
        - VIPMember อยู่แล้ว        → check_and_upgrade() เช็ค rank
        """
        spent = user._total_spent

        if not isinstance(user, VIPMember):
            # เช็คว่าถึงเกณฑ์ VIP ขั้นต่ำหรือยัง
            if spent >= VIPMember.RANK_THRESHOLD["SILVER"]:
                vip = VIPMember(
                    user_id=user.user_id,
                    name=user.name,
                    email=user.email,
                    phone_number=user._phone_number,
                    rank=VIPMember.RANK_SILVER
                )
                # ย้าย state ทั้งหมด
                vip._bookings_history       = user._bookings_history
                vip._coupon_list            = user._coupon_list
                vip._credit                 = user._credit
                vip._status                 = user._status
                vip._completed_tattoo_count = user._completed_tattoo_count
                vip._total_spent            = spent
                # เช็ค rank ทันทีหลังย้าย (อาจ qualify GOLD/PLATINUM เลย)
                vip.check_and_upgrade()
                self._user_list[user.user_id] = vip
                print(f"[SoonSak] 🎉 {vip.name} ได้รับสถานะ VIPMember! "
                      f"rank={vip.rank} (ยอดสะสม {spent:,.2f} บาท)")
        else:
            # เป็น VIP อยู่แล้ว → เช็ค rank upgrade
            user.check_and_upgrade()

    def request_payment_sum(self, order_id: str) -> float:
        """
        ดูยอดรวมที่ต้องชำระของ Order
        (B3: สรุปรายงาน)
        """
        order = self.find_order(order_id)
        if order is None:
            raise ValueError(f"ไม่พบ Order {order_id}")
        total = order.calculate_total()
        print(f"[SoonSak] Order {order_id} ยอดรวม: {total:.2f} บาท")
        return total

    # ─────────────────────────────────────────────
    # Rating
    # ─────────────────────────────────────────────

    def rate_artist(self, user_id: str, artist_id: str,
                    booking: Booking, score: int, comment: str) -> Rating:
        """
        User รีวิว Artist หลังงานเสร็จ
        Business Rule: Booking ต้องมีสถานะ COMPLETED
        """
        self._require_login(user_id)

        # B2: Validation - Booking ต้อง COMPLETED
        if booking.status != Booking.STATUS_COMPLETED:
            raise Exception("สามารถให้คะแนนได้เฉพาะ Booking ที่เสร็จแล้ว")

        # B2: Validation - ตรวจสอบว่าเป็น Booking ของ user นี้
        if booking.user_id != user_id:
            raise PermissionError("ไม่มีสิทธิ์รีวิว Booking ของคนอื่น")

        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        rating = Rating(
            rating_id=self._new_rating_id(),
            score=score,
            comment=comment,
            user_id=user_id,
            artist_id=artist_id
        )
        artist.add_rating(rating)
        print(f"[SoonSak] {user_id} ให้คะแนน Artist {artist_id}: {score}/5")
        return rating

    # ─────────────────────────────────────────────
    # Artist Actions
    # ─────────────────────────────────────────────

    def artist_accept_job(self, artist_id: str, booking: Booking):
        """Artist รับงาน"""
        self._require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.accept_job(booking)

    def artist_reject_job(self, artist_id: str, booking: Booking, reason: str = ""):
        """Artist ปฏิเสธงาน"""
        self._require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.reject_job(booking, reason)

    def artist_complete_job(self, artist_id: str, booking: Booking):
        """
        Artist กดงานเสร็จ
        - เปลี่ยน Booking → COMPLETED
        - เพิ่ม completed_tattoo_count ให้ User
        - ถ้า User ทั่วไปสักครบ 3 ครั้ง → อัปเกรดเป็น VIPMember อัตโนมัติ
        - ถ้าเป็น VIPMember อยู่แล้ว → เช็ค rank upgrade
        """
        self._require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.complete_job(booking)

        # ── อัปเดต completed count ของ User ──
        user = self.find_user(booking.user_id)
        if user is None:
            return

        user._completed_tattoo_count += 1
        print(f"[SoonSak] {user.name} สักแล้วทั้งหมด {user._completed_tattoo_count} ครั้ง")

    def artist_request_studio(self, artist_id: str,
                              studio_name: str, location: str) -> StudioRequest:
        """Artist ส่งคำขอเปิด Studio"""
        self._require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        request = StudioRequest(
            request_id=self._new_request_id(),
            artist_id=artist_id,
            studio_name=studio_name,
            location=location
        )
        artist.request_studio(request)
        return request

    # ─────────────────────────────────────────────
    # Admin Actions
    # ─────────────────────────────────────────────

    def admin_approve_artist(self, admin_id: str, artist_id: str):
        """Admin อนุมัติ Artist"""
        self._require_login(admin_id)
        admin = self._admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        admin.approve_artist(artist)

    def admin_approve_studio(self, admin_id: str,
                             request: StudioRequest) -> Studio:
        """Admin อนุมัติ Studio Request"""
        self._require_login(admin_id)
        admin = self._admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        studio = admin.approve_studio(request, self._studio_list)
        return studio

    def admin_reject_studio(self, admin_id: str, request: StudioRequest):
        """Admin ปฏิเสธ Studio Request"""
        self._require_login(admin_id)
        admin = self._admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        admin.reject_studio(request)

    def admin_suspend_user(self, admin_id: str, user_id: str):
        """Admin ระงับ User"""
        self._require_login(admin_id)
        admin = self._admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")
        admin.suspend_user(user)

    def admin_add_coupon(self, admin_id: str, user_id: str,
                         coupon_code: str, discount: float,
                         expired: date) -> Coupon:
        """Admin เพิ่ม Coupon ให้ User"""
        self._require_login(admin_id)
        admin = self._admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")

        coupon = Coupon(coupon_code, discount, expired)
        user.add_coupon(coupon)
        print(f"[Admin] เพิ่มคูปอง {coupon_code} ({discount}%) ให้ {user.name}")
        return coupon

    # ─────────────────────────────────────────────
    # Reports (B3: สร้างรายงาน)
    # ─────────────────────────────────────────────

    def report_bank_balance(self):
        """รายงานยอดเงินในระบบ"""
        print("\n" + "─" * 40)
        print("  รายงานยอดเงิน SoonSak Bank")
        print("─" * 40)
        self._bank.check_balance()
        history = self._bank.get_history()
        print(f"  รายการทั้งหมด: {len(history)} รายการ")
        for txn in history:
            print(f"  {txn}")
        print("─" * 40 + "\n")

    def report_artist_ratings(self, artist_id: str):
        """รายงานคะแนน Artist"""
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        avg = artist.average_rating()
        print(f"\n[Report] {artist.name} คะแนนเฉลี่ย: {avg:.2f}/5")
        return avg

    def view_artist(self, artist_id: str) -> dict:
        """ดูข้อมูล Artist (User ใช้ก่อนจอง)"""
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        return {
            "artist_id": artist.staff_id,
            "name": artist.name,
            "experience": artist._experience,
            "status": artist.status,
            "avg_rating": artist.average_rating(),
            "deposit_policy": str(artist.deposit_policy),
        }


# ═══════════════════════════════════════════════
# DEMO - รันเพื่อทดสอบระบบ
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    from datetime import date

    def section(title):
        print(f"\n{'═'*60}")
        print(f"  {title}")
        print('═'*60)

    section("DEMO: ระบบ SoonSak - Full Flow Test")

    system = SoonSak()

    # ══════════════════════════════════════════
    # SETUP: ลงทะเบียนทุกคน
    # ══════════════════════════════════════════
    section("1. ลงทะเบียน")

    # User ทั่วไป (จะกลายเป็น VIP อัตโนมัติหลังสัก 3 ครั้ง)
    user1 = system.register_user("USR-001", "อาทิตย์", "sun@mail.com", "0811111111")
    # User ทั่วไปอีกคน (ใช้ทดสอบ cancel flow)
    user2 = system.register_user("USR-002", "จันทร์", "moon@mail.com", "0833333333")

    artist1 = system.register_artist("ART-001", "ช่างแจ็ค", "jack@mail.com", experience=5)
    artist2 = system.register_artist("ART-002", "ช่างแนน", "nan@mail.com", experience=2)
    admin1  = system.register_admin("ADM-001", "ผู้ดูแล", "admin@soonsak.com")

    # ── Login ──
    for uid in ["ADM-001", "ART-001", "ART-002", "USR-001", "USR-002"]:
        system.login(uid)

    # ══════════════════════════════════════════
    # SETUP: Admin อนุมัติ Artist + ตั้ง Policy
    # ══════════════════════════════════════════
    section("2. Admin อนุมัติ Artist")
    system.admin_approve_artist("ADM-001", "ART-001")
    system.admin_approve_artist("ADM-001", "ART-002")

    policy_percent = PercentDepositPolicy(percent=30)
    policy_fixed   = FixedDepositPolicy(fixed_amount=500)
    artist1.set_deposit_policy(policy_percent)
    artist2.set_deposit_policy(policy_fixed)

    # ══════════════════════════════════════════
    # FLOW A: Reject Job (Artist ปฏิเสธงาน)
    # ══════════════════════════════════════════
    section("3. Flow A — Artist ปฏิเสธงาน")
    b_reject = system.create_booking("USR-001", "ART-001", "ข้อมือ", "เล็ก", "ขาว-ดำ", 800.0)
    system.artist_reject_job("ART-001", b_reject, reason="ไม่ว่างในวันที่นัด")
    print(f"  → Booking status: {b_reject.status}")  # CANCELLED

    # ══════════════════════════════════════════
    # FLOW B: User ยกเลิก Booking เอง
    # ══════════════════════════════════════════
    section("4. Flow B — User ยกเลิก Booking เอง")
    b_cancel = system.create_booking("USR-002", "ART-002", "ต้นแขน", "กลาง", "สี", 2000.0)
    system.cancel_booking("USR-002", b_cancel)
    print(f"  → Booking status: {b_cancel.status}")  # CANCELLED

    # ══════════════════════════════════════════
    # FLOW C: สักครั้งแรก 3,000 บาท → ยังไม่ VIP
    # ══════════════════════════════════════════
    section("5. Flow C — จอง → มัดจำ → ชำระเต็ม (ยอดสะสม 3,000)")
    b1 = system.create_booking("USR-001", "ART-001", "แขน", "กลาง", "ขาว-ดำ", 3000.0)
    system.artist_accept_job("ART-001", b1)
    o1 = system.create_order(b1)
    system.process_payment("USR-001", o1, Promptpay("0811111111"), policy_percent)
    system.process_payment("USR-001", o1, Promptpay("0811111111"), pay_full=True)
    o1.order_phase()
    system.artist_complete_job("ART-001", b1)
    system.rate_artist("USR-001", "ART-001", b1, 5, "สวยมาก!")
    u = system.find_user("USR-001")
    print(f"  → ยอดสะสม: {u._total_spent:,.2f} บาท | type: {type(u).__name__}")

    # ══════════════════════════════════════════
    # FLOW D: สักอีก 2,500 → รวม 5,500 → Trigger SILVER VIP
    # ══════════════════════════════════════════
    section("6. Flow D — ยอดสะสมถึง 5,000 → Trigger VIP SILVER")
    b2 = system.create_booking("USR-001", "ART-001", "หลัง", "กลาง", "สี", 2500.0)
    system.artist_accept_job("ART-001", b2)
    o2 = system.create_order(b2)
    system.process_payment("USR-001", o2, Promptpay("0811111111"), policy_percent)
    system.process_payment("USR-001", o2, Promptpay("0811111111"), pay_full=True)
    system.artist_complete_job("ART-001", b2)
    system.rate_artist("USR-001", "ART-001", b2, 4, "โอเคมาก")
    u = system.find_user("USR-001")
    print(f"  → ยอดสะสม: {u._total_spent:,.2f} บาท | type: {type(u).__name__}")
    if isinstance(u, VIPMember):
        print(f"  → {u.vip_status_summary()}")

    # ══════════════════════════════════════════
    # FLOW E: สักต่อให้ถึง 15,000 → GOLD
    # ══════════════════════════════════════════
    section("7. Flow E — ยอดสะสมถึง 15,000 → Trigger VIP GOLD")
    # ต้องการอีก ~10,000 บาท จากยอดปัจจุบัน
    for part, price in [("ขา", 4000.0), ("ต้นคอ", 3500.0), ("หน้าอก", 3000.0)]:
        b = system.create_booking("USR-001", "ART-001", part, "กลาง", "สี", price)
        system.artist_accept_job("ART-001", b)
        o = system.create_order(b)
        system.process_payment("USR-001", o, Promptpay("0811111111"), policy_percent)
        system.process_payment("USR-001", o, Promptpay("0811111111"), pay_full=True)
        system.artist_complete_job("ART-001", b)
    u = system.find_user("USR-001")
    print(f"  → ยอดสะสม: {u._total_spent:,.2f} บาท | type: {type(u).__name__}")
    if isinstance(u, VIPMember):
        print(f"  → {u.vip_status_summary()}")

    # ══════════════════════════════════════════
    # FLOW F: VIP GOLD จอง + Discount + Coupon
    # ══════════════════════════════════════════
    section("8. Flow F — VIP GOLD Booking + Coupon")
    system.admin_add_coupon("ADM-001", "USR-001", "SOONSAK10", 10, date(2026, 12, 31))

    b_vip = system.create_booking("USR-001", "ART-001", "หลังเต็ม", "ใหญ่", "สี", 8000.0)
    system.artist_accept_job("ART-001", b_vip)
    print(f"\n  ราคาเต็ม: 8,000 บาท")
    o_vip = system.create_order(b_vip, apply_vip_discount=True, coupon_code="SOONSAK10")
    system.process_payment("USR-001", o_vip, Promptpay("0811111111"), policy_percent)
    system.process_payment("USR-001", o_vip, Promptpay("0811111111"), pay_full=True)
    o_vip.order_phase()
    system.artist_complete_job("ART-001", b_vip)
    system.rate_artist("USR-001", "ART-001", b_vip, 5, "ดีมากตลอด!")
    u = system.find_user("USR-001")
    if isinstance(u, VIPMember):
        print(f"\n  → VIP Status ล่าสุด: {u.vip_status_summary()}")

    # ══════════════════════════════════════════
    # FLOW G: Studio Request
    # ══════════════════════════════════════════
    section("9. Flow G — Studio Request")
    req = system.artist_request_studio("ART-001", "Jack's Ink Studio", "กรุงเทพฯ")
    system.admin_approve_studio("ADM-001", req)
    req2 = system.artist_request_studio("ART-002", "Nan's Art Studio", "เชียงใหม่")
    system.admin_reject_studio("ADM-001", req2)
    print(f"  → req2 status: {req2.status}")  # REJECTED

    # ══════════════════════════════════════════
    # REPORTS
    # ══════════════════════════════════════════
    section("10. Reports สรุปทั้งระบบ")
    system.report_artist_ratings("ART-001")
    system.report_bank_balance()

    print("\n  📋 User List:")
    for uid, u in system._user_list.items():
        utype = type(u).__name__
        spent = f"{u._total_spent:,.2f}"
        rank  = f" | rank={u.rank}" if isinstance(u, VIPMember) else ""
        print(f"    [{uid}] {u.name} | {utype}{rank} | ยอดสะสม {spent} บาท")

    section("11. Logout")
    for uid in ["USR-001", "USR-002", "ART-001", "ART-002", "ADM-001"]:
        system.logout(uid)

    print("\n" + "═"*60)
    print("   DEMO เสร็จสิ้น ✅")
    print("═"*60)