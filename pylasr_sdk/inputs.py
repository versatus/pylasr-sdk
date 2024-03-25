import json
from typing import (
    Union,
    Dict,
    Set,
    List
)
from outputs import (
    Address,
    AddressOrNamespace,
    U256,
)


class Status:
    """
    A type that denotes the status of a token, whether it can be 'used',
    i.e. have its state altered.
    """

    def __init__(self, state: str):
        valid_states = ["free", "locked"]

        if state not in valid_states:
            raise ValueError

        self.state = state

    @staticmethod
    def from_json(map: str):
        json_status = json.loads(map)

        state = json_status.values()[0]

        return Status(state)

    def to_dict(self):
        return self.state


class Token:
    """
    a type representing a canonical `Token` in the protocol
    """

    def __init__(
        self,
        program_id: Address,
        owner_id: Address,
        balance: U256,
        metadata: Dict[str, str],
        token_ids: List[U256],
        allowance: Dict[Address, U256],
        approvals: Dict[Address, List[U256]],
        data: Dict[str, str],
        status: Status
    ):

        if not all(
            isinstance(program_id, Address),
            isinstance(owner_id, Address),
            isinstance(balance, U256),
            isinstance(metadata, Dict[str, str]),
            isinstance(token_ids, List[U256]),
            isinstance(allowance, Dict[Address, U256]),
            isinstance(approvals, Dict[Address, List[U256]]),
            isinstance(data, Dict[str, str]),
            isinstance(status, Status),
        ):
            raise ValueError

        self.program_id = program_id
        self.owner_id = owner_id
        self.balance = balance
        self.metadata = metadata
        self.token_ids = token_ids
        self.allowance = allowance
        self.approvals = approvals
        self.data = data
        self.status = status

    @staticmethod
    def from_json(map: str):
        json_token = json.loads(map)
        program_id = Address.from_hex(json_token["programId"])
        owner_id = Address.from_hex(json_token["ownerId"])
        balance = U256.from_hex(json_token["balance"])
        metadata = json.loads(json_token["metadata"])
        token_ids = list(json_token["tokenIds"])
        allowance = json.loads(json_token["allowance"])
        approvals = json.loads(json_token["approvals"])
        data = json.loads(json_token["data"])
        status = Status.from_json(json_token["status"])

        return Token(
            program_id,
            owner_id,
            balance,
            metadata,
            token_ids,
            allowance,
            approvals,
            data,
            status
        )

    def to_dict(self):
        return {
            "programId": self.program_id.to_dict(),
            "ownerId": self.owner_id.to_dict(),
            "balance": self.balance.to_dict(),
            "metadata": self.metadata,
            "tokenIds": self.token_ids,
            "allowance": self.allowance,
            "approvals": self.approvals,
            "data": self.data,
            "status": self.status.to_dict()
        }


class AccountType:
    def __init__(self, kind: str, value: Union[None, Address]):
        valid_kinds = ["user", "program"]

        if kind not in valid_kinds:
            return ValueError

        self.kind = kind
        self.value = value

    def to_dict(self):
        if self.kind == "user":
            return "user"

        if self.kind == "program":
            return {"program": self.value.to_dict()}


class Account:
    """
    A type representing the canonical `Account` type in the LASR protocol
    """

    def __init__(
        self,
        account_type: AccountType,
        program_namespace: AddressOrNamespace,
        owner_address: Address,
        programs: Dict[Address, Token],
        nonce: U256,
        program_account_data: Dict[str, str],
        program_account_metadata: Dict[str, str],
        program_account_linked_programs: Set[AddressOrNamespace]
    ):

        if not all(
            isinstance(account_type, AccountType),
            isinstance(program_namespace, AddressOrNamespace),
            isinstance(owner_address, Address),
            isinstance(programs, Dict[Address, Token]),
            isinstance(nonce, U256),
            isinstance(program_account_data, Dict[str, str]),
            isinstance(program_account_metadata, Dict[str, str]),
            isinstance(
                program_account_linked_programs, Set[AddressOrNamespace]
            ),
        ):
            raise ValueError

        self.account_type = account_type
        self.program_namespace = program_namespace
        self.owner_address = owner_address
        self.programs = programs
        self.nonce = nonce
        self.program_account_data = program_account_data
        self.program_account_metadata = program_account_metadata
        self.program_account_linked_programs = program_account_linked_programs

    @staticmethod
    def from_json(map: str):
        json_account = json.loads(map)

        account_type = AccountType.from_json(json_account["accountType"])

        program_namespace = AddressOrNamespace.from_json(
            json_account["programNamespace"]
        )

        owner_address = Address.from_hex(
            json_account["ownerAddress"]
        )

        programs = json.loads(json_account["programs"])

        nonce = U256.from_hex(json_account["nonce"])

        program_account_data = json.loads(
            json_account["programAccountData"]
        )

        program_account_metadata = json.loads(
            json_account["programAccountMetadata"]
        )

        program_account_linked_programs = json.loads(
            json_account["programAccountLinkedPrograms"]
        )

        return Account(
            account_type,
            program_namespace,
            owner_address,
            programs,
            nonce,
            program_account_data,
            program_account_metadata,
            program_account_linked_programs
        )

    def to_dict(self):
        return {
            "accountType": self.account_type.to_dict(),
            "programNamespace": self.program_namespace.to_dict(),
            "ownerAddress": self.owner_address.to_dict(),
            "programs": self.programs,
            "nonce": self.nonce.to_dict(),
            "programAccountData": self.program_account_data,
            "programAccountMetadata": self.program_account_metadata,
            "programAccountLinkedPrograms": self.program_account_linked_programs
        }


class TransactionType:
    """
    A type representing a deserialized canonical `TransactionType` in the LASR
    protocol
    """

    def __init__(self, kind: str, nonce: U256):
        valid_kinds = [
            "bridgeIn",
            "send",
            "call",
            "bridgeOut",
            "registerProgram"
        ]

        if kind not in valid_kinds:
            raise ValueError

        self.kind = kind
        self.nonce = nonce

    @staticmethod
    def from_json(map: str):
        json_transaction_type = json.loads(map)
        kind = list(json_transaction_type.keys())[0]
        nonce = U256.from_hex(list(json_transaction_type.values())[0])

        return TransactionType(kind, nonce)

    def to_dict(self):
        return {
            self.kind: self.nonce.to_dict()
        }


class Transaction:
    """
    A type representing the canonical `Transaction` type in the LASR protocol
    """

    def __init__(
        self,
        transaction_type: TransactionType,
        caller: Address,
        receiver: Address,
        program_id: Address,
        op: str,
        inputs: str,
        value: U256,
        nonce: U256,
        v: int,
        r: U256,
        s: U256,
    ):

        if not all(
            isinstance(transaction_type, TransactionType),
            isinstance(caller, Address),
            isinstance(receiver, Address),
            isinstance(program_id, Address),
            isinstance(op, str),
            isinstance(inputs, str),
            isinstance(value, U256),
            isinstance(nonce, U256),
            isinstance(v, int),
            isinstance(r, U256),
            isinstance(s, U256)
        ):
            raise ValueError

        self.transaction_type = transaction_type
        self.caller = caller
        self.receiver = receiver
        self.program_id = program_id
        self.op = op
        self.inputs = inputs
        self.value = value
        self.nonce = nonce
        self.v = v
        self.r = r
        self.s = s

    @staticmethod
    def from_json(map: str):
        json_transaction = json.loads(map)

        transaction_type = TransactionType.from_json(
            json_transaction["transactionType"]
        )
        caller = Address(list(json_transaction["from"]))
        receiver = Address(list(json_transaction["to"]))
        program_id = Address(list(json_transaction["programId"]))
        op = json_transaction["op"]
        inputs = json_transaction["trasnactionInputs"]
        value = U256.from_hex(json_transaction["value"])
        nonce = U256.from_hex(json_transaction["nonce"])
        v = int(json_transaction["v"])
        r = U256.from_hex(json_transaction["r"])
        s = U256.from_hex(json_transaction["s"])

        return Transaction(
            transaction_type,
            caller,
            receiver,
            program_id,
            op,
            inputs,
            value,
            nonce,
            v,
            r,
            s
        )

    def to_dict(self):
        return {
            "transactionType": self.transaction_type.to_dict(),
            "from": self.caller.to_dict(),
            "to": self.receiver.to_dict(),
            "programId": self.program_id.to_dict(),
            "op": self.op,
            "transactionInputs": self.inputs,
            "value": self.value.to_dict(),
            "nonce": self.nonce.to_dict(),
            "v": self.v,
            "r": self.r.to_dict(),
            "s": self.s.to_dict()
        }


class Inputs:
    """
    A type representing the canonical computeInputs type in the LASR protocol
    """

    def __init__(
        self,
        version: int,
        account_info: Account,
        transaction: Transaction,
        op: str,
        contract_inputs: str
    ):

        if not all(
            isinstance(version, int),
            isinstance(account_info, Account),
            isinstance(transaction, Transaction),
            isinstance(op, str),
            isinstance(contract_inputs, str),
        ):
            raise ValueError

        self.version = version
        self.account_info = account_info
        self.transaction = transaction
        self.op = op
        self.contract_inputs = contract_inputs

    @staticmethod
    def from_json(map: str):
        json_inputs = json.loads(map)

        version = int(json_inputs["version"])
        account_info = Account.from_json(json_inputs["accountInfo"])
        transaction = Transaction.from_json(json_inputs["transaction"])
        op = json_inputs["op"]
        contract_inputs = json_inputs["contractInputs"]

        return Inputs(version, account_info, transaction, op, contract_inputs)

    def to_dict(self):
        return {
            "version": self.version,
            "accountInfo": self.account_info.to_dict(),
            "transaction": self.transaction.to_dict(),
            "op": self.op,
            "contractInputs": self.contract_inputs
        }
