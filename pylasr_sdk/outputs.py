from typing import List, Dict, Tuple, Optional, Union
from enum import Enum


class Address:
    """
    Represents a 20 byte derived address that matches the Ethereum network
    standard:
        params: address_bytes - A 20 byte array

    It is suggested that the developer use the `from_hex` method and use hex
    strings to represent addresses, as they are more human readable for
    debugging purposes
    """

    def __init__(self, address_bytes: List[int]):
        if len(address_bytes) != 20:
            raise ValueError("Address must be 20 bytes long")
        self.address_bytes = bytes(address_bytes)

    def to_dict(self):
        """Converts an address to hexadecimal string to be included in a JSON
        blob"""
        return f"0x{self.address_bytes.hex()}"

    @staticmethod
    def from_hex(hex_str):
        """Takes a hexadecimal string and attempts to convert it into an
        Address"""
        if hex_str.startswith('0x'):
            hex_str = hex_str[2:]
        return Address(bytes.fromhex(hex_str))


class U256:
    """
    A 256 bit number which can be represented as either a 32 byte array
    or a hexadecimal string

        params: value - A 20 byte array

    It is suggested that developers use the `from_hex` method and use
    hex strings to represent U256 and other big numbers.
    """

    def __init__(self, value: List[int]):
        self.value = value

    def to_hex(self):
        """Converts a U256 into a proper hex format"""
        return format(self.value, '064x')

    def to_dict(self):
        """Converts a U256 into a hex format that can be included in a JSON
        blob in the format expect"""
        return f"0x{self.to_hex()}"

    @staticmethod
    def from_list(value_list: List[int]):
        """Converts a list of integers (four 64 bit integers) into a U256"""
        if len(value_list) != 4 or not all(
            isinstance(x, int) for x in value_list
        ):
            raise ValueError(
                "U256 must be initialized with a list of 4 integers"
            )
        return U256(sum(x << (i * 64) for i, x in enumerate(value_list)))

    @staticmethod
    def from_hex(hex_str):
        """Attempts to convert a hexadecimal string into a U256"""
        if hex_str.startswith("0x"):
            hex_str = hex_str[2:]
        value = int(hex_str, 16)
        return U256(value)

    def __truediv__(self, other):
        """Enables deivision on a U256"""
        if not isinstance(other, U256):
            raise TypeError("Division only supported between other U256 types")
        if other.value == 0:
            raise ZeroDivisionError("Division by zero is not possible")

        return U256(self.value // other.value)

    # Enables deivision on a U256
    def __floordiv__(self, other):
        return self.__truediv__(other)


class Namespace:
    """
    Represents and account namespace, namespaces are a future feature
    of LASR, but are not currently enabled. We highly suggest not using
    namespaces currently as transactions that use them will fail
    """

    def __init__(self, namespace: str):
        self.namespace = namespace

    def to_dict(self):
        return self.namespace


class AddressOrNamespace:
    """
    Represents an enumerable type that can have 3 different `kinds`: `Address`,
    `Namespace`, or `This`. This is used to tell the protocol which type
    of account identifier to use. Currently Namespaces are not enabled, so
    developers should *ONLY* use Address or `This`, `This` always defaults
    to the address of the contract being called, which is pulled from the
    `Transaction`'s `to` field
    """

    def __init__(self, kind: str, value: Union[str, Address, Namespace]):
        self.kind = kind
        self.value = value

    def to_dict(self):
        """Based on the `kind` field, it returns a value that can be
        deserialized in the protocol for the corresponding AddressOrNamespace
        type"""

        if self.kind == "This":
            return "this"
        elif self.kind == "Address":
            return {"address": self.value.to_dict()}
        else:
            return {"namespace": self.value.to_dict()}


class Credit:
    """
    Represents a Credit variant of the BalanceValue enum, which is effectively
    a wrapper around a `U256`. This tells the protocol to increase the balance
    of the associated account. Technically, BalanceValue's should never be
    used as part of an `UpdateInstruction`, instead, developers should return
    the `TransferInstruction` or a `CreateInstruction` to alter balance of
    accounts. Currently, the protocol will reject any `TokenUpdate` that
    attempts to alter the Balance of a token, this may change in the future.
    """

    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        """Converts the Credit instance into a JSON serializable map that the
        protocol will be capable of deserializing into this type"""
        return {"credit": self.value.to_hex()}


class Debit:
    """
    Represents a Debit variant of the BalanceValue enum, which is effectively
    a wrapper around a `U256`. This tells the protocol to reduce the balance
    of the associated account. BalanceValue's should never be used as part of
    an `UpdateInstruction`, instead, developers should return the
    `TransferInstruction`, `BurnInstruction, or a `CreateInstruction` to alter
    balance of accounts. Currently the protocol will reject any `TokenUpdate`
    that attempts to alter the Balance of a token, this may change in the
    future.
    """

    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        """Converts the Debit instance into a JSON serializable map that the
        protocol will be capable of deserializing into this type"""
        return {"debit": self.value.to_hex()}


class BalanceValue:
    """
    Represents a BalanceValue enumerable type that has 2 variants: Credit &
    Debit. This is used to tell the protocol to `update` an `Account` `Token`
    balance. Currently, returning `BalanceValue` as part of an `update` will
    be rejected. Developers should only use the `TransferInstruction`,
    `CreateInstruction` or `BurnInstruction` to alter `Account` `Token`
    balances
    """

    def __init__(self, value):
        self.value = value

    def to_dict(self):
        """Converts the BalanceValueInstance into a JSON serializable map that
        the protocol will be capable of deserializing into this type"""
        return {"balance": self.value.to_dict()}


class TokenMetadataInsert:
    """
    Represents a variant in an enumerable type that is used to tell the
    protocol to update a `Token`'s metadata field. This variant is used to
    insert a single key -> value pair.

    The pattern is `key: value`, where both are expected to be strings, but
    can represent any type. Developers should keep track of what metadata
    they are storing in which tokens so that they can use the metadata
    in applications.
    """

    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        """Converts this variant instance into a JSON serializable map that the
        protocol will be capable of deserializing into this variant type"""
        return {"insert": [self.key, self.value]}


class TokenMetadataExtend:
    """
    Represents a variant in an enumerable type that is used to tell the
    protocol to update a `Token`'s metadata field. This variant is used to
    insert multiple key-value pairs, and while it theoretically can be used
    to update a single key -> value pair, developers should opt for the
    `TokenMetadataInsert` class if only updating a single kv pair instead.

    The pattern is { k_1: v_1, ..., k_n: v_n }, whicher all keys and all
    values are expected to be strings, but they can represent any type.
    It is the Developers responsibility to keep track of what metadata values
    represent and document them so that they can be used in applications.
    """

    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        """
        Converts this variant instance into a JSON serializable map that the
        protocol will be capable of deserializing into this variant type
        """
        return {"extend": self.map}


class TokenMetadataRemove:
    """
    Represents a variant in an enumerable type that is used to tell the
    the protocol to update a `Token`'s metadata field. This variant is used
    to remove a single key -> value pair. Currently, "bag of values" or nested
    value removals are not supported. To remove an item in a "bag of values"
    or update a nested value you would want to use the `Insert` or `Extend`
    method to overwrite the existing value.

    This type simply takes a key.
    """

    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        """Converts the key into a JSON serializable map that can be understood
        by the protocol"""
        return {"remove": self.key}


class TokenMetadataValue:
    def __init__(
        self,
        value: Union[
            TokenMetadataInsert,
            TokenMetadataExtend,
            TokenMetadataRemove
        ]
    ):
        self.value = value

    def to_dict(self):
        """
        Converts this enum like class into a JSON serializable map that can be
        deserialized by the protocol into a proper enum variant
        """
        return {"metadata": self.value.to_dict()}


class TokenIdPush:
    """
    This type is used to represent an enum variant in the protocol, it is used
    to `push`, to the end of a vector in the `Token`'s `token_id` field, a new
    token ID. Token IDs are typically used to represent a non-fungible token

    This type is effectively a wrapper around a U256
    """

    def __init__(self, value: U256):
        self.value = value

    def to_dict(self):
        """
        Converts this enum variant into a JSON serializable map that can be
        deserialized by the protocol into the type it represents
        """
        return {"push": self.value.to_dict()}


class TokenIdExtend:
    """
    This type is used to represent an enum variant in the protocol, it is used
    to `Extend` the `Token`'s `token_id` field with more than 1 new token Id.
    Token IDs are typically used to represent a non-fungible token

    This type is effectively a wrapper around an array of U256's
    """

    def __init__(self, items: List[U256]):
        self.items = items

    def to_dict(self):
        """Converts this enum variant into JSON serializable map that can be
        deserialized by the protocol into the type it represents"""
        return {"extend": [item.to_dict() for item in self.items]}


class TokenIdInsert:
    """
    This type is used to represent an enum variant in the protocol, it is used
    to replace an existing token ID. The key is an integer representing the
    index position of an item in the `Token`'s `token_ids` field. Use this
    type with caution as it will replace the token id that is in that position
    currently. Only use this type if that is the intended behavior. This
    type will lead to a failure of a transaction if the index position is
    out of range.
    """

    def __init__(self, key: int, value: U256):
        self.key = key
        self.value = value

    def to_dict(self):
        """Converts this enum variant into a JSON serializable map that can the
        protocol can deserialize into the type it represents"""
        return {"insert": [self.key, self.value.to_dict()]}


class TokenIdPop:
    """
    This type is used to represent an enum variant in the protocol, it is used
    to remove the last item in the `Token`'s `token_ids` field. This will
    burn the token ID, effectively, if there is not a replacement of the same
    ID in another account.
    """

    def __init__(self):
        pass

    def to_dict(self):
        """Returns a string representing this enum variant that can be
        deserialized back into the type in the protocol"""
        return "pop"


class TokenIdRemove:
    """
    This type is used to remove a specific token_id from the `Token`'s
    `token_ids` field, the `key` in this type is the index of the token_id
    attempting to be removed, transaction will fail if the `key` is out of
    range. Use with caution and this could potentially be used to remove the
    wrong token_id, if the token_ids have changed since being read.
    """

    def __init__(self, key: U256):
        self.key = key

    def to_dict(self):
        """Returns a JSON serializable map representing this type"""
        return {"remove": self.key.to_dict()}


class TokenIdValue:
    """
    This type represents an enum that is used to update a `Token`'s `token_ids`
    field. There are 5 methods that can be applied using this enum:

        Push (TokenIdPush)
        Pop (TokenIdPop)
        Insert (TokenIdInsert)
        Extend (TokenIdExtend)
        Remove (TokenIdRemove)

    *WARNING* It is highly recommended that in the vast majority of cases,
    Push, Pop, and Extend be used, as these types act on the final item in the
    array.

    Insert and Remove variants attempt to act on a specific index position
    in the `token_ids` array, which can be dangerous if not used with extreme
    caution *WARNING*
    """

    def __init__(
        self,
        value: Union[
            TokenIdPush,
            TokenIdPop,
            TokenIdInsert,
            TokenIdExtend,
            TokenIdRemove
        ]
    ):
        self.value = value

    def to_dict(self):
        return {"tokenIds": self.value.to_dict()}


class AllowanceInsert:
    """
    This type represents a variant to an enum that is used to insert a new
    account (program or user) and an amount that the account can spend from
    the `Account`/`Token` pair
    """

    def __init__(self, key: Address, value: U256):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"insert": [self.key.to_dict(), self.value.to_dict()]}


class AllowanceExtend:
    def __init__(self, items: List[Tuple[Address, U256]]):
        self.items = items

    def to_dict(self):
        return {
            "extend": [
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
            "remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class AllowanceRevoke:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"revoke": self.key.to_dict()}


class AllowanceValue:
    def __init__(
        self,
        value: Union[
            AllowanceInsert,
            AllowanceExtend,
            AllowanceRemove,
            AllowanceRevoke
        ]
    ):
        self.value = value

    def to_dict(self):
        return {"allowance": self.value.to_dict()}


class ApprovalsInsert:
    def __init__(self, key: Address, value: List[U256]):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"insert": [
            self.key.to_dict(), [inner.to_dict() for inner in self.value]
        ]}


class ApprovalsExtend:
    def __init__(self, items: List[Tuple[Address, U256]]):
        self.items = items

    def to_dict(self):
        return {
            "extend": [
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
            "remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class ApprovalsRevoke:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"revoke": self.key.to_dict()}


class ApprovalsValue:
    def __init__(
        self,
        value: Union[
            ApprovalsInsert,
            ApprovalsExtend,
            ApprovalsRemove,
            ApprovalsRevoke,
        ]
    ):
        self.value = value

    def to_dict(self):
        return {"approvals": self.value.to_dict()}


class TokenDataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"insert": [self.key, self.value]}


class TokenDataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"extend": self.map}


class TokenDataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"remove": self.key}


class TokenDataValue:
    def __init__(
        self,
        value: Union[
            TokenDataInsert,
            TokenDataExtend,
            TokenDataRemove
        ]
    ):
        self.value = value

    def to_dict(self):
        return {"data": self.value.to_dict()}


class StatusValue(Enum):
    FREE = "free"
    LOCKED = "locked"

    def to_dict(self):
        return {"statusValue": self.value}


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
        return {"insert": self.key.to_dict()}


class LinkedProgramsExtend:
    def __init__(self, items: List[Address]):
        self.items = items

    def to_dict(self):
        return {"extend": [item.to_dict() for item in self.items]}


class LinkedProgramsRemove:
    def __init__(self, key: Address):
        self.key = key

    def to_dict(self):
        return {"remove": self.key.to_dict()}


class LinkedProgramsValue:
    def __init__(
        self,
        kind: str,
        value: Union[
            LinkedProgramsInsert,
            LinkedProgramsExtend,
            LinkedProgramsRemove
        ]
    ):
        if not isinstance(kind, str):
            raise ValueError("expected `kind` to be of type `str`")

        valid_kinds = [
            "linkedprogramsremove",
            "linkedprogramsextend",
            "linkedprogramsinsert"
        ]

        if self.kind.lower() not in valid_kinds:
            raise ValueError(f"expected `kind` to be one of {valid_kinds}")

        if self.value not isinstance(value, (LinkedProgramsInsert, LinkedProgramsExtend, LinkedProgramsRemove)):

    def to_dict(self):
        return {"linkedProgramValue": self.value.to_dict()}


class ProgramMetadataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"insert": [self.key, self.value]}


class ProgramMetadataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"extend": self.map}


class ProgramMetadataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"remove": self.key}


class ProgramMetadataValue:
    INSERT = ProgramMetadataInsert
    EXTEND = ProgramMetadataExtend
    REMOVE = ProgramMetadataRemove

    def to_json(self):
        return {"metadata": self.value.to_dict()}


class ProgramDataInsert:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value

    def to_dict(self):
        return {"insert": [self.key, self.value]}


class ProgramDataExtend:
    def __init__(self, map: Dict[str, str]):
        self.map = map

    def to_dict(self):
        return {"extend": self.map}


class ProgramDataRemove:
    def __init__(self, key: str):
        self.key = key

    def to_dict(self):
        return {"remove": self.key}


class ProgramDataValue:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"data": self.value.to_dict()}


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
            "programId": self.program_id.to_dict(),
            "to": self.to.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "tokenIds": [item.to_dict() for item in self.token_ids],
            "updateFields": [item.to_dict() for item in self.update_fields]
        }


class CreateInstruction:
    def __init__(
        self,
        program_namespace: AddressOrNamespace,
        program_id: AddressOrNamespace,
        program_owner: Address,
        total_supply: U256,
        initialized_supply: U256,
        distribution: List[TokenDistribution]
    ):
        self.program_namespace = program_namespace
        self.program_id = program_id
        self.program_owner = program_owner
        self.total_supply = total_supply
        self.initialized_supply = initialized_supply
        self.distribution = distribution

    def to_dict(self):
        return {
            "programNamespace": self.program_namespace.to_dict(),
            "programId": self.program_id.to_dict(),
            "programOwner": self.program_owner.to_dict(),
            "totalSupply": self.total_supply.to_dict(),
            "initializedSupply": self.initialized_supply.to_dict(),
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
            "programId": self.program_id.to_dict(),
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
        return CreateInstruction(
            self.program_namespace,
            self.program_id,
            self.program_owner,
            self.total_supply,
            self.initialized_supply,
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
