from abc import ABC, abstractmethod
from datetime import datetime


class DepositPolicy(ABC):
    @abstractmethod
    def calculate_deposit(self, full_price: float) -> float: pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class FixedDepositPolicy(DepositPolicy):
    def __init__(self, fixed_amount: float):
        if fixed_amount < 0:
            raise ValueError("Deposit amount cannot be negative")
        self.__fixed_amount = fixed_amount

    def calculate_deposit(self, full_price: float) -> float:
        deposit = min(self.__fixed_amount, full_price)
        print(f"[FixedDeposit] Deposit {deposit:.2f} THB")
        return deposit

    def __repr__(self):
        return f"<FixedDepositPolicy amount={self.__fixed_amount}>"


class PercentDepositPolicy(DepositPolicy):
    def __init__(self, percent: float):
        if not (0 < percent <= 100):
            raise ValueError("Percent must be between 0-100")
        self.__percent = percent

    def calculate_deposit(self, full_price: float) -> float:
        deposit = full_price * (self.__percent / 100)
        print(f"[PercentDeposit] Deposit {self.__percent}% = {deposit:.2f} THB")
        return deposit

    def __repr__(self):
        return f"<PercentDepositPolicy percent={self.__percent}%>"


class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Promptpay(PaymentMethod):
    def __init__(self, phone_or_id: str, bank: str = "KBANK"):
        self.__phone_or_id = phone_or_id
        self.__bank = bank

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        print(f"[Promptpay] Sent {amount:.2f} THB to {self.__phone_or_id} ({self.__bank})")
        return True

    def kbank(self):
        print(f"[Promptpay] Connected to KBank successfully")

    def __repr__(self):
        return f"<Promptpay id={self.__phone_or_id} bank={self.__bank}>"


class Transaction:
    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED  = "FAILED"

    def __init__(self, transaction_id: str, amount: float, sender_id: str, receiver_id: str):
        if not transaction_id.startswith("TXN-"):
            raise ValueError("transaction_id must start with TXN-")
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        self.__transaction_id = transaction_id
        self.__amount = amount
        self.__sender_id = sender_id
        self.__receiver_id = receiver_id
        self.__status = self.STATUS_PENDING
        self.__created_at = datetime.now()

    @property
    def transaction_id(self): return self.__transaction_id

    @property
    def amount(self): return self.__amount

    @property
    def status(self): return self.__status

    def mark_success(self):
        self.__status = self.STATUS_SUCCESS
        print(f"[Transaction] {self.__transaction_id} succeeded ({self.__amount:.2f} THB)")

    def mark_failed(self):
        self.__status = self.STATUS_FAILED
        print(f"[Transaction] {self.__transaction_id} failed")

    def __repr__(self):
        return f"<Transaction id={self.__transaction_id} amount={self.__amount} status={self.__status}>"


class SoonSakBank:
    def __init__(self, bank_id: str):
        self.__bank_id = bank_id
        self.__balance: float = 0.0
        self.__transaction_list: list = []

    @property
    def balance(self): return self.__balance

    def deposit(self, amount: float, transaction: Transaction):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        self.__balance += amount
        transaction.mark_success()
        self.__transaction_list.append(transaction)
        print(f"[SoonSakBank] Received {amount:.2f} THB | Balance: {self.__balance:.2f}")

    def withdraw(self, amount: float, transaction: Transaction):
        if amount > self.__balance:
            transaction.mark_failed()
            raise ValueError("Insufficient balance")
        self.__balance -= amount
        transaction.mark_success()
        self.__transaction_list.append(transaction)
        print(f"[SoonSakBank] Transferred {amount:.2f} THB | Balance: {self.__balance:.2f}")

    def check_balance(self) -> float:
        print(f"[SoonSakBank] Balance: {self.__balance:.2f} THB")
        return self.__balance

    def get_history(self) -> list:
        return list(self.__transaction_list)

    def __repr__(self):
        return f"<SoonSakBank id={self.__bank_id} balance={self.__balance:.2f}>"


class Payment:
    def __init__(self, payment_id: str, order, bank: SoonSakBank):
        self.__payment_id = payment_id
        self.__order = order
        self.__bank = bank
        self.__payment_method: PaymentMethod = None
        self.__transactions: list = []
        self.__deposit_policy: DepositPolicy = None

    def set_payment_method(self, method: PaymentMethod):
        self.__payment_method = method
        print(f"[Payment] Selected payment method: {method}")

    def set_deposit_policy(self, policy: DepositPolicy):
        self.__deposit_policy = policy

    def validate(self) -> bool:
        if self.__payment_method is None:
            raise ValueError("Payment method not selected")
        if self.__order.calculate_total() <= 0:
            raise ValueError("Total amount must be greater than 0")
        print(f"[Payment] Validation passed")
        return True

    def pay_deposit(self, user_id: str, txn_counter: int) -> Transaction:
        self.validate()
        total = self.__order.calculate_total()
        if self.__deposit_policy:
            deposit_amount = self.__deposit_policy.calculate_deposit(total)
        else:
            deposit_amount = total * 0.3
        success = self.__payment_method.pay(deposit_amount)
        if not success:
            raise Exception("Payment failed")
        txn = self.__create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=deposit_amount,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )
        self.__bank.deposit(deposit_amount, txn)
        self.__order.pay_deposit(deposit_amount)
        return txn

    def pay_full(self, user_id: str, txn_counter: int) -> Transaction:
        self.validate()
        total = self.__order.calculate_total()
        remaining = total - self.__order.deposit_amount
        if remaining <= 0:
            print("[Payment] Already fully paid")
            return None
        success = self.__payment_method.pay(remaining)
        if not success:
            raise Exception("Payment failed")
        txn = self.__create_transaction(
            txn_id=f"TXN-{txn_counter:03d}",
            amount=remaining,
            sender_id=user_id,
            receiver_id="SOONSAK_BANK"
        )
        self.__bank.deposit(remaining, txn)
        self.__order.pay_full()
        return txn

    def __create_transaction(self, txn_id: str, amount: float,
                             sender_id: str, receiver_id: str) -> Transaction:
        txn = Transaction(
            transaction_id=txn_id,
            amount=amount,
            sender_id=sender_id,
            receiver_id=receiver_id
        )
        self.__transactions.append(txn)
        print(f"[Payment] Created Transaction {txn_id}")
        return txn

    def create_transaction(self, txn_id: str, amount: float,
                           sender_id: str, receiver_id: str) -> Transaction:
        return self.__create_transaction(txn_id, amount, sender_id, receiver_id)

    def __repr__(self):
        return f"<Payment id={self.__payment_id} order={self.__order.order_id}>"
