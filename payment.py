"""
payment.py — DepositPolicy, PaymentMethod, Transaction, SoonSakBank, Payment
"""

from abc import ABC, abstractmethod
from datetime import datetime


class DepositPolicy(ABC):
    """Abstract — นโยบายมัดจำ (Polymorphism)"""

    @abstractmethod
    def calculate_deposit(self, full_price: float) -> float:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class FixedDepositPolicy(DepositPolicy):
    """มัดจำแบบจำนวนตายตัว เช่น 500 บาทเสมอ"""

    def __init__(self, fixed_amount: float):
        if fixed_amount < 0:
            raise ValueError("จำนวนมัดจำต้องไม่ติดลบ")
        self._fixed_amount = fixed_amount

    def calculate_deposit(self, full_price: float) -> float:
        deposit = min(self._fixed_amount, full_price)
        print(f"[FixedDeposit] มัดจำ {deposit:.2f} บาท")
        return deposit

    def __repr__(self):
        return f"<FixedDepositPolicy amount={self._fixed_amount}>"


class PercentDepositPolicy(DepositPolicy):
    """มัดจำแบบเปอร์เซ็นต์ เช่น 30% ของราคาเต็ม"""

    def __init__(self, percent: float):
        if not (0 < percent <= 100):
            raise ValueError("เปอร์เซ็นต์ต้องอยู่ระหว่าง 0-100")
        self._percent = percent

    def calculate_deposit(self, full_price: float) -> float:
        deposit = full_price * (self._percent / 100)
        print(f"[PercentDeposit] มัดจำ {self._percent}% = {deposit:.2f} บาท")
        return deposit

    def __repr__(self):
        return f"<PercentDepositPolicy percent={self._percent}%>"


class PaymentMethod(ABC):
    """Abstract — ช่องทางการชำระเงิน (Polymorphism)"""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Promptpay(PaymentMethod):
    """ชำระผ่าน PromptPay"""

    def __init__(self, phone_or_id: str, bank: str = "KBANK"):
        self._phone_or_id = phone_or_id
        self._bank = bank

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        print(f"[Promptpay] ส่ง {amount:.2f} บาท ไปที่ {self._phone_or_id} ({self._bank})")
        return True

    def kbank(self):
        print(f"[Promptpay] เชื่อมต่อ KBank สำเร็จ")

    def __repr__(self):
        return f"<Promptpay id={self._phone_or_id} bank={self._bank}>"


class Transaction:
    """บันทึกรายการโอนเงิน
    Status: PENDING → SUCCESS / FAILED
    """

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED  = "FAILED"

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
        self._status = self.STATUS_SUCCESS
        print(f"[Transaction] {self._transaction_id} สำเร็จ ({self._amount:.2f} บาท)")

    def mark_failed(self):
        self._status = self.STATUS_FAILED
        print(f"[Transaction] {self._transaction_id} ล้มเหลว")

    def __repr__(self):
        return f"<Transaction id={self._transaction_id} amount={self._amount} status={self._status}>"


class SoonSakBank:
    """บัญชีกลางของระบบ — Composition กับ Transaction"""

    def __init__(self, bank_id: str):
        self._bank_id = bank_id
        self._balance: float = 0.0
        self._transaction_list: list[Transaction] = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount: float, transaction: Transaction):
        if amount <= 0:
            raise ValueError("จำนวนเงินต้องมากกว่า 0")
        self._balance += amount
        transaction.mark_success()
        self._transaction_list.append(transaction)
        print(f"[SoonSakBank] รับเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self._balance:.2f}")

    def withdraw(self, amount: float, transaction: Transaction):
        if amount > self._balance:
            transaction.mark_failed()
            raise ValueError("ยอดเงินในบัญชีไม่พอ")
        self._balance -= amount
        transaction.mark_success()
        self._transaction_list.append(transaction)
        print(f"[SoonSakBank] โอนเงิน {amount:.2f} บาท | ยอดคงเหลือ: {self._balance:.2f}")

    def check_balance(self) -> float:
        print(f"[SoonSakBank] ยอดคงเหลือ: {self._balance:.2f} บาท")
        return self._balance

    def get_history(self) -> list[Transaction]:
        return list(self._transaction_list)

    def __repr__(self):
        return f"<SoonSakBank id={self._bank_id} balance={self._balance:.2f}>"


class Payment:
    """จัดการกระบวนการชำระเงิน
    เชื่อม Order → PaymentMethod → Transaction → SoonSakBank
    """

    def __init__(self, payment_id: str, order, bank: SoonSakBank):
        self._payment_id = payment_id
        self._order = order
        self._bank = bank
        self._payment_method: PaymentMethod = None
        self._transactions: list[Transaction] = []
        self._deposit_policy: DepositPolicy = None

    def set_payment_method(self, method: PaymentMethod):
        self._payment_method = method
        print(f"[Payment] เลือกวิธีชำระ: {method}")

    def set_deposit_policy(self, policy: DepositPolicy):
        self._deposit_policy = policy

    def validate(self) -> bool:
        if self._payment_method is None:
            raise ValueError("ยังไม่ได้เลือกวิธีชำระเงิน")
        if self._order.calculate_total() <= 0:
            raise ValueError("ยอดรวมต้องมากกว่า 0")
        print(f"[Payment] ผ่านการตรวจสอบแล้ว")
        return True

    def pay_deposit(self, user_id: str, txn_counter: int) -> Transaction:
        self.validate()
        total = self._order.calculate_total()
        if self._deposit_policy:
            deposit_amount = self._deposit_policy.calculate_deposit(total)
        else:
            deposit_amount = total * 0.3  # default 30%
        success = self._payment_method.pay(deposit_amount)
        if not success:
            raise Exception("การชำระเงินล้มเหลว")
        txn = self.create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=deposit_amount,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )
        self._bank.deposit(deposit_amount, txn)
        self._order.pay_deposit(deposit_amount)
        return txn

    def pay_full(self, user_id: str, txn_counter: int) -> Transaction:
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