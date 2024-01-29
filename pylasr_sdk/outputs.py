from typing import List, Dict, Tuple, Optional


class Address:
    def __init__(self, address_bytes):
        if len(address_bytes) != 20:
            raise ValueError("Address must be 20 bytes long")
        self.address_bytes = bytes(address_bytes)

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


class BalanceValue:
    def __init__(self, value):
        self.value = value

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


class TokenMetadataValue:
    def __init__(self, value):
        self.value = value

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


class TokenIdValue:
    def __init__(self, value):
        self.value = value

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


class AllowanceValue:
    def __init__(self, value):
        self.value = value

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


class ApprovalsValue:
    def __init__(self, value):
        self.value = value

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


class TokenDataValue:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"Data": self.value.to_dict()}


class StatusValue:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"StatusValue": self.value}


class TokenFieldValue:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def to_dict(self):
        return {self.kind: self.value.to_dict()}


class TokenField:
    def __init__(self, value: str):
        self.value = value

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
    def __init__(
        self,
        account: AddressOrNamespace,
        token: AddressOrNamespace,
        updates: List[TokenUpdateField]
    ):
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
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"Data": self.value.to_dict()}


class ProgramFieldValue:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def to_dict(self):
        return {self.kind: self.value.to_dict()}


class ProgramField:
    def __init__(self, kind: str):
        self.kind = kind

    def to_dict(self):
        return self.kind


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


class TokenOrProgramUpdate:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def to_dict(self):
        return {self.kind: self.value.to_dict()}


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


class Instruction:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def to_dict(self):
        return {
            self.kind: self.value.to_dict()
        }


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
    def __init__(
        self,
        account: Optional[AddressOrNamespace] = None,
        token: Optional[AddressOrNamespace] = None
    ):
        self.account = None
        self.token = None
        self.updates = []

    def add_update_account_address(self, account: AddressOrNamespace):
        self.account = account
        return self

    def add_token_address(self, token_address: AddressOrNamespace):
        self.token = token_address
        return self

    def add_update_field(self, update_field):
        self.updates.append(update_field)
        return self

    def build(self) -> TokenUpdate:
        return TokenUpdate(
            self.account.to_dict(),
            self.token.to_dict(),
            self.updates
        )


class TokenDistributionBuilder:
    def __init__(self):
        self.program_id = None
        self.to = None
        self.amount = None
        self.token_ids = []
        self.update_fields = []

    def set_program_id(self, program_id: AddressOrNamespace):
        self.program_id = program_id
        return self

    def set_receiver(self, receiver: AddressOrNamespace):
        self.to = receiver
        return self

    def set_amount(self, amount: U256):
        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        self.token_ids.append(token_id)
        return self

    def add_update_field(self, update_field: TokenUpdateField):
        self.update_fields.append(update_field)
        return self

    def extend_token_ids(self, items: List[U256]):
        self.token_ids = self.token_ids + items
        return self

    def extend_update_fields(self, items: List[TokenUpdateField]):
        self.update_fields = self.update_fields + items
        return self

    def build(self) -> TokenDistribution:
        return TokenDistribution(
            self.program_id,
            self.to,
            self.amount,
            self.token_ids,
            self.update_fields
        )


class CreateInstructionBuilder:
    def __init__(
        self,
    ):
        self.program_namespace = None
        self.program_id = None
        self.program_owner = None
        self.total_supply = None
        self.initialized_supply = None
        self.distribution = []

    def set_program_namespace(self, program_namespace: AddressOrNamespace):
        self.program_namespace = program_namespace
        return self

    def set_program_id(self, program_id: AddressOrNamespace):
        self.program_id = program_id
        return self

    def set_program_owner(self, program_owner: Address):
        self.program_owner = program_owner
        return self

    def set_total_supply(self, total_supply: U256):
        self.total_supply = total_supply
        return self

    def set_initialized_supply(self, initialized_supply: U256):
        self.initialized_supply = initialized_supply
        return self

    def add_token_distribution(self, token_distribution: TokenDistribution):
        self.distribution.append(token_distribution)
        return self

    def extend_token_distribution(self, items: List[TokenDistribution]):
        self.distribution = self.distribution + items
        return self

    def build(self) -> CreateInstruction:
        CreateInstruction(
            self.program_namespace,
            self.program_id,
            self.program_owner,
            self.total_supply,
            self.distribution
        )


class UpdateInstructionBuilder:
    def __init__(self):
        self.updates = []

    def add_update(self, update: TokenOrProgramUpdate):
        self.updates.append(update)
        return self

    def extend_updates(self, items: List[TokenOrProgramUpdate]):
        self.updates = self.updates + items
        return self

    def build(self) -> UpdateInstruction:
        return UpdateInstruction(self.updates)


class TransferInstructionBuilder:
    def __init__(self):
        self.token = None
        self.transfer_from = None
        self.transfer_to = None
        self.amount = None
        self.ids = []

    def set_token_address(self, token_address: Address):
        self.token = token_address
        return self

    def set_transfer_from(self, transfer_from: AddressOrNamespace):
        self.transfer_from = transfer_from
        return self

    def set_transfer_to(self, transfer_to: AddressOrNamespace):
        self.transfer_to = transfer_to
        return self

    def set_amount(self, amount: U256):
        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        self.ids.append(token_id)
        return self

    def extend_token_ids(self, items: List[U256]):
        self.ids = self.ids + items
        return self

    def build(self) -> TransferInstruction:
        return TransferInstruction(
            self.token,
            self.transfer_from,
            self.transfer_to,
            self.amount,
            self.ids
        )


class BurnInstructionBuilder:
    def __init__(self):
        self.caller = None
        self.program_id = None
        self.token = None
        self.burn_from = None
        self.amount = None
        self.token_ids = []

    def set_caller(self, caller: Address):
        self.caller = caller
        return self

    def set_program_id(self, program_id: AddressOrNamespace):
        self.program_id = program_id
        return self

    def set_token_address(self, token_address: Address):
        self.token_address = token_address
        return self

    def set_burn_from_address(self, burn_from_address: AddressOrNamespace):
        self.burn_from = burn_from_address
        return self

    def set_amount(self, amount: U256):
        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        self.token_ids.append(token_id)
        return self

    def extend_token_ids(self, items: List[U256]):
        self.token_ids = self.token_ids + items
        return self

    def build(self) -> BurnInstruction:
        return BurnInstruction(
            self.caller,
            self.program_id,
            self.token,
            self.burn_from,
            self.amount,
            self.token_ids
        )


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
