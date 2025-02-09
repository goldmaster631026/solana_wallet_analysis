from solders.pubkey import Pubkey
from solders.system_program import SYS_PROGRAM_ID
from solana.rpc.api import BlockingClient
from spl.token.constants import TOKEN_PROGRAM_ID
import struct
import base64
import logging

# Assume these are defined elsewhere to match your JS code
MAINNET_PROGRAM_ID = {
    "AmmV4": Pubkey.from_string("675kQQzXyM2sCpthJjS4p36UehqMxMKE2kdUftYq9EEW"),
    "OPENBOOK_MARKET": Pubkey.from_string("srmqPvymJeFKQ4zGh9VPDbLQUWwcox51LVMkG9xmkLh")
}

# Dummy values, replace with actual layout definitions
LIQUIDITY_STATE_LAYOUT_V4 = {
    "span": 344,  # Replace with actual size
    "offsetOf": lambda field: {
        "baseMint": 68,  # Replace with actual offset
        "quoteMint": 100,  # Replace with actual offset
    }.get(field)
}

MARKET_STATE_LAYOUT_V3 = {
    "span": 376
}

SPL_MINT_LAYOUT = {
    "span": 82
}

# Replace with your actual connection object
connection = BlockingClient("https://api.mainnet-beta.solana.com")  # Replace with your RPC endpoint


def get_associated_authority(program_id: Pubkey) -> Pubkey:
    """Python implementation of Liquidity.getAssociatedAuthority.  Replace with your actual implementation if different."""
    # Dummy implementation - replace with actual logic if needed
    return Pubkey.find_program_address([b"amm authority"], program_id)[0]


def get_market_associated_authority(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    """Python implementation of Market.getAssociatedAuthority. Replace with your actual implementation if different."""
    # Dummy implementation - replace with actual logic if needed
    return Pubkey.find_program_address([market_id.to_bytes_v1(), b"market authority"], program_id)[0]


class Layout:
    def __init__(self, fields, length):
        self.fields = fields
        self.length = length

    def decode(self, data):
        decoded = {}
        for name, format_char, offset in self.fields:
            size = struct.calcsize(format_char)
            value = struct.unpack_from(format_char, data, offset)[0]
            decoded[name] = value
        return decoded

def to_uint64(number: int) -> bytes:
    return struct.pack("<Q", number)


async def fetch_pool_info_by_mint(mint: str):
    """
    Gets pool information for the given token mint address.
    Args:
        mint (str): The mint address of the token.
    Returns:
        dict: A dictionary containing the pool information, or None if not found.
    """
    try:
        logging.info(f"Fetching pool info for Mint: {mint}")
        mint_address = Pubkey.from_string(mint)

        # Fetch program accounts for Raydium's AMM program (AmmV4)
        filters = [
            {"dataSize": LIQUIDITY_STATE_LAYOUT_V4["span"]},
            {
                "memcmp": {
                    "offset": LIQUIDITY_STATE_LAYOUT_V4["offsetOf"]("baseMint"),
                    "bytes": str(mint_address),
                }
            }
        ]

        accounts = connection.get_program_accounts(
            MAINNET_PROGRAM_ID["AmmV4"],
            filters=filters
        )

        if len(accounts) == 0:
            # If no account was found with mint as baseMint, try matching it as quoteMint
            quote_filters = [
                {"dataSize": LIQUIDITY_STATE_LAYOUT_V4["span"]},
                {
                    "memcmp": {
                        "offset": LIQUIDITY_STATE_LAYOUT_V4["offsetOf"]("quoteMint"),
                        "bytes": str(mint_address),
                    }
                }
            ]

            quote_accounts = connection.get_program_accounts(
                MAINNET_PROGRAM_ID["AmmV4"],
                filters=quote_filters
            )

            if len(quote_accounts) == 0:
                raise ValueError(f"No pool found for mint: {mint}")

            # Use the first account found where mint is quoteMint
            pool_account = quote_accounts[0]
            return await decode_pool_and_market_info(pool_account, mint)

        # Use the first account found where mint is baseMint
        pool_account = accounts[0]
        return await decode_pool_and_market_info(pool_account, mint)

    except Exception as e:
        logging.error(f"Error fetching pool info by Mint: {e}")
        return None


async def decode_pool_and_market_info(pool_account, mint):
    """Helper function to decode pool and market info."""
    pool_key = Pubkey.from_string(pool_account.pubkey)
    account_data_base64 = pool_account.account.data
    account_data = base64.b64decode(account_data_base64)

    # Assuming LIQUIDITY_STATE_LAYOUT_V4.decode method exists and works similarly to the JS version
    pool_state = decode_liquidity_state(account_data)
    logging.info(f"Pool account found for Mint: {mint}, Pool ID: {pool_key}")

    # Fetch the market account using the decoded marketId
    market_account = connection.get_account_info(pool_state['marketId'].to_string())
    if market_account.value is None:
        raise ValueError("Market account not found")
    market_account_data_base64 = market_account.value.data[0]
    market_account_data = base64.b64decode(market_account_data_base64)

    logging.info(f"Market account data length: {len(market_account_data)} bytes")
    # Assuming MARKET_STATE_LAYOUT_V3.decode method exists and works similarly to the JS version
    market_info = decode_market_state(market_account_data)

    # Fetch LP mint information
    lp_mint_account = connection.get_account_info(pool_state['lpMint'].to_string())
    if lp_mint_account.value is None:
        raise ValueError("LP mint account not found")

    lp_mint_account_data_base64 = lp_mint_account.value.data[0]
    lp_mint_account_data = base64.b64decode(lp_mint_account_data_base64)

    # Assuming SPL_MINT_LAYOUT.decode method exists and works similarly to the JS version
    lp_mint_info = decode_mint_state(lp_mint_account_data)

    # Calculate the market authority
    market_authority = Pubkey.create_program_address(
        [
            bytes(market_info['ownAddress']),
            to_uint64(market_info['vaultSignerNonce'])
        ],
        MAINNET_PROGRAM_ID["OPENBOOK_MARKET"]
    )

    # Log and return the full set of pool data
    pool_data = {
        "id": pool_key,  # Pool ID
        "baseMint": pool_state['baseMint'],
        "quoteMint": pool_state['quoteMint'],
        "lpMint": pool_state['lpMint'],
        "baseDecimals": pool_state['baseDecimal'],
        "quoteDecimals": pool_state['quoteDecimal'],
        "lpDecimals": lp_mint_info['decimals'],
        "version": 4,  # Set version as the number literal 4 (not a string)
        "programId": Pubkey.from_string(pool_account.account.owner),
        "authority": get_associated_authority(Pubkey.from_string(pool_account.account.owner)),
        "openOrders": pool_state['openOrders'],
        "targetOrders": pool_state['targetOrders'],
        "baseVault": pool_state['baseVault'],
        "quoteVault": pool_state['quoteVault'],
        "withdrawQueue": pool_state['withdrawQueue'],
        "lpVault": pool_state['lpVault'],
        "marketVersion": 3,
        "marketProgramId": pool_state['marketProgramId'],
        "marketId": pool_state['marketId'],
        "marketAuthority": get_market_associated_authority(pool_state['marketProgramId'], pool_state['marketId']),
        "marketBaseVault": market_info['baseVault'],
        "marketQuoteVault": market_info['quoteVault'],
        "marketBids": market_info['bids'],
        "marketAsks": market_info['asks'],
        "marketEventQueue": market_info['eventQueue'],
        "lookupTableAccount": Pubkey.default(),
    }

    logging.info(f"Full pool data: {pool_data}")

    return pool_data


def decode_liquidity_state(data: bytes) -> dict:
    """Decodes the liquidity state data.  Replace with your actual layout."""
    layout = Layout([
        ("status", "<i1", 0),
        ("baseMint", "<32s", 68),
        ("quoteMint", "<32s", 100),
        ("lpMint", "<32s", 132),
        ("baseVault", "<32s", 164),
        ("quoteVault", "<32s", 196),
        ("lpVault", "<32s", 228),
        ("openOrders", "<32s", 260),
        ("targetOrders", "<32s", 292),
        ("withdrawQueue", "<32s", 324),
        ("baseDecimal", "<i1", 33),
        ("quoteDecimal", "<i1", 34),
        ("marketProgramId", "<32s", 35),
        ("marketId", "<32s", 36),
    ], LIQUIDITY_STATE_LAYOUT_V4["span"])
    decoded_data = layout.decode(data)

    # Convert bytes to Pubkey objects
    decoded_data['baseMint'] = Pubkey(bytes(decoded_data['baseMint'][:32]))
    decoded_data['quoteMint'] = Pubkey(bytes(decoded_data['quoteMint'][:32]))
    decoded_data['lpMint'] = Pubkey(bytes(decoded_data['lpMint'][:32]))
    decoded_data['baseVault'] = Pubkey(bytes(decoded_data['baseVault'][:32]))
    decoded_data['quoteVault'] = Pubkey(bytes(decoded_data['quoteVault'][:32]))
    decoded_data['lpVault'] = Pubkey(bytes(decoded_data['lpVault'][:32]))
    decoded_data['openOrders'] = Pubkey(bytes(decoded_data['openOrders'][:32]))
    decoded_data['targetOrders'] = Pubkey(bytes(decoded_data['targetOrders'][:32]))
    decoded_data['withdrawQueue'] = Pubkey(bytes(decoded_data['withdrawQueue'][:32]))
    decoded_data['marketProgramId'] = Pubkey(bytes(decoded_data['marketProgramId'][:32]))
    decoded_data['marketId'] = Pubkey(bytes(decoded_data['marketId'][:32]))

    return decoded_data


def decode_market_state(data: bytes) -> dict:
    """Decodes the market state data. Replace with your actual layout."""

    layout = Layout([
        ("ownAddress", "<32s", 40),
        ("vaultSignerNonce", "<Q", 280),
        ("baseVault", "<32s", 88),
        ("quoteVault", "<32s", 120),
        ("bids", "<32s", 152),
        ("asks", "<32s", 184),
        ("eventQueue", "<32s", 216)
    ], MARKET_STATE_LAYOUT_V3["span"])
    decoded_data = layout.decode(data)

    decoded_data['ownAddress'] = Pubkey(bytes(decoded_data['ownAddress'][:32]))
    decoded_data['baseVault'] = Pubkey(bytes(decoded_data['baseVault'][:32]))
    decoded_data['quoteVault'] = Pubkey(bytes(decoded_data['quoteVault'][:32]))
    decoded_data['bids'] = Pubkey(bytes(decoded_data['bids'][:32]))
    decoded_data['asks'] = Pubkey(bytes(decoded_data['asks'][:32]))
    decoded_data['eventQueue'] = Pubkey(bytes(decoded_data['eventQueue'][:32]))

    return decoded_data


def decode_mint_state(data: bytes) -> dict:
    """Decodes the mint state data. Replace with your actual layout."""
    layout = Layout([
        ("decimals", "<i1", 44),
    ], SPL_MINT_LAYOUT["span"])
    decoded_data = layout.decode(data)
    return decoded_data


# Example usage:
async def main():
    logging.basicConfig(level=logging.INFO)
    mint_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wDQk61v5kxw9"  # Example mint address, replace with a real one
    pool_info = await fetch_pool_info_by_mint(mint_address)
    if pool_info:
        print("Pool Info:", pool_info)
    else:
        print("Pool not found.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
