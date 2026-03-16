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
    def __init__(self):
        self.__user_list: list[User]     = []
        self.__artist_list: list[Artist] = []
        self.__admin_list: list[Admin]   = []
        self.__order_list: list[Order]   = []
        self.__studio_list: list[Studio] = []
        self.__bank = SoonSakBank(bank_id="SSB-001")
        self.__booking_counter  = 0
        self.__order_counter    = 0
        self.__txn_counter      = 0
        self.__rating_counter   = 0
        self.__event_counter    = 0
        self.__request_counter  = 0
        self.__logged_in_users: list[str] = []
        self.__appointment_counter = 0 
        
    @property
    def _user_list(self): return self.__user_list

    @property
    def _artist_list(self): return self.__artist_list

    @property
    def _admin_list(self): return self.__admin_list

    @property
    def _order_list(self): return self.__order_list

    @property
    def _studio_list(self): return self.__studio_list

    @property
    def _logged_in_users(self): return self.__logged_in_users

    def _new_appointment_id(self) -> str:
        self.__appointment_counter += 1
        return f"APT-{self.__appointment_counter:03d}"
    
    def add_appointment(
        self,
        user_id: str,
        booking: Booking,
        appointment_date: date,
        start_time: str = "10:00",
        end_time: str = "18:00"
    ) -> Appointment:
        self.__require_login(user_id)
        
        artist = self.find_artist(booking.artist_id)
        if not artist.is_available(appointment_date):
            raise Exception(f"Artist {booking.artist_id} ไม่ว่างวันที่ {appointment_date}")
        
        session_number = booking.appointment_count + 1
        appointment = Appointment(
            appointment_id=self._new_appointment_id(),
            booking_id=booking.booking_id,
            session_number=session_number,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time
        )
        
        booking.add_appointment(appointment)
        
        event = Event(
            event_id=f"EVT-{self.__event_counter+1:03d}",
            event_name=f"Tattoo Session #{session_number} for {booking.user_id}",
            event_date=appointment_date,
            start_time=start_time,
            end_time=end_time
        )
        self.__event_counter += 1
        artist.manage_time(event)
        
        print(f"[SoonSak] เพิ่ม Appointment #{session_number} (วันที่ {appointment_date}) เข้า Booking {booking.booking_id}")
        return appointment
    
    def _new_booking_id(self) -> str:
        self.__booking_counter += 1
        return f"BKG-{self.__booking_counter:03d}"

    def _new_order_id(self) -> str:
        self.__order_counter += 1
        return f"ORD-{self.__order_counter:03d}"

    def _new_rating_id(self) -> str:
        self.__rating_counter += 1
        return f"RAT-{self.__rating_counter:03d}"

    def _new_request_id(self) -> str:
        self.__request_counter += 1
        return f"REQ-{self.__request_counter:03d}"

    def login(self, user_id: str, password: str) -> bool:
        entity = self.find_user(user_id) or self.find_artist(user_id) or self.__find_admin(user_id)
        if entity is None:
            print(f"[Login] ไม่พบ ID: {user_id}")
            return False
        if not entity.check_password(password):
            print(f"[Login] รหัสผ่านไม่ถูกต้อง")
            return False
        if isinstance(entity, User) and entity.status == User.STATUS_SUSPENDED:
            print(f"[Login] บัญชี {user_id} ถูกระงับ")
            return False
        if user_id not in self.__logged_in_users:
            self.__logged_in_users.append(user_id)
        print(f"[Login] {entity.name} ล็อกอินสำเร็จ")
        return True

    def logout(self, user_id: str):
        if user_id in self.__logged_in_users:
            self.__logged_in_users.remove(user_id)
            print(f"[Logout] {user_id} ออกจากระบบแล้ว")
        else:
            print(f"[Logout] {user_id} ยังไม่ได้ล็อกอิน")

    def __require_login(self, user_id: str):
        if user_id not in self.__logged_in_users:
            raise PermissionError(f"{user_id} ต้องล็อกอินก่อน")

    def _require_login(self, user_id: str):
        self.__require_login(user_id)

    def find_user(self, user_id: str) -> User:
        for user in self.__user_list:
            if user.user_id == user_id:
                return user
        return None

    def find_artist(self, artist_id: str) -> Artist:
        for artist in self.__artist_list:
            if artist.staff_id == artist_id:
                return artist
        return None

    def find_order(self, order_id: str) -> Order:
        for order in self.__order_list:
            if order.order_id == order_id:
                return order
        return None

    def __find_admin(self, admin_id: str) -> Admin:
        for admin in self.__admin_list:
            if admin.staff_id == admin_id:
                return admin
        return None

    def register_user(self, user_id: str, name: str, email: str,
                      phone: str, password: str) -> User:
        if self.find_user(user_id) is not None:
            raise ValueError(f"User {user_id} มีอยู่แล้ว")
        user = User(user_id, name, email, phone, password)
        self.__user_list.append(user)
        print(f"[Register] ลงทะเบียน {user} สำเร็จ")
        return user

    def register_artist(self, staff_id: str, name: str, email: str,
                        password: str, experience: int = 0) -> Artist:
        if self.find_artist(staff_id) is not None:
            raise ValueError(f"Artist {staff_id} มีอยู่แล้ว")
        artist = Artist(staff_id, name, email, password, experience)
        self.__artist_list.append(artist)
        print(f"[Register] ลงทะเบียน {artist} สำเร็จ รอ Admin อนุมัติ")
        return artist

    def register_admin(self, staff_id: str, name: str, email: str,
                       password: str) -> Admin:
        admin = Admin(staff_id, name, email, password)
        self.__admin_list.append(admin)
        print(f"[Register] สร้าง Admin {admin} สำเร็จ")
        return admin

    def create_booking(self, user_id: str, artist_id: str,
                   body_part: str, size: str, color_tone: str,
                   base_price: float,
                   description: str = "",
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

        active = [b for b in user.view_history()
                if hasattr(b, 'status') and b.status in (Booking.STATUS_WAITING, Booking.STATUS_ACCEPTED)]
        if len(active) >= user.max_bookings:
            raise Exception(f"จองพร้อมกันได้สูงสุด {user.max_bookings} รายการ")

        booking = Booking(
            booking_id=self._new_booking_id(),
            user_id=user_id, 
            artist_id=artist_id,
            body_part=body_part, 
            size=size, 
            color_tone=color_tone,
            base_price=base_price,
            description=description,
            reference_image=reference_image
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

    def create_order(self, booking: Booking,
                 apply_vip_discount: bool = True,
                 coupon_code: str = None) -> Order:
        user = self.find_user(booking.user_id)
        final_price = booking.base_price

        if apply_vip_discount and user is not None and isinstance(user, VIPMember):
            discount = user.calculate_discount(final_price)
            final_price -= discount
            print(f"[SoonSak] หักส่วนลด VIP {user.rank}: {booking.base_price:.2f} -> {final_price:.2f} บาท")

        if coupon_code and user is not None:
            try:
                final_price = user.use_coupon(coupon_code, final_price)
                print(f"[SoonSak] หักคูปอง {coupon_code}: ราคาสุดท้าย {final_price:.2f} บาท")
            except ValueError as e:
                print(f"[SoonSak] ใช้คูปองไม่ได้: {e}")

        booking.set_price(final_price)
        order = Order(order_id=self._new_order_id(), booking=booking)
        self.__order_list.append(order)
        print(f"[SoonSak] สร้าง {order} สำเร็จ")
        return order

    def process_payment(self, user_id: str, order: Order,
                        payment_method: PaymentMethod,
                        deposit_policy: DepositPolicy = None,
                        pay_full: bool = False) -> Payment:
        self.__require_login(user_id)
        payment = Payment(payment_id=f"PAY-{self.__order_counter:03d}", order=order, bank=self.__bank)
        payment.set_payment_method(payment_method)
        if deposit_policy:
            payment.set_deposit_policy(deposit_policy)

        if pay_full:
            payment.pay_full(user_id, self.__txn_counter + 1)
            self.__txn_counter += 1
            user = self.find_user(user_id)
            if user is not None:
                remaining = order.calculate_total() - order.deposit_amount
                user.add_spent(remaining if remaining > 0 else order.calculate_total())
                self.__check_vip_upgrade(user)
        else:
            payment.pay_deposit(user_id, self.__txn_counter + 1)
            self.__txn_counter += 1

        return payment

    def __check_vip_upgrade(self, user: User):
        spent = user._total_spent
        if not isinstance(user, VIPMember):
            if spent >= VIPMember.THRESHOLD_SILVER:
                vip = VIPMember(user.user_id, user.name, user.email,
                                user._phone_number, user._password)
                vip._bookings_history.extend(user.view_history())
                vip._coupon_list.extend(user._coupon_list)
                vip._credit = user._credit
                vip._status = user._status
                vip._completed_tattoo_count = user._completed_tattoo_count
                vip._total_spent = spent
                vip.check_and_upgrade()
                for i, u in enumerate(self.__user_list):
                    if u.user_id == user.user_id:
                        self.__user_list[i] = vip
                        break
                print(f"[SoonSak] {vip.name} ได้รับสถานะ VIPMember! rank={vip.rank} (ยอดสะสม {spent:,.2f} บาท)")
        else:
            user.check_and_upgrade()

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
        if user is not None:
            user._completed_tattoo_count += 1
            print(f"[SoonSak] {user.name} สักแล้วทั้งหมด {user._completed_tattoo_count} ครั้ง")

    def artist_request_studio(self, artist_id: str, studio_name: str, location: str) -> StudioRequest:
        self.__require_login(artist_id)
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        request = StudioRequest(self._new_request_id(), artist_id, studio_name, location)
        artist.request_studio(request)
        return request

    def admin_approve_artist(self, admin_id: str, artist_id: str):
        self.__require_login(admin_id)
        admin = self.__find_admin(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        admin.approve_artist(artist)

    def admin_approve_studio(self, admin_id: str, request: StudioRequest) -> Studio:
        self.__require_login(admin_id)
        admin = self.__find_admin(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        return admin.approve_studio(request, self.__studio_list)

    def admin_reject_studio(self, admin_id: str, request: StudioRequest):
        self.__require_login(admin_id)
        admin = self.__find_admin(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        admin.reject_studio(request)

    def admin_suspend_user(self, admin_id: str, user_id: str):
        self.__require_login(admin_id)
        admin = self.__find_admin(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")
        admin.suspend_user(user)

    def admin_add_coupon(self, admin_id: str, user_id: str,
                         coupon_code: str, discount: float, expired: date) -> Coupon:
        self.__require_login(admin_id)
        admin = self.__find_admin(admin_id)
        if admin is None:
            raise PermissionError("ไม่มีสิทธิ์ Admin")
        user = self.find_user(user_id)
        if user is None:
            raise ValueError(f"ไม่พบ User {user_id}")
        coupon = Coupon(coupon_code, discount, expired)
        user.add_coupon(coupon)
        print(f"[Admin] เพิ่มคูปอง {coupon_code} ({discount}%) ให้ {user.name}")
        return coupon

    def rate_artist(self, user_id: str, artist_id: str,
                    booking: Booking, score: int, comment: str) -> Rating:
        self.__require_login(user_id)
        if booking.status != Booking.STATUS_COMPLETED:
            raise Exception("ให้คะแนนได้เฉพาะ Booking ที่ COMPLETED")
        if booking.user_id != user_id:
            raise PermissionError("ไม่มีสิทธิ์รีวิว Booking ของคนอื่น")
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        rating = Rating(self._new_rating_id(), score, comment, user_id, artist_id)
        artist.add_rating(rating)
        print(f"[SoonSak] {user_id} ให้คะแนน Artist {artist_id}: {score}/5")
        return rating

    def report_bank_balance(self):
        print("\n" + "-" * 40)
        print("  รายงานยอดเงิน SoonSak Bank")
        print("-" * 40)
        self.__bank.check_balance()
        history = self.__bank.get_history()
        print(f"  รายการทั้งหมด: {len(history)} รายการ")
        for txn in history:
            print(f"  {txn}")
        print("-" * 40 + "\n")

    def report_artist_ratings(self, artist_id: str):
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        avg = artist.average_rating()
        print(f"\n[Report] {artist.name} คะแนนเฉลี่ย: {avg:.2f}/5")
        return avg

    def view_artist(self, artist_id: str) -> str:
        artist = self.find_artist(artist_id)
        if artist is None:
            raise ValueError(f"ไม่พบ Artist {artist_id}")
        return (
            f"artist_id     : {artist.staff_id}\n"
            f"name          : {artist.name}\n"
            f"experience    : {artist._experience} ปี\n"
            f"status        : {artist.status}\n"
            f"avg_rating    : {artist.average_rating():.2f}/5\n"
            f"deposit_policy: {artist.deposit_policy}"
        )