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
        self.__fixed_amount = fixed_amount

    def calculate_deposit(self, full_price: float) -> float:
        """คืนยอดมัดจำแบบ fixed (Polymorphism override)"""
        deposit = min(self.__fixed_amount, full_price)  # ไม่เกินราคาจริง
        print(f"[FixedDeposit] มัดจำ {deposit:.2f} บาท (Fixed)")
        return deposit

    def __repr__(self):
        return f"<FixedDepositPolicy amount={self.__fixed_amount}>"


class PercentDepositPolicy(DepositPolicy):
    """
    มัดจำแบบเปอร์เซ็นต์ เช่น 30% ของราคาเต็ม
    """

    def __init__(self, percent: float):
        if not (0 < percent <= 100):
            raise ValueError("เปอร์เซ็นต์ต้องอยู่ระหว่าง 0-100")
        self.__percent = percent

    def calculate_deposit(self, full_price: float) -> float:
        """คืนยอดมัดจำแบบ percent (Polymorphism override)"""
        deposit = full_price * (self.__percent / 100)
        print(f"[PercentDeposit] มัดจำ {self.__percent}% = {deposit:.2f} บาท")
        return deposit

    def __repr__(self):
        return f"<PercentDepositPolicy percent={self.__percent}%>"


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
        self.__phone_or_id = phone_or_id
        self.__bank = bank

    def pay(self, amount: float) -> bool:
        """
        ส่งคำสั่งชำระเงินผ่าน PromptPay (Polymorphism override)
        จำลองการเชื่อมต่อธนาคาร
        """
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        print(f"[Promptpay] ส่ง {amount:.2f} บาท ไปที่ {self.__phone_or_id} ({self.__bank})")
        return True  # สมมติว่าสำเร็จเสมอในระบบ demo

    def kbank(self):
        """เชื่อมต่อ KBank API (จำลอง)"""
        print(f"[Promptpay] เชื่อมต่อ KBank สำเร็จ")

    def __repr__(self):
        return f"<Promptpay id={self.__phone_or_id} bank={self.__bank}>"


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

        self.__transaction_id = transaction_id
        self.__amount = amount
        self.__sender_id = sender_id
        self.__receiver_id = receiver_id
        self.__status = self.STATUS_PENDING
        self.__created_at = datetime.now()

    @property
    def transaction_id(self):
        return self.__transaction_id

    @property
    def amount(self):
        return self.__amount

    @property
    def status(self):
        return self.__status

    def mark_success(self):
        """บันทึกว่าโอนสำเร็จ"""
        self.__status = self.STATUS_SUCCESS
        print(f"[Transaction] {self.__transaction_id} สำเร็จ ({self.__amount:.2f} บาท)")

    def mark_failed(self):
        """บันทึกว่าโอนล้มเหลว"""
        self.__status = self.STATUS_FAILED
        print(f"[Transaction] {self.__transaction_id} ล้มเหลว")

    def __repr__(self):
        return (f"<Transaction id={self.__transaction_id} "
                f"amount={self.__amount} status={self.__status}>")


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
        self.__bank_id = bank_id
        self.__balance: float = 0.0
        self.__transaction_list: list[Transaction] = []  # B3: เก็บ History

    @property
    def balance(self):
        return self.__balance

    def deposit(self, amount: float, transaction: Transaction):
        """รับเงินเข้าบัญชี"""
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self.__balance += amount
        transaction.mark_success()
        self.__transaction_list.append(transaction)
        print(f"[SoonSakBank] รับเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self.__balance:.2f}")

    def withdraw(self, amount: float, transaction: Transaction):
        """โอนเงินออกไปให้ Artist"""
        if amount > self.__balance:
            transaction.mark_failed()
            raise ValueError("ยอดเงินในบัญชีไม่พอ")
        self.__balance -= amount
        transaction.mark_success()
        self.__transaction_list.append(transaction)
        print(f"[SoonSakBank] โอนเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self.__balance:.2f}")

    def check_balance(self) -> float:
        """ตรวจสอบยอดคงเหลือ"""
        print(f"[SoonSakBank] ยอดคงเหลือ: {self.__balance:.2f} บาท")
        return self.__balance

    def get_history(self) -> list[Transaction]:
        """ดูประวัติ Transaction ทั้งหมด (B3: เก็บ History)"""
        return list(self.__transaction_list)

    def __repr__(self):
        return f"<SoonSakBank id={self.__bank_id} balance={self.__balance:.2f}>"


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
        self.__payment_id = payment_id
        self.__order = order              # Order object
        self.__bank = bank
        self.__payment_method: PaymentMethod = None
        self.__transactions: list[Transaction] = []
        self.__deposit_policy: DepositPolicy = None

    def set_payment_method(self, method: PaymentMethod):
        """เลือกวิธีชำระเงิน"""
        self.__payment_method = method
        print(f"[Payment] เลือกวิธีชำระ: {method}")

    def set_deposit_policy(self, policy: DepositPolicy):
        """กำหนด DepositPolicy"""
        self.__deposit_policy = policy

    def validate(self) -> bool:
        """
        ตรวจสอบก่อนชำระ (B2: Validation)
        - มี payment method หรือยัง
        - Order อยู่ในสถานะที่ชำระได้
        - ยอดเงินถูกต้อง
        """
        if self.__payment_method is None:
            raise ValueError("ยังไม่ได้เลือกวิธีชำระเงิน")
        if self.__order.calculate_total() <= 0:
            raise ValueError("ยอดรวมต้องมากกว่า 0")
        print(f"[Payment] ผ่านการตรวจสอบแล้ว")
        return True

    def pay_deposit(self, user_id: str, txn_counter: int) -> Transaction:
        """
        ชำระมัดจำ
        ใช้ DepositPolicy คำนวณยอด แล้วโอนผ่าน PaymentMethod
        """
        self.validate()

        total = self.__order.calculate_total()

        # คำนวณมัดจำตาม policy
        if self.__deposit_policy:
            deposit_amount = self.__deposit_policy.calculate_deposit(total)
        else:
            deposit_amount = total * 0.3  # default 30%

        # ชำระผ่าน payment method
        success = self.__payment_method.pay(deposit_amount)
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
        self.__bank.deposit(deposit_amount, txn)
        self.__order.pay_deposit(deposit_amount)
        return txn

    def pay_full(self, user_id: str, txn_counter: int) -> Transaction:
        """ชำระส่วนที่เหลือทั้งหมด"""
        self.validate()

        total = self.__order.calculate_total()
        remaining = total - self.__order.deposit_amount

        if remaining <= 0:
            print("[Payment] ชำระครบแล้ว ไม่ต้องชำระเพิ่ม")
            return None

        success = self.__payment_method.pay(remaining)
        if not success:
            raise Exception("การชำระเงินล้มเหลว")

        txn = self.create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=remaining,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )

        self.__bank.deposit(remaining, txn)
        self.__order.pay_full()
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
        self.__transactions.append(txn)
        print(f"[Payment] สร้าง Transaction {txn_id} สำเร็จ")
        return txn

    def __repr__(self):
        return f"<Payment id={self.__payment_id} order={self.__order.order_id}>"