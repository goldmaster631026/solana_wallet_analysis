from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solana.rpc.api import Client
from construct import Struct, int, U64, U128, Bytes, Flag
import base64

# Constants (replace with actual values)
MAINNET_PROGRAM_ID_AMM_V4 = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")  # Raydium AMM V4 Program ID
MAINNET_PROGRAM_ID_OPENBOOK_MARKET = Pubkey.from_string("srmqPvymJeFKQ4zGh9VPDbLvm3hYxPHwg9z3ZiISPV")  # OpenBook Market Program ID
SPL_TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJj5Jybbm89VG2tZq9ayssGAfk")
RENT_PROGRAM_ID = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# Layout Definitions (using Construct) - adjust based on actual Raydium layout
# **IMPORTANT**: These layouts *must* match the on-chain data structures.  This is the trickiest part - you'll need to carefully inspect the Raydium program's source code or documentation to get the correct layouts.  These are *examples* and almost certainly need modification.

LIQUIDITY_STATE_LAYOUT_V4 = Struct(
    "status" / U64,  # Added Status Field based on the error you mentioned.
    "nonce" / U8,
    "baseMint" / Bytes(32),
    "quoteMint" / Bytes(32),
    "lpMint" / Bytes(32),
    "baseVault" / Bytes(32),
    "quoteVault" / Bytes(32),
    "lpVault" / Bytes(32),
    "openOrders" / Bytes(32),
    "targetOrders" / Bytes(32),
    "withdrawQueue" / Bytes(32),
    "marketId" / Bytes(32),
    "marketProgramId" / Bytes(32),
    "baseDecimal" / U8,
    "quoteDecimal" / U8,
    "padding" / Bytes(14),
)

MARKET_STATE_LAYOUT_V3 = Struct(
    "status" / U64, # Added Status Field based on the error you mentioned.
    "baseMint" / Bytes(32),
    "quoteMint" / Bytes(32),
    "baseVault" / Bytes(32),
    "quoteVault" / Bytes(32),
    "bids" / Bytes(32),
    "asks" / Bytes(32),
    "eventQueue" / Bytes(32),
    "ownAddress" / Bytes(32),
    "vaultSignerNonce" / U64,
    "baseLotSize" / U64,
    "quoteLotSize" / U64,
    "feeRateBps" / U64,
    "referrerRebatesAccrued" / U64,
)


SPL_MINT_LAYOUT = Struct(
    "mint_authority_option" / U8,
    "mint_authority" / Bytes(32),
    "supply" / U64,
    "decimals" / U8,
    "is_initialized" / Flag,
    "freeze_authority_option" / U8,
    "freeze_authority" / Bytes(32)
)

# Helper Functions (Solana-specific)

def get_associated_authority(program_id: Pubkey) -> Pubkey:
    """Derives the associated authority for a given program ID."""
    # Replace with the actual derivation logic used by Raydium
    # This is a placeholder - Raydium's actual authority derivation may be different!
    seed = b"amm authority"
    program_address, nonce = Pubkey.find_program_address([seed], program_id)
    return program_address, nonce # Return both address and nonce.  The JS code only returns the address...

def get_market_associated_authority(market_program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    """Derives the associated authority for a given market ID."""
    # Replace with the actual derivation logic used by OpenBook
     # This is a placeholder - OpenBook's actual authority derivation may be different!
    seed = bytes(market_id)  # Using the market ID as seed
    program_address, nonce = Pubkey.find_program_address([seed], market_program_id)
    return program_address, nonce # Return both address and nonce. The JS code only returns the address...


async def fetch_pool_info_by_mint(mint: str, connection: Client):
    """
    Gets pool information for the given token mint address.

    Args:
        mint (str): The mint address of the token.
        connection (Client): Solana RPC Client

    Returns:
        dict | None: A dictionary containing pool information, or None if not found.
    """
    try:
        print(f"Fetching pool info for Mint: {mint}")
        mint_address = Pubkey.from_string(mint)

        # --- Search for accounts where mint is the baseMint ---
        filters = [
            {"dataSize": len(LIQUIDITY_STATE_LAYOUT_V4.build({}))},  # Check data size
            {
                "memcmp": {
                    "offset": 9,  # Offset of baseMint in LIQUIDITY_STATE_LAYOUT_V4 - Adjusted Offset based on Struct
                    "bytes": str(mint_address),  #Need to compare string representation
                }
            },
        ]
        accounts = await connection.get_program_accounts(MAINNET_PROGRAM_ID_AMM_V4, filters=filters, encoding="base64")

        if not accounts:
            # --- Search for accounts where mint is the quoteMint ---
            filters = [
                {"dataSize": len(LIQUIDITY_STATE_LAYOUT_V4.build({}))},  # Check data size
                {
                    "memcmp": {
                        "offset": 41,  # Offset of quoteMint in LIQUIDITY_STATE_LAYOUT_V4 - Adjusted Offset based on Struct
                        "bytes": str(mint_address),  #Need to compare string representation
                    }
                },
            ]
            accounts = await connection.get_program_accounts(MAINNET_PROGRAM_ID_AMM_V4, filters=filters, encoding="base64")

            if not accounts:
                raise ValueError(f"No pool found for mint: {mint}")

        # Use the first account found
        account = accounts[0]
        return await decode_pool_and_market_info(account, mint, connection)

    except Exception as e:
        print(f"Error fetching pool info by Mint: {e}")
        return None


async def decode_pool_and_market_info(account: dict, mint: str, connection: Client):
    """
    Decodes pool and market information from the given account data.

    Args:
        account (dict): The account data.
        mint (str): The mint address.
        connection (Client): Solana RPC Client

    Returns:
        dict: A dictionary containing the decoded pool and market information.
    """
    pubkey = Pubkey.from_string(account['pubkey'])
    account_data = base64.b64decode(account['account']['data'][0]) # Decode base64 encoded data
    pool_state = LIQUIDITY_STATE_LAYOUT_V4.parse(account_data)

    print(f"Pool account found for Mint: {mint}, Pool ID: {pubkey}")

    # --- Fetch and Decode Market Account ---
    market_id_bytes = bytes(pool_state.marketId)
    market_id = Pubkey(market_id_bytes)
    market_account_info = await connection.get_account_info(market_id)

    if market_account_info["result"] is None:
        raise ValueError("Market account not found")

    market_account_data = base64.b64decode(market_account_info["result"]["value"]["data"][0])
    market_info = MARKET_STATE_LAYOUT_V3.parse(market_account_data)

    # --- Fetch and Decode LP Mint Account ---
    lp_mint_bytes = bytes(pool_state.lpMint)
    lp_mint_id = Pubkey(lp_mint_bytes)
    lp_mint_account_info = await connection.get_account_info(lp_mint_id)

    if lp_mint_account_info["result"] is None:
        raise ValueError("LP mint account not found")

    lp_mint_account_data = base64.b64decode(lp_mint_account_info["result"]["value"]["data"][0])
    lp_mint_info = SPL_MINT_LAYOUT.parse(lp_mint_account_data)

    # --- Calculate Authorities ---
    pool_authority, pool_nonce = get_associated_authority(Pubkey(account['account']['owner']))
    market_authority, market_nonce = get_market_associated_authority(Pubkey(pool_state.marketProgramId), market_id)


    # --- Construct pool_data dictionary ---
    pool_data = {
        "id": pubkey,
        "baseMint": Pubkey(pool_state.baseMint),
        "quoteMint": Pubkey(pool_state.quoteMint),
        "lpMint": Pubkey(pool_state.lpMint),
        "baseDecimals": pool_state.baseDecimal,
        "quoteDecimals": pool_state.quoteDecimal,
        "lpDecimals": lp_mint_info.decimals,
        "version": 4,
        "programId": Pubkey(account['account']['owner']),
        "authority": pool_authority,
        "openOrders": Pubkey(pool_state.openOrders),
        "targetOrders": Pubkey(pool_state.targetOrders),
        "baseVault": Pubkey(pool_state.baseVault),
        "quoteVault": Pubkey(pool_state.quoteVault),
        "withdrawQueue": Pubkey(pool_state.withdrawQueue),
        "lpVault": Pubkey(pool_state.lpVault),
        "marketVersion": 3,
        "marketProgramId": Pubkey(pool_state.marketProgramId),
        "marketId": market_id,
        "marketAuthority": market_authority,
        "marketBaseVault": Pubkey(market_info.baseVault),
        "marketQuoteVault": Pubkey(market_info.quoteVault),
        "marketBids": Pubkey(market_info.bids),
        "marketAsks": Pubkey(market_info.asks),
        "marketEventQueue": Pubkey(market_info.eventQueue),
        "lookupTableAccount": Pubkey(SYS_PROGRAM_ID), # Placeholder
    }

    print("Full pool data:", pool_data)
    return pool_data

# Example Usage (replace with your actual Solana RPC endpoint and mint address)
async def main():
    solana_rpc_url = "https://api.mainnet-beta.solana.com"  # Replace with your RPC endpoint
    connection = Client(solana_rpc_url)
    mint_address = "J5vBmSwngfd9m8rxYACYtFJYKJNW1xhy6xJmp3nMxbfG"  # Replace with the mint address you want to query
    pool_info = await fetch_pool_info_by_mint(mint_address, connection)

    if pool_info:
        print("Pool Info:", pool_info)
    else:
        print("No pool info found for that mint.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
