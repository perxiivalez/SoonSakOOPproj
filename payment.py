"""
payment.py
==========
ไฟล์นี้จัดการทุกอย่างที่เกี่ยวกับการเงิน ได้แก่
- DepositPolicy (Abstract + FixedDepositPolicy + PercentDepositPolicy)
- PaymentMethod (Abstract + Promptpay)
- Transaction
- SoonSakBank
- Payment (Controller การชำระเงิน)
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ─────────────────────────────────────────────
# DepositPolicy (Abstract)
# ─────────────────────────────────────────────

class DepositPolicy(ABC):
    """
    นโยบายการเก็บมัดจำ (Abstract Class)
    Subclass ต้อง implement calculate_deposit()
    นี่คือ Polymorphism: แต่ละ policy คำนวณต่างกัน
    """

    @abstractmethod
    def calculate_deposit(self, full_price: float) -> float:
        """คำนวณยอดมัดจำจากราคาเต็ม"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class FixedDepositPolicy(DepositPolicy):
    """
    มัดจำแบบกำหนดจำนวนตายตัว เช่น 500 บาทเสมอ
    """

    def __init__(self, fixed_amount: float):
        if fixed_amount < 0:
            raise ValueError("จำนวนมัดจำต้องไม่ติดลบ")
        self._fixed_amount = fixed_amount

    def calculate_deposit(self, full_price: float) -> float:
        """คืนยอดมัดจำแบบ fixed (Polymorphism override)"""
        deposit = min(self._fixed_amount, full_price)  # ไม่เกินราคาจริง
        print(f"[FixedDeposit] มัดจำ {deposit:.2f} บาท (Fixed)")
        return deposit

    def __repr__(self):
        return f"<FixedDepositPolicy amount={self._fixed_amount}>"


class PercentDepositPolicy(DepositPolicy):
    """
    มัดจำแบบเปอร์เซ็นต์ เช่น 30% ของราคาเต็ม
    """

    def __init__(self, percent: float):
        if not (0 < percent <= 100):
            raise ValueError("เปอร์เซ็นต์ต้องอยู่ระหว่าง 0-100")
        self._percent = percent

    def calculate_deposit(self, full_price: float) -> float:
        """คืนยอดมัดจำแบบ percent (Polymorphism override)"""
        deposit = full_price * (self._percent / 100)
        print(f"[PercentDeposit] มัดจำ {self._percent}% = {deposit:.2f} บาท")
        return deposit

    def __repr__(self):
        return f"<PercentDepositPolicy percent={self._percent}%>"


# ─────────────────────────────────────────────
# PaymentMethod (Abstract)
# ─────────────────────────────────────────────

class PaymentMethod(ABC):
    """
    วิธีการชำระเงิน (Abstract Class)
    แต่ละ subclass ใช้ช่องทางต่างกัน
    """

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """ดำเนินการชำระเงิน คืน True ถ้าสำเร็จ"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Promptpay(PaymentMethod):
    """
    ชำระเงินผ่าน PromptPay
    """

    def __init__(self, phone_or_id: str, bank: str = "KBANK"):
        self._phone_or_id = phone_or_id
        self._bank = bank

    def pay(self, amount: float) -> bool:
        """
        ส่งคำสั่งชำระเงินผ่าน PromptPay (Polymorphism override)
        จำลองการเชื่อมต่อธนาคาร
        """
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        print(f"[Promptpay] ส่ง {amount:.2f} บาท ไปที่ {self._phone_or_id} ({self._bank})")
        return True  # สมมติว่าสำเร็จเสมอในระบบ demo

    def kbank(self):
        """เชื่อมต่อ KBank API (จำลอง)"""
        print(f"[Promptpay] เชื่อมต่อ KBank สำเร็จ")

    def __repr__(self):
        return f"<Promptpay id={self._phone_or_id} bank={self._bank}>"


# ─────────────────────────────────────────────
# Transaction
# ─────────────────────────────────────────────

class Transaction:
    """
    บันทึกรายการโอนเงินแต่ละครั้ง
    Status: PENDING → SUCCESS / FAILED

    ID format: TXN-001
    """

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    def __init__(self, transaction_id: str, amount: float,
                 sender_id: str, receiver_id: str):
        if not transaction_id.startswith("TXN-"):
            raise ValueError("transaction_id ต้องขึ้นต้นด้วย TXN-")
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")

        self._transaction_id = transaction_id
        self._amount = amount
        self._sender_id = sender_id
        self._receiver_id = receiver_id
        self._status = self.STATUS_PENDING
        self._created_at = datetime.now()

    @property
    def transaction_id(self):
        return self._transaction_id

    @property
    def amount(self):
        return self._amount

    @property
    def status(self):
        return self._status

    def mark_success(self):
        """บันทึกว่าโอนสำเร็จ"""
        self._status = self.STATUS_SUCCESS
        print(f"[Transaction] {self._transaction_id} สำเร็จ ({self._amount:.2f} บาท)")

    def mark_failed(self):
        """บันทึกว่าโอนล้มเหลว"""
        self._status = self.STATUS_FAILED
        print(f"[Transaction] {self._transaction_id} ล้มเหลว")

    def __repr__(self):
        return (f"<Transaction id={self._transaction_id} "
                f"amount={self._amount} status={self._status}>")


# ─────────────────────────────────────────────
# SoonSakBank
# ─────────────────────────────────────────────

class SoonSakBank:
    """
    บัญชีธนาคารกลางของระบบ SoonSak
    รับเงินมัดจำและค่าบริการ ก่อนโอนให้ Artist
    มี Composition กับ Transaction (เก็บประวัติทุกรายการ)
    """

    def __init__(self, bank_id: str):
        self._bank_id = bank_id
        self._balance: float = 0.0
        self._transaction_list: list[Transaction] = []  # B3: เก็บ History

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float, transaction: Transaction):
        """รับเงินเข้าบัญชี"""
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self._balance += amount
        transaction.mark_success()
        self._transaction_list.append(transaction)
        print(f"[SoonSakBank] รับเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self._balance:.2f}")

    def withdraw(self, amount: float, transaction: Transaction):
        """โอนเงินออกไปให้ Artist"""
        if amount > self._balance:
            transaction.mark_failed()
            raise ValueError("ยอดเงินในบัญชีไม่พอ")
        self._balance -= amount
        transaction.mark_success()
        self._transaction_list.append(transaction)
        print(f"[SoonSakBank] โอนเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self._balance:.2f}")

    def check_balance(self) -> float:
        """ตรวจสอบยอดคงเหลือ"""
        print(f"[SoonSakBank] ยอดคงเหลือ: {self._balance:.2f} บาท")
        return self._balance

    def get_history(self) -> list[Transaction]:
        """ดูประวัติ Transaction ทั้งหมด (B3: เก็บ History)"""
        return list(self._transaction_list)

    def __repr__(self):
        return f"<SoonSakBank id={self._bank_id} balance={self._balance:.2f}>"


# ─────────────────────────────────────────────
# Payment
# ─────────────────────────────────────────────

class Payment:
    """
    จัดการกระบวนการชำระเงินทั้งหมด
    เชื่อม Order → PaymentMethod → Transaction → SoonSakBank

    กระบวนการ:
    1. validate()     - ตรวจสอบความถูกต้อง
    2. pay()          - ส่งคำสั่งชำระผ่าน PaymentMethod
    3. create_transaction() - บันทึกรายการ
    """

    def __init__(self, payment_id: str, order, bank: SoonSakBank):
        self._payment_id = payment_id
        self._order = order              # Order object
        self._bank = bank
        self._payment_method: PaymentMethod = None
        self._transactions: list[Transaction] = []
        self._deposit_policy: DepositPolicy = None

    def set_payment_method(self, method: PaymentMethod):
        """เลือกวิธีชำระเงิน"""
        self._payment_method = method
        print(f"[Payment] เลือกวิธีชำระ: {method}")

    def set_deposit_policy(self, policy: DepositPolicy):
        """กำหนด DepositPolicy"""
        self._deposit_policy = policy

    def validate(self) -> bool:
        """
        ตรวจสอบก่อนชำระ (B2: Validation)
        - มี payment method หรือยัง
        - Order อยู่ในสถานะที่ชำระได้
        - ยอดเงินถูกต้อง
        """
        if self._payment_method is None:
            raise ValueError("ยังไม่ได้เลือกวิธีชำระเงิน")
        if self._order.calculate_total() <= 0:
            raise ValueError("ยอดรวมต้องมากกว่า 0")
        print(f"[Payment] ผ่านการตรวจสอบแล้ว")
        return True

    def pay_deposit(self, user_id: str, txn_counter: int) -> Transaction:
        """
        ชำระมัดจำ
        ใช้ DepositPolicy คำนวณยอด แล้วโอนผ่าน PaymentMethod
        """
        self.validate()

        total = self._order.calculate_total()

        # คำนวณมัดจำตาม policy
        if self._deposit_policy:
            deposit_amount = self._deposit_policy.calculate_deposit(total)
        else:
            deposit_amount = total * 0.3  # default 30%

        # ชำระผ่าน payment method
        success = self._payment_method.pay(deposit_amount)
        if not success:
            raise Exception("การชำระเงินล้มเหลว")

        # บันทึก Transaction
        txn = self.create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=deposit_amount,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )

        # บันทึกเข้า Bank
        self._bank.deposit(deposit_amount, txn)
        self._order.pay_deposit(deposit_amount)
        return txn

    def pay_full(self, user_id: str, txn_counter: int) -> Transaction:
        """ชำระส่วนที่เหลือทั้งหมด"""
        self.validate()

        total = self._order.calculate_total()
        remaining = total - self._order.deposit_amount

        if remaining <= 0:
            print("[Payment] ชำระครบแล้ว ไม่ต้องชำระเพิ่ม")
            return None

        success = self._payment_method.pay(remaining)
        if not success:
            raise Exception("การชำระเงินล้มเหลว")

        txn = self.create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=remaining,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )

        self._bank.deposit(remaining, txn)
        self._order.pay_full()
        return txn

    def create_transaction(self, txn_id: str, amount: float,
                           sender_id: str, receiver_id: str) -> Transaction:
        """สร้าง Transaction ใหม่และบันทึกไว้"""
        txn = Transaction(
            transaction_id=txn_id,
            amount=amount,
            sender_id=sender_id,
            receiver_id=receiver_id
        )
        self._transactions.append(txn)
        print(f"[Payment] สร้าง Transaction {txn_id} สำเร็จ")
        return txn

    def __repr__(self):
        return f"<Payment id={self._payment_id} order={self._order.order_id}>"
