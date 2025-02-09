/**
   * Gets pool information for the given token mint address.
   * @async
   * @param {string} mint - The mint address of the token.
   * @returns {LiquidityPoolKeys | null} 
   */
async fetchPoolInfoByMint(mint) {
    try {
      console.log(`Fetching pool info for Mint: ${mint}`);
      const mintAddress = new PublicKey(mint);

      // Fetch program accounts for Raydium's AMM program (AmmV4)
      const accounts = await connection.getProgramAccounts(
        MAINNET_PROGRAM_ID.AmmV4,  // Raydium AMM V4 Program ID
        {
          filters: [
            { dataSize: LIQUIDITY_STATE_LAYOUT_V4.span },  // Ensure the correct data size for liquidity pool state
            {
              memcmp: {  // Memory comparison to match base mint
                offset: LIQUIDITY_STATE_LAYOUT_V4.offsetOf("baseMint"),
                bytes: mintAddress.toBase58(),
              }
            }
          ]
        }
      );

      if (accounts.length === 0) {
        // If no account was found with mint as baseMint, try matching it as quoteMint
        const quoteAccounts = await connection.getProgramAccounts(
          MAINNET_PROGRAM_ID.AmmV4,  // Raydium AMM V4 Program ID
          {
            filters: [
              { dataSize: LIQUIDITY_STATE_LAYOUT_V4.span },  // Ensure the correct data size for liquidity pool state
              {
                memcmp: {  // Memory comparison to match quote mint
                  offset: LIQUIDITY_STATE_LAYOUT_V4.offsetOf("quoteMint"),
                  bytes: mintAddress.toBase58(),
                }
              }
            ]
          }
        );

        if (quoteAccounts.length === 0) {
          throw new Error(`No pool found for mint: ${mint}`);
        }

        // Use the first account found where mint is quoteMint
        const poolAccount = quoteAccounts[0];
        return await this.decodePoolAndMarketInfo(poolAccount, mint);
      }

      // Use the first account found where mint is baseMint
      const poolAccount = accounts[0];
      return await this.decodePoolAndMarketInfo(poolAccount, mint);

    } catch (error) {
      console.error("Error fetching pool info by Mint:", error);
      return null;
    }
}

  // Helper function to decode pool and market info
  async decodePoolAndMarketInfo(poolAccount, mint) {
    const poolState = LIQUIDITY_STATE_LAYOUT_V4.decode(poolAccount.account.data);
    console.log(`Pool account found for Mint: ${mint}, Pool ID: ${poolAccount.pubkey.toString()}`);

    // Fetch the market account using the decoded marketId
    const marketAccount = await connection.getAccountInfo(poolState.marketId);
    if (!marketAccount) {
      throw new Error("Market account not found");
    }

    console.log(`Market account data length: ${marketAccount.data.length} bytes`);
    const marketInfo = MARKET_STATE_LAYOUT_V3.decode(marketAccount.data);

    // Fetch LP mint information
    const lpMintAccount = await connection.getAccountInfo(poolState.lpMint);
    if (!lpMintAccount) {
      throw new Error("LP mint account not found");
    }

    const lpMintInfo = SPL_MINT_LAYOUT.decode(lpMintAccount.data);

    // Calculate the market authority
    const marketAuthority = PublicKey.createProgramAddressSync(
      [
        marketInfo.ownAddress.toBuffer(),
        marketInfo.vaultSignerNonce.toArrayLike(Buffer, "le", 8),
      ],
      MAINNET_PROGRAM_ID.OPENBOOK_MARKET
    );

    // Log and return the full set of pool data
    const poolData = {
      id: poolAccount.pubkey,  // Pool ID
      baseMint: poolState.baseMint,
      quoteMint: poolState.quoteMint,
      lpMint: poolState.lpMint,
      baseDecimals: poolState.baseDecimal.toNumber(),
      quoteDecimals: poolState.quoteDecimal.toNumber(),
      lpDecimals: lpMintInfo.decimals,
      version: 4,  // Set version as the number literal 4 (not a string)
      programId: poolAccount.account.owner,
      authority: Liquidity.getAssociatedAuthority({
        programId: poolAccount.account.owner,
      }).publicKey,
      openOrders: poolState.openOrders,
      targetOrders: poolState.targetOrders,
      baseVault: poolState.baseVault,
      quoteVault: poolState.quoteVault,
      withdrawQueue: poolState.withdrawQueue,
      lpVault: poolState.lpVault,
      marketVersion: 3,
      marketProgramId: poolState.marketProgramId,
      marketId: poolState.marketId,
      marketAuthority: Market.getAssociatedAuthority({
        programId: poolState.marketProgramId,
        marketId: poolState.marketId,
      }).publicKey,
      marketBaseVault: marketInfo.baseVault,
      marketQuoteVault: marketInfo.quoteVault,
      marketBids: marketInfo.bids,
      marketAsks: marketInfo.asks,
      marketEventQueue: marketInfo.eventQueue,
      lookupTableAccount: PublicKey.default,
    };

    console.log("Full pool data:", poolData);

    return poolData;
  }