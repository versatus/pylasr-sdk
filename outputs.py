from enum import Enum
from typing import List, Dict, Tuple, Optional


class Address:
    def __init__(self, address_bytes):
        if len(address_bytes) != 20:
            raise ValueError("Address must be 20 bytes long")
        self.address_bytes = address_bytes

    def to_dict(self):
        return {"Address": f"0x{self.address_bytes.hex()}"}

    @staticmethod
    def from_hex(hex_str):
        if hex_str.startswith('0x'):
            hex_str = hex_str[2:]
        return Address(bytes.fromhex(hex_str))


class U256:
    def __init__(self, value):
        self.value = value

    def to_hex(self):
        return format(self.value, '064x')

    def to_dict(self):
        return {'U256': f"0x{self.to_hex()}"}

    @staticmethod
    def from_list(value_list: List[int]):
        if len(value_list) != 4 or not all(
            isinstance(x, int) for x in value_list
        ):
            raise ValueError(
                "U256 must be initialized with a list of 4 integers"
            )
        return U256(sum(x << (i * 64) for i, x in enumerate(value_list)))

    @staticmethod
    def from_hex(hex_str):
        if hex_str.startswith("0x"):
            hex_str = hex_str[2:]
        value = int(hex_str, 16)
        return U256(value)


class Namespace:
    def __init__(self, namespace: str):
        self.namespace = namespace

    def to_dict(self):
        return {"Namespace": self.namespace}


class AddressOrNamespace:
    THIS = "This"
    ADDRESS = Address
    NAMESPACE = Namespace

    def to_dict(self):
        if self.value == "This":
            return "This"
        else:
            return self.value.to_dict()


class Credit:
    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        return {"Credit": self.value.to_hex()}


class Debit:
    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        return {"Debit": self.value.to_hex()}


class BalanceValue(Enum):
    CREDIT = Credit
    DEBIT = Debit

    def to_dict(self):
        return {"Balance": self.value.to_dict()}


class TokenMetadataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"Insert": [self.key, self.value]}


class TokenMetadataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"Extend": self.map}


class TokenMetadataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key}


class TokenMetadataValue(Enum):
    INSERT = TokenMetadataInsert
    EXTEND = TokenMetadataExtend
    REMOVE = TokenMetadataRemove

    def to_dict(self):
        return {"Metadata": self.value.to_dict()}


class TokenIdPush:
    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        return {"Push": self.value.to_dict()}


class TokenIdExtend:
    def __init__(self, items: List[U256]):
        self.items = items

    def to_dict(self):
        return {"Extend": [item.to_dict() for item in self.items]}


class TokenIdInsert:
    def __init__(self, key: int, value: U256):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"Insert": [self.key, self.value.to_dict()]}


class TokenIdPop:
    def __init__(self):
        pass

    def to_dict(self):
        return {"Pop"}


class TokenIdRemove:
    def __init__(self, key: U256):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key.to_dict()}


class TokenIdValue(Enum):
    PUSH = TokenIdPush
    EXTEND = TokenIdExtend
    INSERT = TokenIdInsert
    POP = TokenIdPop
    REMOVE = TokenIdRemove

    def to_dict(self):
        return {"TokenIds": self.value.to_dict()}


class AllowanceInsert:
    def __init__(self, key: Address, value: U256):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"Insert": [self.key.to_dict(), self.value.to_dict()]}


class AllowanceExtend:
    def __init__(self, items: List[Tuple[Address, U256]]):
        self.items = items

    def to_dict(self):
        return {
            "Extend": [
                [item[0].to_dict(),
                 item[1].to_dict()
                 ] for item in self.items
            ]
        }


class AllowanceRemove:
    def __init__(self, key: Address, items: List[U256]):
        self.key = key
        self.items = items

    def to_dict(self):
        return {
            "Remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class AllowanceRevoke:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"Revoke": self.key.to_dict()}


class AllowanceValue(Enum):
    INSERT = AllowanceInsert
    EXTEND = AllowanceExtend
    REMOVE = AllowanceRemove
    REVOKE = AllowanceRevoke

    def to_dict(self):
        return {"Allowance": self.value.to_dict()}


class ApprovalsInsert:
    def __init__(self, key: Address, value: List[U256]):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"Insert": [
            self.key.to_dict(), [inner.to_dict() for inner in self.value]
        ]}


class ApprovalsExtend:
    def __init__(self, items: List[Tuple[Address, U256]]):
        self.items = items

    def to_dict(self):
        return {
            "Extend": [
                [item[0].to_dict(),
                 item[1].to_dict()
                 ] for item in self.items
            ]
        }


class ApprovalsRemove:
    def __init__(self, key: Address, items: List[U256]):
        self.key = key
        self.items = items

    def to_dict(self):
        return {
            "Remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class ApprovalsRevoke:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"Revoke": self.key.to_dict()}


class ApprovalsValue(Enum):
    INSERT = ApprovalsInsert
    EXTEND = ApprovalsExtend
    REMOVE = ApprovalsRemove
    REVOKE = ApprovalsRevoke

    def to_dict(self):
        return {"Approvals": self.value.to_dict()}


class TokenDataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        {"Insert": [self.key, self.value]}


class TokenDataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"Extend": self.map}


class TokenDataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key}


class TokenDataValue(Enum):
    INSERT = TokenDataInsert
    EXTEND = TokenDataExtend
    REMOVE = TokenDataRemove

    def to_dict(self):
        return {"Data": self.value.to_dict()}


class StatusValue(Enum):
    REVERSE = "Reverse"
    LOCK = "Lock"
    UNLOCK = "Unlock"

    def to_dict(self):
        return {"Status": {"StatusValue": self.value}}


class TokenFieldValue(Enum):
    BALANCE = BalanceValue
    METADATA = TokenMetadataValue
    TOKEN_IDS = TokenIdValue
    ALLOWANCE = AllowanceValue
    APPROVALS = ApprovalsValue
    DATA = TokenDataValue
    STATUS = StatusValue

    def to_dict(self):
        return self.value.to_dict()


class TokenField(Enum):
    PROGRAM_ID = "ProgramId"
    OWNER_ID = "OwnerId"
    BALANCE = "Balance"
    METADATA = "Metadata"
    TOKEN_IDS = "TokenIds"
    ALLOWANCE = "Allowance"
    APPROVALS = "Approvals"
    DATA = "Data"
    STATUS = "Status"

    def to_dict(self):
        return self.value


class TokenUpdateField:
    def __init__(self, field: TokenField, value: TokenFieldValue):
        self.field = field
        self.value = value

    def to_dict(self):
        return {
            "field": self.field.to_dict(),
            "value": self.value.to_dict(),
        }


class TokenUpdate:
    def __init__(self, account, token, updates):
        self.account = account
        self.token = token
        self.updates = updates

    def to_dict(self):
        return {
            "account": self.account,
            "token": self.token,
            "updates": [update.to_dict() for update in self.updates]
        }


class LinkedProgramsInsert:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"Insert": self.key.to_dict()}


class LinkedProgramsExtend:
    def __init__(self, items: List[Address]):
        self.items = items

    def to_dict(self):
        return {"Extend": [item.to_dict() for item in self.items]}


class LinkedProgramsRemove:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key.to_dict()}


class LinkedProgramsValue:
    INSERT = LinkedProgramsInsert
    EXTEND = LinkedProgramsExtend
    REMOVE = LinkedProgramsRemove

    def to_dict(self):
        return {"LinkedPrograms": {"LinkedProgramValue": self.value.to_dict()}}


class ProgramMetadataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"Insert": [self.key, self.value]}


class ProgramMetadataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"Extend": self.map}


class ProgramMetadataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key}


class ProgramMetadataValue:
    INSERT = ProgramMetadataInsert
    EXTEND = ProgramMetadataExtend
    REMOVE = ProgramMetadataRemove

    def to_json(self):
        return {"Metadata": self.value.to_dict()}


class ProgramDataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        {"Insert": [self.key, self.value]}


class ProgramDataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"Extend": self.map}


class ProgramDataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"Remove": self.key}


class ProgramDataValue:
    INSERT = ProgramDataInsert
    EXTEND = ProgramDataExtend
    REMOVE = ProgramDataRemove

    def to_dict(self):
        return {"Data": self.value.to_dict()}


class ProgramFieldValue(Enum):
    LINKED_PROGRAMS = LinkedProgramsValue
    METADATA = ProgramMetadataValue
    DATA = ProgramDataValue

    def to_dict(self):
        return self.value.to_dict()


class ProgramField(Enum):
    LINKED_PROGRAMS = "LinkedPrograms"
    METADATA = "Metadata"
    DATA = "Data"

    def to_dict(self):
        pass


class ProgramUpdateField:
    def __init__(self, field: ProgramField, value: ProgramFieldValue):
        self.field = field
        self.value = value

    def to_dict(self):
        return {
            "field": self.field.to_dict(),
            "value": self.value.to_dict()
        }


class ProgramUpdate:
    def __init__(self, account, updates):
        self.account = account
        self.updates = updates

    def to_dict(self):
        return {
            "account": self.account,
            "updates": [update.to_dict() for update in self.updates]
        }


class TokenOrProgramUpdate(Enum):
    TOKEN_UPDATE_FIELD = TokenUpdateField
    PROGRAM_UPDATE_FIELD = ProgramUpdateField

    def to_dict(self):
        return self.value.to_dict()


class TokenDistribution:
    def __init__(
        self,
        program_id: AddressOrNamespace,
        to: AddressOrNamespace,
        amount: Optional[U256],
        token_ids: List[U256],
        update_fields: List[TokenUpdateField]
    ):
        self.program_id = program_id
        self.to = to
        self.amount = amount
        self.token_ids = token_ids
        self.update_fields = update_fields

    def to_dict(self):
        return {
            "program_id": self.program_id.to_dict(),
            "to": self.to.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "token_ids": [item.to_dict() for item in self.token_ids],
            "update_fields": [item.to_dict() for item in self.update_fields]
        }


class CreateInstruction:
    def __init__(
        self,
        program_namespace: AddressOrNamespace,
        program_id: AddressOrNamespace,
        program_owner: Address,
        total_supply: U256,
        distribution: List[TokenDistribution]
    ):
        self.program_namespace = program_namespace
        self.program_id = program_id
        self.program_owner = program_owner
        self.total_supply = total_supply
        self.distribution = distribution

    def to_dict(self):
        return {
            "program_namespace": self.program_namespace.to_dict(),
            "program_id": self.program_id.to_dict(),
            "program_owner": self.program_owner.to_dict(),
            "total_supply": self.total_supply.to_dict(),
            "distribution": [
                dist.to_dict() for dist in self.distribution
            ]
        }


class UpdateInstruction:
    def __init__(self, updates: List[TokenOrProgramUpdate]):
        self.updates = updates

    def to_dict(self):
        return {
            "updates": [update.to_dict() for update in self.updates]
        }


class TransferInstruction:
    def __init__(
        self,
        token: Address,
        transfer_from: AddressOrNamespace,
        transfer_to: AddressOrNamespace,
        amount: Optional[U256],
        ids: List[U256]
    ):
        self.token = token
        self.transfer_from = transfer_from
        self.transfer_to = transfer_to
        self.amount = amount
        self.ids = ids

    def to_dict(self):
        return {
            "token": self.token.to_dict(),
            "from": self.transfer_from.to_dict(),
            "to": self.transfer_to.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "ids": [item.to_dict() for item in self.ids]
        }


class BurnInstruction:
    def __init__(
        self,
        caller: Address,
        program_id: AddressOrNamespace,
        token: Address,
        burn_from: AddressOrNamespace,
        amount: Optional[U256],
        token_ids: List[U256],
    ):
        self.caller = caller
        self.program_id = program_id
        self.token = token
        self.burn_from = burn_from
        self.amount = amount
        self.token_ids = token_ids

    def to_dict(self):
        return {
            "caller": self.caller.to_dict(),
            "program_id": self.program_id.to_dict(),
            "token": self.token.to_dict(),
            "from": self.burn_from.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "ids": [item.to_dict() for item in self.token_ids]
        }


class LogInstruction:

    def to_dict(self):
        return {}


class Instruction(Enum):
    CREATE = CreateInstruction
    UPDATE = UpdateInstruction
    TRANSFER = TransferInstruction
    BURN = BurnInstruction
    LOG = LogInstruction

    def to_dict(self):
        return self.value.to_dict()


class Outputs:
    def __init__(self, inputs, instructions: Instruction):
        self.inputs = inputs
        self.instructions = instructions

    def to_dict(self):
        return {
            "inputs": self.inputs,
            "instructions": [
                instruction.to_dict() for instruction in self.instructions
            ]
        }


class TokenUpdateBuilder:
    def __init__(self, account, token):
        self.account = account
        self.token = token
        self.updates = []

    def add_update_field(self, update_field):
        self.updates.append(update_field)
        return self

    def build(self):
        return TokenUpdate(
            AddressOrNamespace("Address", self.account).to_dict(),
            AddressOrNamespace("Address", self.token).to_dict(),
            self.updates
        )


class TokenDistributionBuilder:
    pass


class CreateInstructionBuilder:
    pass


class UpdateInstructionBuilder:
    def __init__(self):
        self.updates = []

    def add_update(self, update):
        self.updates.append(update)
        return self

    def build(self):
        return UpdateInstruction(self.updates)


class TransferInstructionBuilder:
    pass


class BurnInstructionBuilder:
    pass


class LogInstructionBuilder:
    pass


class OutputBuilder:
    def __init__(self):
        self.inputs = None
        self.instructions = []

    def set_inputs(self, inputs):
        self.inputs = inputs
        return self

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        return self

    def build(self):
        return Outputs(self.inputs, self.instructions)
