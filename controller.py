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
        # ── ข้อมูลหลักของระบบ (Strictly Private) ──
        self.__user_list: dict[str, User] = {}       # user_id → User
        self.__artist_list: dict[str, Artist] = {}   # staff_id → Artist
        self.__admin_list: dict[str, Admin] = {}     # staff_id → Admin
        self.__order_list: dict[str, Order] = {}     # order_id → Order
        self.__studio_list: list[Studio] = []
        self.__bank = SoonSakBank(bank_id="SSB-001")

        # ── Counters สำหรับ generate ID ──
        self.__booking_counter = 0
        self.__order_counter = 0
        self.__txn_counter = 0
        self.__rating_counter = 0
        self.__event_counter = 0
        self.__request_counter = 0

        # ── Session ──
        self.__logged_in_users: set[str] = set()

        print("=" * 50)
        print("  ระบบ SoonSak เริ่มต้นแล้ว")
        print("=" * 50)

    # ─────────────────────────────────────────────
    # ID Generators
    # ─────────────────────────────────────────────

    def __new_booking_id(self) -> str:
        self.__booking_counter += 1
        return f"BKG-{self.__booking_counter:03d}"

    def __new_order_id(self) -> str:
        self.__order_counter += 1
        return f"ORD-{self.__order_counter:03d}"

    def __new_txn_id(self) -> str:
        self.__txn_counter += 1
        return f"TXN-{self.__txn_counter:03d}"

    def __new_rating_id(self) -> str:
        self.__rating_counter += 1
        return f"RAT-{self.__rating_counter:03d}"

    def __new_event_id(self) -> str:
        self.__event_counter += 1
        return f"EVT-{self.__event_counter:03d}"

    def __new_request_id(self) -> str:
        self.__request_counter += 1
        return f"REQ-{self.__request_counter:03d}"

    # ─────────────────────────────────────────────
    # Authentication
    # ─────────────────────────────────────────────

    def login(self, user_id: str) -> bool:
        entity = self.find_user(user_id) or self.__artist_list.get(user_id) or self.__admin_list.get(user_id)

        if entity is None:
            print(f"[Login] ไม่พบ ID: {user_id}")
            return False

        if isinstance(entity, User) and entity.status == User.STATUS_SUSPENDED:
            print(f"[Login] บัญชี {user_id} ถูกระงับ ไม่สามารถล็อกอินได้")
            return False

        self.__logged_in_users.add(user_id)
        print(f"[Login] {entity.name} ล็อกอินสำเร็จ")
        return True

    def logout(self, user_id: str):
        if user_id in self.__logged_in_users:
            self.__logged_in_users.discard(user_id)
            print(f"[Logout] {user_id} ออกจากระบบแล้ว")
        else:
            print(f"[Logout] {user_id} ยังไม่ได้ล็อกอิน")

    def __require_login(self, user_id: str):
        if user_id not in self.__logged_in_users:
            raise PermissionError(f"{user_id} ต้องล็อกอินก่อน")

    # ─────────────────────────────────────────────
    # User Management
    # ─────────────────────────────────────────────

    def register_user(self, user_id: str, name: str,
                      email: str, phone: str,
                      is_vip: bool = False, vip_rank: str = "SILVER") -> User:
        if user_id in self.__user_list:
            raise ValueError(f"User {user_id} มีอยู่แล้ว")

        if is_vip:
            user = VIPMember(user_id, name, email, phone, vip_rank)
        else:
            user = User(user_id, name, email, phone)

        self.__user_list[user_id] = user
        print(f"[Register] ลงทะเบียน {user} สำเร็จ")
        return user

    def register_artist(self, staff_id: str, name: str,
                        email: str, experience: int = 0) -> Artist:
        if staff_id in self.__artist_list:
            raise ValueError(f"Artist {staff_id} มีอยู่แล้ว")
        artist = Artist(staff_id, name, email, experience)
        self.__artist_list[staff_id] = artist
        print(f"[Register] ลงทะเบียน {artist} สำเร็จ รอ Admin อนุมัติ")
        return artist

    def register_admin(self, staff_id: str, name: str, email: str) -> Admin:
        admin = Admin(staff_id, name, email)
        self.__admin_list[staff_id] = admin
        print(f"[Register] สร้าง Admin {admin} สำเร็จ")
        return admin

    def find_user(self, user_id: str) -> User:
        return self.__user_list.get(user_id)

    def find_artist(self, artist_id: str) -> Artist:
        return self.__artist_list.get(artist_id)

    def find_order(self, order_id: str) -> Order:
        return self.__order_list.get(order_id)

    # ─────────────────────────────────────────────
    # Booking Flow
    # ─────────────────────────────────────────────

    def create_booking(self, user_id: str, artist_id: str,
                       body_part: str, size: str,
                       color_tone: str, base_price: float,
                       reference_image: str = "") -> Booking:
        self.__require_login(user_id)

        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")

        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        if artist.status != Artist.STATUS_VERIFIED:
            raise Exception(f"Artist {artist_id} ยังไม่ผ่านการยืนยันตัวตน")

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

        booking_id = self.__new_booking_id()
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

        user.add_history(booking)
        print(f"[SoonSak] สร้าง {booking} สำเร็จ")
        return booking

    def cancel_booking(self, user_id: str, booking: Booking):
        self.__require_login(user_id)
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
        user = self.find_user(booking.user_id)
        final_price = booking.base_price

        if apply_vip_discount and user is not None and isinstance(user, VIPMember):
            discount = user.calculate_discount(final_price)
            final_price -= discount
            print(f"[SoonSak] หักส่วนลด VIP {user.rank}: ราคาจาก {booking.base_price:.2f} → {final_price:.2f} บาท")

        if coupon_code and user is not None:
            try:
                final_price = user.use_coupon(coupon_code, final_price)
                print(f"[SoonSak] หักคูปอง {coupon_code}: ราคาสุดท้าย {final_price:.2f} บาท")
            except ValueError as e:
                print(f"[SoonSak] ⚠️ ใช้คูปองไม่ได้: {e}")

        booking.set_price(final_price)

        order_id = self.__new_order_id()
        order = Order(order_id=order_id)
        order.add_booking(booking)
        self.__order_list[order_id] = order
        print(f"[SoonSak] สร้าง {order} สำเร็จ")
        return order

    def process_payment(self, user_id: str, order: Order,
                        payment_method: PaymentMethod,
                        deposit_policy: DepositPolicy = None,
                        pay_full: bool = False) -> Payment:
        self.__require_login(user_id)

        payment = Payment(
            payment_id=f"PAY-{self.__order_counter:03d}",
            order=order,
            bank=self.__bank
        )
        payment.set_payment_method(payment_method)

        if deposit_policy:
            payment.set_deposit_policy(deposit_policy)

        if pay_full:
            txn = payment.pay_full(user_id, self.__txn_counter + 1)
            self.__txn_counter += 1

            total_paid = order.calculate_total()
            user = self.find_user(user_id)
            if user is not None:
                user.add_spent(total_paid)
                self.__check_vip_upgrade(user)
        else:
            txn = payment.pay_deposit(user_id, self.__txn_counter + 1)
            self.__txn_counter += 1

        return payment

    def __check_vip_upgrade(self, user):
        spent = user.total_spent

        if not isinstance(user, VIPMember):
            if spent >= VIPMember.RANK_THRESHOLD["SILVER"]:
                vip = VIPMember(
                    user_id=user.user_id,
                    name=user.name,
                    email=user.email,
                    phone_number=user._User__phone_number,
                    rank=VIPMember.RANK_SILVER
                )
                vip._User__bookings_history       = user._User__bookings_history
                vip._User__coupon_list            = user._User__coupon_list
                vip._User__credit                 = user.credit
                vip._User__status                 = user.status
                vip._User__completed_tattoo_count = user.completed_tattoo_count
                vip._User__total_spent            = spent

                vip.check_and_upgrade()
                self.__user_list[user.user_id] = vip
                print(f"[SoonSak] 🎉 {vip.name} ได้รับสถานะ VIPMember! "
                      f"rank={vip.rank} (ยอดสะสม {spent:,.2f} บาท)")
        else:
            user.check_and_upgrade()

    def request_payment_sum(self, order_id: str) -> float:
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
        self.__require_login(user_id)

        if booking.status != Booking.STATUS_COMPLETED:
            raise Exception("สามารถให้คะแนนได้เฉพาะ Booking ที่เสร็จแล้ว")

        if booking.user_id != user_id:
            raise PermissionError("ไม่มีสิทธิ์รีวิว Booking ของคนอื่น")

        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        rating = Rating(
            rating_id=self.__new_rating_id(),
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
        self.__require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.accept_job(booking)

    def artist_reject_job(self, artist_id: str, booking: Booking, reason: str = ""):
        self.__require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.reject_job(booking, reason)

    def artist_complete_job(self, artist_id: str, booking: Booking):
        self.__require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        artist.complete_job(booking)

        user = self.find_user(booking.user_id)
        if user is None:
            return

        user._User__completed_tattoo_count += 1
        print(f"[SoonSak] {user.name} สักแล้วทั้งหมด {user.completed_tattoo_count} ครั้ง")

    def artist_request_studio(self, artist_id: str,
                              studio_name: str, location: str) -> StudioRequest:
        self.__require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")

        request = StudioRequest(
            request_id=self.__new_request_id(),
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
        self.__require_login(admin_id)
        admin = self.__admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        admin.approve_artist(artist)

    def admin_approve_studio(self, admin_id: str,
                             request: StudioRequest) -> Studio:
        self.__require_login(admin_id)
        admin = self.__admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        studio = admin.approve_studio(request, self.__studio_list)
        return studio

    def admin_reject_studio(self, admin_id: str, request: StudioRequest):
        self.__require_login(admin_id)
        admin = self.__admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        admin.reject_studio(request)

    def admin_suspend_user(self, admin_id: str, user_id: str):
        self.__require_login(admin_id)
        admin = self.__admin_list.get(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")
        admin.suspend_user(user)

    def admin_add_coupon(self, admin_id: str, user_id: str,
                         coupon_code: str, discount: float,
                         expired: date) -> Coupon:
        self.__require_login(admin_id)
        admin = self.__admin_list.get(admin_id)
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
    # Reports
    # ─────────────────────────────────────────────

    def report_bank_balance(self):
        print("\n" + "─" * 40)
        print("  รายงานยอดเงิน SoonSak Bank")
        print("─" * 40)
        self.__bank.check_balance()
        history = self.__bank.get_history()
        print(f"  รายการทั้งหมด: {len(history)} รายการ")
        for txn in history:
            print(f"  {txn}")
        print("─" * 40 + "\n")

    def report_artist_ratings(self, artist_id: str):
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        avg = artist.average_rating()
        print(f"\n[Report] {artist.name} คะแนนเฉลี่ย: {avg:.2f}/5")
        return avg

    def view_artist(self, artist_id: str) -> dict:
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        return {
            "artist_id": artist.staff_id,
            "name": artist.name,
            "experience": artist._Artist__experience,
            "status": artist.status,
            "avg_rating": artist.average_rating(),
            "deposit_policy": str(artist.deposit_policy),
        }


# ═══════════════════════════════════════════════
# DEMO - รันเพื่อทดสอบระบบ (พร้อม Expected Output)
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    from datetime import date

    def section(title):
        print(f"\n{'═'*60}")
        print(f"  {title}")
        print('═'*60)

    section("DEMO: ระบบ SoonSak - Full Flow Test")

    system = SoonSak()

    section("1. ลงทะเบียน")

    user1 = system.register_user("USR-001", "อาทิตย์", "sun@mail.com", "0811111111")
    user2 = system.register_user("USR-002", "จันทร์", "moon@mail.com", "0833333333")

    artist1 = system.register_artist("ART-001", "ช่างแจ็ค", "jack@mail.com", experience=5)
    artist2 = system.register_artist("ART-002", "ช่างแนน", "nan@mail.com", experience=2)
    admin1  = system.register_admin("ADM-001", "ผู้ดูแล", "admin@soonsak.com")

    for uid in ["ADM-001", "ART-001", "ART-002", "USR-001", "USR-002"]:
        system.login(uid)

    section("2. Admin อนุมัติ Artist")
    system.admin_approve_artist("ADM-001", "ART-001")
    system.admin_approve_artist("ADM-001", "ART-002")

    policy_percent = PercentDepositPolicy(percent=30)
    policy_fixed   = FixedDepositPolicy(fixed_amount=500)
    artist1.set_deposit_policy(policy_percent)
    artist2.set_deposit_policy(policy_fixed)

    section("3. Flow A — Artist ปฏิเสธงาน")
    b_reject = system.create_booking("USR-001", "ART-001", "ข้อมือ", "เล็ก", "ขาว-ดำ", 800.0)
    system.artist_reject_job("ART-001", b_reject, reason="ไม่ว่างในวันที่นัด")
    print(f"  → [Actual] Booking status: {b_reject.status} | [Expected]: CANCELLED")

    section("4. Flow B — User ยกเลิก Booking เอง")
    b_cancel = system.create_booking("USR-002", "ART-002", "ต้นแขน", "กลาง", "สี", 2000.0)
    system.cancel_booking("USR-002", b_cancel)
    print(f"  → [Actual] Booking status: {b_cancel.status} | [Expected]: CANCELLED")

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
    print(f"  → [Actual] ยอดสะสม: {u.total_spent:,.2f} บาท | [Expected]: 3,000.00 บาท")
    print(f"  → [Actual] Type: {type(u).__name__} | [Expected]: User")

    section("6. Flow D — ยอดสะสมถึง 5,000 → Trigger VIP SILVER")
    b2 = system.create_booking("USR-001", "ART-001", "หลัง", "กลาง", "สี", 2500.0)
    system.artist_accept_job("ART-001", b2)
    o2 = system.create_order(b2)
    system.process_payment("USR-001", o2, Promptpay("0811111111"), policy_percent)
    system.process_payment("USR-001", o2, Promptpay("0811111111"), pay_full=True)
    system.artist_complete_job("ART-001", b2)
    system.rate_artist("USR-001", "ART-001", b2, 4, "โอเคมาก")
    u = system.find_user("USR-001")
    print(f"  → [Actual] ยอดสะสม: {u.total_spent:,.2f} บาท | [Expected]: 5,500.00 บาท")
    print(f"  → [Actual] Type: {type(u).__name__} | [Expected]: VIPMember")
    if isinstance(u, VIPMember):
        print(f"  → {u.vip_status_summary()} | [Expected Rank]: SILVER")

    section("7. Flow E — ยอดสะสมถึง 15,000 → Trigger VIP GOLD")
    for part, price in [("ขา", 4000.0), ("ต้นคอ", 3500.0), ("หน้าอก", 3000.0)]:
        b = system.create_booking("USR-001", "ART-001", part, "กลาง", "สี", price)
        system.artist_accept_job("ART-001", b)
        o = system.create_order(b)
        system.process_payment("USR-001", o, Promptpay("0811111111"), policy_percent)
        system.process_payment("USR-001", o, Promptpay("0811111111"), pay_full=True)
        system.artist_complete_job("ART-001", b)
    u = system.find_user("USR-001")
    print(f"  → [Actual] ยอดสะสม: {u.total_spent:,.2f} บาท | [Expected]: 16,000.00 บาท")
    if isinstance(u, VIPMember):
        print(f"  → {u.vip_status_summary()} | [Expected Rank]: GOLD")

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
        # 8000 หักลด VIP 10% (800) เหลือ 7200, ใช้คูปองอีก 10% (720) เหลือ 6480.
        # ยอดรวมก่อนหน้าคือ 16000 + 6480 = 22480 บาท
        print(f"\n  → [Actual] VIP Status ล่าสุด: {u.vip_status_summary()}")
        print(f"  → [Expected ยอดสะสม]: 22,480.00 บาท")

    section("9. Flow G — Studio Request")
    req = system.artist_request_studio("ART-001", "Jack's Ink Studio", "กรุงเทพฯ")
    system.admin_approve_studio("ADM-001", req)
    req2 = system.artist_request_studio("ART-002", "Nan's Art Studio", "เชียงใหม่")
    system.admin_reject_studio("ADM-001", req2)
    print(f"  → [Actual] req2 status: {req2.status} | [Expected]: REJECTED")

    section("10. Reports สรุปทั้งระบบ")
    system.report_artist_ratings("ART-001")
    system.report_bank_balance()

    print("\n  📋 User List:")
    # ใช้ Name Mangling ดึงข้อมูลเพื่อ Report
    for uid, u in system._SoonSak__user_list.items():
        utype = type(u).__name__
        spent = f"{u.total_spent:,.2f}"
        rank  = f" | rank={u.rank}" if isinstance(u, VIPMember) else ""
        print(f"    [{uid}] {u.name} | {utype}{rank} | ยอดสะสม {spent} บาท")

    section("11. Logout")
    for uid in ["USR-001", "USR-002", "ART-001", "ART-002", "ADM-001"]:
        system.logout(uid)

    print("\n" + "═"*60)
    print("   DEMO เสร็จสิ้น ✅")
    print("═"*60)