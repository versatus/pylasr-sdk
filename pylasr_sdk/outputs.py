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
        if not isinstance(kind, str):
            raise ValueError

        if not isinstance(
                value,
                (str, Address, Namespace)
        ):
            raise ValueError

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
        if not isinstance(value, U256):
            raise ValueError

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
        if not isinstance(value, U256):
            raise ValueError

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

    def __init__(self, value: Union[Debit, Credit]):
        if not isinstance(value, (Debit, Credit)):
            raise ValueError

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
        if not isinstance(key, str):
            raise ValueError

        if not isinstance(value, str):
            raise ValueError

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
        if not isinstance(map, Dict[str, str]):
            raise ValueError

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
        if not isinstance(key, str):
            raise ValueError

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
        if not isinstance(
            value,
            (
                TokenMetadataInsert,
                TokenMetadataExtend,
                TokenMetadataRemove
            )
        ):
            raise ValueError

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
        if not isinstance(value, U256):
            raise ValueError

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
        if not isinstance(items, List[U256]):
            raise ValueError

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
        if not isinstance(key, int):
            raise ValueError

        if not isinstance(value, U256):
            raise ValueError

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
        if not isinstance(key, U256):
            raise ValueError

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
        if not isinstance(
            value,
            (
                TokenIdPush,
                TokenIdPop,
                TokenIdInsert,
                TokenIdExtend,
                TokenIdRemove
            )
        ):
            raise ValueError

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"tokenIds": self.value.to_dict()}


class AllowanceInsert:
    """
    This type represents a variant to an enum that is used to insert a new
    account (program or user) and an amount that the account can spend from
    the `Account`/`Token` pair
    """

    def __init__(self, key: Address, value: U256):
        if not isinstance(key, Address):
            raise ValueError

        if not isinstance(value, U256):
            raise ValueError

        self.key = key
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": [self.key.to_dict(), self.value.to_dict()]}


class AllowanceExtend:
    """
    This type represents a variant to an enum that is used to exend multiple
    new accounts (program or user) and an amount that the account can spend
    from the `Account`/`Token` pair
    """

    def __init__(self, items: List[Tuple[Address, U256]]):
        if not isinstance(items, List[Tuple[Address, U256]]):
            raise ValueError

        self.items = items

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "extend": [
                [item[0].to_dict(),
                 item[1].to_dict()
                 ] for item in self.items
            ]
        }


class AllowanceRemove:
    """
    This type represents a variant to an enum that is used to remove accounts
    that are currently allowed to spend from the `Account`/`Token` pair
    """

    def __init__(self, key: Address, items: List[U256]):
        if not isinstance(key, Address):
            raise ValueError

        if not isinstance(items, List[U256]):
            raise ValueError

        self.key = key
        self.items = items

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class AllowanceRevoke:
    """
    This type represents a variant to an enum that is used to revoke allowances
    granted to other accounts
    """

    def __init__(self, key: Address):

        if not isinstance(key, Address):
            raise ValueError

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"revoke": self.key.to_dict()}


class AllowanceValue:
    """
    This type represents an enum that can take a variant to allow the
    `Account`/`Token` pair to have it's allowance field updated.
    """

    def __init__(
        self,
        value: Union[
            AllowanceInsert,
            AllowanceExtend,
            AllowanceRemove,
            AllowanceRevoke
        ]
    ):

        if not isinstance(
            value,
            (
                AllowanceInsert,
                AllowanceExtend,
                AllowanceRemove,
                AllowanceRevoke
            )
        ):
            raise ValueError

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"allowance": self.value.to_dict()}


class ApprovalsInsert:
    """
    Similar to Allowance insert, approvals give a more broad allowance with
    no set value. This type represents a variant to an enum-like type that
    can take multiple different variants. This variant allows for a single
    (user or program) account to have approval to spend a given `Token`
    from a given `Account`
    """

    def __init__(self, key: Address, value: List[U256]):
        if not isinstance(key, Address):
            raise ValueError

        if not isinstance(value, List[U256]):
            raise ValueError

        self.key = key
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": [
            self.key.to_dict(), [inner.to_dict() for inner in self.value]
        ]}


class ApprovalsExtend:
    """
    Similar to `ApprovalsInsert`, extend allows the granting of approval
    to multiple (user or program) accounts at the same time.
    """

    def __init__(self, items: List[Tuple[Address, U256]]):
        if not isinstance(items, List[Tuple[Address, U256]]):
            raise ValueError

        self.items = items

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "extend": [
                [item[0].to_dict(),
                 item[1].to_dict()
                 ] for item in self.items
            ]
        }


class ApprovalsRemove:
    """
    This type represents a variant that allows for the removal of a previously
    approved account from the `Account`/`Token` pair's approvals field. The
    account removed will no longer have approval to spend the given `Token`
    from the given `Account`
    """

    def __init__(self, key: Address, items: List[U256]):
        if not isinstance(key, Address):
            raise ValueError

        if not isinstance(items, List[U256]):
            raise ValueError

        self.key = key
        self.items = items

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "remove": [
                self.key.to_dict(),
                [inner.to_dict() for inner in self.items]
            ]}


class ApprovalsRevoke:
    """
    Revoke is similar to remove, but is specific to a single approved account
    where Remove can remove multiple accounts at the same time.
    """

    def __init__(self, key: Address):
        if not isinstance(key, Address):
            raise ValueError("expected `key` to be type `Address`")

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"revoke": self.key.to_dict()}


class ApprovalsValue:
    """
    An enum-like type that can take 1 of 4 variants to alter a given `Account`
    /`Token` approvals field
    """

    def __init__(
        self,
        value: Union[
            ApprovalsInsert,
            ApprovalsExtend,
            ApprovalsRemove,
            ApprovalsRevoke,
        ]
    ):
        if not isinstance(
                value,
                (
                    ApprovalsInsert,
                    ApprovalsExtend,
                    ApprovalsRemove,
                    ApprovalsRevoke
                )
        ):
            raise ValueError(
                """
                expected `value` to be one of:
                ApprovalsInsert, ApprovalsExtend,
                ApprovalsRemove, ApprovalsRevoke
                """
            )

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"approvals": self.value.to_dict()}


class TokenDataInsert:
    """
    An enum variant like type that allows for a single key-value pair to
    be inserted in a given `Account`/`Token` `data` field.
    """

    def __init__(self, key: str, value: str):
        if not isinstance(key, str):
            raise ValueError

        if not isinstance(value, str):
            raise ValueError

        self.key = key
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": [self.key, self.value]}


class TokenDataExtend:
    """
    Similar to Insert, but allows for multiple key-value pairs, structured
    as a map, inserted into a given `Account`/`Token` `data` field
    """

    def __init__(self, map: Dict[str, str]):
        if not isinstance(map, Dict[str, str]):
            raise ValueError

        self.map = map

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"extend": self.map}


class TokenDataRemove:
    """
    Allows for the removal of a key-value pair from an `Account`/`Token` data
    field
    """

    def __init__(self, key: str):
        if not isinstance(key, str):
            raise ValueError

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"remove": self.key}


class TokenDataValue:
    """
    An enum-like type that allows the updating of a given `Account`/`Token`
    pair `data` field
    """

    def __init__(
        self,
        value: Union[
            TokenDataInsert,
            TokenDataExtend,
            TokenDataRemove
        ]
    ):
        if not isinstance(
            value,
            (
                TokenDataInsert,
                TokenDataExtend,
                TokenDataRemove
            )
        ):
            raise ValueError

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"data": self.value.to_dict()}


class StatusValue(Enum):
    """
    An enum variant used to update the value of an `Account`/`Token`
    `status` field.
    """

    def __init__(self, value: str):
        valid_kinds = [
            "free",
            "locked"
        ]

        if value not in valid_kinds:
            raise ValueError(f"expected `value` to be one of {valid_kinds}")

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"statusValue": self.value}


class TokenFieldValue:
    """
    A type that is used to update a given field in an `Account`/`Token`
    """

    def __init__(
        self,
        kind: str,
        value: Union[
            StatusValue,
            TokenDataValue,
            TokenMetadataValue,
            ApprovalsValue,
            AllowanceValue,
            TokenIdValue,
            BalanceValue
        ]
    ):

        if not isinstance(kind, str):
            raise ValueError

        if not isinstance(
            value,
            (
                StatusValue,
                TokenDataValue,
                TokenMetadataValue,
                ApprovalsValue,
                AllowanceValue,
                TokenIdValue,
                BalanceValue
            )
        ):
            raise ValueError

        self.kind = kind
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {self.kind: self.value.to_dict()}


class TokenField:
    """
    A Type representing a field in a `Token`
    """

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return self.value


class TokenUpdateField:
    """
    A type representing a field in an `Account`/`Token` pair that will
    be updated
    """

    def __init__(self, field: TokenField, value: TokenFieldValue):

        if not isinstance(field, TokenField):
            raise ValueError("expected `field` to be type `TokenField`")

        if not isinstance(value, TokenFieldValue):
            raise ValueError("expected `value` to be type `TokenFieldValue")

        self.field = field
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "field": self.field.to_dict(),
            "value": self.value.to_dict(),
        }


class TokenUpdate:
    """
    A type representing a group of updates to apply to an `Account`/`Token`
    pair
    """

    def __init__(
        self,
        account: AddressOrNamespace,
        token: AddressOrNamespace,
        updates: List[TokenUpdateField]
    ):
        if not isinstance(account, AddressOrNamespace):
            raise ValueError("expected type `AddressOrNamespace`")

        if not isinstance(token, AddressOrNamespace):
            raise ValueError("expected type `AddressOrNamespace`")

        if not isinstance(updates, List[TokenUpdateField]):
            raise ValueError("expected type `AddressOrNamespace`")

        self.account = account
        self.token = token
        self.updates = updates

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "account": self.account,
            "token": self.token,
            "updates": [update.to_dict() for update in self.updates]
        }


class LinkedProgramsInsert:
    """
    An enum variant-like type that is used to insert a new LinkedProgram
    into a Program Account.
    """

    def __init__(self, key: Address):
        if not isinstance(key, Address):
            raise ValueError("expected type `Address`")

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": self.key.to_dict()}


class LinkedProgramsExtend:
    """
    An enum variant-like type that is used to insert multiple new
    LinkedPrograms into a Program Account
    """

    def __init__(self, items: List[Address]):

        if not isinstance(items, List[Address]):
            raise ValueError("expected type `List[Address]`")

        self.items = items

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"extend": [item.to_dict() for item in self.items]}


class LinkedProgramsRemove:
    """
    An enum variant-like type that is used to remove a LinkedProgram from
    a Program Account
    """

    def __init__(self, key: Address):
        if not isinstance(key, Address):
            raise ValueError("expected type `Address`")

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"remove": self.key.to_dict()}


class LinkedProgramsValue:
    """
    An enum-like type that is used to update the LinkedPrograms field
    of a Program Account
    """

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

        if kind.lower() not in valid_kinds:
            raise ValueError(f"expected `kind` to be one of {valid_kinds}")

        if not isinstance(
                value,
                (
                    LinkedProgramsInsert,
                    LinkedProgramsExtend,
                    LinkedProgramsRemove
                )
        ):
            raise ValueError(
                """expected `value` to be one of
                LinkedProgramsInsert, LinkedProgramsExtend or
                LinkedProgramsRemove"""
            )

        self.kind = kind
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"linkedProgramValue": self.value.to_dict()}


class ProgramMetadataInsert:
    """
    An enum variant-like type that is used to insert a single key-value
    pair into a Program Account metadata field
    """

    def __init__(self, key: str, value: str):
        if not isinstance(key, str):
            raise ValueError

        if not isinstance(value, str):
            raise ValueError

        self.key = key
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": [self.key, self.value]}


class ProgramMetadataExtend:
    """
    An enum variant-like type that is used to insert multiple key-value
    pairs into a Program Account metadata field
    """

    def __init__(self, map: Dict[str, str]):
        if not isinstance(map, Dict[str, str]):
            raise ValueError

        self.map = map

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"extend": self.map}


class ProgramMetadataRemove:
    """
    An enum variant-like type that is used to remove a single key-value
    pair from a Program Account
    """

    def __init__(self, key: str):
        if not isinstance(key, str):
            raise ValueError

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"remove": self.key}


class ProgramMetadataValue:
    """
    An enum-like type that is used to update the program_metadata field
    in a Program Account
    """

    def __init__(
        self,
        kind: str,
        value: Union[
            ProgramMetadataInsert,
            ProgramMetadataExtend,
            ProgramMetadataRemove
        ]
    ):
        if not isinstance(kind, str):
            raise ValueError("expected `kind` to be `str`")

        valid_kinds = [
            "programmetadatainsert",
            "programmetadataextend",
            "programmetadataremove"
        ]

        if kind.lower() not in valid_kinds:
            raise ValueError(f"expected kind to be one of {valid_kinds}")

        if not isinstance(
            value,
            (
                ProgramMetadataInsert,
                ProgramMetadataExtend,
                ProgramMetadataRemove
            )
        ):
            raise ValueError(
                """
                expected `value` to be one of:
                ProgramMetadataInsert,
                ProgramMetadataExtend,
                ProgramMetadataRemove
                """
            )

        self.kind = kind
        self.value = value

    def to_json(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"metadata": self.value.to_dict()}


class ProgramDataInsert:
    """
    An enum variant-like type that is used to insert a single key-value pair
    into the program_data field
    """

    def __init__(self, key: str, value: str):
        if not isinstance(key, str):
            raise ValueError

        if not isinstance(value, str):
            raise ValueError

        self.key = key
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"insert": [self.key, self.value]}


class ProgramDataExtend:
    """
    An enum variant-like type that is used to insert multiple key-value pairs
    into the program_data field
    """

    def __init__(self, map: Dict[str, str]):
        if not isinstance(map, Dict[str, str]):
            raise ValueError

        self.map = map

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"extend": self.map}


class ProgramDataRemove:
    """
    An enum variant-like type that is ussed to remove a key-value pair from the
    program_data field
    """

    def __init__(self, key: str):
        if not isinstance(key, str):
            raise ValueError

        self.key = key

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"remove": self.key}


class ProgramDataValue:
    """
    A type used to represent a value being updated in a program data field
    """

    def __init__(
        self,
        value: Union[
            ProgramDataInsert,
            ProgramDataExtend,
            ProgramDataRemove
        ]
    ):
        if not isinstance(
            value,
            (
                ProgramDataInsert,
                ProgramDataExtend,
                ProgramDataRemove
            )
        ):
            raise ValueError

        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {"data": self.value.to_dict()}


class ProgramFieldValue:
    """
    A type used to represent a field `kind` and value to update a program
    data field
    """

    def __init__(
        self,
        kind: str,
        value: Union[
            LinkedProgramsValue,
            ProgramMetadataValue,
            ProgramDataValue
        ]
    ):
        if not isinstance(kind, str):
            raise ValueError

        if not isinstance(
            value,
            (
                LinkedProgramsValue,
                ProgramMetadataValue,
                ProgramDataValue
            )
        ):
            raise ValueError

        self.kind = kind
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {self.kind: self.value.to_dict()}


class ProgramField:
    """
    A type representing one of multiple types that can be updated in the
    program account
    """

    def __init__(self, kind: str):
        if not isinstance(kind, str):
            raise ValueError

        self.kind = kind

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return self.kind


class ProgramUpdateField:
    """
    A type representing an program field to be updated, with a given value
    """

    def __init__(self, field: ProgramField, value: ProgramFieldValue):
        if not isinstance(field, ProgramField):
            raise ValueError

        if not isinstance(value, ProgramFieldValue):
            raise ValueError

        self.field = field
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "field": self.field.to_dict(),
            "value": self.value.to_dict()
        }


class ProgramUpdate:
    """
    A type that is used to pass multiple updates to a given program account
    """

    def __init__(
        self,
        account: AddressOrNamespace,
        updates: List[ProgramUpdateField]
    ):
        if not isinstance(account, AddressOrNamespace):
            raise ValueError

        if not isinstance(updates, List[ProgramUpdateField]):
            raise ValueError

        self.account = account
        self.updates = updates

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "account": self.account,
            "updates": [update.to_dict() for update in self.updates]
        }


class TokenOrProgramUpdate:
    """
    An enum-like type that can represent either a Token update or Program
    update.
    """

    def __init__(self, kind: str, value: Union[TokenUpdate, ProgramUpdate]):
        if not isinstance(kind, str):
            raise ValueError

        if not isinstance(value, (TokenUpdate, ProgramUpdate)):
            raise ValueError

        self.kind = kind
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {self.kind: self.value.to_dict()}


class TokenDistribution:
    """
    This type is included in a CreateInstruction to distribute
    token and token data at the creation.
    """

    def __init__(
        self,
        program_id: AddressOrNamespace,
        to: AddressOrNamespace,
        amount: Optional[U256],
        token_ids: List[U256],
        update_fields: List[TokenUpdateField]
    ):

        if not all(
            isinstance(program_id, AddressOrNamespace),
            isinstance(to, AddressOrNamespace),
            isinstance(amount, (None, U256)),
            isinstance(token_ids, List[U256]),
            isinstance(update_fields, List[TokenUpdateField])
        ):
            raise ValueError

        self.program_id = program_id
        self.to = to
        self.amount = amount
        self.token_ids = token_ids
        self.update_fields = update_fields

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "programId": self.program_id.to_dict(),
            "to": self.to.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "tokenIds": [item.to_dict() for item in self.token_ids],
            "updateFields": [item.to_dict() for item in self.update_fields]
        }


class CreateInstruction:
    """
    One of 4 instruction variants, this instruction is used as a `constructor`
    of sorts. This instruction can be used to simply create the first
    instance of a new token in the LASR protocol, airdrop tokens, create/mint
    additional supply of a token, set the metadata, and initial data of the
    token, and more.

    params:
        program_namespace: An address or namespace representing the
        program that governs this token

        program_id: An address or namespace representing the program
        account

        owner: the address of the owner of this program

        total_supply: the total supply that will ever exist for this token

        initialized_supply: the initial supply created on the first call
        to a function or method that returns this type

        distribution: an array of distributions to be applied upon the
        return of this type
    """

    def __init__(
        self,
        program_namespace: AddressOrNamespace,
        program_id: AddressOrNamespace,
        program_owner: Address,
        total_supply: U256,
        initialized_supply: U256,
        distribution: List[TokenDistribution]
    ):

        if not all(
            isinstance(program_namespace, AddressOrNamespace),
            isinstance(program_id, AddressOrNamespace),
            isinstance(program_owner, Address),
            isinstance(total_supply, U256),
            isinstance(initialized_supply, U256),
            isinstance(distribution, List[TokenDistribution])
        ):
            raise ValueError

        self.program_namespace = program_namespace
        self.program_id = program_id
        self.program_owner = program_owner
        self.total_supply = total_supply
        self.initialized_supply = initialized_supply
        self.distribution = distribution

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
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
    """
    This type informs the protocol to update one or more tokens owned by
    one or more accounts. This instruction is only valid if it contains
    updates for token(s) the program returning it governs, or has been
    explicitly granted approval to update. This type is effectively a wrapper
    around an array of `TokenOrProgram` updates. This type, however, is applied
    as a single atomic unit, if any of the `TokenOrProgramUpdate`s it contains
    are invalid or fail, the entire application of this type is invalid or
    fails
    """

    def __init__(self, updates: List[TokenOrProgramUpdate]):

        if not isinstance(updates, List[TokenOrProgramUpdate]):
            raise ValueError

        self.updates = updates

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "updates": [update.to_dict() for update in self.updates]
        }


class TransferInstruction:
    """
    This type informs the LASR protocol to transfer the balance from one
    `Account`/`Token` pair, or a list of non-fungible `tokenIds` from one
    `Account`/`Token` pair to another `Account`.
    """

    def __init__(
        self,
        token: Address,
        transfer_from: AddressOrNamespace,
        transfer_to: AddressOrNamespace,
        amount: Optional[U256],
        ids: List[U256]
    ):

        if not all(
            isinstance(token, Address),
            isinstance(transfer_from, AddressOrNamespace),
            isinstance(transfer_to, AddressOrNamespace),
            isinstance(amount, (None, U256)),
            isinstance(ids, List[U256])
        ):
            raise ValueError

        self.token = token
        self.transfer_from = transfer_from
        self.transfer_to = transfer_to
        self.amount = amount
        self.ids = ids

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "token": self.token.to_dict(),
            "from": self.transfer_from.to_dict(),
            "to": self.transfer_to.to_dict(),
            "amount": "null" if self.amount is None else self.amount.to_dict(),
            "ids": [item.to_dict() for item in self.ids]
        }


class BurnInstruction:
    """
    This type informs the LASR protocol to burn the `amount` from the balance,
    or one or more non-fungible `tokenIds` from the given `Account`. This
    instruction is only valid if the `caller` or the program returning it has
    explicit approval for the `burn_from` `Account` for the given `token`.
    """

    def __init__(
        self,
        caller: Address,
        program_id: AddressOrNamespace,
        token: Address,
        burn_from: AddressOrNamespace,
        amount: Optional[U256],
        token_ids: List[U256],
    ):

        if not all(
            isinstance(caller, Address),
            isinstance(program_id, AddressOrNamespace),
            isinstance(token, Address),
            isinstance(burn_from, AddressOrNamespace),
            isinstance(amount, (None, U256)),
            isinstance(token_ids, List[U256])
        ):
            raise ValueError

        self.caller = caller
        self.program_id = program_id
        self.token = token
        self.burn_from = burn_from
        self.amount = amount
        self.token_ids = token_ids

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
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
        """
        Returns a JSON serializable map representing this type
        """
        return {}


class Instruction:
    """
    This type is an enum-like type that can be one of 4 possible variants,
    CreateInstruction, UpdateInstruction, TransferInstruction, BurnInstruction
    """

    def __init__(
        self,
        kind: str,
        value: Union[
            CreateInstruction,
            BurnInstruction,
            UpdateInstruction,
            TransferInstruction
        ]
    ):
        if not all(
            isinstance(kind, str),
            isinstance(
                value,
                (
                    CreateInstruction,
                    BurnInstruction,
                    UpdateInstruction,
                    TransferInstruction
                )
            )
        ):
            raise ValueError

        self.kind = kind
        self.value = value

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            self.kind: self.value.to_dict()
        }


class Outputs:
    """
    This type is the wrapper around the entirity of what will be returned
    from a given program back to the LASR protocol for validation & processing.
    """

    def __init__(self, inputs: str, instructions: List[Instruction]):

        if not all(
            isinstance(input, str),
            isinstance(instructions, List[Instruction])
        ):
            raise ValueError

        self.inputs = inputs
        self.instructions = instructions

    def to_dict(self):
        """
        Returns a JSON serializable map representing this type
        """
        return {
            "inputs": self.inputs,
            "instructions": [
                instruction.to_dict() for instruction in self.instructions
            ]
        }


class TokenUpdateBuilder:
    """
    This type provides a simple Builder pattern for building TokenUpdate's
    more easily. This is a helper class that enables the developer to ensure
    they are building and returning valid TokenUpdate's for instructions
    which contain such a type.
    """

    def __init__(
        self,
        account: Optional[AddressOrNamespace] = None,
        token: Optional[AddressOrNamespace] = None
    ):
        self.account = None
        self.token = None
        self.updates = []

    def add_update_account_address(self, account: AddressOrNamespace):
        """
        Adds a new account address to the TokenUpdate
        """
        if not isinstance(account, AddressOrNamespace):
            raise ValueError

        self.account = account
        return self

    def add_token_address(self, token_address: AddressOrNamespace):
        """
        Adds a new `token` address to the TokenUpdate
        """
        if not isinstance(token_address, AddressOrNamespace):
            raise ValueError
        self.token = token_address
        return self

    def add_update_field(self, update_field: TokenUpdateField):
        """
        Appends a single update_field
        """
        if not isinstance(update_field, TokenUpdateField):
            raise ValueError

        self.updates.append(update_field)
        return self

    def extend_update_fields(self, update_fields: List[TokenUpdateField]):
        """
        Appends multiple update_fields to the TokenUpdate
        """
        if not isinstance(update_fields, List[TokenUpdateField]):
            raise ValueError

        self.updates = self.updates + update_fields

    def build(self) -> TokenUpdate:
        """
        Takes this builder class and builds/converts it to a TokenUpdate
        """
        if self.account is None:
            raise ValueError

        if self.token is None:
            raise ValueError

        if len(self.updates) == 0:
            raise ValueError

        return TokenUpdate(
            self.account.to_dict(),
            self.token.to_dict(),
            self.updates
        )


class TokenDistributionBuilder:
    """
    This type provides a simple Builder pattern class for building
    `TokenDistribution`s. `TokenDistribution`s are an essential component
    of the `CreateInstruction` type, and it is important that they are built
    correctly with all required fields, and that all fields are of the correct
    type. This builder type ensures the developer building LASR programs is
    able to build them with ease.
    """

    def __init__(self):
        self.program_id = None
        self.to = None
        self.amount = None
        self.token_ids = []
        self.update_fields = []

    def set_program_id(self, program_id: AddressOrNamespace):
        """
        Sets the program_id for the TokenDistribution
        """
        if not isinstance(program_id, AddressOrNamespace):
            raise ValueError

        self.program_id = program_id
        return self

    def set_receiver(self, receiver: AddressOrNamespace):
        """
        Sets the receiver address for this TokenDistribution
        """
        if not isinstance(receiver, AddressOrNamespace):
            raise ValueError
        self.to = receiver
        return self

    def set_amount(self, amount: U256):
        """
        Sets the amount of the token to be distributed to the receiver
        """
        if not isinstance(amount, U256):
            raise ValueError

        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        """
        Adds a single tokenId to the token distribution (used primarily for
        non-fungible tokens).
        """
        if not isinstance(token_id, U256):
            raise ValueError

        self.token_ids.append(token_id)
        return self

    def add_update_field(self, update_field: TokenUpdateField):
        """
        Adds a single update_field to the TokenDistribution
        """
        if not isinstance(update_field, TokenUpdateField):
            raise ValueError

        self.update_fields.append(update_field)
        return self

    def extend_token_ids(self, items: List[U256]):
        """
        adds multiple token_ids to a given TokenDistribution
        """
        if not isinstance(items, List[U256]):
            raise ValueError

        self.token_ids = self.token_ids + items
        return self

    def extend_update_fields(self, items: List[TokenUpdateField]):
        """
        adds multiple update_fields to a single TokenDistribution
        """
        if not isinstance(items, List[TokenUpdateField]):
            raise ValueError

        self.update_fields = self.update_fields + items
        return self

    def build(self) -> TokenDistribution:
        """
        Converts this builder type to a proper TokenDistribution
        """
        if self.program_id is None:
            raise ValueError

        if self.to is None:
            raise ValueError

        if self.amount is None:
            raise ValueError

        return TokenDistribution(
            self.program_id,
            self.to,
            self.amount,
            self.token_ids,
            self.update_fields
        )


class CreateInstructionBuilder:
    """
    This is a Builder pattern type that makes it easier for developers to
    build properly structured CreateInstructions.
    """

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
        """
        sets the address or namespace of the program for which the token
        is being created
        """
        if not isinstance(program_namespace, AddressOrNamespace):
            raise ValueError

        self.program_namespace = program_namespace
        return self

    def set_program_id(self, program_id: AddressOrNamespace):
        """
        sets the program id for the token being created, though this seems
        redundant with the program_namespace, for factory-like contracts this
        is necessary
        """
        if not isinstance(program_id, AddressOrNamespace):
            raise ValueError

        self.program_id = program_id
        return self

    def set_program_owner(self, program_owner: Address):
        """
        sets the owner of the program, typically the caller, though in certain
        circumstances ownership may be handed off to a different account, such
        as an account governed by a multisig, or another program
        """
        if not isinstance(program_owner, Address):
            raise ValueError

        self.program_owner = program_owner
        return self

    def set_total_supply(self, total_supply: U256):
        """
        sets the total supply for a new token that is being created for the
        first time. If this is used on CreateInstruction returned for a token
        that already exists, the Instruction will be considered invalid
        """
        if not isinstance(total_supply, U256):
            raise ValueError

        self.total_supply = total_supply
        return self

    def set_initialized_supply(self, initialized_supply: U256):
        """
        sets the initialized_supply for a new token that is being created
        for the first time. If this is used on a CreateInstruction returned
        for a token that already exists, the Instruction will be considered
        invalid
        """
        if not isinstance(initialized_supply, U256):
            raise ValueError

        self.initialized_supply = initialized_supply
        return self

    def add_token_distribution(self, token_distribution: TokenDistribution):
        """
        adds a single new TokenDistribution to the CreateInstruction
        """
        if not isinstance(token_distribution, TokenDistribution):
            raise ValueError

        self.distribution.append(token_distribution)
        return self

    def extend_token_distribution(self, items: List[TokenDistribution]):
        """
        adds multiple new TokenDistributions to the CreateInstruction
        """
        if not isinstance(items, List[TokenDistribution]):
            raise ValueError

        self.distribution = self.distribution + items
        return self

    def build(self) -> CreateInstruction:
        """
        Converts this builder type into a properly structured CreateInstruction
        """
        if self.program_namespace is None:
            raise ValueError

        if self.program_id is None:
            raise ValueError

        if self.program_owner is None:
            raise ValueError

        if self.total_supply is None:
            self.total_supply = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

        if self.initialized_supply is None:
            self.initialized_supply = self.total_supply

        return Instruction(
            "create",
            CreateInstruction(
                self.program_namespace,
                self.program_id,
                self.program_owner,
                self.total_supply,
                self.initialized_supply,
                self.distribution
            )
        )


class UpdateInstructionBuilder:
    """
    This type is a Builder pattern type that provides a simple way for
    developers to build properly structured UpdateInstructions
    """

    def __init__(self):
        self.updates = []

    def add_update(self, update: TokenOrProgramUpdate):
        """
        adds a single TokenOrProgramUpdate to the UpdateInstruction
        """
        if not isinstance(update, TokenOrProgramUpdate):
            raise ValueError

        self.updates.append(update)
        return self

    def extend_updates(self, items: List[TokenOrProgramUpdate]):

        if not isinstance(items, List[TokenOrProgramUpdate]):
            raise ValueError

        self.updates = self.updates + items
        return self

    def build(self) -> UpdateInstruction:
        """
        converts this builder type into a properly structured UpdateInstruction
        """
        return Instruction("update", UpdateInstruction(self.updates))


class TransferInstructionBuilder:
    """
    This is a Builder type that makes the process of building properly
    structured TransferInstructions simpler for developers
    """

    def __init__(self):
        self.token = None
        self.transfer_from = None
        self.transfer_to = None
        self.amount = None
        self.ids = []

    def set_token_address(self, token_address: Address):
        """
        sets the address of the token being transfered
        """
        if not isinstance(token_address, Address):
            raise ValueError

        self.token = token_address
        return self

    def set_transfer_from(self, transfer_from: AddressOrNamespace):
        """
        sets the address or namespace of the account the token is being
        transfered from
        """
        if not isinstance(transfer_from, AddressOrNamespace):
            raise ValueError

        self.transfer_from = transfer_from
        return self

    def set_transfer_to(self, transfer_to: AddressOrNamespace):
        """
        sets the address or namespace of the token being transfered to
        """
        if not isinstance(transfer_to, AddressOrNamespace):
            raise ValueError

        self.transfer_to = transfer_to
        return self

    def set_amount(self, amount: U256):
        """
        sets the amount of the token being transferred
        """

        if not isinstance(amount, U256):
            raise ValueError

        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        """
        adds a single tokenId to the transfer instruction, typically used
        for transferring non-fungible tokens
        """
        if not isinstance(token_id, U256):
            raise ValueError

        self.ids.append(token_id)
        return self

    def extend_token_ids(self, items: List[U256]):
        """
        adds multiple tokenIds to the transfer instruction, typically used
        for transferring non-fungible tokens
        """
        self.ids = self.ids + items
        return self

    def build(self) -> TransferInstruction:
        """
        converts this builder type into a properly structured
        TransferInstruction
        """
        return Instruction(
            "transfer",
            TransferInstruction(
                self.token,
                self.transfer_from,
                self.transfer_to,
                self.amount,
                self.ids
            )
        )


class BurnInstructionBuilder:
    """
    This is a Builder pattern type to make building properly structured
    BurnInstructions simple for developers
    """

    def __init__(self):
        self.caller = None
        self.program_id = None
        self.token = None
        self.burn_from = None
        self.amount = None
        self.token_ids = []

    def set_caller(self, caller: Address):
        """
        sets the address of the original caller of the program/function/method
        returning this instruction
        """
        if not isinstance(caller, Address):
            raise ValueError

        self.caller = caller
        return self

    def set_program_id(self, program_id: AddressOrNamespace):
        """
        sets the program_id of the program that is returning this instruction
        """
        if not isinstance(program_id, AddressOrNamespace):
            raise ValueError

        self.program_id = program_id
        return self

    def set_token_address(self, token_address: Address):
        """
        sets the address of the token to be burned by this instruction
        """
        if not isinstance(token_address, Address):
            raise ValueError

        self.token_address = token_address
        return self

    def set_burn_from_address(self, burn_from_address: AddressOrNamespace):
        """
        sets the address to the account from which the burn will be applied
        """
        if not isinstance(burn_from_address, AddressOrNamespace):
            raise ValueError

        self.burn_from = burn_from_address
        return self

    def set_amount(self, amount: U256):
        """
        sets t he amount of the token to burn
        """
        if not isinstance(amount, U256):
            raise ValueError

        self.amount = amount
        return self

    def add_token_id(self, token_id: U256):
        """
        adds a single token id to the burn instruction, typically used
        for non-fungible tokens
        """
        if not isinstance(token_id, U256):
            raise ValueError

        self.token_ids.append(token_id)
        return self

    def extend_token_ids(self, items: List[U256]):
        """
        adds multiple token ids to the burn instruction, typically used for
        non-fungible tokens
        """
        if not isinstance(items, List[U256]):
            raise ValueError

        self.token_ids = self.token_ids + items
        return self

    def build(self) -> BurnInstruction:
        """
        converts the builder type into a properly structured burn instruction
        """
        return Instruction(
            "burn",
            BurnInstruction(
                self.caller,
                self.program_id,
                self.token,
                self.burn_from,
                self.amount,
                self.token_ids
            )
        )


class LogInstructionBuilder:
    pass


class OutputBuilder:
    """
    This type is a Builder type to build Outputs, the canonical type that
    LASR programs return to the LASR protocol.
    """

    def __init__(self):
        self.inputs = None
        self.instructions = []

    def set_inputs(self, inputs: str):
        """
        sets the inputs provided to the program by the protocol
        """
        if not isinstance(inputs, str):
            raise ValueError

        self.inputs = inputs
        return self

    def add_instruction(self, instruction: Instruction):
        """
        adds a single instruction to the Output
        """
        if not isinstance(instruction, Instruction):
            raise ValueError
        self.instructions.append(instruction)
        return self

    def extend_instructions(self, instructions: List[Instruction]):
        """
        Adds multiple instructions to the Output
        """
        if not isinstance(instructions, List[Instruction]):
            raise ValueError

        self.instructions = self.instructions + instructions

    def build(self):
        """
        converts this builder type into proper Outputs
        """
        return Outputs(self.inputs, self.instructions)
